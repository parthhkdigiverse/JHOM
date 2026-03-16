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

router = APIRouter()

NAVY = colors.HexColor("#2E3192")
GOLD = colors.HexColor("#C5A059")

# ==========================================
#  HELPERS
# ==========================================

def get_pdf_buffer(payload: QuotePayload):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    current_y = height - 40

    def draw_header(canv):
        # Gold Logo (Left)
        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(GOLD)
        canv.drawString(margin, height - 40, "JHOM EXIM")
        canv.drawString(margin, height - 58, "WORLDWIDE LLP")
        
        # Contact Info (Right)
        canv.setFont("Helvetica", 9)
        canv.setFillColor(colors.black)
        canv.drawRightString(width - margin, height - 40, "478, AR Mal, Mota Varachha, Surat,")
        canv.drawRightString(width - margin, height - 52, "Gujarat, India-394101.")
        canv.drawRightString(width - margin, height - 64, "https://jhomeximworldwide.com")
        canv.drawRightString(width - margin, height - 76, "ceo@jhomeximworldwide.com")
        
        # Header Lines
        canv.setLineWidth(4)
        canv.setStrokeColor(NAVY)
        canv.line(margin, height - 90, width - margin, height - 90)
        canv.setLineWidth(2)
        canv.setStrokeColor(GOLD)
        canv.line(margin, height - 96, width - margin, height - 96)

    def check_page_break(canv, needed, current_y):
        if current_y - needed < 50:
            canv.showPage()
            draw_header(canv)
            return height - 120
        return current_y

    # Initial Header and Start Y
    draw_header(c)
    current_y = height - 130

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin, current_y, "Greetings from JHOM EXIM WORLDWIDE LLP!")
    current_y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(margin, current_y, "We are pleased to offer you a quotation for the export of premium-quality products.")
    current_y -= 15
    c.drawString(margin, current_y, "Please find the detailed proposal below.")
    current_y -= 25
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Product Details")
    current_y -= 25

    bullet_indent = margin + 20
    
    if payload.products:
        for i, product in enumerate(payload.products):
            current_y = check_page_break(c, 100, current_y) 
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin, current_y, f"{i+1}. {product.name}")
            current_y -= 20
            c.setFont("Helvetica", 11)
            c.drawString(bullet_indent, current_y, f"•  Quantity: {product.quantity}")
            current_y -= 15
            c.drawString(bullet_indent, current_y, f"•  Packaging: {product.packaging}")
            current_y -= 15
            c.drawString(bullet_indent, current_y, f"•  Grade: {product.grade}")
            current_y -= 15
            c.drawString(bullet_indent, current_y, f"•  Origin: {product.origin}")
            current_y -= 25

    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    current_y = check_page_break(c, 80, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, f"Price Terms ({payload.price_term})")
    current_y -= 25
    
    c.setFont("Helvetica", 11)
    if payload.products:
        for product in payload.products:
            current_y = check_page_break(c, 20, current_y)
            formatted_price = "{:,.2f}".format(product.price)
            c.drawString(bullet_indent, current_y, f"•  {product.name}: ${formatted_price}")
            current_y -= 15
        
    current_y -= 10
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    current_y = check_page_break(c, 80, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Payment Terms") 
    current_y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(bullet_indent, current_y, f"•  {payload.advance_pct}% Advance of the total {payload.price_term} Value upon order confirmation")
    current_y -= 15
    c.drawString(bullet_indent, current_y, f"•  {payload.balance_pct}% Balance under Irrevocable Letter of Credit (LC) at sight")
    current_y -= 25
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    current_y = check_page_break(c, 60, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Estimated Delivery Timeline")
    current_y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(bullet_indent, current_y, f"•  {payload.delivery_mode}: {payload.timeline} (depending on vessel schedule & clearance)")
    current_y -= 40

    current_y = check_page_break(c, 30, current_y)
    c.drawString(margin, current_y, "We look forward to building a strong and successful business relationship with you.")

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
