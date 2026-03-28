## Étape 0 — Préparer l’environnement de Diva Land

> **But de ce document**  
> T’aider à préparer proprement ton environnement de travail pour Diva Land (Python, Pygame, structure de projet), comme si tu suivais un TP guidé.

---

### 1. Objectif pédagogique de l’étape

- **Comprendre** de quoi tu as besoin pour lancer un projet Pygame propre.
- **Savoir organiser** les dossiers de ton jeu pour que la suite du projet soit claire.
- **Préparer** dès maintenant les fichiers standards d’un projet sérieux (par exemple `requirements.txt`).

> **Comment le jury le voit**  
> Un environnement bien préparé montre que tu traites ton jeu comme un vrai logiciel, pas juste un script rapide.

---

### 2. Pré-requis

- **Connaissances** :
  - Bases de Python (variables, fonctions, fichiers `.py`).
  - Savoir ouvrir un terminal / PowerShell et naviguer dans des dossiers.
- **Outils installés** :
  - Python 3.x installé et accessible dans le terminal (`python --version`).
  - Un éditeur de code (VS Code, Cursor, PyCharm, etc.).

> **Remarque prof**  
> Si tu n’es pas à l’aise avec le terminal, ce n’est pas grave. Cette étape est justement faite pour t’habituer doucement.

---

### 3. Dépendances prévues du projet

Ce que ton jeu utilisera (côté Python) :

- **Bibliothèques indispensables** :
  - `pygame` : moteur 2D pour afficher la fenêtre, gérer les images, les sons, les entrées clavier/souris.
- **Optionnel plus tard** (tu peux juste les noter ici, sans les utiliser tout de suite) :
  - Une bibliothèque pour manipuler plus proprement les données (par exemple `pydantic`, ou juste `dataclasses` de la stdlib).

Dans un fichier futur `requirements.txt`, tu mettras par exemple :

```text
pygame
```

> **Pourquoi `requirements.txt` est important**  
> - Pour toi : tu sais exactement de quoi ton projet dépend.  
> - Pour le jury : il peut recréer ton environnement facilement.  
> - Pour plus tard : si tu changes de PC, tu peux réinstaller les dépendances d’un coup.

---

### 4. Structure de dossiers prévue pour Diva Land

Nous allons viser cette organisation globale (ne t’inquiète pas, tu ne dois pas tout créer d’un coup) :

```text
DivaLand/
  main.py
  core/
    game.py
    states.py
  systems/
    economy_manager.py
    xp_manager.py
    inventory.py
    save_manager.py
  scenes/
    main_menu.py
    hub.py
    xo.py
    golf.py
    piano.py
    riding.py
    cooking.py
    studio.py
  ui/
    widgets.py
    hud.py
  assets/
    sprites/
    audio/
    fonts/
    data/
      levels.json
      items.json
      recipes.json
      golf_courses.json
      piano_tracks.json
  docs/
    etape0_environnement.md
    etape1_architecture_projet.md
    ...
```

#### 4.1. Rôle de chaque grand dossier

- **`core/`**  
  Contiendra le “cœur” technique du jeu :
  - la boucle principale (`game.py`),
  - la gestion des écrans/états (`states.py`).

- **`systems/`**  
  Contiendra les systèmes globaux qui ne dépendent pas d’un mini-jeu en particulier :
  - système d’XP et de niveaux,
  - système économique (monnaies),
  - inventaire et objets,
  - sauvegarde/chargement.

- **`scenes/`**  
  Chaque fichier décrira une **scène jouable** ou un écran important :
  - le Hub,
  - chaque mini-jeu,
  - le menu principal, etc.

- **`ui/`**  
  Résumera tous les **composants d’interface** réutilisables :
  - boutons, barres d’XP, cadres, fenêtres pop‑up,
  - HUD (affichage des infos de jeu pendant que tu joues).

- **`assets/`**  
  Regroupera tout ce qui n’est pas du code Python :
  - `sprites/` : images, personnages, décors, icônes.
  - `audio/` : musiques, effets sonores, bruitages.
  - `fonts/` : fichiers de polices (pour appliquer ta charte graphique).
  - `data/` : fichiers JSON avec le contenu du jeu (niveaux, items, recettes…).

- **`docs/`**  
  Dossier de documentation interne (comme ce fichier).  
  Il montre ton **réflexe de documentation**, très apprécié dans un projet académique.

> **Conseil prof**  
> Tu peux déjà créer les dossiers vides si tu veux t’organiser. Tu n’es pas obligé de remplir tout de suite chaque fichier.

---

### 5. Checklist de fin d’étape

À la fin de l’étape 0, tu dois pouvoir répondre **oui** à ces questions :

1. **Sais-tu où vivra ton projet ?**
   - Exemple : `c:\Users\admin\Desktop\DivaLandByDoaa` ou un dossier similaire.
2. **Sais-tu quelles bibliothèques Python seront utilisées ?**
   - Au minimum : `pygame`.
3. **As-tu une idée claire de la structure de dossiers cible ?**
   - Tu es capable de redessiner la structure ci‑dessus sur papier.
4. **Comprends-tu l’utilité d’un fichier `requirements.txt` ?**
   - Même si tu ne l’as pas encore créé, tu sais à quoi il servira.

Si tu bloques sur un des points, note ta question à la fin de ce fichier avant de passer à l’étape 1.

---

### 6. Notes personnelles / questions

> Utilise cette section comme un carnet de bord.  
> Tu peux y écrire ce qui te semble flou, ou les commandes que tu souhaites mémoriser.

- …

