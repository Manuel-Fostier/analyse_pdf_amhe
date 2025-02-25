import tkinter as tk
from tkinter import messagebox, ttk
from extracteur_string import extract_text_elements

class OperaNovaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OPERA NOVA - RECHERCHE DE TEXTE")

        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

        # Label et champ de saisie pour la chaîne de caractères à rechercher
        self.label_search = tk.Label(root, text="Chaîne de caractères:")
        self.label_search.grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        self.entry_search = tk.Entry(root)
        self.entry_search.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=10)

        # Bouton pour afficher les informations
        self.show_info_button = tk.Button(root, text="Afficher les informations", command=self.show_info)
        self.show_info_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Zone de texte pour afficher les informations
        self.info_text = tk.Text(root, height=10, width=40)
        self.info_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def show_info(self):
        search_string = self.entry_search.get()

        if not search_string:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        pdf_path = 'Achille Marozzo - opéra nova.pdf'
        titles, titles_1, chapters, paragraphs, filtered_paragraphs = extract_text_elements(pdf_path, search_string)
        
        info = f"Nombre d'occurrences trouvées: {len(filtered_paragraphs)}\n"

        previous_title = None
        previous_title1 = None

        for para in filtered_paragraphs:
            if para.chapter.title1.title.text != previous_title:
                info += f"#{para.chapter.title1.title.text}\n"
                previous_title = para.chapter.title1.title.text

            if para.chapter.title1.text != previous_title1:
                info += f"##{para.chapter.title1.text}\n"
                previous_title1 = para.chapter.title1.text

            info += f"###{para.chapter.text}\n"
            info += f"Paragraph {para.index}:\n{para.text}\n"

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)

if __name__ == "__main__":
    root = tk.Tk()
    app = OperaNovaGUI(root)
    root.mainloop()