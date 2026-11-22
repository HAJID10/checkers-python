import unittest

from checkers.damier import Damier
from checkers.piece import Piece
from checkers.position import Position as P


def damier_vide():
    damier = Damier()
    damier.cases = {}
    return damier


class TestDamierInitial(unittest.TestCase):
    def setUp(self):
        self.damier = Damier()

    def test_douze_pieces_par_couleur(self):
        couleurs = [piece.couleur for piece in self.damier.cases.values()]
        self.assertEqual(couleurs.count("blanc"), 12)
        self.assertEqual(couleurs.count("noir"), 12)

    def test_pieces_sur_cases_foncees(self):
        self.assertTrue(all((p.ligne + p.colonne) % 2 == 1 for p in self.damier.cases))

    def test_position_est_dans_damier(self):
        self.assertTrue(self.damier.position_est_dans_damier(P(0, 0)))
        self.assertTrue(self.damier.position_est_dans_damier(P(7, 7)))
        self.assertFalse(self.damier.position_est_dans_damier(P(8, 0)))
        self.assertFalse(self.damier.position_est_dans_damier(P(0, -1)))

    def test_deplacement_valide_pion_blanc(self):
        self.assertTrue(self.damier.piece_peut_se_deplacer_vers(P(5, 0), P(4, 1)))

    def test_deplacement_hors_damier_refuse(self):
        # Bogue signalé par le correcteur : (5,0) -> (4,-1) était accepté.
        self.assertFalse(self.damier.piece_peut_se_deplacer_vers(P(5, 0), P(4, -1)))

    def test_deplacement_vers_case_occupee_refuse(self):
        self.assertFalse(self.damier.piece_peut_se_deplacer_vers(P(6, 1), P(5, 0)))

    def test_pion_ne_recule_pas(self):
        damier = damier_vide()
        damier.cases[P(4, 3)] = Piece("blanc", "pion")
        self.assertFalse(damier.piece_peut_se_deplacer_vers(P(4, 3), P(5, 4)))

    def test_pieces_bloquees_ne_peuvent_pas_bouger(self):
        # Bogue signalé : (0,7) et (6,3) étaient considérées mobiles.
        self.assertFalse(self.damier.piece_peut_se_deplacer(P(0, 7)))
        self.assertFalse(self.damier.piece_peut_se_deplacer(P(6, 3)))
        self.assertTrue(self.damier.piece_peut_se_deplacer(P(5, 2)))

    def test_aucune_prise_au_debut(self):
        # Bogue signalé : toute pièce était considérée capable de prendre.
        self.assertFalse(self.damier.piece_peut_faire_une_prise(P(3, 4)))
        self.assertFalse(self.damier.piece_peut_faire_une_prise(P(5, 2)))
        self.assertFalse(self.damier.piece_de_couleur_peut_faire_une_prise("blanc"))
        self.assertFalse(self.damier.piece_de_couleur_peut_faire_une_prise("noir"))

    def test_les_deux_couleurs_peuvent_bouger(self):
        self.assertTrue(self.damier.piece_de_couleur_peut_se_deplacer("blanc"))
        self.assertTrue(self.damier.piece_de_couleur_peut_se_deplacer("noir"))
        self.assertFalse(self.damier.piece_de_couleur_peut_se_deplacer("bleu"))


class TestPrisesEtDeplacements(unittest.TestCase):
    def setUp(self):
        self.damier = damier_vide()
        self.damier.cases[P(4, 3)] = Piece("blanc", "pion")
        self.damier.cases[P(3, 4)] = Piece("noir", "pion")

    def test_saut_par_dessus_adversaire(self):
        self.assertTrue(self.damier.piece_peut_sauter_vers(P(4, 3), P(2, 5)))
        self.assertTrue(self.damier.piece_peut_sauter_vers(P(3, 4), P(5, 2)))

    def test_saut_vers_arriere_permis(self):
        self.damier.cases[P(5, 2)] = Piece("noir", "pion")
        self.assertTrue(self.damier.piece_peut_sauter_vers(P(4, 3), P(6, 1)))

    def test_saut_par_dessus_sa_couleur_refuse(self):
        self.damier.cases[P(3, 2)] = Piece("blanc", "pion")
        self.assertFalse(self.damier.piece_peut_sauter_vers(P(4, 3), P(2, 1)))

    def test_saut_vers_case_occupee_ou_hors_damier_refuse(self):
        self.damier.cases[P(2, 5)] = Piece("noir", "pion")
        self.assertFalse(self.damier.piece_peut_sauter_vers(P(4, 3), P(2, 5)))
        self.damier.cases[P(1, 6)] = Piece("blanc", "pion")
        self.damier.cases[P(0, 7)] = Piece("noir", "pion")
        self.assertFalse(self.damier.piece_peut_sauter_vers(P(1, 6), P(-1, 8)))

    def test_deplacer_ok(self):
        self.assertEqual(self.damier.deplacer(P(4, 3), P(3, 2)), "ok")
        self.assertIsNone(self.damier.recuperer_piece_a_position(P(4, 3)))
        self.assertEqual(self.damier.recuperer_piece_a_position(P(3, 2)), Piece("blanc", "pion"))

    def test_deplacer_prise_retire_la_piece(self):
        self.assertEqual(self.damier.deplacer(P(4, 3), P(2, 5)), "prise")
        self.assertIsNone(self.damier.recuperer_piece_a_position(P(3, 4)))
        self.assertEqual(len(self.damier.cases), 1)

    def test_deplacer_erreur_ne_modifie_rien(self):
        avant = dict(self.damier.cases)
        self.assertEqual(self.damier.deplacer(P(4, 3), P(4, 5)), "erreur")
        self.assertEqual(self.damier.deplacer(P(0, 0), P(1, 1)), "erreur")
        self.assertEqual(self.damier.cases, avant)

    def test_promotion_en_dame(self):
        damier = damier_vide()
        damier.cases[P(1, 2)] = Piece("blanc", "pion")
        damier.cases[P(6, 1)] = Piece("noir", "pion")
        damier.deplacer(P(1, 2), P(0, 1))
        damier.deplacer(P(6, 1), P(7, 0))
        self.assertTrue(damier.recuperer_piece_a_position(P(0, 1)).est_dame())
        self.assertTrue(damier.recuperer_piece_a_position(P(7, 0)).est_dame())

    def test_dame_recule(self):
        damier = damier_vide()
        damier.cases[P(3, 3)] = Piece("blanc", "dame")
        self.assertTrue(damier.piece_peut_se_deplacer_vers(P(3, 3), P(4, 4)))
        self.assertTrue(damier.piece_peut_se_deplacer_vers(P(3, 3), P(2, 2)))


if __name__ == "__main__":
    unittest.main()
