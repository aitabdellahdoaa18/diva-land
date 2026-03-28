"""
ui/theme.py — Couleurs et constantes visuelles (charte proche du GDD Diva Land).

Pourquoi un fichier séparé ?
- Évite de répéter des codes couleur partout dans le code.
- Si tu changes la DA, tu modifies un seul endroit.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Palette (inspirée §12.4 du GDD : rose pastel, doré, violet doux)
# ---------------------------------------------------------------------------
PRIMARY = (249, 168, 212)       # #F9A8D4 — rose principal
SECONDARY = (253, 230, 138)    # #FDE68A — jaune doré
ACCENT = (167, 139, 250)       # #A78BFA — violet doux
BG = (255, 245, 247)           # #FFF5F7 — fond clair
TEXT = (55, 48, 68)            # texte lisible sur fond clair
WHITE = (255, 255, 255)
MUTED = (156, 163, 175)

# ---------------------------------------------------------------------------
# Fenêtre et cadence (étape 0 / bonnes pratiques)
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1280   # largeur logique de la fenêtre (pixels)
SCREEN_HEIGHT = 720   # hauteur logique
FPS = 60              # images par seconde visées (fluidité)
