"""
core/game.py — Classe `Game` : fenêtre Pygame, horloge, systèmes, boucle principale.

Flux pédagogique (une frame) :
    1) pygame.event.get()  → événements OS (clavier, souris, fermeture fenêtre)
    2) current_state.handle_events(...)
    3) current_state.update(dt)
    4) current_state.render(screen)
    5) pygame.display.flip() + clock.tick(FPS)

`dt` (delta time) : temps en secondes depuis la frame précédente — utile pour mouvements fluides.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pygame

from core import media
from core.states import GameState, MenuState
from systems.economy_manager import EconomyManager
from systems.inventory import Inventory
from systems.save_manager import SaveManager
from systems.sound_manager import SoundManager
from systems.xp_manager import XPManager
from ui import theme


class Game:
    """
    Point central du moteur : instancie Pygame et délègue aux états.

    Attributs utiles pour l’enseignement :
        screen          — Surface principale (tout le dessin y passe)
        clock           — pygame.time.Clock pour limiter les FPS
        running         — False => sortie de la boucle
        current_state   — instance de GameState active
        economy/xp/inv  — systèmes globaux partagés
    """

    def __init__(self) -> None:
        # Racine du projet = dossier parent de `core/` (où se trouve main.py à côté).
        self.root = Path(__file__).resolve().parent.parent
        self.save_path = self.root / "save.json"

        # États globaux hors gameplay immédiat (résultat du dernier mini-jeu).
        self.last_minigame_result: dict[str, Any] | None = None
        # Scores “meilleur score” par id mini-jeu (normalisé 0–100 ou brut selon ton choix).
        self.minigame_scores: dict[str, int] = {}

        # Systèmes
        self.economy = EconomyManager()
        self.xp = XPManager()
        self.inventory = Inventory()
        self.save_manager = SaveManager(self.save_path)
        self.sounds = SoundManager(self.root)

        # Pygame sera initialisé dans run() pour éviter les effets de import AVANT main.
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.running = False
        self.font_ui: pygame.font.Font | None = None
        self.font_title: pygame.font.Font | None = None

        # L’état initial sera créé après `init_pygame()` car les polices Pygame n’existent pas encore.
        self.current_state: GameState | None = None

        # Textures UI (remplies dans init_pygame après set_mode + convert).
        self.img_menu_bg: pygame.Surface | None = None
        self.img_hub_map: pygame.Surface | None = None
        self.img_princess: pygame.Surface | None = None
        self.img_kitchen_portal: pygame.Surface | None = None
        self.img_horse_portal: pygame.Surface | None = None
        self.img_golf_bg: pygame.Surface | None = None
        # Fonds plein écran (cuisine / équitation).
        self.img_kitchen_bg: pygame.Surface | None = None
        self.img_riding_raw: pygame.Surface | None = None  # image complète pour parallax
        # Grille 2×4 de `princess_costumes.jpg`
        self.costume_cells: list[pygame.Surface] = []

    def load_shared_images(self) -> None:
        """
        Charge les JPG listés par le côté design — chemins : assets/sprites/*.jpg
        Appelé une fois que pygame.display est actif (convert plus fiable / performant).
        """
        sprites = self.root / "assets" / "sprites"
        w, h = theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT
        raw = media.try_load_convert(sprites / "title_screen.jpg")
        self.img_menu_bg = media.scale_stretch(raw, w, h) if raw else None

        raw_map = media.try_load_convert(sprites / "world_map.jpg")
        self.img_hub_map = media.scale_stretch(raw_map, w, h) if raw_map else None

        raw_pr = media.try_load_convert(sprites / "princess_main.jpg")
        if raw_pr:
            self.img_princess = media.scale_fit(raw_pr, 380, 440)
            # Fond blanc du personnage → transparence pour le poser sur la carte.
            self.img_princess.set_colorkey((255, 255, 255))
        else:
            self.img_princess = None

        raw_k = media.try_load_convert(sprites / "kitchen_scene.jpg")
        self.img_kitchen_portal = media.scale_fit(raw_k, 280, 140) if raw_k else None
        self.img_kitchen_bg = media.scale_stretch(raw_k, w, h) if raw_k else None

        raw_h = media.try_load_convert(sprites / "horse_riding.jpg")
        self.img_horse_portal = media.scale_fit(raw_h, 280, 140) if raw_h else None
        self.img_riding_raw = raw_h  # conservé pour défilement / découpe parallax

        raw_golf = media.try_load_convert(sprites / "castle_dusk.jpg")
        self.img_golf_bg = media.scale_stretch(raw_golf, w, h) if raw_golf else None

        raw_sheet = media.try_load_convert(sprites / "princess_costumes.jpg")
        self.costume_cells = self._split_costume_sheet(raw_sheet) if raw_sheet else []

    @staticmethod
    def _split_costume_sheet(sheet: pygame.Surface) -> list[pygame.Surface]:
        """Découpe une grille 4×2 en 8 surfaces (copies indépendantes)."""
        sw, sh = sheet.get_size()
        cell_w, cell_h = max(1, sw // 4), max(1, sh // 2)
        out: list[pygame.Surface] = []
        for row in range(2):
            for col in range(4):
                area = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
                subs = sheet.subsurface(area).copy()
                out.append(subs)
        return out

    def get_hub_princess_surface(self) -> pygame.Surface | None:
        """Sprite à afficher sur le hub selon la tenue équipée."""
        idx = self.inventory.costume_index
        if idx is not None and 0 <= idx < len(self.costume_cells):
            return media.scale_fit(self.costume_cells[idx], 380, 440)
        return self.img_princess

    def init_pygame(self) -> None:
        """Initialise les modules Pygame, la fenêtre, les polices par défaut."""
        # pygame.init() : charge les sous-systèmes (vidéo, fonts, etc.)
        pygame.init()
        # Fenêtre avec taille fixe définie dans theme.py (design stable).
        self.screen = pygame.display.set_mode((theme.SCREEN_WIDTH, theme.SCREEN_HEIGHT))
        pygame.display.set_caption("Diva Land — Prototype Pygame")
        self.clock = pygame.time.Clock()
        # Police système par défaut : 0 charge une font “par défaut” (sans fichier .ttf).
        self.font_ui = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 64)
        self.load_shared_images()
        self.sounds.setup()

    def change_state(self, new_state: GameState) -> None:
        """
        Change l’état courant (Menu ↔ Hub ↔ Mini-jeu ↔ Résultats).

        Pourquoi passer un objet et pas juste un string ?
        - Typage clair, auto-complétion, moins d’erreurs que des noms magiques.
        """
        self.current_state = new_state

    def try_autoload(self) -> None:
        """
        Charge la sauvegarde si elle existe (au démarrage).
        Le menu pourra proposer “Continuer” plus tard ; pour l’instant on charge au lancement du jeu
        dans main.py AVANT la boucle, via un appel explicite depuis l’extérieur si besoin.
        """
        data = self.save_manager.load()
        if not data:
            return
        self.apply_save_data(data)

    def apply_save_data(self, data: dict[str, Any]) -> None:
        """Réinjecte un dict JSON dans les systèmes (après load)."""
        self.xp.load_from_dict(data)
        self.economy.load_from_dict(
            {
                "coins": data.get("coins", 0),
                "stars": data.get("stars", 0),
                "crowns": data.get("crowns", 0),
            }
        )
        self.inventory.load_from_dict(
            {
                "inventory": data.get("inventory", []),
                "equipped": data.get("equipped", {}),
            }
        )
        # Scores mini-jeux si présents
        scores = data.get("minigame_scores", {})
        if isinstance(scores, dict):
            self.minigame_scores = {str(k): int(v) for k, v in scores.items()}

    def build_save_data(self) -> dict[str, Any]:
        """Construit le dict global écrit dans save.json (aligné GDD)."""
        xp_d = self.xp.to_dict()
        return {
            "player_level": xp_d["player_level"],
            "player_xp": xp_d["player_xp"],
            **self.economy.to_dict(),
            **self.inventory.to_dict(),
            "unlocked_content": [],  # à remplir quand tu brancheras les déblocages (GDD §7.2)
            "minigame_scores": dict(self.minigame_scores),
        }

    def save_game(self) -> None:
        """Persistance : assemble l’état et l’écrit sur disque."""
        self.save_manager.save(self.build_save_data())

    def run(self) -> None:
        """Boucle principale : cœur du programme côté jeu vidéo."""
        self.init_pygame()
        assert self.screen is not None and self.clock is not None
        # Une fois pygame.font prêt, on peut instancier le premier écran (boutons utilisent la police).
        if self.current_state is None:
            self.current_state = MenuState(self)

        self.running = True
        # Boucle tant que running True (quit via état menu ou fermeture fenêtre).
        while self.running:
            # dt en secondes ; utile pour physique/animations indépendantes du framerate.
            dt_ms = self.clock.tick(theme.FPS)
            dt = dt_ms / 1000.0

            # 1) Récupérer tous les événements en attente (file FIFO).
            events = pygame.event.get()
            for event in events:
                # Croix de la fenêtre = QUIT : on arrête proprement.
                if event.type == pygame.QUIT:
                    self.save_game()
                    self.running = False

            # Si on a quitté via QUIT, on ne traite plus l’état cette frame.
            if not self.running:
                break

            # 2–4) Délégation complète à l’état courant.
            assert self.current_state is not None
            self.current_state.handle_events(events)
            self.current_state.update(dt)
            self.current_state.render(self.screen)

            # Double buffering : affiche le buffer back sur l’écran physique.
            pygame.display.flip()

        pygame.quit()

    def request_quit(self) -> None:
        """
        Quitte l’application proprement : sauvegarde puis coupe la boucle.
        Appelé depuis le menu (bouton Quitter) plutôt que de dupliquer la logique partout.
        """
        self.save_game()
        self.running = False
