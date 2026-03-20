import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from schemas.quotation import QuotePayload, QuotationResponse, ProductItem
from database.models import Admin, Quotation, Buyer
from utils.auth import get_current_admin
from reportlab.pdfbase.pdfmetrics import stringWidth

router = APIRouter()

NAVY = colors.HexColor("#2E3192")
GOLD = colors.HexColor("#C5A059")

# ==========================================
#  HELPERS
# ==========================================

def get_pdf_buffer(payload):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    margin_x = 50
    margin_top = 40
    margin_bottom = 50

    y = height - 110

    content_width = width - (2 * margin_x)

    # COLORS
    NAVY = colors.HexColor("#2E3192")
    GOLD = colors.HexColor("#C5A059")
    LINK_BLUE = colors.HexColor("#1A73E8")

    # LINE HEIGHTS (VERY IMPORTANT)
    LINE_11 = 14
    LINE_12 = 16
    LINE_13 = 18

    # ---------------- HEADER ----------------
    def draw_header(canv):
        # LEFT TITLE
        canv.setFont("Times-Bold", 16)
        canv.setFillColor(GOLD)
        canv.drawString(margin_x, height - margin_top - 14, "JHOM EXIM WORLDWIDE LLP")

        canv.setFont("Times-Italic", 12)
        canv.setFillColor(colors.black)
        canv.drawString(margin_x, height - margin_top - 30, '"Three Minds, One Vision."')

        # RIGHT SIDE
        canv.setFont("Times-Roman", 9)
        right_y = height - margin_top

        canv.drawRightString(width - margin_x, right_y, "478, AR Mall, Mota Varachha, Surat, Gujarat")
        canv.drawRightString(width - margin_x, right_y - 12, "India - 394101")
        canv.drawRightString(width - margin_x, right_y - 24, "www.jhomeximworldwide.com")
        c.setFillColor(LINK_BLUE)
        canv.drawRightString(width - margin_x, right_y - 36, "sales@jhomeximworldwide.com")


        # LINES
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(3)
        canv.line(margin_x, height - 85, width - margin_x, height - 85)

        canv.setStrokeColor(GOLD)
        canv.setLineWidth(1.5)
        canv.line(margin_x, height - 90, width - margin_x, height - 90)

    def check_page_break(y, needed=80):
        if y - needed < margin_bottom:
            c.showPage()
            draw_header(c)
            return height - 110
        return y

    draw_header(c)

    # ---------------- GREETING ----------------
    c.setFillColor(colors.black)
    c.setFont("Times-Bold", 11)
    c.drawString(margin_x, y, "Greetings from JHOM EXIM WORLDWIDE LLP!")
    y -= LINE_12

    c.setFont("Times-Roman", 10)
    c.drawString(margin_x, y, "We are pleased to offer you a quotation for the export of premium-quality Cardamom,as per your interest.")
    y -= LINE_11
    c.drawString(margin_x, y, "Please find the detailed proposal below.")
    y -= 20

    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # ---------------- PRODUCT DETAILS ----------------
    c.setFont("Times-Bold", 13)
    c.drawString(margin_x, y, "Product Details")
    y -= 20

    for i, product in enumerate(payload.products):
        y = check_page_break(y)

        c.setFont("Times-Bold", 11)
        c.drawString(margin_x, y, f"{i+1}. {product.name}")
        y -= LINE_11

        c.setFont("Times-Roman", 11)
        c.drawString(margin_x + 20, y, f"• Quantity: {product.quantity}")
        y -= LINE_11
        c.drawString(margin_x + 20, y, f"• Packaging: {product.packaging}")
        y -= LINE_11
        c.drawString(margin_x + 20, y, f"• Grade: {product.grade}")
        y -= LINE_11
        c.drawString(margin_x + 20, y, f"• Origin: {product.origin}")
        y -= 18

    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # ---------------- PRICE TERMS ----------------
    c.setFont("Times-Bold", 13)
    c.drawString(margin_x, y, f"Price Terms ({payload.price_term})")
    y -= 20

    c.setFont("Times-Roman", 11)
    for product in payload.products:
        price = "{:,.2f}".format(product.price)
        c.drawString(margin_x + 20, y, f"• {product.name}: ${price}")
        y -= LINE_11

    y -= 10
    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # ---------------- PAYMENT TERMS ----------------
    c.setFont("Times-Bold", 13)
    c.drawString(margin_x, y, "Payment Terms")
    y -= 20

    c.setFont("Times-Roman", 11)
    c.drawString(margin_x + 20, y, f"• {payload.advance_pct}% Advance of total value upon confirmation")
    y -= LINE_11
    c.drawString(margin_x + 20, y, f"• {payload.balance_pct}% Balance via Irrevocable LC at sight")
    y -= 20

    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # ---------------- DELIVERY ----------------
    c.setFont("Times-Bold", 13)
    c.drawString(margin_x, y, "Estimated Delivery Timeline")
    y -= 20

    c.setFont("Times-Roman", 11)
    c.drawString(margin_x + 20, y, f"• {payload.delivery_mode}: {payload.timeline} (depending on vessel schedule & clearance)")
    y -= 30

    # ---------------- CLOSING ----------------
    c.drawString(margin_x, y, "We look forward to building a strong and successful business relationship with you.")
    y -= 30

    # ---------------- SIGNATURE ----------------
    c.setFont("Times-Roman", 11)
    c.drawString(margin_x, y, "Warm regards,")
    y -= 12

    c.setFont("Times-Bold", 11)
    c.drawString(margin_x, y, "Jeel A Borad")
    y -= 12

    c.setFont("Times-Roman", 10)
    c.drawString(margin_x, y, "CEO & Founder")
    y -= 20
    c.drawString(margin_x, y, "+91 87800 27334")
    y -= 12

    c.setFillColor(LINK_BLUE)
    c.setStrokeColor(LINK_BLUE)

    c.drawString(margin_x, y, "jhomeximworldwidellp@gmail.com")
    c.line(margin_x, y - 2, margin_x + stringWidth("jhomeximworldwidellp@gmail.com", c._fontname, c._fontsize), y - 2)
    y -= 20
    c.drawString(margin_x, y, "www.jhomeximworldwide.com")
    c.line(margin_x, y - 2, margin_x + stringWidth("www.jhomeximworldwide.com", c._fontname, c._fontsize), y - 2)

    y -= 12
    c.setFillColor(colors.black)
    c.setFont("Times-Bold", 10)
    c.drawString(margin_x, y, "JHOM EXIM WORLDWIDE LLP")
    y -= 12

    c.setFont("Times-Roman", 9)
    c.drawString(margin_x, y, "Surat, Gujarat, India.")

    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
