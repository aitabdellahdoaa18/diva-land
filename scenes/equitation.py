"""
scenes/equitation.py — Mini-jeu Équitation (runner) : galop automatique, sauts, obstacles.

- Fond `horse_riding.jpg` en parallax horizontal
- ESPACE / flèche HAUT : saut (gravité simple)
- Haies (hautes) et rochers (bas) arrivent de la droite
- 3 vies, 60 s, score = distance parcourue (scroll)
- Récompenses alignées sur `golf.py` (normalisation → pièces / XP / étoiles)
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from core.states import GameState, HubState, ResultState
from ui import theme

if TYPE_CHECKING:
    from core.game import Game

# ---------------------------------------------------------------------------
# Constantes gameplay
# ---------------------------------------------------------------------------
GROUND_Y = 540
HORSE_ANCHOR_X = 240
SCROLL_SPEED_BASE = 340.0  # vitesse de défilement du monde (px/s)
SCROLL_RAMP = 4.5  # accélération légère avec le temps
GRAVITY = 2400.0
JUMP_VELOCITY = -640.0  # vers le haut (axe y Pygame : vy négatif)

GAME_DURATION = 60.0  # secondes
MAX_LIVES = 3
INVULN_DURATION = 1.85  # s après une collision

# Distance de référence pour score ~100 % sur une partie complète sans mourir
TARGET_DISTANCE_FOR_FULL_SCORE = 11000.0


@dataclass
class Obstacle:
    """Obstacle en coordonnées monde (x croissant avec la distance)."""

    x_world: float
    kind: str  # "hurdle" | "rock"
    width: int
    height: int
    y_top: int  # coin haut-gauche à l’écran quand x_screen connu


def _make_obstacle(x_world: float) -> Obstacle:
    if random.random() < 0.52:
        return Obstacle(x_world, "hurdle", 32, 88, GROUND_Y - 92)
    return Obstacle(x_world, "rock", 58, 42, GROUND_Y - 44)


class EquitationMinigameState(GameState):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None
        self.font = game.font_ui

        self.scroll_distance = 0.0
        self.scroll_speed = SCROLL_SPEED_BASE
        self.parallax = 0.0

        self.jump_height = 0.0  # hauteur au-dessus du sol (px)
        self.vy = 0.0

        self.time_left = GAME_DURATION
        self.lives = MAX_LIVES
        self.invuln = 0.0

        self.obstacles: list[Obstacle] = []

        self._stopped_music = False
        self._gallop_on = False
        self._game_over = False

        self.btn_quit = pygame.Rect(theme.SCREEN_WIDTH - 130, 12, 110, 36)

    def _world_to_screen_x(self, x_world: float) -> int:
        return int(x_world - self.scroll_distance)

    def _spawn_initial(self) -> None:
        """Obstacles devant le joueur (coordonnées monde)."""
        x = self.scroll_distance + float(theme.SCREEN_WIDTH + 260)
        for _ in range(4):
            self.obstacles.append(_make_obstacle(x))
            x += random.uniform(340, 520)

    def _maybe_spawn(self) -> None:
        """Enchaîne les obstacles tant qu’il reste de la place à droite de l’écran."""
        if not self.obstacles:
            self._spawn_initial()
            return
        last = max(self.obstacles, key=lambda o: o.x_world)
        screen_right = last.x_world - self.scroll_distance
        while screen_right < theme.SCREEN_WIDTH + random.uniform(260, 400):
            gap = random.uniform(360, 520)
            last = _make_obstacle(last.x_world + gap)
            self.obstacles.append(last)
            screen_right = last.x_world - self.scroll_distance

    def _horse_bottom_y(self) -> int:
        return int(GROUND_Y - self.jump_height)

    def _horse_hitbox(self) -> pygame.Rect:
        """Rectangle de collision (corps + cavalier), resserré pour jeu équitable."""
        b = self._horse_bottom_y()
        return pygame.Rect(HORSE_ANCHOR_X - 42, b - 92, 88, 78)

    def _try_jump(self) -> None:
        if self.jump_height <= 0.5 and abs(self.vy) < 80.0:
            self.vy = JUMP_VELOCITY
            self.game.sounds.play_jump()

    def _take_hit(self) -> None:
        if self.invuln > 0.0 or self._game_over:
            return
        self.game.sounds.play_hit()
        self.lives -= 1
        if self.lives <= 0:
            self._finish_run(early_death=True)
            return
        self.invuln = INVULN_DURATION

    def _check_collisions(self) -> None:
        hb = self._horse_hitbox()
        for ob in self.obstacles:
            sx = self._world_to_screen_x(ob.x_world)
            r = pygame.Rect(sx, ob.y_top, ob.width, ob.height)
            if hb.colliderect(r):
                self._take_hit()
                return

    def _purge_obstacles(self) -> None:
        keep: list[Obstacle] = []
        for ob in self.obstacles:
            sx = self._world_to_screen_x(ob.x_world)
            if sx + ob.width > -80:
                keep.append(ob)
        self.obstacles = keep

    def _finish_run(self, *, early_death: bool) -> None:
        if self._game_over:
            return
        self._game_over = True
        self.game.sounds.stop_gallop()

        dist = max(0.0, self.scroll_distance)
        # Score normalisé 0–100 (comme golf : distance / objectif)
        normalized = int(max(0, min(100, round(100.0 * dist / TARGET_DISTANCE_FOR_FULL_SCORE))))
        if early_death:
            normalized = min(normalized, 38)

        coins = 15 + int((normalized / 100.0) * 25)
        xp = 25 + int((normalized / 100.0) * 35)
        stars = 2 if normalized >= 82 else 1 if normalized >= 55 else 0

        self.game.economy.add_coins(coins)
        self.game.economy.add_stars(stars)
        unlocks = self.game.xp.add_xp(xp)
        prev = self.game.minigame_scores.get("riding", 0)
        self.game.minigame_scores["riding"] = max(prev, normalized)

        result_txt = (
            f"distance {int(dist)} px, temps restant {max(0, self.time_left):.1f}s"
            if not early_death
            else f"lose — plus de vies, distance {int(dist)} px"
        )

        self.game.last_minigame_result = {
            "minigame": "riding",
            "result": result_txt,
            "coins": coins,
            "stars": stars,
            "xp": xp,
            "normalized": normalized,
            "level_unlock_hints": unlocks,
        }
        self.game.change_state(ResultState(self.game))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self._game_over:
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_quit.collidepoint(event.pos):
                    self.game.sounds.stop_gallop()
                    self.game.sounds.play_ui_click()
                    self.game.sounds.stop_music()
                    self.game.change_state(HubState(self.game))
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    self._try_jump()
                if event.key == pygame.K_ESCAPE:
                    self.game.sounds.stop_gallop()
                    self.game.sounds.stop_music()
                    self.game.change_state(HubState(self.game))

    def update(self, dt: float) -> None:
        if not self._stopped_music:
            self.game.sounds.stop_music()
            self._stopped_music = True
        if not self._gallop_on and not self._game_over:
            self.game.sounds.start_gallop_loop()
            self._gallop_on = True

        if self._game_over:
            return

        self.time_left -= dt
        if self.time_left <= 0.0:
            self.time_left = 0.0
            self._finish_run(early_death=False)
            return

        self.invuln = max(0.0, self.invuln - dt)

        # Physique saut
        self.vy += GRAVITY * dt
        self.jump_height -= self.vy * dt
        if self.jump_height < 0.0:
            self.jump_height = 0.0
            self.vy = 0.0

        t = GAME_DURATION - self.time_left
        self.scroll_speed = SCROLL_SPEED_BASE + SCROLL_RAMP * t
        delta = self.scroll_speed * dt
        self.scroll_distance += delta
        self.parallax += delta * 0.35

        if not self.obstacles:
            self._spawn_initial()
        self._maybe_spawn()
        self._purge_obstacles()

        if self.invuln <= 0.0:
            self._check_collisions()

    def _draw_parallax(self, surface: pygame.Surface) -> None:
        raw = self.game.img_riding_raw
        if raw is None:
            surface.fill((150, 190, 220))
            return
        sh = theme.SCREEN_HEIGHT
        sw = theme.SCREEN_WIDTH
        rw, rh = raw.get_size()
        if rh <= 0:
            return
        scale_w = max(sw + 160, int(rw / rh * sh * 1.45))
        wide = pygame.transform.smoothscale(raw, (scale_w, sh))
        off = int(self.parallax) % max(1, wide.get_width() - sw)
        surface.blit(wide, (0, 0), (off, 0, sw, sh))

    def _draw_ground(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface,
            (86, 140, 72),
            (0, GROUND_Y, theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT - GROUND_Y),
        )
        pygame.draw.line(surface, (60, 110, 55), (0, GROUND_Y), (theme.SCREEN_WIDTH, GROUND_Y), 4)

    def _draw_horse_rider(self, surface: pygame.Surface) -> None:
        bx = HORSE_ANCHOR_X
        by = self._horse_bottom_y()

        # Cheval (forme simple)
        pygame.draw.ellipse(surface, (240, 240, 245), (bx - 55, by - 38, 110, 52))
        pygame.draw.ellipse(surface, (210, 200, 190), (bx + 28, by - 42, 34, 28))
        pygame.draw.circle(surface, (40, 35, 35), (bx + 48, by - 28), 8)

        # Princesse (sprite équipée si dispo)
        spr = self.game.get_hub_princess_surface()
        if spr is not None:
            ph = min(130, spr.get_height())
            pw = int(spr.get_width() * (ph / spr.get_height()))
            pr = pygame.transform.smoothscale(spr, (pw, ph))
            surface.blit(pr, (bx - pw // 2 + 8, by - ph - 8))

        if self.invuln > 0.0 and int(self.invuln * 6) % 2 == 0:
            # Clignotement invulnérabilité
            flash = pygame.Surface((120, 120), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 70))
            surface.blit(flash, (bx - 60, by - 110))

    def render(self, surface: pygame.Surface) -> None:
        self._draw_parallax(surface)
        self._draw_ground(surface)

        for ob in self.obstacles:
            sx = self._world_to_screen_x(ob.x_world)
            r = pygame.Rect(sx, ob.y_top, ob.width, ob.height)
            if ob.kind == "hurdle":
                pygame.draw.rect(surface, (139, 90, 43), r, border_radius=4)
                pygame.draw.rect(surface, (90, 55, 30), r, width=2, border_radius=4)
                pygame.draw.rect(surface, (180, 140, 90), (r.x + 4, r.y - 6, r.w - 8, 8))
            else:
                pygame.draw.ellipse(surface, (100, 100, 108), r)
                pygame.draw.ellipse(surface, (70, 72, 78), r, width=2)

        self._draw_horse_rider(surface)

        # Cœurs (vies restantes pleins)
        for i in range(MAX_LIVES):
            cx = 40 + i * 38
            cy = 108
            full = i < self.lives
            col_fill = (236, 72, 110) if full else (200, 200, 210)
            col_out = (180, 30, 60) if full else (160, 160, 170)
            # Deux lobes + pointe (coeur simplifié)
            pygame.draw.circle(surface, col_fill, (cx, cy), 11)
            pygame.draw.circle(surface, col_fill, (cx + 18, cy), 11)
            pygame.draw.polygon(surface, col_fill, [(cx - 10, cy + 4), (cx + 28, cy + 4), (cx + 9, cy + 24)])
            pygame.draw.arc(surface, col_out, (cx - 13, cy - 13, 26, 26), 2.2, 4.0, 2)
            pygame.draw.arc(surface, col_out, (cx + 5, cy - 13, 26, 26), -0.9, 1.0, 2)

        # HUD
        font = self.font
        t1 = f"Temps : {self.time_left:.1f} s"
        t2 = f"Distance : {int(self.scroll_distance)}"
        t3 = f"Vies : {self.lives}"
        surface.blit(font.render(t1, True, theme.TEXT), (24, 20))
        surface.blit(font.render(t2, True, theme.TEXT), (24, 52))
        surface.blit(font.render(t3, True, theme.MUTED), (24, 76))
        surface.blit(
            font.render("ESPACE / ↑ sauter — Invincible brièvement après touche", True, theme.MUTED),
            (260, 20),
        )

        pygame.draw.rect(surface, theme.MUTED, self.btn_quit, border_radius=6)
        q = font.render("Quitter", True, theme.WHITE)
        surface.blit(q, (self.btn_quit.x + 12, self.btn_quit.y + 5))
