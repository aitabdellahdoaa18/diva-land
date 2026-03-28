"""
systems/xp_manager.py — Niveaux et XP selon le GDD §7.1.

Formule : XP_requise pour passer du niveau n au n+1 :
    xp_required(n) = 100 + 50 * n
(où n est le niveau *actuel* avant montée ; on implémente la version du tableau du GDD.)
"""
from __future__ import annotations


def xp_required_for_next_level(current_level: int) -> int:
    """
    Retourne l’XP nécessaire pour passer de `current_level` à `current_level + 1`.

    Exemple GDD : niveau 1→2 : 150 ; on fixe donc :
        pour level=1 -> 100 + 50*1 = 150  ✓
    """
    return 100 + 50 * int(current_level)


class XPManager:
    """
    Gère level, xp dans le niveau courant, et applique les montées en cascade.

    Convention : `self.level` commence à 1 comme dans le GDD (niveau du joueur affiché).
    `self.xp` est l’XP *accumulée dans le niveau en cours* vers le palier suivant.
    """

    def __init__(self, level: int = 1, xp: int = 0) -> None:
        self.level = max(1, int(level))  # jamais en dessous de 1
        self.xp = max(0, int(xp))

    def xp_needed_for_next(self) -> int:
        """Combien d’XP encore nécessaires pour le prochain niveau (affichage barre)."""
        need = xp_required_for_next_level(self.level)
        return max(0, need - self.xp)

    def add_xp(self, amount: int) -> list[str]:
        """
        Ajoute de l’XP ; si plusieurs niveaux sont franchis d’un coup, on boucle.

        Retour :
            Liste d’IDs de déblocages “logiques” (strings) — à enrichir avec ton `levels.json`.
            Pour l’instant : messages génériques ou IDs à mapper plus tard.
        """
        if amount <= 0:
            return []

        self.xp += amount
        unlocks: list[str] = []

        # Tant qu’on a assez d’XP pour le palier courant, on monte de niveau.
        while True:
            need = xp_required_for_next_level(self.level)
            if self.xp < need:
                break
            self.xp -= need
            self.level += 1
            # Placeholder : en prod tu lirais `levels.json` pour savoir quoi débloquer.
            unlocks.append(f"level_up_{self.level}")

        return unlocks

    def to_dict(self) -> dict[str, int]:
        return {"player_level": self.level, "player_xp": self.xp}

    def load_from_dict(self, data: dict) -> None:
        self.level = max(1, int(data.get("player_level", data.get("level", 1))))
        self.xp = max(0, int(data.get("player_xp", data.get("xp", 0))))
