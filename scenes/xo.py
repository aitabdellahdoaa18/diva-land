"""
scenes/xo.py — Mini-jeu Morpion (GDD §9.1) intégré à l’architecture par états.

Contenu pédagogique :
- Grille 3×3 représentée par une liste de listes d’entiers.
- Gestion des clics souris → conversion (px → cellule).
- IA “facile” = coup aléatoire sur case vide (compatible avec le GDD niveau Facile).
- Fin de partie → calcul des récompenses → mise à jour Economy + XP → passage à ResultState.

Extension future (pour ton rapport / code) :
- Ajouter niveau Moyen (heuristique) et Difficile (minimax) comme décrit dans le GDD.
"""
from __future__ import annotations

import random
from typing import Literal, TYPE_CHECKING

import pygame

from core.states import GameState, ResultState
from ui import theme

if TYPE_CHECKING:
    from core.game import Game

# Constantes “énumération légère” : évite les nombres magiques 0/1/2 sans explication.
EMPTY = 0
PLAYER_X = 1  # humain
AI_O = 2      # ordinateur

Outcome = Literal["win", "lose", "draw"]


def _check_line(a: int, b: int, c: int) -> int | None:
    """Si trois cases identiques non vides, renvoie ce symbole ; sinon None."""
    if a == b == c and a != EMPTY:
        return a
    return None


def evaluate_board(grid: list[list[int]]) -> tuple[int | None, bool]:
    """
    Retourne (winner_token, board_full).

    winner_token :
        None si la partie continue,
        PLAYER_X / AI_O si alignement trouvé,
        Dans le cas match nul complet sans alignement, winner_token rest None et board_full True.
    """
    # Lignes
    for r in range(3):
        w = _check_line(grid[r][0], grid[r][1], grid[r][2])
        if w is not None:
            return w, False
    # Colonnes
    for c in range(3):
        w = _check_line(grid[0][c], grid[1][c], grid[2][c])
        if w is not None:
            return w, False
    # Diagonales
    w = _check_line(grid[0][0], grid[1][1], grid[2][2])
    if w is not None:
        return w, False
    w = _check_line(grid[0][2], grid[1][1], grid[2][0])
    if w is not None:
        return w, False

    full = all(grid[r][c] != EMPTY for r in range(3) for c in range(3))
    return None, full


