"""
main.py — Point d’entrée du jeu Diva Land (lancer ce fichier).

Comment l’exécuter (Windows, PowerShell) :
    cd c:\\Users\\admin\\Desktop\\DivaLandByDoaa
    python -m pip install -r requirements.txt
    python main.py

Rôle :
- Crée une instance de `Game`.
- Charge éventuellement `save.json` (persistant dans le dossier du projet).
- Démarre la boucle Pygame (`game.run()`).

Note ingénieur :
- Le bloc `if __name__ == "__main__":` garantit que ce code ne s’exécute que lorsque
  tu lances le script directement (pas quand un autre module fait `import main`).
"""
from __future__ import annotations

from core.game import Game


def main() -> None:
    """Fonction principale : tout le setup minimal avant la boucle."""
    game = Game()
    # Chargement automatique de la sauvegarde si elle existe (économie + XP + inventaire).
    game.try_autoload()
    game.run()


if __name__ == "__main__":
    main()
