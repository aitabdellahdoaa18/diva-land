"""
scenes/cuisine.py — Mini-jeu Cuisine Royale de Diva Land.

Comment ça marche :
- Une recette s'affiche avec des ingrédients à cliquer dans le bon ordre
- Le joueur clique les ingrédients dans l'ordre indiqué par la recette
- Bon ordre → points + combo
- Mauvais ordre → perd une vie
- 5 recettes à compléter en 90 secondes
- Fond : kitchen_scene.jpg
"""
from __future__ import annotations  # Permet les annotations de type modernes

import random  # Pour mélanger les ingrédients à l'écran
from dataclasses import dataclass  # Pour créer des classes simples
from typing import TYPE_CHECKING  # Pour éviter les imports circulaires

import pygame  # Bibliothèque principale du jeu

from core.states import GameState, HubState, ResultState  # États du jeu
from ui import theme  # Couleurs et dimensions de l'écran

if TYPE_CHECKING:
    from core.game import Game  # Importé seulement pour les annotations de type

# ---------------------------------------------------------------------------
# Constantes — contrôlent le comportement du mini-jeu Cuisine
# ---------------------------------------------------------------------------
GAME_DURATION    = 90.0   # Durée totale en secondes
MAX_LIVES        = 3      # Nombre de vies au départ
RECIPES_TO_WIN   = 5      # Nombre de recettes à compléter pour gagner

# Couleurs des ingrédients
INGREDIENT_COLORS = {
    "🥚 Oeuf":       (255, 240, 180),  # Jaune pâle
    "🧁 Farine":     (245, 235, 220),  # Blanc cassé
    "🍫 Chocolat":   (120,  70,  40),  # Marron
    "🍓 Fraise":     (255,  80,  80),  # Rouge
    "🥛 Lait":       (240, 240, 255),  # Blanc bleuté
    "🍯 Miel":       (255, 195,  50),  # Doré
    "🧈 Beurre":     (255, 215, 100),  # Jaune beurre
    "🍋 Citron":     (255, 255,  80),  # Jaune citron
    "🍎 Pomme":      (200,  50,  50),  # Rouge pomme
    "🍪 Sucre":      (255, 245, 200),  # Blanc sucre
}

# Recettes : liste ordonnée d'ingrédients à cliquer dans l'ordre
RECIPES = [
    {"nom": "Cupcake Princesse 🧁",   "ingredients": ["🥚 Oeuf", "🧁 Farine", "🧈 Beurre", "🍓 Fraise"]},
    {"nom": "Gâteau Chocolat 🍫",     "ingredients": ["🥚 Oeuf", "🍫 Chocolat", "🧁 Farine", "🥛 Lait"]},
    {"nom": "Tarte au Citron 🍋",     "ingredients": ["🧁 Farine", "🧈 Beurre", "🍋 Citron", "🥚 Oeuf"]},
    {"nom": "Muffin Pomme 🍎",        "ingredients": ["🍎 Pomme", "🧁 Farine", "🥚 Oeuf", "🍯 Miel"]},
    {"nom": "Biscuit Royal 🍪",       "ingredients": ["🧁 Farine", "🧈 Beurre", "🍪 Sucre", "🥚 Oeuf"]},
    {"nom": "Smoothie Fraise 🍓",     "ingredients": ["🍓 Fraise", "🥛 Lait", "🍯 Miel", "🍋 Citron"]},
]


@dataclass
class IngredientButton:
    """Représente un bouton ingrédient cliquable à l'écran."""
    name: str           # Nom de l'ingrédient
    rect: pygame.Rect   # Rectangle cliquable
    color: tuple        # Couleur de fond
    used: bool = False  # True si déjà utilisé dans cette recette


