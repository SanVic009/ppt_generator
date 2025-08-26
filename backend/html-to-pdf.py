from weasyprint import HTML, CSS
from weasyprint.formatting_structure import boxes

# Hardcoded paths
INPUT_HTML = "/home/sanvict/Documents/ppt_generator/backend/temp/html_outputs/20250826_180540_slide4.html"
OUTPUT_PDF = "22222222.pdf"

# 16:9 aspect ratio PowerPoint dimensions (in mm)
# 254mm × 143.51mm is equivalent to 10in × 5.65in (standard 16:9 PowerPoint size)
css = CSS(string='''
    @page {
        size: 1920px 1080px;
        margin: 0mm;
    }
    body {
        margin: 0;
        padding: 0;
    }
''')

try:
    HTML(filename=INPUT_HTML).write_pdf(OUTPUT_PDF, stylesheets=[css])
    print(f"PDF created at: {OUTPUT_PDF}")
except Exception as e:
    print(f"Error while converting: {e}")