#  ROUTES
# ==========================================

@router.post("/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    payload: QuotePayload,
    current_admin: Admin = Depends(get_current_admin)
):
    buyer = None
    if payload.buyer_id:
        buyer = await Buyer.get(payload.buyer_id)
    
    new_quote = Quotation(
        buyer_id=buyer,
        products=[p.model_dump() for p in payload.products],
        price_term=payload.price_term,
        advance_pct=payload.advance_pct,
        balance_pct=payload.balance_pct,
        delivery_mode=payload.delivery_mode,
        timeline=payload.timeline,
        created_by=current_admin
    )
    await new_quote.insert()
    return new_quote

@router.get("/", response_model=List[QuotationResponse])
async def list_quotations(
    current_admin: Admin = Depends(get_current_admin)
):
    return await Quotation.find_all().sort("-created_at").to_list()

@router.get("/{quote_id}", response_model=QuotationResponse)
async def get_quotation(
    quote_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    quote = await Quotation.get(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quote

@router.put("/{quote_id}", response_model=QuotationResponse)
async def update_quotation(
    quote_id: PydanticObjectId,
    payload: QuotePayload,
    current_admin: Admin = Depends(get_current_admin)
):
    quote = await Quotation.get(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    buyer = None
    if payload.buyer_id:
        buyer = await Buyer.get(payload.buyer_id)

    quote.buyer_id = buyer
    quote.products = [p.model_dump() for p in payload.products]
    quote.price_term = payload.price_term
    quote.advance_pct = payload.advance_pct
    quote.balance_pct = payload.balance_pct
    quote.delivery_mode = payload.delivery_mode
    quote.timeline = payload.timeline
    quote.updated_at = datetime.utcnow()
    
    await quote.save()
    return quote

@router.delete("/{quote_id}")
async def delete_quotation(
    quote_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    quote = await Quotation.get(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    await quote.delete()
    return {"message": "Quotation deleted"}

@router.post("/generate-pdf")
async def generate_pdf(
    payload: QuotePayload,
    current_admin: Admin = Depends(get_current_admin)
):
    buffer = get_pdf_buffer(payload)
    
    first_product = payload.products[0].name if payload.products else "Items"
    filename = f"Quotation_{first_product}.pdf".replace(" ", "_")
    
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(buffer, media_type='application/pdf', headers=headers)

@router.get("/{quote_id}/pdf")
async def generate_saved_pdf(
    quote_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    quote = await Quotation.get(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Map model to payload
    payload = QuotePayload(
        buyer_id=str(quote.buyer_id.id) if quote.buyer_id else None,
        products=[ProductItem(**p) for p in quote.products],
        price_term=quote.price_term,
        advance_pct=quote.advance_pct,
        balance_pct=quote.balance_pct,
        delivery_mode=quote.delivery_mode,
        timeline=quote.timeline
    )
    
    buffer = get_pdf_buffer(payload)
    filename = f"Quotation_{quote_id}.pdf"
    
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(buffer, media_type='application/pdf', headers=headers)
