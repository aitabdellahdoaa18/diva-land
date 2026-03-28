"""
core/states.py — États du jeu (Menu, Hub, Résultats) et classe de base `GameState`.

Pattern “State” :
- La classe Game délègue ; chaque écran implémente les 3 méthodes handle_events / update / render.
- On évite un énorme if/elif dans la boucle : le polymorphisme remplace les branches.

Imports différés :
- Depuis HubState, on importe les scènes de mini-jeux *à l’intérieur* des méthodes pour
  éviter les imports circulaires (scenes.xo importe GameState depuis ici).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

from ui import theme
from ui.widgets import TextButton

if TYPE_CHECKING:
    from core.game import Game


class GameState(ABC):
    """Contrat minimal de tout écran du jeu."""

    def __init__(self, game: Game) -> None:
        self.game = game  # référence vers le moteur : accès aux systèmes, changer d’état, etc.

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Traite la liste d’événements pygame de cette frame."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Met à jour la logique ; dt = secondes depuis la frame précédente."""

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Dessine l’écran sur la surface principale."""


class MenuState(GameState):
    """Menu principal : entrée dans l’expérience Diva Land."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None and game.font_title is not None
        w, h = theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT
        # Deux boutons centrés verticalement sous le titre.
        self.btn_play = TextButton(
            pygame.Rect(w // 2 - 160, h // 2 + 40, 320, 56),
            "Personnaliser",
            game.font_ui,
            callback=self._on_play,
            sound_hook=game.sounds.play_ui_click,
        )
        self.btn_quit = TextButton(
            pygame.Rect(w // 2 - 160, h // 2 + 120, 320, 56),
            "Quitter + sauver",
            game.font_ui,
            callback=self._on_quit,
            bg=theme.MUTED,
            sound_hook=game.sounds.play_ui_click,
        )

    def _on_play(self) -> None:
        """Vers l’écran de personnalisation puis le hub (bouton Commencer)."""
        from scenes.customization import CustomizationState

        self.game.change_state(CustomizationState(self.game))

    def _on_quit(self) -> None:
        """Quitte le programme après sauvegarde (voir Game.request_quit)."""
        self.game.request_quit()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.btn_play.set_hover(mouse)
        self.btn_quit.set_hover(mouse)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_play.contains(event.pos):
                    self.btn_play.on_click()
                elif self.btn_quit.contains(event.pos):
                    self.btn_quit.on_click()

    def update(self, dt: float) -> None:
        _ = dt
        self.game.sounds.stop_music()

    def render(self, surface: pygame.Surface) -> None:
        # Fond : `title_screen.jpg` — le titre graphique est déjà dans l’illustration.
        if self.game.img_menu_bg is not None:
            surface.blit(self.game.img_menu_bg, (0, 0))
            veil = pygame.Surface((theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT), pygame.SRCALPHA)
            veil.fill((30, 20, 50, 55))
            surface.blit(veil, (0, 0))
        else:
            surface.fill(theme.BG)

        title_col = (255, 255, 255) if self.game.img_menu_bg else theme.TEXT
        sub = self.game.font_ui.render("Diva Land — Choisis une option", True, title_col)
        surface.blit(sub, (theme.SCREEN_WIDTH // 2 - sub.get_width() // 2, theme.SCREEN_HEIGHT // 2 - 20))
        self.btn_play.draw(surface)
        self.btn_quit.draw(surface)


class HubState(GameState):
    """
    Hub central : fond world_map.jpg, princesse princess_main.jpg, portails dont
    Cuisine / Équitation utilisent kitchen_scene.jpg et horse_riding.jpg.
    """

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        # (clé mini-jeu, rectangle cliquable, libellé, couleur repli, image_portail)
        # image_portail : None | "kitchen" | "horse"
        self.portals: list[
            tuple[str, pygame.Rect, str, tuple[int, int, int], str | None]
        ] = [
            ("xo", pygame.Rect(160, 180, 240, 88), "XO Stratégique", theme.ACCENT, None),
            ("golf", pygame.Rect(420, 180, 240, 88), "Mini Golf", theme.PRIMARY, None),
            ("piano", pygame.Rect(680, 180, 240, 88), "Piano Rythmique", theme.SECONDARY, None),
            (
                "riding",
                pygame.Rect(200, 320, 300, 132),
                "Équitation",
                (144, 205, 244),
                "horse",
            ),
            (
                "cooking",
                pygame.Rect(530, 320, 300, 132),
                "Cuisine Royale",
                (251, 146, 60),
                "kitchen",
            ),
            ("studio", pygame.Rect(860, 320, 240, 88), "Studio Créatif", (52, 211, 153), None),
        ]

        assert game.font_ui is not None
        self.btn_menu = TextButton(
            pygame.Rect(32, theme.SCREEN_HEIGHT - 80, 220, 48),
            "Menu principal",
            game.font_ui,
            callback=self._back_menu,
            bg=theme.MUTED,
            sound_hook=game.sounds.play_ui_click,
        )
        self._hub_music_started = False

    def _back_menu(self) -> None:
        # Retour menu sans perdre la partie : sauvegarde conseillée au passage.
        self.game.save_game()
        self.game.change_state(MenuState(self.game))

    def _open_portal(self, key: str) -> None:
        """Router vers la bonne scène — import local pour limiter le couplage."""
        if key == "xo":
            from scenes.xo import XOMinigameState

            self.game.change_state(XOMinigameState(self.game))
            return
        if key == "golf":
            from scenes.golf import GolfMinigameState

            self.game.change_state(GolfMinigameState(self.game))
            return
        from scenes.coming_soon import ComingSoonState

        titles = {p[0]: p[2] for p in self.portals}
        if key == "cooking":
            self.game.change_state(
                ComingSoonState(self.game, titles.get(key, key), bg_mode="cooking")
            )
            return
        if key == "riding":
            from scenes.equitation import EquitationMinigameState

            self.game.change_state(EquitationMinigameState(self.game))
            return
        self.game.change_state(ComingSoonState(self.game, titles.get(key, key), bg_mode="default"))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.btn_menu.set_hover(mouse)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_menu.contains(event.pos):
                    self.btn_menu.on_click()
                    continue
                for key, rect, _label, _c, _img in self.portals:
                    if rect.collidepoint(event.pos):
                        self.game.sounds.play_ui_click()
                        self._open_portal(key)

    def update(self, dt: float) -> None:
        _ = dt
        if not self._hub_music_started:
            self.game.sounds.play_hub_music()
            self._hub_music_started = True

    def render(self, surface: pygame.Surface) -> None:
        # Carte du monde en fond plein écran.
        if self.game.img_hub_map is not None:
            surface.blit(self.game.img_hub_map, (0, 0))
        else:
            surface.fill(theme.BG)

        font = self.game.font_ui
        assert font is not None

        # Bandeau lisible pour le HUD (sans masquer toute la carte).
        hud_bg = pygame.Surface((theme.SCREEN_WIDTH, 96), pygame.SRCALPHA)
        hud_bg.fill((255, 245, 247, 210))
        surface.blit(hud_bg, (0, 0))

        bal = self.game.economy.get_balances()
        hud = (
            f"Niveau {self.game.xp.level} — XP {self.game.xp.xp} "
            f"(encore {self.game.xp.xp_needed_for_next()} pour suivant) | "
            f"Pièces {bal['coins']}  Étoiles {bal['stars']}  Couronnes {bal['crowns']}"
        )
        surface.blit(font.render(hud, True, theme.TEXT), (20, 16))
        surface.blit(font.render("Hub — choisis un mini-jeu (portails)", True, theme.MUTED), (20, 52))

        pr = self.game.get_hub_princess_surface()
        if pr is not None:
            px = theme.SCREEN_WIDTH // 2 - pr.get_width() // 2
            py = theme.SCREEN_HEIGHT - pr.get_height() - 24
            surface.blit(pr, (px, py))

        for _key, rect, label, color, img_kind in self.portals:
            img_surface: pygame.Surface | None = None
            if img_kind == "kitchen":
                img_surface = self.game.img_kitchen_portal
            elif img_kind == "horse":
                img_surface = self.game.img_horse_portal

            if img_surface is not None:
                # Image redimensionnée au rectangle du portail (remplissage net).
                scaled = pygame.transform.smoothscale(img_surface, (rect.width, rect.height))
                surface.blit(scaled, rect.topleft)
                pygame.draw.rect(surface, theme.WHITE, rect, width=3, border_radius=14)
            else:
                pygame.draw.rect(surface, color, rect, border_radius=14)
                pygame.draw.rect(surface, theme.TEXT, rect, width=2, border_radius=14)

            # Libellé en surimpression (ombre puis texte) pour rester lisible sur photo ou couleur.
            txt = font.render(label, True, theme.WHITE)
            sh = font.render(label, True, (0, 0, 0))
            tx, ty = rect.x + 10, rect.bottom - 8 - txt.get_height()
            surface.blit(sh, (tx + 1, ty + 1))
            surface.blit(txt, (tx, ty))

        self.btn_menu.draw(surface)


class ResultState(GameState):
    """Après un mini-jeu : affiche récompenses et renvoie au hub."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None
        self.btn_continue = TextButton(
            pygame.Rect(theme.SCREEN_WIDTH // 2 - 160, theme.SCREEN_HEIGHT - 120, 320, 56),
            "Continuer vers le Hub",
            game.font_ui,
            callback=self._to_hub,
            sound_hook=game.sounds.play_ui_click,
        )
        self._played_result_sfx = False

    def _to_hub(self) -> None:
        self.game.save_game()
        self.game.change_state(HubState(self.game))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.btn_continue.set_hover(mouse)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_continue.contains(event.pos):
                    self.btn_continue.on_click()

    def update(self, dt: float) -> None:
        _ = dt
        if not self._played_result_sfx:
            self.game.sounds.stop_gallop()
            res = self.game.last_minigame_result or {}
            txt = str(res.get("result", "")).lower()
            # Jingle “victoire” seulement si ce n’est pas une défaite / abandon explicite.
            if not any(x in txt for x in ("abandon", "lose", "défaite", "defaite", "échec", "echec")):
                self.game.sounds.play_victory()
            if int(res.get("coins", 0) or 0) > 0:
                self.game.sounds.play_coin()
            self._played_result_sfx = True

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BG)
        font = self.game.font_ui
        assert font is not None
        title = font.render("Résultats du mini-jeu", True, theme.TEXT)
        surface.blit(title, (theme.SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        res = self.game.last_minigame_result or {}
        lines = [
            f"Mini-jeu : {res.get('minigame', '?')}",
            f"Résultat brut : {res.get('result', '?')}",
            f"XP gagnée : +{res.get('xp', 0)}",
            f"Pièces gagnées : +{res.get('coins', 0)}",
            f"Étoiles gagnées : +{res.get('stars', 0)}",
        ]
        y = 200
        for line in lines:
            surface.blit(font.render(line, True, theme.TEXT), (theme.SCREEN_WIDTH // 2 - 200, y))
            y += 36

        self.btn_continue.draw(surface)
