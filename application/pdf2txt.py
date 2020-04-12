# coding: utf-8


import PyPDF2
import re
import json

index = ""
all_text = ""

with open('CONFIG.json', 'r') as f:
    CONFIG = json.load(f)
    PDF_FOLDER = CONFIG['PDF_FOLDER']

with open(f'{PDF_FOLDER}/Leiautes do eSocial v2.5 (cons. até NT 17.2019).pdf', 'rb') as f:
    read_pdf = PyPDF2.PdfFileReader(f)
    number_of_pages = read_pdf.getNumPages()
    for i in range(1, number_of_pages):
        page = read_pdf.getPage(i)

        # Obtém o texto dos PDF's
        page_content = page.extractText()
        
        # Regex de cabeçalho das páginas. Pode ser removido
        strip_header = re.sub(r' \n \nLeiautes do eSocial \n-\n \nVersão 2.5 \(consolidada até NT 17/2019\)\n \n \n \nPágina \n\d+\n \nde \n166\n \n \n', '', page_content, re.MULTILINE)
        
        if i < 3: # Sumário
            index += strip_header
        else: #     Resto das páginas
            all_text += strip_header

with open('index.txt', 'w') as f:
    f.write(index)
with open('all_text.txt', 'w') as f:
    f.write(all_text)
