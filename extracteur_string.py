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

def create_and_append_paragraphs(text, chapter, chapter_index):
    paragraphs = []
    if text == "":
        return ""
    # Split the accumulated text into paragraphs
    paragraphs_text = re.split(r'\n(?=[A-ZÉÈÊËÀÂÎÔÛÜÇ])', text)
    # Associate each Paragraph to current Chapter
    for para_index, para in enumerate(paragraphs_text, start=1):
        paragraphs.append(Paragraph(para, para_index, chapter[chapter_index]))

    return paragraphs

def extract_text_elements(pdf_path, search_string, page_range):

    # Ajuster la plage de pages pour l'indexage à partir de zéro
    adjusted_page_range = [page - 1 for page in page_range]
    # Lire le fichier PDF
    words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in adjusted_page_range:
            page = pdf.pages[page_num]
            words += page.extract_words(keep_blank_chars=True, extra_attrs=['size'])

    titles = [Title("", 0)]
    current_title = ""
    title_index = 1
    titles_1 = [Title1("", 0, titles[0])]
    current_title_1 = ""
    title_1_index = 1
    chapters = [Chapter("", 0, titles_1[0])]
    current_chapter = ""
    chapter_index = 1
    paragraphs = []
    text_content = ""
    previous_word_size = 0
    word_text = ""

    for i, word in enumerate(words):
        word_text = word['text']
        if word_text != ' ' :
            current_word_size = round(word['size'])

            # Set previous_word_size value on first run
            if previous_word_size == 0 :
                previous_word_size = current_word_size
            
            if(current_word_size != previous_word_size) :
                if previous_word_size == 80:
                    titles.append(Title(current_title.strip(), title_index))
                    title_index += 1
                    current_title = ""

                elif previous_word_size == 25 :
                    titles_1.append(Title1(current_title_1.strip(), title_1_index, titles[title_index-1]))
                    title_1_index += 1
                    current_title_1 = ""

                elif previous_word_size == 20 :
                    chapters.append(Chapter(current_chapter.strip(), chapter_index, titles_1[title_1_index-1]))
                    chapter_index += 1
                    current_chapter = ""

                else :                  
                    paragraphs += create_and_append_paragraphs(text_content, chapters, chapter_index-1)
                    text_content = ""                          

            if current_word_size == 80:
                current_title += word_text

            elif current_word_size == 25:
                current_title_1 += word_text

            elif current_word_size == 20:
                current_chapter += word_text

            else:
                # Add a newline if the difference in doctop between the current and next word is greater than 3
                if i < len(words) - 1 and abs(words[i + 1]['doctop'] - word['doctop']) > 20: #diff entre deux lignes 14, entre deux paragraphes 25,9
                    text_content += word_text
                    text_content += '\n'
                else:
                    text_content += word_text

            previous_word_size = current_word_size

    # Taking account last paragraph of the last page
    if text_content.split() :
        paragraphs += create_and_append_paragraphs(text_content, chapters, chapter_index-1)

    # Filtrer les paragraphes contenant le search_string
    filtered_paragraphs = [para for para in paragraphs if search_string in para.text]

    # Compter le nombre d'occurrences trouvées
    num_occurrences = sum(para.text.lower().count(search_string.lower()) for para in filtered_paragraphs)

    # Afficher le nombre d'occurrences trouvées
    print(f"Nombre d'occurrences trouvées: {num_occurrences}\n")

    # Afficher les titres et paragraphes trouvés avec le numéro du paragraphe
    previous_title = None
    previous_title1 = None

    for para in filtered_paragraphs:
        title = para.chapter.title1.title.text
        if title != previous_title and title:
            print(f"#{title}")
            previous_title = title

        title1 = para.chapter.title1.text
        if title1 != previous_title1 and title1:
            print(f"##{title1}")
            previous_title1 = title1

        chapter = para.chapter.text
        if chapter :
            print(f"###{chapter}")

        print(f"Paragraph {para.index}:\n{para.text}\n")

    return titles, titles_1, chapters, paragraphs, filtered_paragraphs

def parse_page_range(input_str):
    try:
        # Vérifier si input_str contient des caractères non numériques ou spéciaux autres que '-'
        if any(not char.isdigit() and char != '-' for char in input_str):
            raise ValueError("Erreur : L'entrée contient des caractères non numériques ou spéciaux autres que '-'.")

        # Vérifier si '-' est le premier ou le dernier caractère
        if input_str.startswith('-') or input_str.endswith('-'):
            raise ValueError("Erreur : '-' ne peut pas être le premier ou le dernier caractère.")

        if '-' in input_str:
            # Cas où l'entrée est de la forme "start-end"
            start, end = map(int, input_str.split('-'))
            if start == 0 or end == 0:
                raise ValueError("Erreur : La page 0 n'est pas valide.")
            return range(start, end + 1)
        elif ',' in input_str:
            # Cas où l'entrée est de la forme "page1, page2, page3, ..."
            pages = list(map(int, input_str.split(',')))
            if 0 in pages:
                raise ValueError("Erreur : La page 0 n'est pas valide.")
            return pages
        else:
            # Cas où l'entrée est un seul numéro de page
            page = int(input_str)
            if page == 0:
                raise ValueError("Erreur : La page 0 n'est pas valide.")
            return [page]
    except ValueError as e:
        print(e)
        return []

def main():
    pdf_path = 'Achille Marozzo - opéra nova.pdf'
    search_string = input("Entrez la chaîne de caractères à rechercher: ")
    search_range  = input("Personnaliser la plage de pages (ex: 32-65 ou 32, 34, 60, 63): ")
    page_range = parse_page_range(search_range)
    if not  page_range :
        print("Plage invalide !")
    else :
        extract_text_elements(pdf_path, search_string, page_range)

if __name__ == "__main__":
    main()