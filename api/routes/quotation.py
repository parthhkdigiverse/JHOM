import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from schemas.quotation import QuotePayload

from database.models import Admin
from utils.auth import get_current_admin

router = APIRouter()

NAVY = colors.HexColor("#2E3192")
GOLD = colors.HexColor("#C5A059")

@router.post("/generate-pdf")
async def generate_pdf(
    payload: QuotePayload,
    current_admin: Admin = Depends(get_current_admin)
):
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

    def check_page_break(canv, needed):
        nonlocal current_y
        if current_y - needed < 50:
            canv.showPage()
            draw_header(canv)
            current_y = height - 120
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
            current_y = check_page_break(c, 100) 
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

    current_y = check_page_break(c, 80)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, f"Price Terms ({payload.price_term})")
    current_y -= 25
    
    c.setFont("Helvetica", 11)
    if payload.products:
        for product in payload.products:
            current_y = check_page_break(c, 20)
            formatted_price = "{:,.2f}".format(product.price)
            c.drawString(bullet_indent, current_y, f"•  {product.name}: ${formatted_price}")
            current_y -= 15
        
    current_y -= 10
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    current_y = check_page_break(c, 80)
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

    current_y = check_page_break(c, 60)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Estimated Delivery Timeline")
    current_y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(bullet_indent, current_y, f"•  {payload.delivery_mode}: {payload.timeline} (depending on vessel schedule & clearance)")
    current_y -= 40

    current_y = check_page_break(c, 30)
    c.drawString(margin, current_y, "We look forward to building a strong and successful business relationship with you.")

    c.save()
    buffer.seek(0)
    
    first_product = payload.products[0].name if payload.products else "Items"
    filename = f"Quotation_{first_product}.pdf".replace(" ", "_")
    
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(buffer, media_type='application/pdf', headers=headers)
