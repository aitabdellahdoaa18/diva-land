"""
systems/save_manager.py — Persistance JSON (inspiré GDD §11.4).

Choix de conception :
- Un fichier unique `save.json` à la racine du projet (simple pour un TP / soutenance).
- Backup optionnel : on pourra ajouter `save_backup.json` plus tard.

Import `json` : module Python standard pour lire/écrire du JSON.
Import `pathlib.Path` : chemins propres Windows/Linux/Mac.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SaveManager:
    """
    Sauvegarde l’état global du jeu sous forme de dictionnaire sérialisable.

    Méthode : assemble un dict “plat” depuis Economy/XP/Inventory + scores mini-jeux.
    """

    def __init__(self, save_path: Path) -> None:
        # save_path est un objet Path : ex. DivaLandByDoaa / "save.json"
        self.save_path = save_path

    def exists(self) -> bool:
        """True si une sauvegarde est déjà présente sur disque."""
        return self.save_path.is_file()

    def load(self) -> dict[str, Any]:
        """
        Lit le JSON et renvoie un dict Python.
        Si fichier absent/corrompu : dict vide (le jeu créera une nouvelle partie).
        """
        if not self.exists():
            return {}
        try:
            text = self.save_path.read_text(encoding="utf-8")
            data = json.loads(text)
            if not isinstance(data, dict):
                return {}
            return data
        except (OSError, json.JSONDecodeError):
            # OSError : fichier verrouillé, etc. JSONDecodeError : fichier tronqué.
            return {}

    def save(self, data: dict[str, Any]) -> None:
        """
        Écrit le dict en JSON indenté (lisible quand tu ouvres le fichier pour débugger).
        ensure_ascii=False permet d’écrire correctement les accents français.
        """
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.save_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
