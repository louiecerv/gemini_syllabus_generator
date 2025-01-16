from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import markdown
import tempfile
from html.parser import HTMLParser
import streamlit as st

import markdown
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_data = []
        self.current_row = []
        self.in_table = False
        self.paragraphs = []
        self.current_paragraph = ""
        self.in_bold = False
        self.in_italic = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr':
            self.current_row = []
        elif tag == 'td' or tag == 'th':
            pass  # No action needed here
        elif tag == 'p':
            self.current_paragraph = ""
        elif tag == 'b':
            self.in_bold = True
        elif tag == 'i':
            self.in_italic = True

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr':
            self.table_data.append(self.current_row)
        elif tag == 'td' or tag == 'th':
            pass  # No action needed here
        elif tag == 'p':
            self.paragraphs.append(self.current_paragraph)
        elif tag == 'b':
            self.in_bold = False
        elif tag == 'i':
            self.in_italic = False

    def handle_data(self, data):
        if self.in_table:
            # Strip leading/trailing whitespace and non-breaking spaces
            cleaned_data = data.strip().replace('\xa0', ' ')  
            self.current_row.append(cleaned_data)
        elif self.current_paragraph is not None:
            if self.in_bold:
                data = f"**{data}**"
            if self.in_italic:
                data = f"*{data}*"
            self.current_paragraph += data


def process_markdown(markdown_text):
    """
    Processes markdown text to extract table data and paragraphs,
    preserving bold and italic formatting.

    Args:
        markdown_text: The markdown text to process.

    Returns:
        A tuple containing:
            - A list of lists representing the table data.
            - A list of strings representing the paragraphs with formatting.
    """
    html = markdown.markdown(markdown_text)
    parser = MyHTMLParser()
    parser.feed(html)

    # Debugging prints (you can remove these later)
    print("HTML:", html)
    print("Table Data:", parser.table_data)
    print("Paragraphs:", parser.paragraphs)

    return parser.table_data, parser.paragraphs


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

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    doc.pagesize = A4
    doc.orientation = "landscape"  
    elements = []

    page_width, page_height = A4
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

    table = Table(data, colWidths=[available_width / len(data[0])] * len(data[0])) 

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    elements.append(table)

    footer = Paragraph("* Latest data was provided as of December 2024.", styles['Normal'])
    footer.fontSize = 10
    elements.append(footer)

    doc.build(elements)
    return filepath


