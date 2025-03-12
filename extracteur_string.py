import pdfplumber
import re


class TextElement:
    def __init__(self, text, index):
        self.text = text
        self.index = index


class Title(TextElement):
    def __init__(self, text, index):
        super().__init__(text, index)
        self.titles_1_list = [Title1("", 0, self)]
        self.SIZE = 80


class Title1(TextElement):
    def __init__(self, text, index, title):
        super().__init__(text, index)
        self.parent_title = title
        self.chapter_list = [Chapter("", 0, self)]
        self.SIZE = 25


class Chapter(TextElement):
    def __init__(self, text, index, title1):
        super().__init__(text, index)
        self.parent_title1 = title1
        self.paragraph_list = []
        self.SIZE = 20


class Paragraph(TextElement):
    def __init__(self, text, index, chapter):
        super().__init__(text, index)
        self.parent_chapter = chapter


def add_title(titles, text, index):
    if len(titles) == 1 and titles[0].text == "":
        titles[0] = Title(text.strip(), 0)
    else:
        titles.append(Title(text.strip(), index))


def add_title1(text, index, title):
    # if len(title.titles_1_list) == 1 and title.titles_1_list[0].text == "":
    #     title.titles_1_list[0] = Title1(text.strip(), 0, title)
    # else:
    title.titles_1_list.append(Title1(text.strip(), index, title))


def add_chapter(text, index, title_1):
    # if len(title_1.chapter_list) == 1 and title_1.chapter_list[0].text == "":
    #     title_1.chapter_list[0] = Chapter(text.strip(), 0, title_1)
    # else:
    title_1.chapter_list.append(Chapter(text.strip(), index, title_1))


def create_and_append_paragraphs(text, chapter):
    if text == "":
        return ""

    # Split the accumulated text into paragraphs
    paragraphs_text = re.split(r"\n(?=[A-ZÉÈÊËÀÂÎÔÛÜÇ])", text)
    # Associate each Paragraph to current Chapter
    for para_index, para in enumerate(paragraphs_text, start=1):
        chapter.paragraph_list.append(Paragraph(para, para_index, chapter))


def extract_text_elements(pdf_path, search_string, page_range):

    # Ajuster la plage de pages pour l'indexage à partir de zéro
    adjusted_page_range = [page - 1 for page in page_range]
    # Lire le fichier PDF
    words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in adjusted_page_range:
            page = pdf.pages[page_num]
            words += page.extract_words(keep_blank_chars=True,
                                        extra_attrs=["size"])
    titles = [Title("", 0)]
    current_title = titles[0]
    current_title_text = ""
    title_index = 1

    current_title_1 = current_title.titles_1_list[0]
    current_title_1_text = ""
    title_1_index = 1

    current_chapter = current_title.titles_1_list[0].chapter_list[0]
    current_chapter_text = ""
    chapter_index = 1

    text_content = ""
    previous_word_size = 0
    word_text = ""

    for i, word in enumerate(words):
        word_text = word["text"]
        if word_text != " ":
            current_word_size = round(word["size"])

            # Set previous_word_size value on first run
            if previous_word_size == 0:
                previous_word_size = current_word_size

            if current_word_size != previous_word_size:
                if previous_word_size == current_title.SIZE:
                    add_title(titles, current_title_text, len(titles))
                    current_title = titles[-1]
                    current_title_1 = current_title.titles_1_list[0]
                    current_chapter = current_title.titles_1_list[0].chapter_list[0]
                    title_index += 1
                    current_title_text = ""
                elif previous_word_size == current_title_1.SIZE:
                    add_title1(current_title_1_text,
                               title_1_index, current_title)
                    current_title_1 = current_title.titles_1_list[-1]
                    current_chapter = current_title_1.chapter_list[0]
                    title_1_index += 1
                    current_title_1_text = ""
                elif previous_word_size == current_chapter.SIZE:
                    add_chapter(current_chapter_text,
                                chapter_index, current_title_1)
                    current_chapter = current_title_1.chapter_list[-1]
                    chapter_index += 1
                    current_chapter_text = ""
                else:
                    create_and_append_paragraphs(text_content, current_chapter)
                    text_content = ""

            if current_word_size == current_title.SIZE:
                current_title_text += word_text
            elif current_word_size == current_title_1.SIZE:
                current_title_1_text += word_text
            elif current_word_size == current_chapter.SIZE:
                current_chapter_text += word_text
            else:
                # Add a newline if the difference in doctop between the current and next word is greater than 3
                # diff entre deux lignes 14, entre deux paragraphes 25,9
                if (i < len(words) - 1 and abs(words[i + 1]["doctop"] - word["doctop"]) > 20):
                    text_content += word_text
                    text_content += "\n"
                else:
                    text_content += word_text

            previous_word_size = current_word_size

    # Taking account last paragraph of the last page
    if text_content.split():
        create_and_append_paragraphs(text_content, current_chapter)

    return titles


