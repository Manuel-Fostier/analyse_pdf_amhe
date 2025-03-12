import tkinter as tk
from tkinter import messagebox, ttk
from extracteur_string import (
    extract_text_elements,
    parse_page_range,
    find_paragraphs_containing_string,
    sub_string_qty,
    filtered_paragraphs_to_string,
)


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
        self.string_search = tk.Label(root, text="Chaîne de caractères:")
        self.string_search.grid(row=2, column=0, sticky=tk.E, padx=10, pady=10)
        self.entry_string_search = tk.Entry(root)
        self.entry_string_search.grid(
            row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=10)

        # Label 2 et champ de saisie pour la plage dans laquelle faire la chercher
        self.range_search = tk.Label(root, text="Plage de recherche:")
        self.range_search.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)
        self.entry_range_search = tk.Entry(root)
        self.entry_range_search.grid(
            row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=10)

        # Bouton pour afficher les informations
        self.show_info_button = tk.Button(
            root, text="Afficher les informations", command=self.show_info)
        self.show_info_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.root.bind('<Return>', lambda event=None: self.show_info())

        # Zone de texte pour afficher les informations
        self.info_text = tk.Text(root, height=40, width=160)
        self.info_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def show_info(self):
        search_string = self.entry_string_search.get()
        search_range = self.entry_range_search.get()

        if not search_string:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        page_range = parse_page_range(search_range)
        if not search_range:
            messagebox.showerror(
                "Erreur", "Veuillez entrer une plage valide. Ex : 1-2")

        pdf_path = 'Achille Marozzo - opéra nova.pdf'
        titles = extract_text_elements(pdf_path,  page_range)
        filtered_paragraphs = find_paragraphs_containing_string(
            titles, search_string)

        num_occurrences = sub_string_qty(filtered_paragraphs, search_string)
        info = f"Nombre d'occurrences trouvées: {num_occurrences}\n"

        info += filtered_paragraphs_to_string(filtered_paragraphs)

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)


if __name__ == "__main__":
    root = tk.Tk()
    app = OperaNovaGUI(root)
    root.mainloop()