class XOMinigameState(GameState):
    """Boucle locale du morpion : un tour joueur puis éventuellement un tour IA."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None
        # Nouvelle grille vide pour chaque partie.
        self.grid: list[list[int]] = [[EMPTY] * 3 for _ in range(3)]
        self.turn: Literal["player", "ai"] = "player"
        self.game_over = False
        self.outcome: Outcome | None = None

        # Rectangle englobant la grille : tout le dessin est relatif à `self.board_rect.origin`.
        side = min(theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT) // 2
        self.board_rect = pygame.Rect(0, 0, side, side)
        self.board_rect.center = (theme.SCREEN_WIDTH // 2, theme.SCREEN_HEIGHT // 2 + 20)
        self.cell = side // 3  # taille d’une case en pixels

        self.font = game.font_ui
        self.hint = "Tu joues les X — clique une case vide."
        self._stopped_menu_music = False

    def _cell_from_mouse(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """
        Convertit un clic souris en indices (row, col) si à l’intérieur du plateau.
        Retour None si en dehors du plateau (clic ignoré).
        """
        x, y = pos
        if not self.board_rect.collidepoint(x, y):
            return None
        # Coordonnées locales dans le carré du plateau.
        lx = x - self.board_rect.x
        ly = y - self.board_rect.y
        col = lx // self.cell
        row = ly // self.cell
        if 0 <= row < 3 and 0 <= col < 3:
            return row, col
        return None

    def _ai_random_move(self) -> None:
        """
        IA niveau *Facile* du GDD : choisit une case vide au hasard.

        Complexité O(1) amortie : au pire 9 cases — négligeable.
        """
        empties = [(r, c) for r in range(3) for c in range(3) if self.grid[r][c] == EMPTY]
        if not empties:
            return
        r, c = random.choice(empties)
        self.grid[r][c] = AI_O

    def _finalize(self, outcome: Outcome) -> None:
        """
        Applique les récompenses GDD (§9.1 tableau scoring) puis enchaîne vers ResultState.

        Pourquoi centraliser ici ?
        - Sépare clairement “règles du morpion” et “progression globale du RPG léger”.
        """
        self.game_over = True
        self.outcome = outcome

        # Tableau du GDD : Victoire / Nul / Défaite → pièces + XP.
        if outcome == "win":
            coins, xp, stars = 30, 50, 1
        elif outcome == "draw":
            coins, xp, stars = 15, 25, 0
        else:
            coins, xp, stars = 10, 10, 0

        self.game.economy.add_coins(coins)
        self.game.economy.add_stars(stars)
        unlock_messages = self.game.xp.add_xp(xp)

        # Score normalisé 0–100 (pédagogique — simplifié) : win=100, draw=50, lose=20.
        normalized = 100 if outcome == "win" else 50 if outcome == "draw" else 20
        prev = self.game.minigame_scores.get("xo", 0)
        self.game.minigame_scores["xo"] = max(prev, normalized)

        # Dictionnaire consommé par `ResultState` : contrat décrit dans etape9.md.
        self.game.last_minigame_result = {
            "minigame": "xo",
            "result": outcome,
            "coins": coins,
            "stars": stars,
            "xp": xp,
            "normalized": normalized,
            "level_unlock_hints": unlock_messages,
        }

        self.game.change_state(ResultState(self.game))

    def _resolve_after_player_move(self) -> None:
        """Après coup joueur : test victoire / nul, sinon tour IA, puis re-test."""
        winner, full = evaluate_board(self.grid)
        if winner == PLAYER_X:
            self._finalize("win")
            return
        if full:
            self._finalize("draw")
            return

        self.turn = "ai"
        self._ai_random_move()
        self.turn = "player"

        winner2, full2 = evaluate_board(self.grid)
        if winner2 == AI_O:
            self._finalize("lose")
        elif full2:
            self._finalize("draw")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        # Si la partie est finie, on a déjà basculé d’état ; garde-fou défensif.
        if self.game_over:
            return
        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            if event.button != 1:  # clic gauche uniquement
                continue
            if self.turn != "player":
                continue
            cell = self._cell_from_mouse(event.pos)
            if cell is None:
                continue
            r, c = cell
            if self.grid[r][c] != EMPTY:
                continue
            self.grid[r][c] = PLAYER_X
            self._resolve_after_player_move()

    def update(self, dt: float) -> None:
        if not self._stopped_menu_music:
            self.game.sounds.stop_music()
            self._stopped_menu_music = True
        _ = dt  # ici pas d’animation temporelle ; Golf/Cheval l’utiliseront.

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BG)
        title = self.font.render("XO Stratégique — Morpion (prototype)", True, theme.TEXT)
        surface.blit(title, (theme.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        hint_surf = self.font.render(self.hint, True, theme.MUTED)
        surface.blit(hint_surf, (theme.SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, 90))

        # Cadre du plateau.
        pygame.draw.rect(surface, theme.WHITE, self.board_rect, border_radius=8)
        pygame.draw.rect(surface, theme.ACCENT, self.board_rect, width=3, border_radius=8)

        # Quadrillage (lignes internes).
        for i in range(1, 3):
            x = self.board_rect.x + i * self.cell
            pygame.draw.line(surface, theme.MUTED, (x, self.board_rect.y), (x, self.board_rect.bottom), 2)
            y = self.board_rect.y + i * self.cell
            pygame.draw.line(surface, theme.MUTED, (self.board_rect.x, y), (self.board_rect.right, y), 2)

        # Symboles X / O dessinés en vectoriel simple (pas d’images encore).
        for r in range(3):
            for c in range(3):
                cx = self.board_rect.x + c * self.cell + self.cell // 2
                cy = self.board_rect.y + r * self.cell + self.cell // 2
                margin = self.cell // 6
                if self.grid[r][c] == PLAYER_X:
                    # X = deux segments diagonaux.
                    pygame.draw.line(
                        surface,
                        theme.TEXT,
                        (cx - self.cell // 2 + margin, cy - self.cell // 2 + margin),
                        (cx + self.cell // 2 - margin, cy + self.cell // 2 - margin),
                        4,
                    )
                    pygame.draw.line(
                        surface,
                        theme.TEXT,
                        (cx + self.cell // 2 - margin, cy - self.cell // 2 + margin),
                        (cx - self.cell // 2 + margin, cy + self.cell // 2 - margin),
                        4,
                    )
                elif self.grid[r][c] == AI_O:
                    # O = cercle.
                    pygame.draw.circle(surface, theme.PRIMARY, (cx, cy), self.cell // 2 - margin, 4)
