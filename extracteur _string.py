import pdfplumber
import re

# Chemin vers le fichier PDF
pdf_path = 'Achille Marozzo - opéra nova.pdf'

class TextElement:
    def __init__(self, text, index):
        self.text = text
        self.index = index

class Title(TextElement):
    def __init__(self, text, index):
        super().__init__(text, index)

class Paragraph(TextElement):
    def __init__(self, text, index, title):
        super().__init__(text, index)
        self.title = title




# Lire le fichier PDF
with pdfplumber.open(pdf_path) as pdf:
    
    # for page_num in range(32, 63):  # Les numéros de page PDF sont indexés à partir de zéro
    for page_num in range(58, 59):
        page = pdf.pages[page_num]        
        words = page.extract_words(keep_blank_chars = True, extra_attrs = ['size'])      

titles = []
current_title = ""
title_index = 1
paragraphs = []
text_content = ""

for i, word in enumerate(words):
    if 20 < word['size'] < 21:
        if text_content.strip() and current_title == "":            
            # Split the accumulated text into paragraphs
            paragraphs_text  = re.split(r'\n(?=[A-ZÉÈÊËÀÂÎÔÛÜÇ])', text_content) 
            text_content = ""
            for para_index, para  in enumerate(paragraphs_text, start=1):
                # Create a Paragraph object and associate it with the most recent title
                paragraphs.append(Paragraph(para, para_index, titles[title_index-1]))
            title_index += 1
        current_title += word['text']
    else:
        if current_title.strip():
             # Create a Title object
            titles.append(Title(current_title.strip(),title_index))            
            current_title = ""
        # Add a newline if the difference in doctop between the current and next word is greater than 3
        if i < len(words) - 1 and abs(words[i + 1]['doctop'] - word['doctop']) > 20: #diff entre deux lignes 14, entre deux paragraphes 25,9
            text_content += word['text']
            text_content += '\n'
        else:
            text_content += word['text']
            


# Filtrer les paragraphes contenant "falso manco"
falso_manco_paragraphs = [para for para in paragraphs if "falso manco" in para.text]

# Afficher les titres et paragraphes trouvés avec le numéro du paragraphe
for para in falso_manco_paragraphs:
    print(f"{para.title.text}")
    print(f"Paragraph {para.index}:\n{para.text}\n")