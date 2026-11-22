import unittest

from checkers.partie import Partie
from checkers.piece import Piece
from checkers.position import Position as P


def partie_avec(pieces, joueur="blanc"):
    """Crée une partie avec seulement les pièces données ({Position: Piece})."""
    partie = Partie()
    partie.damier.cases = dict(pieces)
    partie.couleur_joueur_courant = joueur
    partie._mettre_a_jour_doit_prendre()
    return partie


class TestValidation(unittest.TestCase):
    def test_etat_initial(self):
        partie = Partie()
        self.assertEqual(partie.couleur_joueur_courant, "blanc")
        self.assertFalse(partie.doit_prendre)

    def test_source_vide_ne_plante_pas(self):
        valide, message = Partie().position_source_valide(P(4, 4))
        self.assertFalse(valide)
        self.assertTrue(message)

    def test_source_hors_damier(self):
        self.assertFalse(Partie().position_source_valide(P(-1, 9))[0])

    def test_source_adverse_refusee(self):
        self.assertFalse(Partie().position_source_valide(P(2, 1))[0])

    def test_source_bloquee_refusee(self):
        self.assertFalse(Partie().position_source_valide(P(6, 1))[0])

    def test_coup_valide_premier_tour(self):
        # Bogue signalé : (5,0) -> (4,1) était refusé.
        partie = Partie()
        resultat, _ = partie.jouer_coup(P(5, 0), P(4, 1))
        self.assertEqual(resultat, "ok")
        self.assertEqual(partie.couleur_joueur_courant, "noir")

    def test_coup_invalide_ne_change_pas_de_joueur(self):
        partie = Partie()
        resultat, _ = partie.jouer_coup(P(5, 0), P(3, 2))
        self.assertEqual(resultat, "erreur")
        self.assertEqual(partie.couleur_joueur_courant, "blanc")

    def test_cibles_possibles(self):
        self.assertEqual(Partie().cibles_possibles(P(5, 2)), [P(4, 1), P(4, 3)])


class TestPriseObligatoire(unittest.TestCase):
    def setUp(self):
        self.partie = partie_avec({
            P(5, 2): Piece("blanc", "pion"),
            P(5, 6): Piece("blanc", "pion"),
            P(4, 3): Piece("noir", "pion"),
            P(0, 1): Piece("noir", "pion"),
        })

    def test_doit_prendre(self):
        self.assertTrue(self.partie.doit_prendre)

    def test_piece_qui_ne_peut_pas_prendre_refusee(self):
        self.assertFalse(self.partie.position_source_valide(P(5, 6))[0])

    def test_deplacement_simple_refuse_si_prise_possible(self):
        self.assertEqual(self.partie.jouer_coup(P(5, 2), P(4, 1))[0], "erreur")

    def test_prise_valide(self):
        self.assertEqual(self.partie.jouer_coup(P(5, 2), P(3, 4))[0], "prise")
        self.assertEqual(self.partie.couleur_joueur_courant, "noir")


class TestPrisesMultiples(unittest.TestCase):
    def setUp(self):
        self.partie = partie_avec({
            P(6, 1): Piece("blanc", "pion"),
            P(5, 2): Piece("noir", "pion"),
            P(3, 4): Piece("noir", "pion"),
            P(5, 6): Piece("blanc", "pion"),
            P(0, 7): Piece("noir", "pion"),
        })

    def test_le_meme_joueur_continue(self):
        resultat, _ = self.partie.jouer_coup(P(6, 1), P(4, 3))
        self.assertEqual(resultat, "prise_continue")
        self.assertEqual(self.partie.couleur_joueur_courant, "blanc")
        self.assertEqual(self.partie.position_source_forcee, P(4, 3))

    def test_seule_la_piece_forcee_peut_jouer(self):
        self.partie.jouer_coup(P(6, 1), P(4, 3))
        self.assertFalse(self.partie.position_source_valide(P(5, 6))[0])
        self.assertTrue(self.partie.position_source_valide(P(4, 3))[0])

    def test_fin_de_la_prise_multiple(self):
        self.partie.jouer_coup(P(6, 1), P(4, 3))
        resultat, _ = self.partie.jouer_coup(P(4, 3), P(2, 5))
        self.assertEqual(resultat, "prise")
        self.assertEqual(self.partie.couleur_joueur_courant, "noir")
        self.assertIsNone(self.partie.position_source_forcee)


class TestFinDePartie(unittest.TestCase):
    def test_partie_en_cours(self):
        self.assertFalse(Partie().partie_terminee())
        self.assertIsNone(Partie().gagnant())

    def test_joueur_sans_piece_perd(self):
        partie = partie_avec({P(4, 3): Piece("blanc", "pion")}, joueur="noir")
        self.assertTrue(partie.partie_terminee())
        self.assertEqual(partie.gagnant(), "blanc")

    def test_joueur_bloque_perd(self):
        partie = partie_avec({
            P(7, 0): Piece("noir", "pion"),
            P(6, 1): Piece("blanc", "pion"),
            P(5, 2): Piece("blanc", "pion"),
        }, joueur="noir")
        self.assertTrue(partie.partie_terminee())
        self.assertEqual(partie.gagnant(), "blanc")


class TestConsole(unittest.TestCase):
    def test_entrees_invalides_ne_plantent_pas(self):
        import builtins
        from unittest import mock

        # Après une cible invalide, la source est redemandée (le joueur peut changer de pièce).
        entrees = iter(["abc", "", "4 4", "5 0", "9 9", "5 0", "4 1"])
        with mock.patch.object(builtins, "input", lambda _: next(entrees)), mock.patch("builtins.print"):
            source, cible = Partie().demander_positions_deplacement()
        self.assertEqual((source, cible), (P(5, 0), P(4, 1)))


if __name__ == "__main__":
    unittest.main()
