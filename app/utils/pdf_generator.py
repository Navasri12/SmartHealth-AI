import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_prediction_pdf(prediction, user, patient_profile, disease_info, output_path):
    """Generates a professional PDF health summary report for a given prediction."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#198754'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#212529')
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#842029')
    )

    story = []

    # Header section
    story.append(Paragraph("SmartHealth AI — Patient Assessment Summary", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')} | System Version: {prediction.model_version}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d6efd'), spaceAfter=15))

    # Patient Information Table
    patient_data = [
        [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(user.name, body_style),
         Paragraph("<b>Assessment ID:</b>", body_style), Paragraph(f"SH-{prediction.id:05d}", body_style)],
        [Paragraph("<b>Email:</b>", body_style), Paragraph(user.email, body_style),
         Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(user.date_of_birth or 'N/A', body_style)],
        [Paragraph("<b>Gender:</b>", body_style), Paragraph(user.gender or 'N/A', body_style),
         Paragraph("<b>Blood Group:</b>", body_style), Paragraph(patient_profile.blood_group if patient_profile else 'N/A', body_style)],
        [Paragraph("<b>Height / Weight:</b>", body_style), Paragraph(f"{patient_profile.height or 'N/A'} cm / {patient_profile.weight or 'N/A'} kg" if patient_profile else 'N/A', body_style),
         Paragraph("<b>Known Allergies:</b>", body_style), Paragraph(patient_profile.allergies if patient_profile and patient_profile.allergies else 'None reported', body_style)]
    ]

    p_table = Table(patient_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 15))

    # Assessment Result Box
    story.append(Paragraph("AI Assessment Results", h2_style))
    
    result_data = [
        [Paragraph("<b>Possible Health Condition:</b>", body_style), Paragraph(f"<font color='#0d6efd'><b>{prediction.predicted_disease}</b></font>", body_style)],
        [Paragraph("<b>Model Confidence Probability:</b>", body_style), Paragraph(f"<b>{prediction.probability}%</b>", body_style)],
        [Paragraph("<b>Overall Severity Risk Level:</b>", body_style), Paragraph(prediction.severity_score or 'Moderate', body_style)]
    ]
    r_table = Table(result_data, colWidths=[2.2*inch, 4.8*inch])
    r_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e7f1ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#9ec5fe')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b6d4fe')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(r_table)
    story.append(Spacer(1, 15))

    # Selected Symptoms Table
    story.append(Paragraph("Analyzed Symptoms", h2_style))
    sym_headers = [Paragraph("<b>Symptom Name</b>", body_style), Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Duration</b>", body_style)]
    sym_rows = [sym_headers]

    for ps in prediction.selected_symptoms:
        sym_rows.append([
            Paragraph(ps.symptom_name, body_style),
            Paragraph(ps.severity or 'Moderate', body_style),
            Paragraph(ps.duration or '1-3 days', body_style)
        ])

    s_table = Table(sym_rows, colWidths=[3.2*inch, 1.9*inch, 1.9*inch])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e9ecef')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ced4da')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 15))

    # Health Guidance & Disease Overview
    if disease_info:
        story.append(Paragraph("Condition Overview & Guidance", h2_style))
        story.append(Paragraph(f"<b>Description:</b> {disease_info.description}", body_style))
        story.append(Spacer(1, 4))
        if disease_info.prevention:
            story.append(Paragraph(f"<b>Prevention & Self-Care:</b> {disease_info.prevention}", body_style))
            story.append(Spacer(1, 4))
        if disease_info.recommendations:
            story.append(Paragraph(f"<b>General Recommendations:</b> {disease_info.recommendations}", body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))

    # Immediate Precautions & Patient Next Steps
    from app.ml.predictor import predictor_service
    selected_symptoms_dict = {
        ps.symptom_code: {'severity': ps.severity, 'duration': ps.duration}
        for ps in prediction.selected_symptoms
    }
    precautions = predictor_service.get_immediate_precautions(prediction.predicted_disease, selected_symptoms_dict)

    if precautions:
        story.append(Paragraph("Immediate Precautions & Patient Next Steps", h2_style))
        prec_rows = [[Paragraph("<b>Precautions Category</b>", body_style), Paragraph("<b>Actionable Instruction</b>", body_style)]]
        for prec in precautions:
            prec_rows.append([
                Paragraph(f"<b>{prec['title']}</b>", body_style),
                Paragraph(prec['detail'], body_style)
            ])
        prec_table = Table(prec_rows, colWidths=[2.3*inch, 4.7*inch])
        prec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fff3cd')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ffe69c')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(prec_table)
        story.append(Spacer(1, 15))


    # Medical Disclaimer Box
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#f5c2c7'), spaceAfter=8))
    disclaimer_text = (
        "<b>IMPORTANT MEDICAL DISCLAIMER:</b> SmartHealth AI is an educational and decision-support application. "
        "The predictions and health insights contained in this document DO NOT constitute a professional medical diagnosis, "
        "treatment plan, or prescription. Always consult a qualified physician or healthcare provider for medical evaluation, "
        "diagnosis, and treatment. If you experience severe symptoms such as chest pain or breathing difficulty, seek emergency care immediately."
    )
    disc_table = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[7.0*inch])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8d7da')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f5c2c7')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(disc_table)

    doc.build(story)
    return output_path
