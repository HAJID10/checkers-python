import unittest

from checkers.position import Position


class TestPosition(unittest.TestCase):
    def test_diagonales_bas(self):
        self.assertEqual(Position(4, 4).positions_diagonales_bas(), [Position(5, 3), Position(5, 5)])

    def test_diagonales_haut(self):
        self.assertEqual(Position(4, 4).positions_diagonales_haut(), [Position(3, 3), Position(3, 5)])

    def test_quatre_diagonales(self):
        self.assertEqual(Position(2, 2).quatre_positions_diagonales(),
                         [Position(1, 1), Position(1, 3), Position(3, 1), Position(3, 3)])

    def test_quatre_sauts(self):
        self.assertEqual(Position(4, 4).quatre_positions_sauts(),
                         [Position(2, 2), Position(2, 6), Position(6, 2), Position(6, 6)])

    def test_egalite_et_hachage(self):
        self.assertEqual(Position(1, 2), Position(1, 2))
        self.assertNotEqual(Position(1, 2), Position(2, 1))
        self.assertNotEqual(Position(1, 2), "(1, 2)")
        self.assertEqual(len({Position(1, 2), Position(1, 2)}), 1)


if __name__ == "__main__":
    unittest.main()
