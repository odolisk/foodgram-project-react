import os

from reportlab.lib.colors import black, blue
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.conf import settings
from django.http import HttpResponse


def generate_PDF(pivot_list):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_list.pdf"')
    folder = settings.FONTS_PATH
    ttf_file = os.path.join(folder, 'PTAstraSans-Regular.ttf')
    pdfmetrics.registerFont(TTFont('PTAstraSans', ttf_file, 'UTF-8'))

    doc = canvas.Canvas(response, pagesize=A4)

    logo_path = os.path.join(folder, 'logo.png')
    logo = ImageReader(logo_path)
    doc.drawImage(logo, 30, 710, mask='auto')

    doc.setFillColor(blue)
    doc.drawString(270, 820, ('http://odolisk.ru'))

    doc.setFillColor(black)
    doc.setFont('PTAstraSans', 32)
    doc.drawString(250, 770, 'Foodgram')

    doc.setFont('PTAstraSans', 18)
    doc.drawString(170, 720, 'сайт вкусных рецептов для програмистов')

    doc.setDash([1, 1, 3, 3, 1, 4, 4, 1], 0)
    doc.setLineWidth(1)
    doc.line(30, 690, 575, 690)

    doc.setDash(1, 0)
    doc.setFillColor(black)
    doc.setFont('PTAstraSans', 24)
    doc.drawString(120, 630, 'Список необходимых ингредиентов')

    doc.setLineWidth(2)
    doc.line(120, 620, 490, 620)

    doc.setFont('PTAstraSans', 16)
    height = 570
    marker_sym = chr(8226)
    for (name, params) in pivot_list.items():
        amount = params['amount']
        mes_unit = params['measurement_unit']
        list_elem = f'{marker_sym} {name} - {amount} {mes_unit}'
        doc.drawString(75, height, list_elem)
        height -= 20
    doc.showPage()
    doc.save()
    return response
