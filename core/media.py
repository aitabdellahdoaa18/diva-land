"""
core/media.py — Chargement et redimensionnement d’images (JPG/PNG).

Place tes fichiers dans : assets/sprites/
Si un fichier manque, le jeu continue avec un fond couleur (pas de crash).

`convert()` après chargement : met le format des pixels en accord avec l/display pour blit plus rapide.
"""
from __future__ import annotations

from pathlib import Path

import pygame


def try_load_convert(path: Path) -> pygame.Surface | None:
    """Charge une image depuis le disque ou None si absente / erreur."""
    try:
        if path.is_file():
            return pygame.image.load(str(path)).convert()
    except (pygame.error, OSError):
        pass
    return None


def scale_stretch(surface: pygame.Surface, width: int, height: int) -> pygame.Surface:
    """Étire exactement à width×height (fonds plein écran menu / hub)."""
    return pygame.transform.smoothscale(surface, (width, height))


def scale_fit(surface: pygame.Surface, max_width: int, max_height: int) -> pygame.Surface:
    """Réduit/agrandit en gardant le ratio ; tient dans max_width × max_height."""
    w, h = surface.get_size()
    if w <= 0 or h <= 0:
        return surface
    scale = min(max_width / w, max_height / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    return pygame.transform.smoothscale(surface, (nw, nh))
