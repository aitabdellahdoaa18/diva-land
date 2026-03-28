"""
ui/widgets.py — Petits composants UI réutilisables (bouton texte).

Pourquoi une classe Button ?
- On évite de dupliquer : test collision souris + dessin rectangle + texte.
- Pattern classique en jeux 2D : “widget” = rectangle + comportement.
"""
from __future__ import annotations

from collections.abc import Callable

import pygame

from ui import theme


class TextButton:
    """
    Bouton rectangulaire avec libellé centré.

    Champs importants :
        rect    — zone cliquable pygame.Rect
        text    — chaîne affichée
        callback — fonction sans argument appelée si clic valide (optionnel)
    """

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        *,
        callback: "callable[[], None] | None" = None,
        bg: tuple[int, int, int] | None = None,
        fg: tuple[int, int, int] | None = None,
        radius: int = 12,
        sound_hook: Callable[[], None] | None = None,
    ) -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.callback = callback
        self.sound_hook = sound_hook  # ex. game.sounds.play_ui_click
        # Couleurs par défaut cohérentes avec la charte Diva Land.
        self.bg = bg or theme.PRIMARY
        self.fg = fg or theme.TEXT
        self.radius = radius
        self.hovered = False  # mis à jour chaque frame pour feedback visuel

    def contains(self, pos: tuple[int, int]) -> bool:
        """True si la position souris est dans le rectangle du bouton."""
        return self.rect.collidepoint(pos)

    def set_hover(self, mouse_pos: tuple[int, int]) -> None:
        """Met à jour hovered selon la souris (appel depuis l’état chaque frame)."""
        self.hovered = self.contains(mouse_pos)

    def on_click(self) -> None:
        """Joue le son UI puis le callback si défini."""
        if self.sound_hook is not None:
            self.sound_hook()
        if self.callback is not None:
            self.callback()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dessine le bouton : fond arrondi + contour + texte centré.
        Si survol : fond un peu plus clair (feedback immédiat pour le joueur).
        """
        bg = self.bg
        if self.hovered:
            # Éclaircit légèrement le fond au survol (effet UX simple).
            bg = tuple(min(255, c + 25) for c in bg)

        # Pygame n’a pas de rounded rect natif partout : on utilise draw.rect si besoin,
        # mais pygame 2 propose gfxdraw ; pour rester simple : rectangle arrondi via Surface.
        pygame.draw.rect(surface, bg, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, theme.ACCENT, self.rect, width=2, border_radius=self.radius)

        label = self.font.render(self.text, True, self.fg)
        # Centrage : position du texte = centre du rect - demi-taille du label.
        tx = self.rect.centerx - label.get_width() // 2
        ty = self.rect.centery - label.get_height() // 2
        surface.blit(label, (tx, ty))
