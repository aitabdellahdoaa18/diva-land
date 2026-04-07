"""
scenes/piano.py — Mini-jeu Piano Rythmique de Diva Land.

Comment ça marche :
- Des notes tombent du haut de l'écran vers le bas
- Le joueur appuie sur A S D F quand la note arrive dans la zone de frappe
- PERFECT = note frappée au bon moment → combo + score élevé
- GOOD    = note frappée un peu en retard/avance → score moyen
- MISS    = note ratée → combo cassé
- 60 secondes de jeu, récompenses selon le score final
"""
from __future__ import annotations  # Permet les annotations de type modernes

import random  # Pour générer les notes aléatoirement
from dataclasses import dataclass, field  # Pour créer des classes simples
from typing import TYPE_CHECKING  # Pour éviter les imports circulaires

import pygame  # Bibliothèque principale du jeu

from core.states import GameState, HubState, ResultState  # États du jeu
from ui import theme  # Couleurs et dimensions de l'écran

if TYPE_CHECKING:
    from core.game import Game  # Importé seulement pour les annotations de type

# ---------------------------------------------------------------------------
# Constantes — contrôlent le comportement du mini-jeu Piano
# ---------------------------------------------------------------------------
GAME_DURATION    = 60.0    # Durée totale du mini-jeu en secondes
NOTE_SPEED       = 280.0   # Vitesse de chute des notes (pixels par seconde)
NOTE_SPAWN_DELAY = 1.2     # Délai entre chaque nouvelle note (secondes)
NOTE_WIDTH       = 90      # Largeur d'une note en pixels
NOTE_HEIGHT      = 40      # Hauteur d'une note en pixels

# Zone de frappe : bande horizontale où le joueur doit appuyer
HIT_ZONE_Y      = 580      # Position Y du centre de la zone de frappe
HIT_ZONE_HEIGHT = 80       # Hauteur de la zone de frappe (tolérance)

# Fenêtres de précision pour les jugements
PERFECT_WINDOW  = 30       # ±30 px du centre = PERFECT
GOOD_WINDOW     = 60       # ±60 px du centre = GOOD (sinon MISS)

# Les 4 colonnes du piano avec leurs touches clavier
COLUMNS = [
    {"key": pygame.K_a, "label": "A", "x": 220, "color": (255, 105, 180)},  # Rose
    {"key": pygame.K_s, "label": "S", "x": 360, "color": (255, 165,  80)},  # Orange
    {"key": pygame.K_d, "label": "D", "x": 500, "color": (100, 200, 255)},  # Bleu
    {"key": pygame.K_f, "label": "F", "x": 640, "color": (150, 255, 150)},  # Vert
]

# Couleurs des jugements
COLOR_PERFECT = (255, 230,  50)  # Jaune doré
COLOR_GOOD    = (100, 220, 255)  # Bleu clair
COLOR_MISS    = (200, 100, 100)  # Rouge doux


@dataclass
class Note:
    """Représente une note qui tombe du haut de l'écran."""
    col_index: int    # Indice de la colonne (0=A, 1=S, 2=D, 3=F)
    y: float          # Position Y actuelle de la note (augmente en tombant)
    hit: bool = False # True si la note a déjà été frappée (évite le double comptage)
    missed: bool = False  # True si la note est passée sans être frappée


@dataclass
class Feedback:
    """Message de feedback affiché brièvement après une frappe (PERFECT / GOOD / MISS)."""
    text: str          # Texte à afficher
    color: tuple       # Couleur du texte
    x: int             # Position X à l'écran
    timer: float = 0.8 # Durée d'affichage en secondes (disparaît après)