def find_paragraphs_containing_string(titles, search_string):
    filtered_paragraphs = []
    for title in titles:
        for title_1 in title.titles_1_list:
            for chapter in title_1.chapter_list:
                for para in chapter.paragraph_list:
                    if (search_string in para.text):
                        filtered_paragraphs.append(para)

    return filtered_paragraphs


def print_filtered_paragraphs(filtered_paragraphs, search_string):
    # Compter le nombre d'occurrences trouvées
    num_occurrences = sum(para.text.lower().count(
        search_string.lower()) for para in filtered_paragraphs)

    # Display search string, number of occurrences, and paragraphs found
    print(f"Search String: {search_string}")
    print(f"Nombre d'occurrences trouvées: {num_occurrences}\n")

    # Afficher les titres et paragraphes trouvés avec le numéro du paragraphe
    previous_title = None
    previous_title1 = None

    for para in filtered_paragraphs:
        title = para.parent_chapter.parent_title1.parent_title.text
        if title != previous_title and title:
            print(f"#{title}")
            previous_title = title

        title1 = para.parent_chapter.parent_title1.text
        if title1 != previous_title1 and title1:
            print(f"##{title1}")
            previous_title1 = title1

        chapter = para.parent_chapter.text
        if chapter:
            print(f"###{chapter}")

        print(f"Paragraph {para.index}:\n{para.text}\n")


def parse_page_range(input_str):
    try:
        # Vérifier si input_str contient des caractères non numériques ou spéciaux autres que '-'
        if any(not char.isdigit() and char != "-" for char in input_str):
            raise ValueError(
                "Erreur : L'entrée contient des caractères non numériques ou spéciaux autres que '-'."
            )

        # Vérifier si '-' est le premier ou le dernier caractère
        if input_str.startswith("-") or input_str.endswith("-"):
            raise ValueError(
                "Erreur : '-' ne peut pas être le premier ou le dernier caractère."
            )

        if "-" in input_str:
            # Cas où l'entrée est de la forme "start-end"
            start, end = map(int, input_str.split("-"))
            if start == 0 or end == 0:
                raise ValueError("Erreur : La page 0 n'est pas valide.")
            return range(start, end + 1)
        elif "," in input_str:
            # Cas où l'entrée est de la forme "page1, page2, page3, ..."
            pages = list(map(int, input_str.split(",")))
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
    pdf_path = "Achille Marozzo - opéra nova.pdf"
    # search_string = input("Entrez la chaîne de caractères à rechercher: ")
    search_string = "guardia di testa"
    # search_range  = input("Personnaliser la plage de pages (ex: 32-65 ou 32, 34, 60, 63): ")
    # search_range = '34-102' # Livre 3
    # search_range = '35-55' # 1er assault
    # search_range = '56-65' # 2eme assault
    search_range = '35-65' # 1er et 2eme assault
    # search_range = '66-70' # 3eme assault droit fil contre droit fil
    # search_range = '70-73' # 3eme assault falso contre falso
    # search_range = '66-73' # 3eme assault complet
    # search_range = '56'
    page_range = parse_page_range(search_range)
    if not page_range:
        print("Plage invalide !")
    else:
        titles = extract_text_elements(pdf_path, search_string, page_range)
        filtered_paragraphs = find_paragraphs_containing_string(
            titles, search_string)
        print_filtered_paragraphs(filtered_paragraphs, search_string)


if __name__ == "__main__":
    main()
