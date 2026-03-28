# Audio — Diva Land

## Fichiers utilisés par le code

| Rôle | Chemin conseillé | Note |
|------|------------------|------|
| Clic bouton | `sfx/ui_click.*` | WAV généré automatiquement si absent |
| Pièce | `sfx/coin.*` | idem |
| Galop | `sfx/gallop.*` | idem |
| Victoire | `sfx/victory.ogg` | Ex. [Win Jingle Fupi](https://opengameart.org/content/win-jingle) → `winfretless_0.ogg` renommé |
| Musique hub | `music/hub_loop.*` | WAV généré si absent ; remplace par ta piste |

## Liens demandés (téléchargement manuel si besoin)

1. **Clic** — <https://freesound.org/people/InspectorJ/sounds/411648/> (télécharge le preview / fichier, place en `sfx/ui_click.wav` ou `.ogg`).
2. **Musique hub — Princess Title Theme** — rechercher sur [OpenGameArt](https://opengameart.org) « Princess Title » ou équivalent CC0 ; place en `music/hub_loop.ogg`.
3. **Victoire** — <https://opengameart.org/content/win-jingle> → fichier direct souvent `winfretless_0.ogg` → `sfx/victory.ogg`.
4. **Pièce** — <https://freesound.org/people/GameAudio/sounds/220173/>.
5. **Galop** — <https://freesound.org/people/aglinder/sounds/375859/>.

Après copie, relance le jeu : le `SoundManager` préfère tes fichiers aux WAV générés.
