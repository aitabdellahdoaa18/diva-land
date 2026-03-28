## Étape 1 — Architecture de base du projet Diva Land

> **But de ce document**  
> Décrire l’architecture logique de ton projet (dossiers, fichiers, responsabilités) avant d’écrire du code, pour que tu aies une carte claire de ton jeu.

---

### 1. Objectif pédagogique de l’étape

- **Penser comme un architecte logiciel** : découper le jeu en modules.
- **Savoir où écrire quoi** : ne pas mélanger la logique du hub, des mini‑jeux, de l’UI, etc.
- **Préparer la lisibilité pour le jury** : quelqu’un qui ouvre ton projet doit comprendre rapidement l’organisation.

---

### 2. Vue d’ensemble de l’architecture

Nous allons structurer Diva Land autour de **5 grands blocs** :

1. `core/` — cœur du moteur de jeu (boucle Pygame, gestion d’états).
2. `systems/` — systèmes globaux (XP, économie, inventaire, sauvegarde).
3. `scenes/` — scènes et mini‑jeux (Hub, XO, Golf, etc.).
4. `ui/` — interface utilisateur réutilisable.
5. `assets/` — données et média (images, sons, JSON de contenu).

> **Idée clé**  
> Chaque bloc a une responsabilité bien définie. Cela rend ton code plus facile à maintenir, à présenter et à faire évoluer.

---

### 3. Détail des fichiers prévus par dossier

#### 3.1. Dossier `core/`

- **`core/game.py`**
  - Contiendra la classe principale `Game`.
  - Rôle : initialiser Pygame, créer la fenêtre, lancer la boucle principale (`run()`).
  - Gère :  
    - l’état courant du jeu (Menu, Hub, Mini‑jeu, etc.),  
    - la fréquence de rafraîchissement (FPS),  
    - la délégation des événements/updates/rendus à l’état actif.

- **`core/states.py`**
  - Contiendra :
    - une classe de base `GameState` (état générique),
    - des classes dérivées : `MenuState`, `HubState`, `MiniGameState`, `ResultState`, etc.
  - Rôle : représenter chaque **écran logique** du jeu.
  - Chaque état aura typiquement des méthodes :
    - `handle_events(events)`
    - `update(dt)`
    - `render(surface)`

> **Commentaire prof**  
> `Game` sait *quel* état est actif, mais ne connaît pas les détails de XO, Golf, etc. C’est l’état qui s’occupe du concret.

---

#### 3.2. Dossier `systems/`

- **`systems/economy_manager.py`**
  - Gère les **monnaies** : Pièces, Étoiles, Couronnes.
  - Applique les règles économiques définies dans le GDD (tableau des gains, coût des items).
  - Fournit des fonctions du type :
    - `add_coins(amount)`, `add_stars(amount)`, `add_crowns(amount)`
    - `can_afford(cost)` / `spend(cost)`

- **`systems/xp_manager.py`**
  - Gère la **progression en niveaux**.
  - Utilise la formule \(XP_{requise}(n) = 100 + 50 \times n\).
  - Répond à des fonctions comme :
    - `add_xp(source, amount)`
    - `get_level()`, `get_xp()`
    - `check_level_up()` (et retourne les déblocages éventuels).

- **`systems/inventory.py`**
  - Gère les **items possédés** et **équipés** :
    - vêtements, accessoires,
    - décorations du Hub, etc.
  - Données typiques :
    - liste d’IDs d’items possédés,
    - slots d’équipement (`head`, `dress`, `accessory`, …).

- **`systems/save_manager.py`**
  - Gère la **sauvegarde et le chargement** (fichiers JSON).
  - Connaît le format de sauvegarde décrit dans ton GDD (section 11.4).
  - Offre des fonctions du type :
    - `save_game(state_dict)`
    - `load_game() -> state_dict`

> **Commentaire prof**  
> Ces systèmes sont comme des “services” indépendants. Ils ne se soucient pas du rendu graphique, seulement des données.

---

