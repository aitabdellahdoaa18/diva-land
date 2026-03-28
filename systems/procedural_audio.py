"""
Génération de fichiers WAV courts (mono 44.1 kHz) si les assets distants
ne sont pas téléchargeables automatiquement.

But : le jeu reste jouable hors-ligne avec des sons “placeholder” propres.
Remplace-les par les fichiers des liens indiqués dans assets/audio/README.md.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def _write_mono_wav(path: Path, samples: list[float], rate: int = 44100) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for x in samples:
            s = int(max(-1.0, min(1.0, x)) * 32767)
            wf.writeframes(struct.pack("<h", s))


def ensure_ui_click_wav(path: Path) -> None:
    """Clic bref (type UI) ~50 ms avec decay exponentiel."""
    if path.is_file():
        return
    rate = 44100
    dur = 0.055
    n = int(rate * dur)
    out: list[float] = []
    for i in range(n):
        t = i / rate
        env = math.exp(-t * 90.0)
        # Petit “pop” bande-passé approximé = bruit haute fréquence amorti.
        sig = env * math.sin(2 * math.pi * 1800.0 * t) * 0.35
        out.append(sig)
    _write_mono_wav(path, out, rate)


def ensure_coin_wav(path: Path) -> None:
    """Deux bips ascendants (récompense / pièce)."""
    if path.is_file():
        return
    rate = 44100
    out: list[float] = []
    for freq, dur_ms in [(880.0, 70), (1320.0, 90)]:
        n = int(rate * (dur_ms / 1000.0))
        for i in range(n):
            t = i / rate
            env = math.sin((i + 1) / n * math.pi)  # fenêtre en S
            out.append(env * math.sin(2 * math.pi * freq * t) * 0.28)
    _write_mono_wav(path, out, rate)


def ensure_gallop_wav(path: Path) -> None:
    """Motif rythmique basse fréquence (effet galop simplifié, 1 boucle ~0,5 s)."""
    if path.is_file():
        return
    rate = 44100
    total = int(0.55 * rate)
    out = [0.0] * total
    pulses = 4
    for p in range(pulses):
        start = int(total * (p / pulses))
        leng = int(rate * 0.04)
        for i in range(leng):
            if start + i >= total:
                break
            t = i / rate
            env = math.exp(-t * 35.0)
            sig = env * math.sin(2 * math.pi * 95.0 * t) * 0.45
            out[start + i] += sig
    # normalisation douce
    peak = max(abs(x) for x in out) or 1.0
    out = [x / peak * 0.9 for x in out]
    _write_mono_wav(path, out, rate)


def ensure_victory_wav(path: Path) -> None:
    """Court jingle “succès” si aucun victory.ogg externe n’est fourni."""
    if path.is_file():
        return
    rate = 44100
    out: list[float] = []
    for freq, ms in [(523.25, 90), (659.25, 90), (783.99, 120), (1046.5, 160)]:
        n = int(rate * (ms / 1000.0))
        for i in range(n):
            t = i / rate
            env = math.sin((i + 1) / n * math.pi)
            out.append(env * math.sin(2 * math.pi * freq * t) * 0.22)
    _write_mono_wav(path, out, rate)


def ensure_jump_wav(path: Path) -> None:
    """Petit « whoosh » ascendant (saut)."""
    if path.is_file():
        return
    rate = 44100
    out: list[float] = []
    n = int(rate * 0.12)
    for i in range(n):
        t = i / rate
        f0 = 400 + 800 * (t / 0.12)
        env = math.sin((i + 1) / n * math.pi)
        out.append(env * math.sin(2 * math.pi * f0 * t) * 0.25)
    _write_mono_wav(path, out, rate)


def ensure_hit_wav(path: Path) -> None:
    """Impact bref (collision obstacle)."""
    if path.is_file():
        return
    rate = 44100
    n = int(rate * 0.15)
    out: list[float] = []
    for i in range(n):
        t = i / rate
        env = math.exp(-t * 18.0)
        noise = math.sin(2 * math.pi * (55.0 + 120 * t) * t) * 0.4
        out.append(env * noise)
    peak = max(abs(x) for x in out) or 1.0
    out = [x / peak * 0.85 for x in out]
    _write_mono_wav(path, out, rate)


def ensure_hub_loop_wav(path: Path) -> None:
    """
    Boucle musicale très simple (arpège majeur) — remplace par une vraie OGG/Music.
    Durée ~3,2 s ; la musique Pygame boucle avec mixer.music.
    """
    if path.is_file():
        return
    rate = 44100
    dur = 3.2
    n = int(rate * dur)
    freqs = [523.25, 659.25, 783.99, 1046.50]  # C5 E5 G5 C6
    out: list[float] = []
    for i in range(n):
        t = i / rate
        # changer de note toutes les 0,2 s
        step = min(len(freqs) - 1, int(t / 0.2) % (len(freqs) * 2))
        if step >= len(freqs):
            step = len(freqs) * 2 - 1 - step
        if step < 0:
            step = 0
        f = freqs[step % len(freqs)]
        # LFO très lent pour éviter la monotonie
        trem = 0.5 + 0.5 * math.sin(2 * math.pi * 2.0 * t)
        sig = 0.08 * trem * math.sin(2 * math.pi * f * t)
        out.append(sig)
    _write_mono_wav(path, out, rate)
