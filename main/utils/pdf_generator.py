import io
import os
import markdown
from xhtml2pdf import pisa
from pypdf import PdfWriter, PdfReader
from django.conf import settings
from django.contrib.staticfiles import finders

# Margins
TOP_MARGIN = "140pt"    
BOTTOM_MARGIN = "100pt" 
SIDE_MARGIN = "60pt"

def sanitize_text(text: str) -> str:
    """
    Cleans text to ensure PDF compatibility.
    """
    if not text:
        return ""
        
    replacements = {
        "–": "-", "—": "-", "’": "'", "‘": "'", "‑": "-",
        "“": '"', "”": '"', "…": "...", "•": "*",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Aggressive ASCII normalization
    text = text.encode("ascii", "ignore").decode("ascii")
    return text

def create_pdf_bytes(markdown_content: str) -> bytes:
    """
    Generates a PDF in memory with the template overlay.
    """
    # 1. Locate the Template using Django Finders
    # This searches all static folders (app-level and project-level)
    template_path = finders.find('images/report_bg.pdf')
    
    # Fallback: If finder fails (e.g. during development in some setups), try manual path
    if not template_path:
        template_path = os.path.join(settings.BASE_DIR, 'main', 'static', 'images', 'report.pdf')

    if not template_path or not os.path.exists(template_path):
        # Specific Error Message for Debugging
        raise FileNotFoundError(
            f"Background PDF not found. Searched at: {template_path}. "
            "Ensure 'report_bg.pdf' is inside 'main/static/images/' or your project 'static/images/' folder."
        )

    # 2. Sanitize and Convert to HTML
    cleaned_content = sanitize_text(markdown_content)
    html_body = markdown.markdown(cleaned_content, extensions=['extra', 'codehilite', 'sane_lists'])
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @page {{
                size: a4 portrait;
                margin-top: {TOP_MARGIN};
                margin-bottom: {BOTTOM_MARGIN};
                margin-left: {SIDE_MARGIN};
                margin-right: {SIDE_MARGIN};
                background-color: transparent;
            }}
            body {{ font-family: Helvetica, sans-serif; font-size: 11pt; }}
            h1, h2, h3 {{ color: #2E3E4E; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 20px; }}
            p, ul, li {{ line-height: 1.5; }}
            pre {{
                background-color: #f4f4f4; padding: 10px; border-radius: 5px;
                font-family: 'Courier New', Courier, monospace; font-size: 10pt;
                white-space: pre-wrap; word-wrap: break-word; border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # 3. Generate Content PDF
    content_pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_template, dest=content_pdf_buffer, encoding='utf-8')
    
    if pisa_status.err:
        raise Exception("Error generating HTML PDF")

    # 4. Merge with Background Template
    content_pdf_buffer.seek(0)
    content_reader = PdfReader(content_pdf_buffer)
    template_reader = PdfReader(template_path)
    writer = PdfWriter()
    
    # We assume the background is on the first page of the template PDF
    bg_page = template_reader.pages[0]

    for content_page in content_reader.pages:
        # Merge content ON TOP of the background
        content_page.merge_page(bg_page, over=False)
        writer.add_page(content_page)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer.getvalue()