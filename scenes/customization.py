"""
Écran de personnalisation (avant le hub) :
- `princess_main.jpg` au centre comme tenue d’origine (costume_index == -1).
- Les 8 cellules de `princess_costumes.jpg` en vignettes cliquables.
- « Commencer » → sauvegarde + hub.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from core.states import GameState, HubState
from ui import theme
from ui.widgets import TextButton

if TYPE_CHECKING:
    from core.game import Game


class CustomizationState(GameState):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None and game.font_title is not None
        w = theme.SCREEN_WIDTH
        self.preview_rect = pygame.Rect(0, 0, 340, 420)
        self.preview_rect.center = (w // 2, 270)

        self.thumb_rects: list[tuple[int, pygame.Rect]] = []
        tw, th, gap = 108, 138, 10
        grid_left = (w - (4 * tw + 3 * gap)) // 2
        base_y = 500
        idx = 0
        for row in range(2):
            for col in range(4):
                r = pygame.Rect(grid_left + col * (tw + gap), base_y + row * (th + gap), tw, th)
                self.thumb_rects.append((idx, r))
                idx += 1

        self.btn_original = TextButton(
            pygame.Rect(40, theme.SCREEN_HEIGHT - 130, 240, 48),
            "Tenue d'origine",
            game.font_ui,
            callback=self._use_original,
            bg=theme.MUTED,
            sound_hook=game.sounds.play_ui_click,
        )
        self.btn_start = TextButton(
            pygame.Rect(w // 2 - 140, theme.SCREEN_HEIGHT - 130, 280, 56),
            "Commencer",
            game.font_ui,
            callback=self._to_hub,
            sound_hook=game.sounds.play_ui_click,
        )

    def _use_original(self) -> None:
        self.game.inventory.costume_index = -1

    def _pick(self, i: int) -> None:
        if 0 <= i < len(self.game.costume_cells):
            self.game.inventory.costume_index = i

    def _to_hub(self) -> None:
        self.game.save_game()
        self.game.change_state(HubState(self.game))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.btn_original.set_hover(mouse)
        self.btn_start.set_hover(mouse)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_original.contains(event.pos):
                    self.btn_original.on_click()
                    continue
                if self.btn_start.contains(event.pos):
                    self.btn_start.on_click()
                    continue
                for idx, rect in self.thumb_rects:
                    if rect.collidepoint(event.pos):
                        self.game.sounds.play_ui_click()
                        self._pick(idx)

    def update(self, dt: float) -> None:
        _ = dt
        self.game.sounds.stop_music()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((255, 248, 252))
        font = self.game.font_ui
        assert font is not None

        t = self.game.font_title.render("Ta princesse", True, theme.TEXT)
        surface.blit(t, (theme.SCREEN_WIDTH // 2 - t.get_width() // 2, 36))
        surface.blit(
            font.render("Choisis une tenue (clic) puis Commencer.", True, theme.MUTED),
            (theme.SCREEN_WIDTH // 2 - 260, 100),
        )

        pygame.draw.rect(surface, theme.WHITE, self.preview_rect, border_radius=16)
        pygame.draw.rect(surface, theme.ACCENT, self.preview_rect, width=3, border_radius=16)

        # Aperçu central : tenue d’origine ou costume équipé
        if self.game.inventory.costume_index < 0:
            src = self.game.img_princess
        else:
            ci = self.game.inventory.costume_index
            src = (
                self.game.costume_cells[ci]
                if 0 <= ci < len(self.game.costume_cells)
                else self.game.img_princess
            )

        if src is not None:
            scaled = pygame.transform.smoothscale(
                src,
                (self.preview_rect.width - 16, self.preview_rect.height - 16),
            )
            dx = self.preview_rect.centerx - scaled.get_width() // 2
            dy = self.preview_rect.centery - scaled.get_height() // 2
            surface.blit(scaled, (dx, dy))

        # Vignettes 0..7
        for idx, rect in self.thumb_rects:
            if idx < len(self.game.costume_cells):
                thumb = pygame.transform.smoothscale(self.game.costume_cells[idx], (rect.w - 6, rect.h - 6))
                surface.blit(thumb, (rect.x + 3, rect.y + 3))
            else:
                pygame.draw.rect(surface, theme.MUTED, rect, border_radius=10)

            sel = self.game.inventory.costume_index == idx
            border_col = theme.SECONDARY if sel else theme.TEXT
            pygame.draw.rect(surface, border_col, rect, width=3 if sel else 2, border_radius=10)
            lbl = font.render(str(idx + 1), True, theme.WHITE)
            surface.blit(lbl, (rect.right - lbl.get_width() - 6, rect.y + 6))

        if self.game.inventory.costume_index < 0:
            tag = font.render("Mode : illustration d'origine", True, theme.PRIMARY)
            surface.blit(tag, (self.preview_rect.x, self.preview_rect.bottom + 12))

        self.btn_original.draw(surface)
        self.btn_start.draw(surface)
