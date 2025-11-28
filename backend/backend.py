"""
Simple Payroll Backend (FastAPI + ReportLab)
--------------------------------------------
Run locally:
    pip install fastapi uvicorn reportlab pydantic python-multipart
    uvicorn main:app --reload --port 8000
"""

from datetime import datetime
from io import BytesIO
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

app = FastAPI(title="Payroll API")

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PayrollRequest(BaseModel):
    employeeId: str
    employeeName: str
    payPeriodStart: str
    payPeriodEnd: str
    hoursWorked: float
    hourlyRate: float
    taxRatePercent: float
    deductions: float = 0.0
    notes: str | None = None

def generate_pdf(data: PayrollRequest) -> BytesIO:
    gross = data.hoursWorked * data.hourlyRate
    taxes = gross * (data.taxRatePercent / 100)
    net = gross - taxes - data.deductions

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    w, h = LETTER

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, h-1*inch, "Payroll Statement")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, h-1.3*inch, f"Generated: {datetime.now()}")

    y = h-1.8*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Employee Info")
    c.setFont("Helvetica", 11)
    y -= 0.25*inch
    c.drawString(1*inch, y, f"ID: {data.employeeId}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Name: {data.employeeName}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Period: {data.payPeriodStart} → {data.payPeriodEnd}")

    y -= 0.4*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Pay Summary")
    c.setFont("Helvetica", 11)
    y -= 0.25*inch
    c.drawString(1*inch, y, f"Hours: {data.hoursWorked}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Rate: {data.hourlyRate}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Gross: {gross:.2f}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Taxes: {taxes:.2f}")
    y -= 0.2*inch
    c.drawString(1*inch, y, f"Deductions: {data.deductions:.2f}")
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, f"Net Pay: {net:.2f}")

    if data.notes:
        y -= 0.4*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Notes")
        y -= 0.25*inch
        c.setFont("Helvetica", 11)
        c.drawString(1*inch, y, data.notes)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

@app.post("/api/payroll")
def payroll(data: PayrollRequest):
    pdf = generate_pdf(data)
    headers = {"Content-Disposition": f'attachment; filename="Payroll_{data.employeeId}.pdf"'}
    return StreamingResponse(pdf, media_type="application/pdf", headers=headers)

@app.get("/health")
def health():
    return {"status": "ok"}
