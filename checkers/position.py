"""Position sur le damier, en notation matricielle : (0, 0) est le coin supérieur gauche."""


class Position:
    """Une position à deux coordonnées : ligne et colonne.

    On ajoute une unité de colonne en allant vers la droite et une unité de ligne en allant vers le bas.
    Toutes les positions (même négatives) sont permises ici ; c'est le Damier qui valide les bornes.

    Attributes:
        ligne (int): La ligne de la position.
        colonne (int): La colonne de la position.
    """

    def __init__(self, ligne, colonne):
        self.ligne = int(ligne)
        self.colonne = int(colonne)

    def positions_diagonales_bas(self):
        """Retourne les deux positions diagonales vers le bas (à gauche puis à droite)."""
        return [Position(self.ligne + 1, self.colonne - 1), Position(self.ligne + 1, self.colonne + 1)]

    def positions_diagonales_haut(self):
        """Retourne les deux positions diagonales vers le haut (à gauche puis à droite)."""
        return [Position(self.ligne - 1, self.colonne - 1), Position(self.ligne - 1, self.colonne + 1)]

    def quatre_positions_diagonales(self):
        """Retourne les quatre positions diagonales adjacentes."""
        return self.positions_diagonales_haut() + self.positions_diagonales_bas()

    def quatre_positions_sauts(self):
        """Retourne les quatre positions diagonales situées à une distance de 2 (les « sauts »)."""
        return [
            Position(self.ligne - 2, self.colonne - 2),
            Position(self.ligne - 2, self.colonne + 2),
            Position(self.ligne + 2, self.colonne - 2),
            Position(self.ligne + 2, self.colonne + 2),
        ]

    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.ligne == other.ligne and self.colonne == other.colonne

    def __hash__(self):
        return hash((self.ligne, self.colonne))

    def __repr__(self):
        return '({}, {})'.format(self.ligne, self.colonne)
