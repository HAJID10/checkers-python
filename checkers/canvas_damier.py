"""Widget Tkinter qui dessine le damier, les pièces et la sélection courante."""

from tkinter import Canvas

from checkers.position import Position

COULEUR_CASE_CLAIRE = "#F0D9B5"
COULEUR_CASE_FONCEE = "#B58863"
COULEUR_SELECTION = "#F6F669"
COULEUR_CIBLE = "#6FB46F"


class CanvasDamier(Canvas):
    """Affichage du damier. Se redimensionne avec la fenêtre en gardant des cases carrées.

    Attributes:
        damier (Damier): Le damier à dessiner.
        n_pixels_par_case (int): Taille d'une case, en pixels.
        position_selectionnee (Position): La pièce surlignée, ou None.
        cibles (list): Les positions où la pièce sélectionnée peut aller (marquées d'un point).
    """

    def __init__(self, parent, damier, n_pixels_par_case=70):
        self.damier = damier
        self.n_pixels_par_case = n_pixels_par_case
        self.position_selectionnee = None
        self.cibles = []

        super().__init__(parent, width=damier.n_colonnes * n_pixels_par_case,
                         height=damier.n_lignes * n_pixels_par_case, highlightthickness=0)
        self.bind("<Configure>", self.redimensionner)

    def position_depuis_pixels(self, x, y):
        """Convertit un clic (en pixels) en Position, ou None si le clic est hors du damier."""
        position = Position(y // self.n_pixels_par_case, x // self.n_pixels_par_case)
        return position if self.damier.position_est_dans_damier(position) else None

    def surligner(self, position, cibles):
        self.position_selectionnee = position
        self.cibles = list(cibles)
        self.actualiser()

    def effacer_surlignage(self):
        self.surligner(None, [])

    def _rectangle_de_case(self, position):
        taille = self.n_pixels_par_case
        x, y = position.colonne * taille, position.ligne * taille
        return x, y, x + taille, y + taille

    def dessiner_cases(self):
        for ligne in range(self.damier.n_lignes):
            for colonne in range(self.damier.n_colonnes):
                position = Position(ligne, colonne)
                if position == self.position_selectionnee:
                    couleur = COULEUR_SELECTION
                elif (ligne + colonne) % 2 == 0:
                    couleur = COULEUR_CASE_CLAIRE
                else:
                    couleur = COULEUR_CASE_FONCEE
                self.create_rectangle(*self._rectangle_de_case(position), fill=couleur, width=0, tags="case")

        # Un point vert sur chaque case où la pièce sélectionnée peut aller.
        rayon = self.n_pixels_par_case // 7
        for cible in self.cibles:
            x0, y0, x1, y1 = self._rectangle_de_case(cible)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            self.create_oval(cx - rayon, cy - rayon, cx + rayon, cy + rayon,
                             fill=COULEUR_CIBLE, width=0, tags="case")

    def dessiner_pieces(self):
        marge = self.n_pixels_par_case // 8
        for position, piece in self.damier.cases.items():
            x0, y0, x1, y1 = self._rectangle_de_case(position)
            remplissage, contour = ("#FAFAFA", "#555555") if piece.est_blanche() else ("#222222", "#000000")
            self.create_oval(x0 + marge, y0 + marge, x1 - marge, y1 - marge,
                             fill=remplissage, outline=contour, width=2, tags="piece")
            if piece.est_dame():
                # Une couronne (anneau doré) distingue les dames des pions.
                marge_dame = self.n_pixels_par_case // 3
                self.create_oval(x0 + marge_dame, y0 + marge_dame, x1 - marge_dame, y1 - marge_dame,
                                 outline="#D4AF37", width=3, tags="piece")

    def redimensionner(self, event):
        taille = min(event.width, event.height)
        self.n_pixels_par_case = max(1, taille // self.damier.n_lignes)
        self.actualiser()

    def actualiser(self):
        """Redessine entièrement le damier."""
        self.delete("all")
        self.dessiner_cases()
        self.dessiner_pieces()
