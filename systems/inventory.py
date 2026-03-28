"""
systems/inventory.py — Items possédés + équipement (GDD inventaire / personnalisation).

Version pédagogique : on stocke des IDs en string ; les détails (nom, sprite) viendront de `items.json`.
"""
from __future__ import annotations


class Inventory:
    """Inventaire simple : propriété + équipement par slot."""

    def __init__(self) -> None:
        # Ensemble pour éviter les doublons (chaque ID une seule fois possédé).
        self.owned: set[str] = set()
        # Slots d’équipement (tu peux en ajouter au fil du projet).
        self.equipped: dict[str, str | None] = {
            "head": None,
            "dress": None,
            "accessory": None,
        }
        # Tenue visuelle hub / personnalisation : -1 = sprite `princess_main`, 0..7 = cellule du sprite sheet.
        self.costume_index: int = -1

    def add_item(self, item_id: str) -> None:
        """Ajoute un item au joueur s’il n’est pas déjà possédé."""
        self.owned.add(item_id)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.owned

    def equip(self, slot: str, item_id: str | None) -> None:
        """
        Équipe un item sur un slot ; None déséquipe.
        Ici on ne valide pas encore contre items.json (étape suivante).
        """
        if slot not in self.equipped:
            return
        self.equipped[slot] = item_id

    def to_dict(self) -> dict:
        """Format proche du GDD pour la sauvegarde."""
        return {
            "inventory": sorted(self.owned),
            "equipped": dict(self.equipped),
            "costume_index": int(self.costume_index),
        }

    def load_from_dict(self, data: dict) -> None:
        inv = data.get("inventory", [])
        self.owned = set(str(x) for x in inv)
        eq = data.get("equipped", {})
        for k in self.equipped:
            v = eq.get(k)
            self.equipped[k] = str(v) if v else None
        ci = data.get("costume_index", -1)
        self.costume_index = int(ci) if ci is not None else -1
        if self.costume_index > 7:
            self.costume_index = 7
