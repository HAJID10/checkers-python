"""Fenêtre principale du jeu de dames (Tkinter)."""

from tkinter import Tk, Frame, Label, Button, NSEW, EW, messagebox

from checkers.canvas_damier import CanvasDamier
from checkers.partie import Partie

COULEUR_ERREUR = "#C0392B"
COULEUR_INFO = "#1F3A93"
COULEUR_SUCCES = "#1E8449"


class FenetrePartie(Tk):
    """Interface graphique : on clique sur une pièce, puis sur la case où la déplacer.

    Attributes:
        partie (Partie): La partie en cours.
        canvas_damier (CanvasDamier): L'affichage du damier.
        etiquette_tour (Label): Indique à qui c'est le tour.
        messages (Label): Messages de rétroaction à l'utilisateur.
    """

    def __init__(self):
        super().__init__()
        self.title("Jeu de dames")
        self.minsize(320, 380)

        self.partie = Partie()

        self.canvas_damier = CanvasDamier(self, self.partie.damier)
        self.canvas_damier.grid(row=0, column=0, sticky=NSEW)
        self.canvas_damier.bind("<Button-1>", self.selectionner)

        barre = Frame(self, padx=8, pady=6)
        barre.grid(row=1, column=0, sticky=EW)
        barre.grid_columnconfigure(0, weight=1)

        self.etiquette_tour = Label(barre, font=("Segoe UI", 12, "bold"), anchor="w")
        self.etiquette_tour.grid(row=0, column=0, sticky=EW)
        Button(barre, text="Nouvelle partie", command=self.nouvelle_partie).grid(row=0, column=1, padx=4)
        Button(barre, text="Quitter", command=self.quitter_jeu).grid(row=0, column=2)

        self.messages = Label(self, anchor="w", padx=8, pady=4)
        self.messages.grid(row=2, column=0, sticky=EW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.actualiser_affichage("Cliquez sur une pièce blanche pour commencer.", COULEUR_INFO)

    # ---------------------------------------------------------------- Affichage

    def afficher_message(self, message, couleur="black"):
        self.messages.config(text=message, foreground=couleur)

    def actualiser_affichage(self, message=None, couleur="black"):
        """Met à jour le damier, l'indicateur de tour et le message."""
        self.canvas_damier.actualiser()
        texte = "Tour des {}s".format(self.partie.couleur_joueur_courant)
        if self.partie.position_source_forcee is not None:
            texte += " — continuez la prise"
        elif self.partie.doit_prendre:
            texte += " — prise obligatoire"
        self.etiquette_tour.config(text=texte)
        if message is not None:
            self.afficher_message(message, couleur)

    # ---------------------------------------------------------------- Interaction

    def selectionner(self, event):
        """Gère un clic sur le damier : sélection de la pièce source, puis de la case cible."""
        if self.partie.partie_terminee():
            return

        position = self.canvas_damier.position_depuis_pixels(event.x, event.y)
        if position is None:
            return

        source = self.partie.position_source_selectionnee
        piece = self.partie.damier.recuperer_piece_a_position(position)

        # Premier clic, ou clic sur une autre pièce du joueur courant : on (re)choisit la pièce source.
        if source is None or (piece is not None and piece.couleur == self.partie.couleur_joueur_courant):
            self.choisir_source(position)
            return

        resultat, message = self.partie.jouer_coup(source, position)
        if resultat == "erreur":
            # Le coup est refusé, mais la pièce reste sélectionnée : le joueur peut réessayer ou en choisir une autre.
            self.partie.position_source_selectionnee = source
            self.afficher_message(message, COULEUR_ERREUR)
            return

        if resultat == "prise_continue":
            forcee = self.partie.position_source_forcee
            self.partie.position_source_selectionnee = forcee
            self.canvas_damier.surligner(forcee, self.partie.cibles_possibles(forcee))
            self.actualiser_affichage(message, COULEUR_SUCCES)
            return

        self.canvas_damier.effacer_surlignage()
        self.actualiser_affichage(message, COULEUR_SUCCES if resultat == "prise" else "black")
        self.verifier_fin_de_partie()

    def choisir_source(self, position):
        valide, message = self.partie.position_source_valide(position)
        if not valide:
            # Pendant une prise multiple, la pièce forcée reste sélectionnée.
            forcee = self.partie.position_source_forcee
            self.partie.position_source_selectionnee = forcee
            if forcee is None:
                self.canvas_damier.effacer_surlignage()
            else:
                self.canvas_damier.surligner(forcee, self.partie.cibles_possibles(forcee))
            self.afficher_message(message, COULEUR_ERREUR)
            return

        self.partie.position_source_selectionnee = position
        self.canvas_damier.surligner(position, self.partie.cibles_possibles(position))
        self.afficher_message("Pièce {} sélectionnée. Cliquez sur une case cible.".format(position), COULEUR_INFO)

    def verifier_fin_de_partie(self):
        gagnant = self.partie.gagnant()
        if gagnant is None:
            return
        texte = "Les {}s gagnent !".format(gagnant)
        self.etiquette_tour.config(text="Partie terminée")
        self.afficher_message(texte, COULEUR_SUCCES)
        if messagebox.askyesno("Partie terminée", texte + "\n\nJouer une nouvelle partie ?", parent=self):
            self.nouvelle_partie()

    def nouvelle_partie(self):
        self.partie = Partie()
        self.canvas_damier.damier = self.partie.damier
        self.canvas_damier.effacer_surlignage()
        self.actualiser_affichage("Nouvelle partie. Les blancs commencent.", COULEUR_INFO)

    def quitter_jeu(self):
        self.destroy()
