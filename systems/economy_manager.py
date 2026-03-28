"""
systems/economy_manager.py — Gestion des trois monnaies (GDD §8.1).

Rôle pédagogique :
- Centraliser toute modification des balances (évite les bugs d’“oubli” de maj).
- Les mini-jeux ne font que demander des ajouts via des appels explicites.
"""
from __future__ import annotations


class EconomyManager:
    """
    Stocke pièces, étoiles, couronnes et expose des méthodes sûres pour les modifier.

    Attributs :
        coins  — monnaie “courante” des récompenses fréquentes.
        stars  — récompenses de performance / défis.
        crowns — récompenses liées aux succès (plus rares).
    """

    def __init__(self, coins: int = 0, stars: int = 0, crowns: int = 0) -> None:
        # Valeurs initiales : en nouvelle partie on part souvent à 0 partout.
        self.coins = int(coins)
        self.stars = int(stars)
        self.crowns = int(crowns)

    # -- Lecture ------------------------------------------------------------
    def get_balances(self) -> dict[str, int]:
        """Retourne un dict pratique pour l’UI ou la sauvegarde (pas de logique ici)."""
        return {"coins": self.coins, "stars": self.stars, "crowns": self.crowns}

    # -- Gains (toujours positifs ou nuls) ----------------------------------
    def add_coins(self, amount: int) -> None:
        """Ajoute des pièces ; refuse les montants négatifs pour éviter les abus."""
        if amount <= 0:
            return
        self.coins += amount

    def add_stars(self, amount: int) -> None:
        """Ajoute des étoiles (même idée que add_coins)."""
        if amount <= 0:
            return
        self.stars += amount

    def add_crowns(self, amount: int) -> None:
        """Ajoute des couronnes."""
        if amount <= 0:
            return
        self.crowns += amount

    # -- Dépenses (achats futurs : boutique) -------------------------------
    def can_afford(self, coins: int = 0, stars: int = 0, crowns: int = 0) -> bool:
        """
        Vérifie si le joueur peut payer un coût multi-monnaies.
        Tous les paramètres sont optionnels (0 = pas exigé pour cette monnaie).
        """
        return (
            self.coins >= coins
            and self.stars >= stars
            and self.crowns >= crowns
        )

    def spend(self, coins: int = 0, stars: int = 0, crowns: int = 0) -> bool:
        """
        Tente de retirer les montants ; retourne False si impossible (sans modifier).
        Pattern standard : "transaction" atomique (tout ou rien).
        """
        if not self.can_afford(coins=coins, stars=stars, crowns=crowns):
            return False
        self.coins -= coins
        self.stars -= stars
        self.crowns -= crowns
        return True

    # -- Sérialisation (pour SaveManager) ----------------------------------
    def to_dict(self) -> dict[str, int]:
        """Représentation minimale pour JSON (clés stables : mêmes noms que le GDD)."""
        return {"coins": self.coins, "stars": self.stars, "crowns": self.crowns}

    def load_from_dict(self, data: dict) -> None:
        """Recharge depuis un dict (après load JSON) ; garde des entiers."""
        self.coins = int(data.get("coins", 0))
        self.stars = int(data.get("stars", 0))
        self.crowns = int(data.get("crowns", 0))
