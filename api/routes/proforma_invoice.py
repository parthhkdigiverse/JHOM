import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import simpleSplit
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from schemas.proforma_invoice import ProformaPayload, ProformaInvoiceResponse, ProformaItem
from database.models import Admin, ProformaInvoice, Buyer, Quotation
from utils.auth import get_current_admin

router = APIRouter()

NAVY = colors.HexColor("#2E3192")
GOLD = colors.HexColor("#C5A059")
LIGHT_GREY = colors.HexColor("#f2f2f2")
BORDER_GREY = colors.HexColor("#dddddd")

# ==========================================
#  HELPERS
# ==========================================

def get_proforma_buffer(payload: ProformaPayload):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setPageCompression(1)
    width, height = A4
    margin = 40
    
    current_y = height - 40

    def draw_header(canv):
        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(GOLD)
        canv.drawString(margin, height - 40, "JHOM EXIM")
        canv.drawString(margin, height - 58, "WORLDWIDE LLP")
        
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

    def draw_footer_lines(canv):
        canv.setLineWidth(4)
        canv.setStrokeColor(NAVY)
        canv.line(margin, 40, width - margin, 40)
        canv.setLineWidth(2)
        canv.setStrokeColor(GOLD)
        canv.line(margin, 46, width - margin, 46)

    def check_page(canv, needed, current_y):
        if current_y - needed < 140:
            draw_footer_lines(canv)
            canv.showPage()
            draw_header(canv)
            return height - 120
        return current_y

    # Render Start
    draw_header(c)
    current_y = height - 120

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, current_y, "PROFORMA INVOICE")
    current_y -= 25

    # Exporter
    current_y = check_page(c, 150, current_y)
    exporter_text = ["JHOM EXIM WORLDWIDE LLP", "Surat, Gujarat, India", "www.jhomeximworldwide.com", "jhomeximworldwidellp@gmail.com", "+91 87800 27334"]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, current_y, "Exporter:")
    current_y -= 12
    c.setFont("Helvetica", 10)
    for line in exporter_text:
        c.drawString(margin, current_y, line)
        current_y -= 12
    current_y -= 10
    
    # Invoice Info
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Proforma Invoice No: {payload.invoice_no}")
    current_y -= 13
    c.drawString(margin, current_y, f"Proforma Invoice Date: {payload.date}")
    current_y -= 13
    if payload.lc_date:
        c.drawString(margin, current_y, f"Letter of Credit Date: {payload.lc_date}")
        current_y -= 13
    if payload.validity:
        c.drawString(margin, current_y, f"Validity: {payload.validity}")
        current_y -= 13
    
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    # Buyer
    current_y = check_page(c, 100, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Buyer Details")
    current_y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, current_y, "Company Name:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, payload.buyer_name)
    current_y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, current_y, "Registered Address:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    addr_lines = simpleSplit(payload.buyer_address, "Helvetica", 10, width - 2*margin)
    for line in addr_lines:
        current_y = check_page(c, 15, current_y)
        c.drawString(margin, current_y, line)
        current_y -= 15
    current_y -= 15
    c.setLineWidth(3)
    c.setStrokeColor(colors.lightgrey)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 20

    # Table
    current_y = check_page(c, 100, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Product Details")
    current_y -= 20
    table_data = [["Sr. No", "Description", "HS Code", "Packaging", "Quantity", "Origin"]]
    for i, p in enumerate(payload.products):
        table_data.append([str(i+1), p.description, p.hs_code, p.packaging, p.quantity, p.origin])
    pt = Table(table_data, colWidths=[40, 150, 80, 100, 85, 60])
    pt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), LIGHT_GREY),('GRID', (0,0), (-1,-1), 1, BORDER_GREY),('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),('FONTSIZE', (0,0), (-1,-1), 9),('ALIGN', (0,0), (-1,-1), 'LEFT'),('VALIGN', (0,0), (-1,-1), 'MIDDLE'),('PADDING', (0,0), (-1,-1), 5)]))
    ptw, pth = pt.wrap(width - 2*margin, height)
    pt.drawOn(c, margin, current_y - pth)
    current_y -= pth + 20

    # Totals/Summary
    current_y = check_page(c, 50, current_y)
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Incoterm: {payload.incoterm}")
    current_y -= 15
    c.drawString(margin, current_y, f"Currency: {payload.currency}")
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 20

    for p in payload.products:
        current_y = check_page(c, 80, current_y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, current_y, p.description)
        current_y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(margin, current_y, f"Quantity: {p.quantity}")
        current_y -= 12
        c.drawString(margin, current_y, f"Rate: {payload.currency} {p.rate:,.2f} / Unit")
        current_y -= 12
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, current_y, f"Total: {payload.currency} {p.total:,.2f}")
        current_y -= 15
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.lightgrey)
        c.line(margin, current_y, width - margin, current_y)
        current_y -= 20

    # Grand Total
    current_y = check_page(c, 100, current_y)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, f"Grand Total {payload.incoterm} Value")
    current_y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, f"{payload.currency} {payload.grand_total:,.2f}")
    current_y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, current_y, "Amount in Words:")
    current_y -= 15
    c.setFont("Helvetica", 10)
    words = simpleSplit(payload.amount_in_words, "Helvetica", 10, width - 2*margin)
    for line in words:
        current_y = check_page(c, 15, current_y)
        c.drawString(margin, current_y, line)
        current_y -= 15
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.grey)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25

    # Signature
    current_y = check_page(c, 120, current_y)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, current_y, "For JHOM EXIM WORLDWIDE LLP")
    current_y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, "Authorized Signatory")
    current_y -= 12
    c.drawString(margin, current_y, "Jeel A. Borad")
    current_y -= 12
    c.drawString(margin, current_y, "CEO & Founder")

    draw_footer_lines(c)
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
#  ROUTES
# ==========================================

