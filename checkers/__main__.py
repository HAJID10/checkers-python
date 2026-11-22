"""Point d'entrée : `python -m checkers` (interface graphique) ou `python -m checkers --console`."""

import sys


def main():
    if "--console" in sys.argv[1:]:
        from checkers.partie import Partie
        gagnant = Partie().jouer()
        print("Partie terminée ! Les {}s gagnent.".format(gagnant))
    else:
        from checkers.interface import FenetrePartie
        FenetrePartie().mainloop()


if __name__ == "__main__":
    main()
