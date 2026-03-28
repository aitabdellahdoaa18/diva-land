"""
systems/sound_manager.py — Sons et musique (mixer Pygame).

Chemins attendus (tu peux remplacer les WAV générés par des fichiers des liens du README) :
- assets/audio/sfx/ui_click.wav | .ogg | .mp3
- assets/audio/sfx/coin.wav | ...
- assets/audio/sfx/gallop.wav | ...
- assets/audio/sfx/victory.ogg (téléchargé OpenGameArt si disponible)
- assets/audio/music/hub_loop.wav | .ogg | .mp3

Les effets courts utilisent `pygame.mixer.Sound`.
La musique d’ambiance utilise `pygame.mixer.music` (une seule piste à la fois).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from systems import procedural_audio


class SoundManager:
    """Chargement paresseux + helpers lecture."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.sfx_dir = root / "assets" / "audio" / "sfx"
        self.music_dir = root / "assets" / "audio" / "music"

        self._click: pygame.mixer.Sound | None = None
        self._coin: pygame.mixer.Sound | None = None
        self._gallop: pygame.mixer.Sound | None = None
        self._jump: pygame.mixer.Sound | None = None
        self._hit: pygame.mixer.Sound | None = None
        self._victory: pygame.mixer.Sound | None = None
        self._hub_music_path: Path | None = None
        self._gallop_channel: pygame.mixer.Channel | None = None

    def setup(self) -> None:
        """
        Initialise le mixer + génère les WAV de secours + charge les Sound.
        À appeler après `pygame.init()` et idéalement après `set_mode` (certaines plateformes).
        """
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            return

        procedural_audio.ensure_ui_click_wav(self.sfx_dir / "ui_click.wav")
        procedural_audio.ensure_coin_wav(self.sfx_dir / "coin.wav")
        procedural_audio.ensure_gallop_wav(self.sfx_dir / "gallop.wav")
        procedural_audio.ensure_hub_loop_wav(self.music_dir / "hub_loop.wav")
        procedural_audio.ensure_victory_wav(self.sfx_dir / "victory.wav")
        procedural_audio.ensure_jump_wav(self.sfx_dir / "jump.wav")
        procedural_audio.ensure_hit_wav(self.sfx_dir / "hit.wav")

        self._click = self._try_sound(["ui_click.wav", "ui_click.ogg", "ui_click.mp3"])
        self._coin = self._try_sound(["coin.wav", "coin.ogg", "coin.mp3"])
        self._gallop = self._try_sound(["gallop.wav", "gallop.ogg", "gallop.mp3"])
        self._jump = self._try_sound(["jump.wav", "jump.ogg", "jump.mp3"])
        self._hit = self._try_sound(["hit.wav", "hit.ogg", "hit.mp3", "collision.wav"])
        self._victory = self._try_sound(["victory.ogg", "victory.wav", "victory.mp3"])

        self._hub_music_path = self._first_existing(
            [
                self.music_dir / "hub_loop.ogg",
                self.music_dir / "hub_loop.mp3",
                self.music_dir / "hub_loop.wav",
                self.music_dir / "princess_theme.ogg",
                self.music_dir / "princess_theme.mp3",
            ]
        )

    def _first_existing(self, paths: list[Path]) -> Path | None:
        for p in paths:
            if p.is_file():
                return p
        return None

    def _try_sound(self, names: list[str]) -> pygame.mixer.Sound | None:
        for name in names:
            p = self.sfx_dir / name
            if p.is_file():
                try:
                    return pygame.mixer.Sound(str(p))
                except pygame.error:
                    continue
        return None

    # --- API jeu -------------------------------------------------------------------------
    def play_ui_click(self) -> None:
        if self._click:
            self._click.play()

    def play_coin(self) -> None:
        if self._coin:
            self._coin.play()

    def play_victory(self) -> None:
        if self._victory:
            self._victory.play()

    def play_hub_music(self) -> None:
        """Boucle la musique du hub si un fichier musique est disponible."""
        if self._hub_music_path is None:
            return
        try:
            pygame.mixer.music.load(str(self._hub_music_path))
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def stop_music(self) -> None:
        pygame.mixer.music.stop()

    def start_gallop_loop(self) -> None:
        if not self._gallop:
            return
        ch = pygame.mixer.find_channel(True)
        if ch is None:
            return
        ch.play(self._gallop, loops=-1)
        self._gallop_channel = ch

    def stop_gallop(self) -> None:
        if self._gallop_channel is not None:
            self._gallop_channel.stop()
            self._gallop_channel = None

    def play_jump(self) -> None:
        if self._jump:
            self._jump.play()

    def play_hit(self) -> None:
        if self._hit:
            self._hit.play()
