"""
scenes/golf.py — Mini Golf complet (GDD §9.2) : 5 trous, physique 2D, scoring.

Contrôles (pédagogiques / clairs) :
- Vise avec la souris : direction = du centre de la balle vers le curseur.
- Clic gauche maintenu : charge la puissance (jauge 0 → 100 %).
- Relâche le clic : frappe la balle (tant qu’elle est à l’arrêt).

Physique (modèle simplifié mais jouable) :
- v ← v * exp(-friction * dt)   friction “air + gazon”
- x ← x + v * dt
- Rebonds sur les bords du terrain + obstacles (rectangles).
- Capture du trou si la balle entre assez lentement dans le cercle du drapeau.

Parcours : 5 trous consécutifs ; par total = 5 × 3 = 15 coups “référence”.
Bonus GDD : multiplicateur selon le nombre de coups *sur un trou* affiché dans l’UI après chaque réussite.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame
from pygame.math import Vector2

from core.states import GameState, HubState, ResultState
from ui import theme

if TYPE_CHECKING:
    from core.game import Game

# ---------------------------------------------------------------------------
# Constantes gameplay
# ---------------------------------------------------------------------------
BALL_RADIUS = 11.0
HOLE_RADIUS = 28.0
PAR_PER_HOLE = 3
NUM_HOLES = 5
MAX_TOTAL_STROKES = 55  # plafond anti-blocage ; au-delà = défaite

# Frottement exponentiel : plus k_grass est grand, plus la balle s’arrête vite.
K_GRASS = 3.2
# Coefficient de restitution (rebond) sur murs/obstacles : 1 = élastique ; 0 = collant.
BOUNCE = 0.72
# Vitesse max à l’instant du tir (pixels / seconde approximatif selon dt).
MAX_SHOT_SPEED = 760.0
# Vitesse en dessous de laquelle on considère la balle “arrêtée”.
REST_SPEED = 18.0
# Nombre de sous-pas physiques par frame (réduit les traversées de murs entre deux frames).
SUBSTEPS = 10


@dataclass
class HoleData:
    """Un trou : position départ, position trou (drapeau), obstacles rectangles."""

    start: tuple[float, float]
    hole: tuple[float, float]
    obstacles: list[pygame.Rect]


def _build_courses() -> list[HoleData]:
    """
    Cinq parcours variés (coord. fenêtre 1280×720, zone de jeu centrale).

    Remarque ingénieur : les coords sont en “monde écran” ; tu pourras les exporter en JSON plus tard.
    """
    return [
        HoleData(
            (220.0, 420.0),
            (1040.0, 400.0),
            [pygame.Rect(460, 280, 44, 220), pygame.Rect(720, 360, 200, 40)],
        ),
        HoleData(
            (1050.0, 200.0),
            (260.0, 440.0),
            [pygame.Rect(400, 240, 360, 38), pygame.Rect(540, 380, 38, 200)],
        ),
        HoleData(
            (200.0, 260.0),
            (980.0, 260.0),
            [pygame.Rect(520, 200, 40, 280)],
        ),
        HoleData(
            (640.0, 520.0),
            (640.0, 200.0),
            [
                pygame.Rect(420, 320, 440, 36),
                pygame.Rect(600, 200, 40, 160),
            ],
        ),
        HoleData(
            (180.0, 360.0),
            (1060.0, 360.0),
            [pygame.Rect(360, 300, 48, 180), pygame.Rect(800, 260, 48, 220)],
        ),
    ]


# Aire de jeu global (murs extérieurs) — la balle rebondit à l’intérieur.
PLAY_RECT = pygame.Rect(72, 96, theme.SCREEN_WIDTH - 144, theme.SCREEN_HEIGHT - 168)


def _clamp_ball_to_play(pos: Vector2) -> Vector2:
    """Garde la balle *statistiquement* dans le rectangle de jeu (filet de sécurité)."""
    pos.x = float(max(PLAY_RECT.left + BALL_RADIUS, min(PLAY_RECT.right - BALL_RADIUS, pos.x)))
    pos.y = float(max(PLAY_RECT.top + BALL_RADIUS, min(PLAY_RECT.bottom - BALL_RADIUS, pos.y)))
    return pos


def _collide_circle_rect(pos: Vector2, vel: Vector2, radius: float, rect: pygame.Rect) -> None:
    """
    Collision cercle / AABB : repousse le centre et réfléchit la composante normale de v.

    Modifie `pos` et `vel` en place (pas de retour) pour rester proche du moteur physique boucle interne.
    """
    closest_x = max(rect.left, min(pos.x, rect.right))
    closest_y = max(rect.top, min(pos.y, rect.bottom))
    dx = pos.x - closest_x
    dy = pos.y - closest_y
    dist = math.hypot(dx, dy)
    if dist >= radius or dist < 1e-5:
        return
    nx = dx / dist
    ny = dy / dist
    overlap = radius - dist
    pos.x += nx * overlap
    pos.y += ny * overlap
    vn = vel.x * nx + vel.y * ny
    if vn < 0:
        # On retire la composante entrante le long de la normale (modèle rebond partiel).
        vel.x -= (1.0 + BOUNCE) * vn * nx
        vel.y -= (1.0 + BOUNCE) * vn * ny


def _collide_play_bounds(pos: Vector2, vel: Vector2) -> None:
    """Rebond sur les quatre murs du grand rectangle PLAY_RECT."""
    if pos.x - BALL_RADIUS <= PLAY_RECT.left:
        pos.x = PLAY_RECT.left + BALL_RADIUS
        vel.x = abs(vel.x) * BOUNCE
    elif pos.x + BALL_RADIUS >= PLAY_RECT.right:
        pos.x = PLAY_RECT.right - BALL_RADIUS
        vel.x = -abs(vel.x) * BOUNCE

    if pos.y - BALL_RADIUS <= PLAY_RECT.top:
        pos.y = PLAY_RECT.top + BALL_RADIUS
        vel.y = abs(vel.y) * BOUNCE
    elif pos.y + BALL_RADIUS >= PLAY_RECT.bottom:
        pos.y = PLAY_RECT.bottom - BALL_RADIUS
        vel.y = -abs(vel.y) * BOUNCE


def _stroke_name_and_multiplier(strokes_on_hole: int) -> tuple[str, float]:
    """
    Table GDD §9.2 (par = 3 sur chaque trou).
    strokes_on_hole : nombre de coups pour rentrer la balle sur CE trou.
    """
    if strokes_on_hole <= 1:
        return "Albatros", 3.0
    if strokes_on_hole == 2:
        return "Eagle", 2.0
    if strokes_on_hole == PAR_PER_HOLE:
        return "Par", 1.0
    if strokes_on_hole == PAR_PER_HOLE + 1:
        return "Bogey", 0.75
    if strokes_on_hole >= PAR_PER_HOLE + 2:
        return "Double Bogey+", 0.5
    # Cas improbable (ex. remapping) : on reste neutre.
    return "Partie", 1.0


class GolfMinigameState(GameState):
    """Mini-golf : enchaîne les trous, accumulateur de coups, fin → ResultState."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None
        self.font = game.font_ui
        self.courses = _build_courses()
        self.hole_index = 0
        self.strokes_total = 0
        self.strokes_this_hole = 0

        self.pos = Vector2(self.courses[0].start)
        self.vel = Vector2(0, 0)
        self.charging = False
        self.power = 0.0  # 0..1 pendant la charge

        self.rolling = False
        self.message = "Vise avec la souris. Maintiens clic gauche pour charger, relâche pour frapper."
        self.last_hole_summary = ""

        self.btn_quit = pygame.Rect(theme.SCREEN_WIDTH - 140, 16, 120, 40)
        self._round_over = False  # évite d’appeler deux fois les fins de partie en physique
        self._stopped_menu_music = False

    # -- accès rapide au trou courant -------------------------------------------------
    @property
    def hole_data(self) -> HoleData:
        return self.courses[self.hole_index]

    @property
    def hole_world(self) -> Vector2:
        return Vector2(self.hole_data.hole)

    def _reset_ball_for_hole(self) -> None:
        """Replace la balle au départ du trou courant, vitesse nulle."""
        self.pos = Vector2(self.hole_data.start)
        self.vel = Vector2(0, 0)
        self.rolling = False
        self.charging = False
        self.power = 0.0
        self.strokes_this_hole = 0

    def _shoot(self, direction: Vector2, power01: float) -> None:
        """Applique une impulsion ; `direction` doit être approximativement normalisé."""
        if direction.length_squared() < 1e-6:
            return
        d = direction.normalize()
        speed = MAX_SHOT_SPEED * max(0.05, min(1.0, power01))
        self.vel = d * speed
        self.rolling = True
        self.strokes_total += 1
        self.strokes_this_hole += 1

    def _try_capture_hole(self) -> None:
        """Si lent et proche du centre du trou, le trou est validé."""
        if self._round_over:
            return
        dist = (self.pos - self.hole_world).length()
        spd = self.vel.length()
        if dist <= HOLE_RADIUS * 0.85 and spd < 140.0:
            name, mult = _stroke_name_and_multiplier(self.strokes_this_hole)
            self.last_hole_summary = f"Trou {self.hole_index + 1}: {name} (×{mult:.2f}) en {self.strokes_this_hole} coup(s)."
            self.message = self.last_hole_summary
            self.hole_index += 1
            self.rolling = False
            self.vel = Vector2(0, 0)
            if self.hole_index >= NUM_HOLES:
                self._finish_success()
            else:
                self._reset_ball_for_hole()

    def _finish_success(self) -> None:
        """Tous les trous réussis : calcule récompenses (GDD fourchettes golf)."""
        if self._round_over:
            return
        self._round_over = True
        par_total = PAR_PER_HOLE * NUM_HOLES
        s = max(1, self.strokes_total)
        # Normalisation “plus tu es sous le par total, mieux c’est”, plafonnée à 100.
        ratio = par_total / s
        normalized = int(max(0, min(100, round(100 * ratio))))

        coins = 15 + int((normalized / 100.0) * 25)
        xp = 25 + int((normalized / 100.0) * 35)
        stars = 2 if normalized >= 82 else 1 if normalized >= 55 else 0

        self.game.economy.add_coins(coins)
        self.game.economy.add_stars(stars)
        unlocks = self.game.xp.add_xp(xp)
        prev = self.game.minigame_scores.get("golf", 0)
        self.game.minigame_scores["golf"] = max(prev, normalized)

        self.game.last_minigame_result = {
            "minigame": "golf",
            "result": f"terminé en {self.strokes_total} coups (par total {par_total})",
            "coins": coins,
            "stars": stars,
            "xp": xp,
            "normalized": normalized,
            "level_unlock_hints": unlocks,
        }
        self.game.change_state(ResultState(self.game))

    def _finish_fail_too_many(self) -> None:
        """Trop de coups globaux : fin négative avec petites récompenses “consolation”."""
        if self._round_over:
            return
        self._round_over = True
        coins, xp, stars = 10, 15, 0
        self.game.economy.add_coins(coins)
        self.game.xp.add_xp(xp)
        self.game.last_minigame_result = {
            "minigame": "golf",
            "result": f"abandon (>{MAX_TOTAL_STROKES} coups)",
            "coins": coins,
            "stars": stars,
            "xp": xp,
            "normalized": 15,
            "level_unlock_hints": [],
        }
        self.game.change_state(ResultState(self.game))

    def _physics_substep(self, dt: float) -> None:
        """Une petite étape de physiques : frottements, intégration, collisions, capture."""
        # Frottement exponentiel stable quelle que soit la fréquence de sous-pas.
        decay = math.exp(-K_GRASS * dt)
        self.vel *= decay
        self.pos += self.vel * dt

        _collide_play_bounds(self.pos, self.vel)
        for ob in self.hole_data.obstacles:
            _collide_circle_rect(self.pos, self.vel, BALL_RADIUS, ob)

        self.pos = _clamp_ball_to_play(self.pos)

        if self.vel.length() < REST_SPEED:
            self.vel = Vector2(0, 0)
            self.rolling = False

        self._try_capture_hole()

        if (
            not self._round_over
            and self.strokes_total >= MAX_TOTAL_STROKES
            and self.hole_index < NUM_HOLES
        ):
            self._finish_fail_too_many()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_quit.collidepoint(event.pos):
                    self.game.sounds.stop_music()
                    self.game.sounds.play_ui_click()
                    self.game.change_state(HubState(self.game))
                    return
                if not self.rolling:
                    self.charging = True
                    self.power = 0.0

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.charging and not self.rolling:
                    mouse = Vector2(pygame.mouse.get_pos())
                    aim = mouse - self.pos
                    self._shoot(aim, self.power)
                    self.charging = False
                    self.power = 0.0

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.sounds.stop_music()
                    self.game.change_state(HubState(self.game))

    def update(self, dt: float) -> None:
        if not self._stopped_menu_music:
            self.game.sounds.stop_music()
            self._stopped_menu_music = True
        if self.charging and not self.rolling:
            # Montée de la jauge tant que le bouton est maintenu (détecté par update, pas event repeat).
            held = pygame.mouse.get_pressed()[0]
            if held:
                self.power = min(1.0, self.power + 1.15 * dt)
            else:
                self.charging = False

        if self.rolling:
            h_dt = dt / float(SUBSTEPS)
            for _ in range(SUBSTEPS):
                self._physics_substep(h_dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.game.img_golf_bg is not None:
            surface.blit(self.game.img_golf_bg, (0, 0))
            veil = pygame.Surface((theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT), pygame.SRCALPHA)
            veil.fill((230, 250, 220, 90))
            surface.blit(veil, (0, 0))
        else:
            surface.fill((210, 235, 200))
        pygame.draw.rect(surface, (120, 160, 90), PLAY_RECT, width=4, border_radius=0)

        # Obstacles du trou courant
        for ob in self.hole_data.obstacles:
            pygame.draw.rect(surface, (85, 60, 40), ob, border_radius=6)
            pygame.draw.rect(surface, (40, 28, 20), ob, width=2, border_radius=6)

        # Trous (vert foncé + drapeau)
        hole_xy = (int(self.hole_world.x), int(self.hole_world.y))
        pygame.draw.circle(surface, (30, 90, 40), hole_xy, int(HOLE_RADIUS))
        pygame.draw.circle(surface, (10, 40, 15), hole_xy, int(HOLE_RADIUS), width=3)
        pygame.draw.line(surface, (90, 90, 90), hole_xy, (hole_xy[0] + 22, hole_xy[1] - 60), 4)
        pygame.draw.polygon(surface, (240, 80, 110), [hole_xy, (hole_xy[0] + 52, hole_xy[1] - 36), (hole_xy[0], hole_xy[1] - 72)])

        # Balle
        pygame.draw.circle(surface, (250, 250, 250), (int(self.pos.x), int(self.pos.y)), int(BALL_RADIUS))
        pygame.draw.circle(surface, (30, 30, 30), (int(self.pos.x), int(self.pos.y)), int(BALL_RADIUS), width=2)

        # Visée + jauge
        if not self.rolling:
            m = Vector2(pygame.mouse.get_pos())
            aim = m - self.pos
            if aim.length_squared() > 1.0:
                end = self.pos + aim.normalize() * min(160.0, aim.length())
                pygame.draw.line(surface, (240, 240, 240), (int(self.pos.x), int(self.pos.y)), (int(end.x), int(end.y)), 3)

        if self.charging:
            bx = 80
            by = theme.SCREEN_HEIGHT - 56
            bw = 280
            bh = 22
            pygame.draw.rect(surface, (40, 40, 40), (bx, by, bw, bh), border_radius=8)
            pygame.draw.rect(surface, theme.SECONDARY, (bx + 2, by + 2, int((bw - 4) * self.power), bh - 4), border_radius=6)

        # Panneaux texte
        hud_lines = [
            f"Mini-Golf — Trou {self.hole_index + 1}/{NUM_HOLES}   |   Coups (trou): {self.strokes_this_hole}   |   Total: {self.strokes_total}",
            f"Par ce trou : {PAR_PER_HOLE}   |   Par campagne : {PAR_PER_HOLE * NUM_HOLES}",
            self.message,
        ]
        y = 12
        for line in hud_lines:
            surf = self.font.render(line, True, theme.TEXT)
            surface.blit(surf, (20, y))
            y += 34

        pygame.draw.rect(surface, theme.MUTED, self.btn_quit, border_radius=8)
        tq = self.font.render("Quitter", True, theme.WHITE)
        surface.blit(tq, (self.btn_quit.x + 18, self.btn_quit.y + 6))
