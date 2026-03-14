import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from schemas.proforma_invoice import ProformaPayload
from reportlab.lib.utils import simpleSplit

from database.models import Admin
from utils.auth import get_current_admin

router = APIRouter()

NAVY = colors.HexColor("#2E3192")
GOLD = colors.HexColor("#C5A059")
LIGHT_GREY = colors.HexColor("#f2f2f2")
BORDER_GREY = colors.HexColor("#dddddd")

@router.post("/generate-pdf")
async def generate_proforma_pdf(
    payload: ProformaPayload,
    current_admin: Admin = Depends(get_current_admin)
):
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

    def check_page(needed):
        nonlocal current_y
        if current_y - needed < 140:
            draw_footer_lines(c)
            c.showPage()
            draw_header(c)
            current_y = height - 120
        return current_y

    # Render Start
    draw_header(c)
    current_y = height - 120

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, current_y, "PROFORMA INVOICE")
    current_y -= 25

    # Exporter and PI Details (Stacked)
    check_page(150)
    exporter_text = [
        "JHOM EXIM WORLDWIDE LLP",
        "Surat, Gujarat, India",
        "www.jhomeximworldwide.com",
        "jhomeximworldwidellp@gmail.com",
        "+91 87800 27334"
    ]
    
    # Exporter
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, current_y, "Exporter:")
    current_y -= 12
    c.setFont("Helvetica", 10)
    for line in exporter_text:
        c.drawString(margin, current_y, line)
        current_y -= 12
        
    current_y -= 10
    
    # Invoice Info (Below Exporter)
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Proforma Invoice No: {payload.id}")
    current_y -= 13
    c.drawString(margin, current_y, f"Proforma Invoice Date: {payload.date}")
    current_y -= 13
    c.drawString(margin, current_y, f"Letter of Credit Date: {payload.lc_date}")
    current_y -= 13
    c.drawString(margin, current_y, f"Validity: {payload.validity}")
    
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 30

    # Buyer Details
    check_page(100)
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
        check_page(15)
        c.drawString(margin, current_y, line)
        current_y -= 15
    
    current_y -= 15
    # Buyer Bottom Border (Thick grey)
    c.setLineWidth(3)
    c.setStrokeColor(colors.lightgrey)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 20

    # Product Table
    check_page(100)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Product Details")
    current_y -= 20
    
    table_data = [["Sr. No", "Description", "HS Code", "Packaging", "Quantity", "Origin"]]
    for i, p in enumerate(payload.products):
        table_data.append([str(i+1), p.description, p.hs_code, p.packaging, p.quantity, p.origin])
        
    pt = Table(table_data, colWidths=[40, 150, 80, 100, 85, 60])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_GREY),
        ('GRID', (0,0), (-1,-1), 1, BORDER_GREY),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    ptw, pth = pt.wrap(width - 2*margin, height)
    pt.drawOn(c, margin, current_y - pth)
    current_y -= pth + 20

    # Incoterm & Currency
    check_page(50)
    c.setFont("Helvetica", 10)
    c.drawString(margin, current_y, f"Incoterm: {payload.incoterm}")
    current_y -= 15
    c.drawString(margin, current_y, f"Currency: {payload.currency}")
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 20

    # Detailed Blocks (Optional match to preview)
    for p in payload.products:
        check_page(80)
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
    check_page(100)
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
        check_page(15)
        c.drawString(margin, current_y, line)
        current_y -= 15
        
    current_y -= 15
    c.setLineWidth(1)
    c.setStrokeColor(colors.grey)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 25

    # Terms Sections
    def draw_sec(title, content):
        nonlocal current_y
        check_page(40 + (len(content) * 15))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, current_y, title)
        current_y -= 18
        c.setFont("Helvetica", 10)
        for line in content:
            c.drawString(margin, current_y, f"• {line}")
            current_y -= 13
        current_y -= 8
        c.setLineWidth(1)
        c.setStrokeColor(colors.lightgrey)
        c.line(margin, current_y, width - margin, current_y)
        current_y -= 15

    draw_sec("Payment Terms", [
        f"{payload.advance_pct}% Advance Payment",
        f"{payload.balance_pct}% Balance under Irrevocable L/C"
    ])
    draw_sec("Delivery & Shipment Terms", [
        f"Mode of Shipment: {payload.mode_of_shipment}",
        f"Estimated Delivery Time: {payload.delivery_time}",
        f"Port of Loading: {payload.port_of_loading}",
        f"Port of Discharge: {payload.port_of_discharge}"
    ])
    draw_sec("Packaging & Quality", [
        "Packaging: Export suitable packing",
        "Export-quality material, processed and packed under strict quality control",
        "Compliance with international export standards"
    ])
    
    # Declaration
    check_page(100)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "Declaration")
    current_y -= 20
    c.setFont("Helvetica", 10)
    dec = "We hereby certify that the goods mentioned above are of Indian origin. The prices and terms stated above are true and correct and agreed mutually between buyer and seller."
    for line in simpleSplit(dec, "Helvetica", 10, width - 2*margin):
        check_page(15)
        c.drawString(margin, current_y, line)
        current_y -= 15

    # Signature (Only Last Page)
    current_y -= 60
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
    filename = f"Proforma_Invoice_{payload.id}.pdf".replace("/", "_")
    return StreamingResponse(buffer, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="{filename}"'})
