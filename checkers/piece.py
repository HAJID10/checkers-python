"""Pièce d'un jeu de dames."""


class Piece:
    """Une pièce d'un jeu de dames.

    Attributes:
        couleur (str): 'blanc' ou 'noir'.
        type_de_piece (str): 'pion' ou 'dame'.
    """

    def __init__(self, couleur, type_de_piece):
        self.couleur = couleur
        self.type_de_piece = type_de_piece

    def est_pion(self):
        return self.type_de_piece == "pion"

    def est_dame(self):
        return self.type_de_piece == "dame"

    def est_blanche(self):
        return self.couleur == "blanc"

    def est_noire(self):
        return self.couleur == "noir"

    def promouvoir(self):
        """Transforme la pièce en dame."""
        self.type_de_piece = "dame"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return NotImplemented
        return self.couleur == other.couleur and self.type_de_piece == other.type_de_piece

    def __repr__(self):
        """'o' / 'O' pour un pion / une dame blanche, 'x' / 'X' pour un pion / une dame noire."""
        symbole = "o" if self.est_blanche() else "x"
        return symbole.upper() if self.est_dame() else symbole
