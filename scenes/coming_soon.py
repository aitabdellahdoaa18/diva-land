"""
Écrans placeholder pour mini-jeux — fonds plein écran selon le mode :
- default : fond uni
- cooking : kitchen_scene.jpg
- riding : horse_riding.jpg avec panoramique (effet parallax léger)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from core.states import GameState, HubState
from ui import theme
from ui.widgets import TextButton

if TYPE_CHECKING:
    from core.game import Game


class ComingSoonState(GameState):
    def __init__(self, game: Game, feature_name: str, bg_mode: str = "default") -> None:
        super().__init__(game)
        self.feature_name = feature_name
        self.bg_mode = bg_mode  # default | cooking | riding
        assert game.font_ui is not None
        self.btn_back = TextButton(
            pygame.Rect(theme.SCREEN_WIDTH // 2 - 140, theme.SCREEN_HEIGHT - 120, 280, 52),
            "Retour au Hub",
            game.font_ui,
            callback=self._to_hub,
            sound_hook=game.sounds.play_ui_click,
        )
        self._parallax = 0.0
        self._gallop_started = False

    def _to_hub(self) -> None:
        self.game.sounds.stop_gallop()
        self.game.change_state(HubState(self.game))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.btn_back.set_hover(mouse)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_back.contains(event.pos):
                    self.btn_back.on_click()

    def update(self, dt: float) -> None:
        self.game.sounds.stop_music()
        if self.bg_mode == "riding":
            self._parallax += 42.0 * dt
            if not self._gallop_started:
                self.game.sounds.start_gallop_loop()
                self._gallop_started = True
        else:
            if self._gallop_started:
                self.game.sounds.stop_gallop()
                self._gallop_started = False

    def _blit_riding_parallax(self, surface: pygame.Surface) -> None:
        raw = self.game.img_riding_raw
        if raw is None:
            surface.fill((180, 210, 230))
            return
        sh = theme.SCREEN_HEIGHT
        sw_scr = theme.SCREEN_WIDTH
        rw, rh = raw.get_size()
        if rh <= 0:
            return
        scale_w = max(sw_scr + 120, int(rw / rh * sh * 1.4))
        wide = pygame.transform.smoothscale(raw, (scale_w, sh))
        max_off = max(1, wide.get_width() - sw_scr)
        xoff = int(self._parallax) % max_off
        surface.blit(wide, (0, 0), (xoff, 0, sw_scr, sh))

    def render(self, surface: pygame.Surface) -> None:
        if self.bg_mode == "cooking" and self.game.img_kitchen_bg is not None:
            surface.blit(self.game.img_kitchen_bg, (0, 0))
        elif self.bg_mode == "riding":
            self._blit_riding_parallax(surface)
        else:
            surface.fill(theme.BG)

        veil = pygame.Surface((theme.SCREEN_WIDTH, 180), pygame.SRCALPHA)
        veil.fill((255, 245, 247, 165))
        surface.blit(veil, (0, 80))

        font = self.game.font_ui
        assert font is not None
        t1 = font.render(f"Mini-jeu : {self.feature_name}", True, theme.TEXT)
        surface.blit(t1, (theme.SCREEN_WIDTH // 2 - t1.get_width() // 2, 200))
        t2 = font.render("Prototype : gameplay à venir (GDD).", True, theme.MUTED)
        surface.blit(t2, (theme.SCREEN_WIDTH // 2 - t2.get_width() // 2, 252))
        self.btn_back.draw(surface)