class PianoMinigameState(GameState):
    """État du mini-jeu Piano — gère la logique complète du rhythm game."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)  # Initialise la classe parente GameState
        assert game.font_ui is not None
        self.font = game.font_ui  # Police pour le HUD

        # ── État du jeu ────────────────────────────────────────────────────
        self.time_left    = GAME_DURATION  # Temps restant en secondes
        self.score        = 0             # Score total accumulé
        self.combo        = 0             # Combo actuel (cassé par un MISS)
        self.max_combo    = 0             # Meilleur combo de la partie
        self.perfects     = 0            # Nombre de PERFECT
        self.goods        = 0            # Nombre de GOOD
        self.misses       = 0            # Nombre de MISS
        self._game_over   = False        # True quand la partie est terminée

        # ── Notes et spawn ─────────────────────────────────────────────────
        self.notes: list[Note] = []      # Notes actuellement à l'écran
        self.spawn_timer = 0.0           # Timer avant la prochaine note

        # ── Feedback visuels ───────────────────────────────────────────────
        self.feedbacks: list[Feedback] = []  # Messages PERFECT/GOOD/MISS affichés

        # ── Touches enfoncées (pour animation des colonnes) ────────────────
        self.keys_pressed = [False] * 4  # Une entrée par colonne

        # ── Bouton Quitter ─────────────────────────────────────────────────
        self.btn_quit = pygame.Rect(theme.SCREEN_WIDTH - 130, 12, 110, 36)

        # ── Arrête la musique du hub ───────────────────────────────────────
        self.game.sounds.stop_music()

    def _spawn_note(self) -> None:
        """Génère une nouvelle note dans une colonne aléatoire en haut de l'écran."""
        col = random.randint(0, 3)  # Choisit une colonne au hasard (0 à 3)
        self.notes.append(Note(col_index=col, y=-NOTE_HEIGHT))  # Commence hors écran en haut

    def _judge_hit(self, col_index: int) -> None:
        """Juge la frappe du joueur sur une colonne.
        Cherche la note la plus proche de la zone de frappe dans cette colonne."""

        # Cherche toutes les notes non frappées dans cette colonne
        candidates = [
            n for n in self.notes
            if n.col_index == col_index and not n.hit and not n.missed
        ]

        if not candidates:
            # Aucune note dans cette colonne → MISS (frappe dans le vide)
            self._add_feedback("MISS", COLOR_MISS, col_index)
            self._break_combo()
            return

        # Trouve la note la plus proche de la zone de frappe
        best = min(candidates, key=lambda n: abs(n.y - HIT_ZONE_Y))
        distance = abs(best.y - HIT_ZONE_Y)  # Distance par rapport au centre de la zone

        if distance <= PERFECT_WINDOW:
            # PERFECT : note frappée au bon moment
            best.hit = True
            self.perfects += 1
            self.combo += 1                          # Augmente le combo
            self.max_combo = max(self.max_combo, self.combo)  # Met à jour le meilleur combo
            bonus = 1 + self.combo // 5              # Bonus de score selon le combo
            self.score += 100 * bonus                # 100 points × bonus combo
            self._add_feedback("PERFECT ✨", COLOR_PERFECT, col_index)

        elif distance <= GOOD_WINDOW:
            # GOOD : note frappée un peu en retard ou en avance
            best.hit = True
            self.goods += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += 50                         # 50 points (pas de bonus combo)
            self._add_feedback("GOOD", COLOR_GOOD, col_index)

        else:
            # Note trop loin de la zone → MISS
            self._add_feedback("MISS", COLOR_MISS, col_index)
            self._break_combo()

    def _break_combo(self) -> None:
        """Casse le combo actuel (remis à 0 après un MISS)."""
        self.combo = 0
        self.misses += 1

    def _add_feedback(self, text: str, color: tuple, col_index: int) -> None:
        """Ajoute un message de feedback visuel au-dessus de la colonne frappée."""
        x = COLUMNS[col_index]["x"]  # Position X de la colonne
        self.feedbacks.append(Feedback(text=text, color=color, x=x))

    def _finish(self) -> None:
        """Termine la partie, calcule les récompenses et passe à l'écran de résultats."""
        if self._game_over:
            return
        self._game_over = True

        # Calcul du score normalisé (0–100) basé sur le ratio PERFECT/(total frappes)
        total_hits = self.perfects + self.goods + self.misses
        if total_hits == 0:
            normalized = 0  # Aucune frappe → score 0
        else:
            # Score = 70% basé sur les PERFECT, 30% sur les GOOD
            normalized = int(min(100, (self.perfects * 100 + self.goods * 50) / max(1, total_hits)))

        # Calcul des récompenses
        coins = 10 + int((normalized / 100.0) * 30)  # Entre 10 et 40 pièces
        xp    = 20 + int((normalized / 100.0) * 40)  # Entre 20 et 60 XP
        stars = 2 if normalized >= 80 else 1 if normalized >= 50 else 0  # 0, 1 ou 2 étoiles

        # Ajoute les récompenses au compte du joueur
        self.game.economy.add_coins(coins)
        self.game.economy.add_stars(stars)
        unlocks = self.game.xp.add_xp(xp)

        # Sauvegarde le meilleur score
        prev = self.game.minigame_scores.get("piano", 0)
        self.game.minigame_scores["piano"] = max(prev, normalized)

        # Prépare les données pour l'écran de résultats
        self.game.last_minigame_result = {
            "minigame": "piano",
            "result": f"score {self.score} | PERFECT×{self.perfects} GOOD×{self.goods} MISS×{self.misses} | combo max {self.max_combo}",
            "coins": coins,
            "stars": stars,
            "xp": xp,
            "normalized": normalized,
            "level_unlock_hints": unlocks,
        }
        self.game.change_state(ResultState(self.game))  # Passe à l'écran de résultats

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Gère les entrées clavier du joueur."""
        if self._game_over:
            return

        # Réinitialise les touches enfoncées chaque frame
        self.keys_pressed = [False] * 4

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clic sur le bouton Quitter → retour au Hub
                if self.btn_quit.collidepoint(event.pos):
                    self.game.sounds.play_ui_click()
                    self.game.change_state(HubState(self.game))
                    return

            if event.type == pygame.KEYDOWN:
                # ÉCHAP → retour au Hub (pas quitter le jeu)
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state(HubState(self.game))
                    return

                # Touches A S D F → frappe les notes des colonnes
                for i, col in enumerate(COLUMNS):
                    if event.key == col["key"]:
                        self.keys_pressed[i] = True  # Anime la colonne
                        self._judge_hit(i)            # Juge la frappe
                        self.game.sounds.play_ui_click()  # Son de frappe

    def update(self, dt: float) -> None:
        """Met à jour la logique du jeu à chaque frame."""
        if self._game_over:
            return

        # Décompte du timer
        self.time_left -= dt
        if self.time_left <= 0.0:
            self.time_left = 0.0
            self._finish()  # Fin de la partie quand le timer atteint 0
            return

        # Spawn des notes selon le timer
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self._spawn_note()                    # Génère une nouvelle note
            self.spawn_timer = NOTE_SPAWN_DELAY   # Réinitialise le timer de spawn

        # Déplace toutes les notes vers le bas
        for note in self.notes:
            if not note.hit:  # Ne déplace pas les notes déjà frappées
                note.y += NOTE_SPEED * dt  # Descend selon la vitesse et le temps écoulé

        # Marque comme manquées les notes qui ont dépassé la zone de frappe
        for note in self.notes:
            if not note.hit and not note.missed and note.y > HIT_ZONE_Y + GOOD_WINDOW + 20:
                note.missed = True   # La note est passée → MISS automatique
                self._break_combo()  # Casse le combo
                self._add_feedback("MISS", COLOR_MISS, note.col_index)

        # Supprime les notes qui sont sorties de l'écran par le bas
        self.notes = [n for n in self.notes if n.y < theme.SCREEN_HEIGHT + 50]

        # Met à jour les feedbacks visuels (diminue leur timer)
        for fb in self.feedbacks:
            fb.timer -= dt
        self.feedbacks = [fb for fb in self.feedbacks if fb.timer > 0]  # Garde les visibles

    def render(self, surface: pygame.Surface) -> None:
        """Dessine tout l'affichage du mini-jeu Piano."""

        # ── 1. Fond dégradé sombre (ambiance scène de concert) ─────────────
        surface.fill((25, 15, 40))  # Fond violet très foncé

        # Lignes de guidage verticales pour chaque colonne
        for col in COLUMNS:
            pygame.draw.line(
                surface,
                (*col["color"][:3], 40),  # Couleur très transparente
                (col["x"] + NOTE_WIDTH // 2, 0),
                (col["x"] + NOTE_WIDTH // 2, theme.SCREEN_HEIGHT),
                2,
            )

        # ── 2. Zone de frappe horizontale ─────────────────────────────────
        # Rectangle semi-transparent indiquant où frapper
        hit_surf = pygame.Surface((theme.SCREEN_WIDTH, HIT_ZONE_HEIGHT), pygame.SRCALPHA)
        hit_surf.fill((255, 255, 255, 20))  # Blanc très transparent
        surface.blit(hit_surf, (0, HIT_ZONE_Y - HIT_ZONE_HEIGHT // 2))

        # Ligne centrale de la zone de frappe
        pygame.draw.line(
            surface,
            (255, 255, 255, 120),
            (0, HIT_ZONE_Y),
            (theme.SCREEN_WIDTH, HIT_ZONE_Y),
            3,
        )

        # ── 3. Touches de piano en bas ────────────────────────────────────
        for i, col in enumerate(COLUMNS):
            pressed = self.keys_pressed[i]  # True si la touche est enfoncée
            color = col["color"]
            # La touche s'illumine quand elle est enfoncée
            bright = tuple(min(255, c + 80) for c in color) if pressed else color
            key_rect = pygame.Rect(col["x"], HIT_ZONE_Y + 40, NOTE_WIDTH, 70)
            pygame.draw.rect(surface, bright, key_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 255, 255), key_rect, width=2, border_radius=8)

            # Label de la touche (A, S, D, F) au centre
            lbl = self.font.render(col["label"], True, (255, 255, 255))
            surface.blit(lbl, (col["x"] + NOTE_WIDTH // 2 - lbl.get_width() // 2,
                                HIT_ZONE_Y + 65))

        # ── 4. Notes qui tombent ───────────────────────────────────────────
        for note in self.notes:
            if note.hit:
                continue  # N'affiche pas les notes déjà frappées
            col = COLUMNS[note.col_index]
            color = col["color"]
            if note.missed:
                # Note manquée → affichée en gris transparent
                color = (100, 100, 100)
            note_rect = pygame.Rect(col["x"], int(note.y), NOTE_WIDTH, NOTE_HEIGHT)
            pygame.draw.rect(surface, color, note_rect, border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255), note_rect, width=2, border_radius=10)

        # ── 5. Feedbacks visuels (PERFECT / GOOD / MISS) ──────────────────
        for fb in self.feedbacks:
            # Le texte monte légèrement avec le temps (effet flottant)
            alpha = int(255 * (fb.timer / 0.8))  # Disparaît progressivement
            txt = self.font.render(fb.text, True, fb.color)
            surface.blit(txt, (fb.x + NOTE_WIDTH // 2 - txt.get_width() // 2,
                                HIT_ZONE_Y - 80))

        # ── 6. HUD — informations en haut ─────────────────────────────────
        # Timer
        surface.blit(self.font.render(f"Temps : {self.time_left:.1f} s", True, (255, 255, 255)), (24, 20))
        # Score
        surface.blit(self.font.render(f"Score : {self.score}", True, (255, 230, 50)), (24, 52))
        # Combo
        if self.combo > 0:
            combo_txt = self.font.render(f"COMBO x{self.combo} 🔥", True, (255, 180, 50))
            surface.blit(combo_txt, (theme.SCREEN_WIDTH // 2 - combo_txt.get_width() // 2, 20))
        # Statistiques
        stats = self.font.render(
            f"PERFECT:{self.perfects}  GOOD:{self.goods}  MISS:{self.misses}",
            True, (180, 180, 200)
        )
        surface.blit(stats, (theme.SCREEN_WIDTH // 2 - stats.get_width() // 2, 52))

        # Instructions en bas
        instr = self.font.render("A  S  D  F  pour frapper les notes  |  ÉCHAP = retour Hub", True, (150, 150, 180))
        surface.blit(instr, (theme.SCREEN_WIDTH // 2 - instr.get_width() // 2, theme.SCREEN_HEIGHT - 30))

        # ── 7. Bouton Quitter ──────────────────────────────────────────────
        pygame.draw.rect(surface, (100, 80, 130), self.btn_quit, border_radius=6)
        q = self.font.render("Quitter", True, (255, 255, 255))
        surface.blit(q, (self.btn_quit.x + 12, self.btn_quit.y + 5))
