# engine/report_generator.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(audit_results: dict, output_filename: str = "reports/Executive_Audit_Summary.pdf"):
    """
    Generates an Executive PDF Summary report based on audit math output.
    """
    summary = audit_results.get("summary", {})
    
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#64748B'))
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=10, leading=14, fontName='Helvetica-Bold')

    story = []

    # Title & Subtitle
    story.append(Paragraph("Executive Loan Pricing Audit Summary", title_style))
    story.append(Paragraph("Automated Margin Leakage & Disparity Risk Analysis", subtitle_style))
    story.append(Spacer(1, 15))

    # High-level Metrics Table
    data = [
        [Paragraph("Metric", bold_style), Paragraph("Audit Result", bold_style)],
        ["Total Loans Audited", f"{summary.get('total_loans_audited', 0):,}"],
        ["Margin Leakage Identified ($)", f"${summary.get('total_leaked_margin_dollars', 0.0):,.2f}"],
        ["Impacted Loans (Rate Drift)", f"{summary.get('total_leaked_loans', 0):,}"],
        ["CFPB Disparity Flags (>25bps cut)", f"{summary.get('cfpb_disparity_flags', 0):,}"]
    ]

    t = Table(data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))

    # Context Section
    story.append(Paragraph("Audit Notes & Regulatory Overview", bold_style))
    story.append(Spacer(1, 6))
    narrative = (
        "This automated report evaluates secondary market execution variance against rate sheet base rates "
        "and Loan-Level Price Adjustments (LLPAs). Unbacked rate concessions exceeding 25 basis points are "
        "flagged for fair lending disparity review under CFPB compliance recommendations."
    )
    story.append(Paragraph(narrative, styles['Normal']))

    # Build PDF
    doc.build(story)
    print(f"Executive PDF report successfully generated at: {output_filename}")

if __name__ == "__main__":
    # Quick standalone test execution
    dummy_results = {
        "summary": {
            "total_loans_audited": 500,
            "total_leaked_margin_dollars": 42150.00,
            "total_leaked_loans": 75,
            "cfpb_disparity_flags": 12
        }
    }
    os.makedirs("reports", exist_ok=True)
    generate_pdf_report(dummy_results)
