"""Compare Arabic fonts for PDF export."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# Test fonts
FONTS = [
    ("Dubai Regular", "C:/Windows/Fonts/DUBAI-REGULAR.TTF"),
    ("Dubai Medium", "C:/Windows/Fonts/DUBAI-MEDIUM.TTF"),
    ("Dubai Bold", "C:/Windows/Fonts/DUBAI-BOLD.TTF"),
    ("Majalla", "C:/Windows/Fonts/majalla.ttf"),
    ("Majalla Bold", "C:/Windows/Fonts/majallab.ttf"),
    ("Naskh", "C:/Windows/Fonts/DTNASKH0.TTF"),
    ("Diwan", "C:/Windows/Fonts/DIWANLTR.TTF"),
    ("Arabic Typesetting", "C:/Windows/Fonts/arabtype.ttf"),
    ("Tahoma", "C:/Windows/Fonts/tahoma.ttf"),
    ("Arial", "C:/Windows/Fonts/arial.ttf"),
]

# Test text
test_arabic = "دراسة جدوى مشروع مركز الخدمات الرقمية"
test_mixed = "المبلغ الإجمالي: 150,000 دج"
test_body = "يهدف هذا المشروع إلى إنشاء مركز خدمات رقمية متكامل يقدم خدمات التحويل الرقمي للشركات والأفراد في ولاية البيض."

def reshape(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def create_font_comparison():
    doc = SimpleDocTemplate(
        "generated_output/font_comparison.pdf",
        pagesize=A4,
        rightMargin=20*2.54, leftMargin=20*2.54,
        topMargin=25*2.54, bottomMargin=25*2.54,
    )
    
    elements = []
    
    for font_name, font_path in FONTS:
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            
            style = ParagraphStyle(
                f"Test_{font_name}",
                fontName=font_name,
                fontSize=14,
                leading=20,
                alignment=TA_RIGHT,
            )
            
            elements.append(Paragraph(f"<b>{font_name}</b>", ParagraphStyle(
                f"Header_{font_name}",
                fontName=font_name,
                fontSize=18,
                leading=24,
                alignment=TA_CENTER,
                spaceAfter=10,
            )))
            
            elements.append(Paragraph(reshape(test_arabic), style))
            elements.append(Paragraph(reshape(test_mixed), style))
            elements.append(Paragraph(reshape(test_body), style))
            elements.append(Spacer(1, 30))
            
        except Exception as e:
            print(f"Error with {font_name}: {e}")
    
    doc.build(elements)
    print("Generated font_comparison.pdf")

if __name__ == "__main__":
    create_font_comparison()
