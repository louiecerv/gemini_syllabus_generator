from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import streamlit as st

def process_markdown(markdown_text):
    table_data = []
    paragraphs = []

    lines = markdown_text.split("\n")
    is_table = False
    for line in lines:
        if "|" in line and not line.strip().startswith("---"):
            columns = line.split("|")
            columns = [col.strip() for col in columns if col.strip()]
            # Check if the row is not just line separators
            if any(col != "---" for col in columns) and not all(col == "---" for col in columns):
                table_data.append(columns)
                is_table = True
        elif is_table:
            break

    if not table_data:
        table_data = None

    for line in lines:
        if "|" not in line and line.strip():
            line = line.strip()
            if line.startswith("#"):
                line = "<b>" + line.lstrip("#").strip() + "</b>"
            paragraphs.append(line)

    return table_data, paragraphs

def create_pdf(data, paragraphs, topic):

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    filepath = temp_file.name

    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch,
                                                        bottomMargin=inch)
    elements = []

    page_width, page_height = landscape(A4)
    available_width = page_width - (doc.leftMargin + doc.rightMargin)

    styles = getSampleStyleSheet()

    for index, paragraph_text in enumerate(paragraphs):
        if index == 0 and paragraph_text.startswith("Module"):
            paragraph = Paragraph(paragraph_text, styles['h1']) 
        else:
            paragraph = Paragraph(paragraph_text, styles['Normal'])
        elements.append(paragraph)
        elements.append(Spacer(1, 12)) 

    if not data or not data[0]:
        return filepath

    else:
        num_columns = len(data[0])
        col_widths = [available_width / num_columns] * num_columns

        wrapped_data = [[Paragraph(cell, styles['Normal']) for cell in row] for row in data]

        table = Table(wrapped_data, colWidths=col_widths)

        style = TableStyle([
            # Set no shading by default. To add shading, change 'None' to a color, e.g., 'colors.grey' or any other color.
            ('BACKGROUND', (0, 0), (-1, 0), None),  # No shading on the header row
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), None),  # No shading on the body rows
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), 'ON')
        ])
        table.setStyle(style)
        elements.append(table)

        # Add a 0.5 inch spacer
        elements.append(Spacer(1, 0.5 * inch))  # 0.5 inches

        footer = Paragraph("Generated using the OBE Syllabus Maker created by the WVSU AI Dev Team (c) 2025.", styles['Normal'])
        elements.append(footer)

        doc.build(elements)
        return filepath