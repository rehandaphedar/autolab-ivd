#!/usr/bin/env python3
import glob
import json
import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

metrics_dir = sys.argv[1]
rejected_dir = sys.argv[2]
output_pdf = sys.argv[3]

passed_records = []
for f in sorted(glob.glob(os.path.join(metrics_dir, "*.json"))):
    with open(f, "r") as fp:
        passed_records.append(json.load(fp))

rejected_records = []
for f in sorted(glob.glob(os.path.join(rejected_dir, "*.json"))):
    batch_id = Path(f).name.replace("_qc.json", "")
    with open(f, "r") as fp:
        data = json.load(fp)
        data["batch_id"] = batch_id
        rejected_records.append(data)

c = canvas.Canvas(output_pdf, pagesize=letter)
width, height = letter

c.setFillColor(colors.HexColor("#1A365D"))  # Deep Clinical Navy
c.rect(0, height - 75, width, 75, fill=1, stroke=0)

c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 16)
c.drawString(40, height - 42, "INSTITUT FÜR LABORATORIUMSMEDIZIN")
c.setFont("Helvetica", 9)
c.drawString(
    40, height - 58, "Automated Diagnostic Pipeline & Batch Verification Report"
)

y = height - 110
c.setFillColor(colors.HexColor("#2D3748"))
c.setFont("Helvetica-Bold", 12)
c.drawString(40, y, "1. Quality Control & Accession Summary")

y -= 18
c.setFont("Helvetica", 10)
c.drawString(
    50, y, f"Total Batches Evaluated: {len(passed_records) + len(rejected_records)}"
)
y -= 15
c.drawString(
    50,
    y,
    f"Passed Batches: {len(passed_records)}  |  Rejected Batches: {len(rejected_records)}",
)

y -= 25
c.setFont("Helvetica-Bold", 10)
c.drawString(50, y, "QC Failure Audit Log:")
y -= 15
c.setFont("Helvetica", 9)

if rejected_records:
    for r in rejected_records:
        hemolysis = r.get("mean_hemolysis", "N/A")
        status = r.get("status", "REJECTED")
        c.setFillColor(colors.HexColor("#C53030"))  # Crimson Red
        c.drawString(
            60,
            y,
            f"• [{r['batch_id']}] STATUS: {status} (Mean Hemolysis Index: {hemolysis})",
        )
        y -= 15
else:
    c.setFillColor(colors.black)
    c.drawString(60, y, "• No batch failures recorded.")
    y -= 15

y -= 20
c.setFillColor(colors.HexColor("#2D3748"))
c.setFont("Helvetica-Bold", 12)
c.drawString(40, y, "2. Diagnostic Model Verification (Passed Batches Only)")

c.setFont("Helvetica", 9)
c.setFillColor(colors.black)

for p in passed_records:
    y -= 22
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        50,
        y,
        f"Batch: {p.get('batch_id', 'Unknown')} (Samples Analyzed: {p.get('samples_trained', 'N/A')})",
    )

    y -= 15
    c.setFont("Helvetica", 9)
    c.drawString(65, y, f"• Accuracy: {p.get('accuracy', 0.0):.4f}")
    y -= 14
    c.drawString(65, y, f"• Intercept: {p.get('intercept', 0.0):.4f}")

    coeffs = p.get("coefficients", {})
    coeff_str = ", ".join([f"{k}: {v:.4f}" for k, v in coeffs.items()])
    y -= 14
    c.drawString(65, y, f"• Feature Coefficients: {coeff_str}")

c.setFont("Helvetica-Oblique", 8)
c.setFillColor(colors.gray)
c.drawString(
    40,
    35,
    "DIN EN ISO 15189 Validated Execution | Generated automatically via Nextflow DSL2",
)

c.showPage()
c.save()