@router.post("/", response_model=ProformaInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_proforma(
    payload: ProformaPayload,
    current_admin: Admin = Depends(get_current_admin)
):
    buyer = await Buyer.get(payload.buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
        
    new_pi = ProformaInvoice(
        invoice_no=payload.invoice_no,
        date=payload.date,
        lc_date=payload.lc_date,
        validity=payload.validity,
        buyer_id=buyer,
        buyer_name=payload.buyer_name,
        buyer_address=payload.buyer_address,
        products=[p.model_dump() for p in payload.products],
        incoterm=payload.incoterm,
        currency=payload.currency,
        advance_pct=payload.advance_pct,
        balance_pct=payload.balance_pct,
        mode_of_shipment=payload.mode_of_shipment,
        delivery_time=payload.delivery_time,
        port_of_loading=payload.port_of_loading,
        port_of_discharge=payload.port_of_discharge,
        amount_in_words=payload.amount_in_words,
        grand_total=payload.grand_total,
        created_by=current_admin
    )
    await new_pi.insert()
    return new_pi

@router.post("/convert/{quote_id}", response_model=ProformaInvoiceResponse)
async def convert_quotation_to_proforma(
    quote_id: PydanticObjectId,
    invoice_no: str,
    current_admin: Admin = Depends(get_current_admin)
):
    quote = await Quotation.get(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
        
    if not quote.buyer_id:
        raise HTTPException(status_code=400, detail="Quotation must have a buyer to convert")
    
    buyer = await quote.buyer_id.fetch()
    
    # Pre-calculate totals for items
    converted_items = []
    grand_total = 0
    for p in quote.products:
        item_total = float(p.get('price', 0)) # Placeholder calculation
        converted_items.append({
            "description": p.get('name'),
            "hs_code": "TBD",
            "packaging": p.get('packaging'),
            "quantity": p.get('quantity'),
            "origin": p.get('origin'),
            "rate": p.get('price'),
            "total": item_total
        })
        grand_total += item_total

    new_pi = ProformaInvoice(
        invoice_no=invoice_no,
        date=datetime.now().strftime("%Y-%m-%d"),
        buyer_id=buyer,
        buyer_name=buyer.company_name,
        buyer_address=buyer.address or "",
        products=converted_items,
        incoterm=quote.price_term,
        currency="USD",
        advance_pct=quote.advance_pct,
        balance_pct=quote.balance_pct,
        mode_of_shipment=quote.delivery_mode,
        delivery_time=quote.timeline,
        port_of_loading="Surat/Mundra",
        port_of_discharge="TBD",
        amount_in_words="TBD",
        grand_total=grand_total,
        created_by=current_admin,
        quotation_id=quote
    )
    
    quote.status = "converted"
    await quote.save()
    await new_pi.insert()
    return new_pi

@router.get("/", response_model=List[ProformaInvoiceResponse])
async def list_proformas(
    current_admin: Admin = Depends(get_current_admin)
):
    return await ProformaInvoice.find_all().sort("-created_at").to_list()

@router.get("/{pi_id}", response_model=ProformaInvoiceResponse)
async def get_proforma(
    pi_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    pi = await ProformaInvoice.get(pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Proforma Invoice not found")
    return pi

@router.delete("/{pi_id}")
async def delete_proforma(
    pi_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    pi = await ProformaInvoice.get(pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Proforma Invoice not found")
    await pi.delete()
    return {"message": "Proforma Invoice deleted"}

@router.post("/generate-pdf")
async def generate_pdf(
    payload: ProformaPayload,
    current_admin: Admin = Depends(get_current_admin)
):
    buffer = get_proforma_buffer(payload)
    filename = f"Proforma_Invoice_{payload.invoice_no}.pdf".replace("/", "_")
    return StreamingResponse(buffer, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="{filename}"'})

@router.get("/{pi_id}/pdf")
async def generate_saved_pi_pdf(
    pi_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    pi = await ProformaInvoice.get(pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Proforma Invoice not found")
    
    payload = ProformaPayload(
        invoice_no=pi.invoice_no,
        date=pi.date,
        lc_date=pi.lc_date,
        validity=pi.validity,
        buyer_id=str(pi.buyer_id.id),
        buyer_name=pi.buyer_name,
        buyer_address=pi.buyer_address,
        products=[ProformaItem(**p) for p in pi.products],
        incoterm=pi.incoterm,
        currency=pi.currency,
        advance_pct=pi.advance_pct,
        balance_pct=pi.balance_pct,
        mode_of_shipment=pi.mode_of_shipment,
        delivery_time=pi.delivery_time,
        port_of_loading=pi.port_of_loading,
        port_of_discharge=pi.port_of_discharge,
        amount_in_words=pi.amount_in_words,
        grand_total=pi.grand_total
    )
    
    buffer = get_proforma_buffer(payload)
    filename = f"Proforma_Invoice_{pi.invoice_no}.pdf"
    
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(buffer, media_type='application/pdf', headers=headers)
