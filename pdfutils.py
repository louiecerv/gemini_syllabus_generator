from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import streamlit as st

def process_markdown(markdown_text):
    """
    Processes markdown formatted text to extract table data and paragraph data.
    Handles cases where the text may or may not contain a table.

    Args:
        markdown_text: The markdown formatted text.

    Returns:
        A tuple containing:
            - table_data: A list of lists representing the table data, or None if no table is found.
            - paragraph_data: A list of strings representing the paragraph data.
    """

    table_data = []
    paragraphs = []

    # Extract table data if it exists
    lines = markdown_text.split("\n")
    is_table = False  # Flag to track if we are currently processing a table
    for line in lines:
        if "|" in line:
            is_table = True
            columns = line.split("|")
            columns = [col.strip() for col in columns]
            table_data.append(columns)
        elif is_table:  # If previous line was part of the table, but this one isn't
            break  # Stop processing the table

    # If no table data was found, set table_data to None
    if not table_data:
        table_data = None

    # Extract paragraph text (regardless of whether a table exists)
    for line in lines:
        if not "|" in line:
            line = line.strip()
            if line.startswith("#"):  # Simple header handling
                line = "<b>" + line.lstrip("#").strip() + "</b>"
            paragraphs.append(line)

    return table_data, paragraphs

def create_pdf(data, paragraphs):
    """
    Creates a PDF with the given data in a table, including a title, footer,
    and paragraphs of text with bold and italic formatting.
    Saves the PDF to a temporary file.

    Args:
        data: A list of lists representing the table data.
        paragraphs: A list of strings representing paragraphs of text
                      (may contain <b></b>, <i></i>, <ul><li></li></ul>,
                      <ol><li></li></ol>, <h1></h1>, <h2></h2> etc.)
        filename: The name of the PDF file to create (without path).
    """

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    filepath = temp_file.name

    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch,
                            bottomMargin=inch)
    elements = []

    page_width, page_height = landscape(A4)  # Use landscape dimensions
    available_width = page_width - (doc.leftMargin + doc.rightMargin)

    styles = getSampleStyleSheet()
    title = Paragraph("Table 1. The Table Title", styles['h1'])
    title.fontSize = 16
    elements.append(title)

    for paragraph_text in paragraphs:
        paragraph = Paragraph(paragraph_text, styles['Normal'])
        elements.append(paragraph)
        elements.append(Spacer(1, 12))

    if not data or not data[0]:
        st.error("No table data found. Please check your input.")
        return None

    # Calculate column widths dynamically
    col_widths = []
    for col_index in range(len(data[0])):
        max_width = max(len(str(row[col_index])) for row in data)
        col_widths.append(max_width * 0.15 * inch)  # Adjust factor as needed

    table = Table(data, colWidths=col_widths)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Added vertical alignment
    ])
    table.setStyle(style)
    elements.append(table)

    footer = Paragraph("* Latest data was provided as of December 2024.", styles['Normal'])
    footer.fontSize = 10
    elements.append(footer)

    doc.build(elements)
    return filepath