class CuisineMinigameState(GameState):
    """État du mini-jeu Cuisine Royale."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        assert game.font_ui is not None
        self.font = game.font_ui  # Police pour le HUD

        # ── État du jeu ────────────────────────────────────────────────────
        self.time_left       = GAME_DURATION   # Temps restant
        self.lives           = MAX_LIVES       # Vies restantes
        self.score           = 0              # Score total
        self.combo           = 0              # Combo actuel
        self.recipes_done    = 0             # Recettes complétées
        self._game_over      = False         # True quand partie terminée

        # ── Recette actuelle ───────────────────────────────────────────────
        self.recipe_order    = random.sample(RECIPES, len(RECIPES))  # Ordre aléatoire
        self.current_recipe  = self.recipe_order[0]  # Recette en cours
        self.current_step    = 0  # Étape actuelle dans la recette (0 = premier ingrédient)

        # ── Feedback visuel ────────────────────────────────────────────────
        self.feedback_text   = ""           # Message affiché (Bravo ! / Erreur !)
        self.feedback_color  = (255, 255, 255)  # Couleur du message
        self.feedback_timer  = 0.0          # Durée restante du feedback

        # ── Ingrédients à l'écran ──────────────────────────────────────────
        self.buttons: list[IngredientButton] = []
        self._create_buttons()  # Génère les boutons ingrédients

        # ── Bouton Quitter ─────────────────────────────────────────────────
        self.btn_quit = pygame.Rect(theme.SCREEN_WIDTH - 130, 12, 110, 36)

        # Arrête la musique du hub
        self.game.sounds.stop_music()

    def _create_buttons(self) -> None:
        """Crée les boutons ingrédients mélangés aléatoirement à l'écran."""
        # Prend tous les ingrédients de la recette + 2 leurres aléatoires
        recipe_ings = self.current_recipe["ingredients"]
        all_ings    = list(INGREDIENT_COLORS.keys())
        decoys      = [i for i in all_ings if i not in recipe_ings]
        decoys      = random.sample(decoys, min(2, len(decoys)))  # 2 faux ingrédients
        displayed   = recipe_ings + decoys                         # Tous les boutons
        random.shuffle(displayed)                                  # Mélange l'ordre

        self.buttons = []
        # Dispose les boutons en grille dans la zone basse de l'écran
        cols     = 3   # 3 colonnes
        btn_w    = 200 # Largeur d'un bouton
        btn_h    = 70  # Hauteur d'un bouton
        padding  = 20  # Espace entre les boutons
        start_x  = theme.SCREEN_WIDTH // 2 - (cols * (btn_w + padding)) // 2
        start_y  = 440  # Position Y du début de la grille

        for i, name in enumerate(displayed):
            col = i % cols       # Colonne actuelle
            row = i // cols      # Rangée actuelle
            x   = start_x + col * (btn_w + padding)
            y   = start_y + row * (btn_h + padding)
            color = INGREDIENT_COLORS.get(name, (200, 200, 200))
            self.buttons.append(IngredientButton(
                name=name,
                rect=pygame.Rect(x, y, btn_w, btn_h),
                color=color,
            ))

    def _next_recipe(self) -> None:
        """Passe à la recette suivante ou termine la partie si toutes sont faites."""
        self.recipes_done += 1  # Une recette de plus complétée

        if self.recipes_done >= RECIPES_TO_WIN:
            # Toutes les recettes complétées → victoire !
            self._finish(won=True)
            return

        # Passe à la recette suivante dans l'ordre
        idx = self.recipes_done % len(self.recipe_order)
        self.current_recipe = self.recipe_order[idx]
        self.current_step   = 0   # Recommence depuis le début de la recette
        self._create_buttons()    # Recrée les boutons pour la nouvelle recette

        # Feedback de succès
        self.feedback_text  = "✨ Recette réussie ! Suivante !"
        self.feedback_color = (100, 255, 150)  # Vert
        self.feedback_timer = 1.5

    def _finish(self, *, won: bool) -> None:
        """Termine la partie et calcule les récompenses."""
        if self._game_over:
            return
        self._game_over = True

        # Score normalisé selon les recettes complétées et le temps restant
        base        = int((self.recipes_done / RECIPES_TO_WIN) * 80)  # 80% selon recettes
        time_bonus  = int((self.time_left / GAME_DURATION) * 20)       # 20% bonus temps
        normalized  = min(100, base + time_bonus)
        if not won:
            normalized = min(normalized, 45)  # Pénalité si perdu

        # Calcul des récompenses
        coins  = 12 + int((normalized / 100.0) * 28)  # Entre 12 et 40 pièces
        xp     = 20 + int((normalized / 100.0) * 40)  # Entre 20 et 60 XP
        stars  = 2 if normalized >= 80 else 1 if normalized >= 50 else 0

        # Ajoute les récompenses
        self.game.economy.add_coins(coins)
        self.game.economy.add_stars(stars)
        unlocks = self.game.xp.add_xp(xp)

        # Sauvegarde le meilleur score
        prev = self.game.minigame_scores.get("cooking", 0)
        self.game.minigame_scores["cooking"] = max(prev, normalized)

        result_txt = (
            f"{'Victoire' if won else 'Défaite'} — {self.recipes_done}/{RECIPES_TO_WIN} recettes"
            f" | score {self.score}"
        )

        self.game.last_minigame_result = {
            "minigame": "cooking",
            "result":   result_txt,
            "coins":    coins,
            "stars":    stars,
            "xp":       xp,
            "normalized": normalized,
            "level_unlock_hints": unlocks,
        }
        self.game.change_state(ResultState(self.game))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Gère les clics du joueur sur les ingrédients."""
        if self._game_over:
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Bouton Quitter → retour au Hub
                if self.btn_quit.collidepoint(event.pos):
                    self.game.sounds.play_ui_click()
                    self.game.change_state(HubState(self.game))
                    return

                # Vérifie si le joueur a cliqué sur un ingrédient
                for btn in self.buttons:
                    if btn.used:
                        continue  # Ignore les ingrédients déjà utilisés
                    if btn.rect.collidepoint(event.pos):
                        self._on_ingredient_click(btn)
                        break

            if event.type == pygame.KEYDOWN:
                # ÉCHAP → retour au Hub
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state(HubState(self.game))
                    return

    def _on_ingredient_click(self, btn: IngredientButton) -> None:
        """Gère le clic sur un ingrédient — vérifie si c'est le bon."""
        expected = self.current_recipe["ingredients"][self.current_step]  # Ingrédient attendu

        if btn.name == expected:
            # ✅ Bon ingrédient !
            btn.used       = True         # Marque comme utilisé
            self.current_step += 1        # Passe à l'étape suivante
            self.combo    += 1            # Augmente le combo
            bonus          = 1 + self.combo // 3  # Bonus selon le combo
            self.score    += 50 * bonus   # 50 points × bonus

            self.game.sounds.play_ui_click()  # Son de succès

            # Vérifie si la recette est complète
            if self.current_step >= len(self.current_recipe["ingredients"]):
                self._next_recipe()  # Passe à la recette suivante
            else:
                # Feedback positif intermédiaire
                self.feedback_text  = "👍 Bon ingrédient !"
                self.feedback_color = (100, 220, 100)  # Vert
                self.feedback_timer = 0.8

        else:
            # ❌ Mauvais ingrédient !
            self.combo  = 0        # Casse le combo
            self.lives -= 1        # Perd une vie
            self.game.sounds.play_hit()  # Son d'erreur

            self.feedback_text  = f"❌ Non ! Il faut : {expected}"
            self.feedback_color = (255, 100, 100)  # Rouge
            self.feedback_timer = 1.2

            if self.lives <= 0:
                self._finish(won=False)  # Plus de vies → défaite

    def update(self, dt: float) -> None:
        """Met à jour la logique à chaque frame."""
        if self._game_over:
            return

        # Décompte du timer
        self.time_left -= dt
        if self.time_left <= 0.0:
            self.time_left = 0.0
            self._finish(won=self.recipes_done >= RECIPES_TO_WIN)
            return

        # Diminue le timer du feedback
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    def render(self, surface: pygame.Surface) -> None:
        """Dessine tout l'affichage du mini-jeu Cuisine."""

        # ── 1. Fond : kitchen_scene.jpg ────────────────────────────────────
        if self.game.img_kitchen_bg is not None:
            surface.blit(self.game.img_kitchen_bg, (0, 0))
        else:
            surface.fill((255, 230, 200))  # Fond orange pâle si image absente

        # Voile semi-transparent pour lisibilité
        veil = pygame.Surface((theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 245, 235, 160))
        surface.blit(veil, (0, 0))

        # ── 2. HUD en haut ─────────────────────────────────────────────────
        font = self.font

        # Timer
        surface.blit(font.render(f"⏱ Temps : {self.time_left:.1f} s", True, (80, 40, 0)), (24, 20))

        # Recettes complétées
        surface.blit(font.render(
            f"Recettes : {self.recipes_done}/{RECIPES_TO_WIN}", True, (80, 40, 0)), (24, 52))

        # Score et combo
        surface.blit(font.render(f"Score : {self.score}", True, (150, 80, 0)), (24, 84))
        if self.combo > 1:
            surface.blit(font.render(f"COMBO x{self.combo} 🔥", True, (255, 150, 0)),
                         (theme.SCREEN_WIDTH // 2 - 80, 20))

        # ── 3. Cœurs (vies restantes) ──────────────────────────────────────
        for i in range(MAX_LIVES):
            cx   = theme.SCREEN_WIDTH - 160 + i * 42
            cy   = 32
            full = i < self.lives
            col  = (236, 72, 110) if full else (200, 200, 210)
            pygame.draw.circle(surface, col, (cx,      cy), 12)
            pygame.draw.circle(surface, col, (cx + 20, cy), 12)
            pygame.draw.polygon(surface, col,
                [(cx - 11, cy + 5), (cx + 31, cy + 5), (cx + 10, cy + 26)])

        # ── 4. Panneau de la recette ───────────────────────────────────────
        recipe_panel = pygame.Rect(
            theme.SCREEN_WIDTH // 2 - 350, 120, 700, 280)
        pygame.draw.rect(surface, (255, 250, 235), recipe_panel, border_radius=16)
        pygame.draw.rect(surface, (200, 160, 80), recipe_panel, width=3, border_radius=16)

        # Nom de la recette
        nom_txt = font.render(f"📋 Recette : {self.current_recipe['nom']}", True, (100, 50, 0))
        surface.blit(nom_txt, (recipe_panel.x + 20, recipe_panel.y + 16))

        # Liste des ingrédients avec indicateur de progression
        ings = self.current_recipe["ingredients"]
        for i, ing in enumerate(ings):
            y_ing = recipe_panel.y + 60 + i * 46
            if i < self.current_step:
                # Ingrédient déjà ajouté → vert avec coche
                color_ing = (80, 180, 80)
                prefix    = "✅ "
            elif i == self.current_step:
                # Ingrédient à ajouter maintenant → orange avec flèche
                color_ing = (220, 120, 0)
                prefix    = "👉 "
            else:
                # Ingrédient futur → gris
                color_ing = (150, 150, 150)
                prefix    = f"{i+1}. "

            ing_txt = font.render(f"{prefix}{ing}", True, color_ing)
            surface.blit(ing_txt, (recipe_panel.x + 30, y_ing))

        # ── 5. Boutons ingrédients ─────────────────────────────────────────
        for btn in self.buttons:
            if btn.used:
                # Ingrédient utilisé → affiché en gris barré
                pygame.draw.rect(surface, (180, 180, 180), btn.rect, border_radius=12)
                txt = font.render(btn.name, True, (120, 120, 120))
            else:
                # Ingrédient disponible → couleur normale avec ombre
                pygame.draw.rect(surface, btn.color, btn.rect, border_radius=12)
                pygame.draw.rect(surface, (150, 100, 50), btn.rect, width=2, border_radius=12)
                txt = font.render(btn.name, True, (60, 30, 0))

            # Centre le texte dans le bouton
            surface.blit(txt, (
                btn.rect.x + btn.rect.width  // 2 - txt.get_width()  // 2,
                btn.rect.y + btn.rect.height // 2 - txt.get_height() // 2,
            ))

        # ── 6. Feedback visuel ─────────────────────────────────────────────
        if self.feedback_timer > 0 and self.feedback_text:
            fb_txt = font.render(self.feedback_text, True, self.feedback_color)
            # Affiche le feedback au centre de l'écran
            fx = theme.SCREEN_WIDTH  // 2 - fb_txt.get_width()  // 2
            fy = theme.SCREEN_HEIGHT // 2 - fb_txt.get_height() // 2 - 20
            # Fond sombre pour lisibilité
            fb_bg = pygame.Rect(fx - 10, fy - 8, fb_txt.get_width() + 20, fb_txt.get_height() + 16)
            pygame.draw.rect(surface, (30, 20, 10, 180), fb_bg, border_radius=10)
            surface.blit(fb_txt, (fx, fy))

        # ── 7. Instruction en bas ──────────────────────────────────────────
        instr = font.render(
            "Clique les ingrédients dans l'ordre 👆  |  ÉCHAP = retour Hub",
            True, (100, 60, 0)
        )
        surface.blit(instr, (
            theme.SCREEN_WIDTH // 2 - instr.get_width() // 2,
            theme.SCREEN_HEIGHT - 30
        ))

        # ── 8. Bouton Quitter ──────────────────────────────────────────────
        pygame.draw.rect(surface, (180, 100, 50), self.btn_quit, border_radius=6)
        q = font.render("Quitter", True, (255, 255, 255))
        surface.blit(q, (self.btn_quit.x + 12, self.btn_quit.y + 5))
