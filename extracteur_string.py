import pdfplumber
import re

class TextElement:
    def __init__(self, text, index):
        self.text = text
        self.index = index

class Title(TextElement):
    def __init__(self, text, index):
        super().__init__(text, index)

class Title1(TextElement):
    def __init__(self, text, index, title):
        super().__init__(text, index)
        self.title = title

class Chapter(TextElement):
    def __init__(self, text, index, title1):
        super().__init__(text, index)
        self.title1 = title1

class Paragraph(TextElement):
    def __init__(self, text, index, chapter):
        super().__init__(text, index)
        self.chapter = chapter

def extract_text_elements(pdf_path, search_string):
    # Lire le fichier PDF
    words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(32, 65):  # Les numéros de page PDF sont indexés à partir de zéro
            page = pdf.pages[page_num]
            words += page.extract_words(keep_blank_chars=True, extra_attrs=['size'])

    titles = []
    current_title = ""
    title_index = 1
    titles_1 = []
    current_title_1 = ""
    title_1_index = 1
    chapters = []
    current_chapter = ""
    chapter_index = 1
    paragraphs = []
    text_content = ""

    for i, word in enumerate(words):
        if word['text'] != ' ' :
            if round(word['size']) == 80:
                if text_content.strip() and current_title == "":
                    title_index += 1
                current_title += word['text']

            elif round(word['size']) == 25:
                if text_content.strip() and current_title_1 == "":
                    title_1_index += 1
                current_title_1 += word['text']

            elif round(word['size']) == 20:
                if text_content.strip() and current_chapter == "":
                    # Split the accumulated text into paragraphs
                    paragraphs_text = re.split(r'\n(?=[A-ZÉÈÊËÀÂÎÔÛÜÇ])', text_content)
                    text_content = ""
                    for para_index, para in enumerate(paragraphs_text, start=1):
                        # Create a Paragraph object and associate it with the most recent Chapter
                        paragraphs.append(Paragraph(para, para_index, chapters[chapter_index-1]))
                    chapter_index += 1
                current_chapter += word['text']
            else:
                if current_title.strip():
                    # Create a Title object
                    titles.append(Title(current_title.strip(), title_index))
                    current_title = ""

                if current_title_1.strip():
                    # Create a Title 1 object
                    titles_1.append(Title1(current_title_1.strip(), title_1_index, titles[title_index-1]))
                    current_title_1 = ""

                if current_chapter.strip():
                    # Create a Chapter object
                    chapters.append(Chapter(current_chapter.strip(), chapter_index, titles_1[title_1_index-1]))
                    current_chapter = ""

                # Add a newline if the difference in doctop between the current and next word is greater than 3
                if i < len(words) - 1 and abs(words[i + 1]['doctop'] - word['doctop']) > 20: #diff entre deux lignes 14, entre deux paragraphes 25,9
                    text_content += word['text']
                    text_content += '\n'
                else:
                    text_content += word['text']

    # Filtrer les paragraphes contenant le search_string
    filtered_paragraphs = [para for para in paragraphs if search_string in para.text]

    # Afficher le nombre d'occurrences trouvées
    print(f"Nombre d'occurrences trouvées: {len(filtered_paragraphs)}\n")

    # Afficher les titres et paragraphes trouvés avec le numéro du paragraphe
    previous_title = None
    previous_title1 = None

    for para in filtered_paragraphs:
        if para.chapter.title1.title.text != previous_title:
            print(f"#{para.chapter.title1.title.text}")
            previous_title = para.chapter.title1.title.text

        if para.chapter.title1.text != previous_title1:
            print(f"##{para.chapter.title1.text}")
            previous_title1 = para.chapter.title1.text

        print(f"###{para.chapter.text}")

        print(f"Paragraph {para.index}:\n{para.text}\n")

    return titles, titles_1, chapters, paragraphs, filtered_paragraphs

def main():
    pdf_path = 'Achille Marozzo - opéra nova.pdf'
    search_string = input("Entrez la chaîne de caractères à rechercher: ")
    extract_text_elements(pdf_path, search_string)

if __name__ == "__main__":
    main()