#### 3.3. Dossier `scenes/`

Chaque fichier ici correspond à une **scène concrète** du jeu, souvent reliée à un état spécifique.

- **`scenes/main_menu.py`**
  - Logique du menu principal (nouvelle partie, charger, quitter).

- **`scenes/hub.py`**
  - Logique du **Jardin Royal** (Hub central) :
    - affichage du personnage,
    - portails vers les mini‑jeux,
    - accès inventaire/boutique.

- **Mini‑jeux** :
  - `scenes/xo.py` : mini‑jeu XO (stratégie logique).
  - `scenes/golf.py` : mini‑jeu Golf (physique 2D).
  - `scenes/piano.py` : mini‑jeu Piano (rythme).
  - `scenes/riding.py` : mini‑jeu Équitation Runner.
  - `scenes/cooking.py` : mini‑jeu Cuisine Royale.
  - `scenes/studio.py` : mini‑jeu Studio Créatif.

> **Point important**  
> Chaque scène/méga-écran doit rester focalisé sur *son* gameplay. La progression globale, l’économie, etc. restent dans `systems/`.

---

#### 3.4. Dossier `ui/`

- **`ui/widgets.py`**
  - Regroupe les **composants UI de base** :
    - boutons,
    - labels (texte),
    - sliders, etc.
  - Objectif : ne pas réécrire la logique d’un bouton dans chaque mini‑jeu.

- **`ui/hud.py`**
  - Contiendra le **HUD principal** (barre d’XP, monnaies, avatar…).
  - Sera utilisé dans le Hub et dans certains mini‑jeux pour garder l’info visible.

---

#### 3.5. Dossier `assets/`

- **`assets/sprites/`**
  - Images : personnages, décors, icônes des monnaies, etc.

- **`assets/audio/`**
  - Sons : clics, succès, échec, musiques des mini‑jeux.

- **`assets/fonts/`**
  - Polices correspondant à ta charte graphique (par ex. Nunito, Poppins…).

- **`assets/data/`**
  - Fichiers de contenu :
    - `levels.json` : progression XP/niveaux.
    - `items.json` : tenues, décors, rareté, coût.
    - `recipes.json` : recettes pour Cuisine.
    - `golf_courses.json` : parcours de golf.
    - `piano_tracks.json` : pistes de piano.

> **Observation prof**  
> Tu peux montrer au jury que ton jeu est “data‑driven” : beaucoup de choses sont décrites dans des fichiers de données plutôt que codées en dur.

---

### 4. Lien avec le GDD existant

Dans ton GDD, la section **11. Architecture Logicielle (pygame/Godot)** propose déjà une structure modulaire.  
Ici, tu **traduits** cette idée dans un projet Pygame :

- `core/` ≈ rôle de la scène principale et du moteur Godot.
- `systems/` ≈ les AutoLoad/Singletons (`GameState`, `EconomyManager`, `XPManager`, etc.).
- `scenes/` ≈ les scènes `.tscn` des mini‑jeux et du hub.
- `assets/data/` ≈ les fichiers JSON déjà mentionnés dans la sauvegarde et le contenu.

> **Message à retenir**  
> Tu respectes la vision du GDD, mais tu l’adaptes à l’écosystème Pygame/Python.

---

### 5. Checklist de fin d’étape

À la fin de l’étape 1, tu dois pouvoir :

1. **Dessiner sur papier** la structure des dossiers et fichiers principaux.
2. **Expliquer le rôle** de chaque grand dossier (`core`, `systems`, `scenes`, `ui`, `assets`).
3. **Montrer à quelqu’un** (prof/jury) où il trouvera :
   - la logique de progression (dans `systems/`),
   - la logique d’un mini‑jeu (dans `scenes/`),
   - les données de contenu (dans `assets/data/`).

Si tu hésites encore sur où placer un fichier dans cette structure, écris ta question tout en bas de ce document.

---

### 6. Notes personnelles / questions

> Utilise cette section pour noter tes propres remarques ou points flous.

- …

