"""Gestion d'une partie : tour des joueurs, prise obligatoire et prises multiples."""

from checkers.damier import Damier
from checkers.position import Position


class Partie:
    """Gestionnaire de partie de dames.

    Attributes:
        damier (Damier): Le damier de la partie.
        couleur_joueur_courant (str): 'blanc' ou 'noir'. Les blancs commencent.
        doit_prendre (bool): True si le joueur courant est obligé de faire une prise.
        position_source_selectionnee (Position): La pièce choisie pour le coup en cours, ou None.
        position_source_forcee (Position): Après une prise, si la même pièce peut encore prendre, le joueur doit
            continuer avec elle. None si aucune pièce n'est forcée.
    """

    def __init__(self):
        self.damier = Damier()
        self.couleur_joueur_courant = "blanc"
        self.doit_prendre = False
        self.position_source_selectionnee = None
        self.position_source_forcee = None
        self._mettre_a_jour_doit_prendre()

    def _mettre_a_jour_doit_prendre(self):
        self.doit_prendre = (self.position_source_forcee is not None or
                             self.damier.piece_de_couleur_peut_faire_une_prise(self.couleur_joueur_courant))

    @property
    def couleur_adversaire(self):
        return "noir" if self.couleur_joueur_courant == "blanc" else "blanc"

    def position_source_valide(self, position_source):
        """Vérifie que le joueur courant peut jouer la pièce à cette position.

        Returns:
            (bool, str): La validité, et un message d'erreur (chaîne vide si valide).
        """
        if not self.damier.position_est_dans_damier(position_source):
            return False, "Cette position est hors du damier."

        piece = self.damier.recuperer_piece_a_position(position_source)
        if piece is None:
            return False, "Aucune pièce à cette position."

        if piece.couleur != self.couleur_joueur_courant:
            return False, "Cette pièce appartient au joueur {}.".format(piece.couleur)

        if self.position_source_forcee is not None and position_source != self.position_source_forcee:
            return False, "Vous devez continuer la prise avec la pièce en {}.".format(self.position_source_forcee)

        if self.doit_prendre:
            if not self.damier.piece_peut_faire_une_prise(position_source):
                return False, "Une prise est obligatoire : choisissez une pièce qui peut prendre."
        elif not self.damier.piece_peut_se_deplacer(position_source):
            return False, "Cette pièce ne peut pas se déplacer."

        return True, ""

    def position_cible_valide(self, position_cible):
        """Vérifie que la pièce sélectionnée peut aller à cette position, en respectant la prise obligatoire.

        Returns:
            (bool, str): La validité, et un message d'erreur (chaîne vide si valide).
        """
        source = self.position_source_selectionnee
        if source is None:
            return False, "Aucune pièce n'est sélectionnée."

        if self.doit_prendre:
            if self.damier.piece_peut_sauter_vers(source, position_cible):
                return True, ""
            return False, "Une prise est obligatoire : ce coup n'est pas une prise valide."

        if self.damier.piece_peut_se_deplacer_vers(source, position_cible):
            return True, ""
        return False, "La position cible n'est pas valide."

    def cibles_possibles(self, position_source):
        """Liste les positions où la pièce à position_source peut aller pendant ce tour."""
        if self.doit_prendre:
            return [cible for cible in position_source.quatre_positions_sauts()
                    if self.damier.piece_peut_sauter_vers(position_source, cible)]
        return [cible for cible in position_source.quatre_positions_diagonales()
                if self.damier.piece_peut_se_deplacer_vers(position_source, cible)]

    def jouer_coup(self, position_source, position_cible):
        """Valide et joue un coup, puis met à jour le tour.

        Returns:
            (str, str): Un résultat parmi "erreur", "ok", "prise" ou "prise_continue" (le même joueur doit encore
                prendre avec la même pièce), et un message pour l'utilisateur.
        """
        valide, message = self.position_source_valide(position_source)
        if not valide:
            return "erreur", message

        self.position_source_selectionnee = position_source
        valide, message = self.position_cible_valide(position_cible)
        if not valide:
            return "erreur", message

        resultat = self.damier.deplacer(position_source, position_cible)
        self.position_source_selectionnee = None

        if resultat == "prise" and self.damier.piece_peut_faire_une_prise(position_cible):
            self.position_source_forcee = position_cible
            self.doit_prendre = True
            return "prise_continue", "Prise ! Continuez à prendre avec la pièce en {}.".format(position_cible)

        self.position_source_forcee = None
        self.couleur_joueur_courant = self.couleur_adversaire
        self._mettre_a_jour_doit_prendre()
        return resultat, "Prise !" if resultat == "prise" else "Déplacement effectué."

    def partie_terminee(self):
        """La partie se termine quand le joueur courant n'a plus aucun coup possible."""
        return not (self.damier.piece_de_couleur_peut_se_deplacer(self.couleur_joueur_courant) or
                    self.damier.piece_de_couleur_peut_faire_une_prise(self.couleur_joueur_courant))

    def gagnant(self):
        """Retourne la couleur gagnante, ou None si la partie n'est pas terminée."""
        return self.couleur_adversaire if self.partie_terminee() else None

    # ------------------------------------------------------------------ Version console

    @staticmethod
    def _demander_position(message):
        while True:
            texte = input(message).replace(",", " ").split()
            if len(texte) == 2 and all(valeur.lstrip("-").isdigit() for valeur in texte):
                return Position(int(texte[0]), int(texte[1]))
            print("Entrez une ligne et une colonne, par exemple : 5 0")

    def demander_positions_deplacement(self):
        """Demande à l'utilisateur une source puis une cible valides. Ne plante jamais, peu importe l'entrée."""
        while True:
            source = self._demander_position("Position source (ligne colonne) : ")
            valide, message = self.position_source_valide(source)
            if not valide:
                print(message)
                continue

            self.position_source_selectionnee = source
            cible = self._demander_position("Position cible (ligne colonne) : ")
            valide, message = self.position_cible_valide(cible)
            if valide:
                return source, cible
            print(message)

    def tour(self):
        """Joue un tour complet en mode console."""
        print(self.damier)
        print("Tour du joueur {}.".format(self.couleur_joueur_courant), end="")
        if self.position_source_forcee is not None:
            print(" Doit prendre avec la pièce en {}.".format(self.position_source_forcee))
        elif self.doit_prendre:
            print(" Doit prendre une pièce.")
        else:
            print()

        source, cible = self.demander_positions_deplacement()
        _, message = self.jouer_coup(source, cible)
        print(message)

    def jouer(self):
        """Joue une partie complète en console et retourne la couleur gagnante."""
        while not self.partie_terminee():
            self.tour()
        print(self.damier)
        return self.gagnant()
