"""Plateau de jeu (8 x 8) et règles de déplacement des pièces."""

from checkers.piece import Piece
from checkers.position import Position


class Damier:
    """Plateau de jeu d'un jeu de dames.

    Attributes:
        cases (dict): Associe une Position à la Piece qui s'y trouve. Une case vide n'a pas de clé.
        n_lignes (int): Nombre de lignes (8).
        n_colonnes (int): Nombre de colonnes (8).
    """

    def __init__(self):
        self.n_lignes = 8
        self.n_colonnes = 8
        self.cases = {}

        # Les pièces occupent les cases foncées (ligne + colonne impaire) des trois premières
        # et trois dernières rangées.
        for ligne in range(self.n_lignes):
            for colonne in range(self.n_colonnes):
                if (ligne + colonne) % 2 == 0:
                    continue
                if ligne <= 2:
                    self.cases[Position(ligne, colonne)] = Piece("noir", "pion")
                elif ligne >= self.n_lignes - 3:
                    self.cases[Position(ligne, colonne)] = Piece("blanc", "pion")

    def recuperer_piece_a_position(self, position):
        """Retourne la pièce à la position donnée, ou None si la case est vide."""
        return self.cases.get(position)

    def position_est_dans_damier(self, position):
        """Vérifie que la position est à l'intérieur du plateau."""
        return 0 <= position.ligne < self.n_lignes and 0 <= position.colonne < self.n_colonnes

    def _case_libre(self, position):
        return self.position_est_dans_damier(position) and position not in self.cases

    def piece_peut_se_deplacer_vers(self, position_piece, position_cible):
        """Indique si la pièce à position_piece peut faire un déplacement simple (sans prise) vers position_cible.

        Un pion avance d'une case en diagonale (vers le haut s'il est blanc, vers le bas s'il est noir).
        Une dame avance d'une case sur n'importe quelle diagonale. La case cible doit être libre et dans le damier.
        """
        piece = self.recuperer_piece_a_position(position_piece)
        if piece is None or not self._case_libre(position_cible):
            return False

        if piece.est_dame():
            positions_possibles = position_piece.quatre_positions_diagonales()
        elif piece.est_blanche():
            positions_possibles = position_piece.positions_diagonales_haut()
        else:
            positions_possibles = position_piece.positions_diagonales_bas()

        return position_cible in positions_possibles

    def piece_peut_sauter_vers(self, position_piece, position_cible):
        """Indique si la pièce à position_piece peut faire une prise en sautant vers position_cible.

        Toute pièce (pion ou dame) peut sauter de deux cases en diagonale, vers l'avant ou l'arrière,
        par-dessus une pièce adverse, vers une case libre.
        """
        piece_source = self.recuperer_piece_a_position(position_piece)
        if piece_source is None or not self._case_libre(position_cible):
            return False

        if position_cible not in position_piece.quatre_positions_sauts():
            return False

        piece_sautee = self.recuperer_piece_a_position(self._position_milieu(position_piece, position_cible))
        return piece_sautee is not None and piece_sautee.couleur != piece_source.couleur

    def piece_peut_se_deplacer(self, position_piece):
        """Indique si la pièce à cette position a au moins un déplacement simple possible."""
        return any(self.piece_peut_se_deplacer_vers(position_piece, cible)
                   for cible in position_piece.quatre_positions_diagonales())

    def piece_peut_faire_une_prise(self, position_piece):
        """Indique si la pièce à cette position a au moins une prise possible."""
        return any(self.piece_peut_sauter_vers(position_piece, cible)
                   for cible in position_piece.quatre_positions_sauts())

    def _positions_de_couleur(self, couleur):
        return [position for position, piece in self.cases.items() if piece.couleur == couleur]

    def piece_de_couleur_peut_se_deplacer(self, couleur):
        """Indique si au moins une pièce de cette couleur peut faire un déplacement simple."""
        return any(self.piece_peut_se_deplacer(position) for position in self._positions_de_couleur(couleur))

    def piece_de_couleur_peut_faire_une_prise(self, couleur):
        """Indique si au moins une pièce de cette couleur peut faire une prise."""
        return any(self.piece_peut_faire_une_prise(position) for position in self._positions_de_couleur(couleur))

    def deplacer(self, position_source, position_cible):
        """Effectue un déplacement ou une prise, puis promeut le pion en dame s'il atteint la dernière rangée.

        Returns:
            str: "ok" pour un déplacement simple, "prise" si une pièce adverse a été prise, "erreur" si le coup
                est invalide (le damier n'est alors pas modifié).
        """
        if self.piece_peut_se_deplacer_vers(position_source, position_cible):
            resultat = "ok"
        elif self.piece_peut_sauter_vers(position_source, position_cible):
            del self.cases[self._position_milieu(position_source, position_cible)]
            resultat = "prise"
        else:
            return "erreur"

        piece = self.cases.pop(position_source)
        self.cases[position_cible] = piece

        derniere_rangee = 0 if piece.est_blanche() else self.n_lignes - 1
        if piece.est_pion() and position_cible.ligne == derniere_rangee:
            piece.promouvoir()

        return resultat

    @staticmethod
    def _position_milieu(position_a, position_b):
        return Position((position_a.ligne + position_b.ligne) // 2, (position_a.colonne + position_b.colonne) // 2)

    def __repr__(self):
        """Représentation texte du damier, utilisée par la version console."""
        s = " +-0-+-1-+-2-+-3-+-4-+-5-+-6-+-7-+\n"
        for i in range(self.n_lignes):
            s += str(i) + "| "
            for j in range(self.n_colonnes):
                piece = self.recuperer_piece_a_position(Position(i, j))
                s += (str(piece) if piece else " ") + " | "
            s += "\n +---+---+---+---+---+---+---+---+\n"
        return s
