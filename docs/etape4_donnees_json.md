## Étape 4 — Données JSON : niveaux, items, recettes, parcours, pistes

> **But de ce document**  
> Transformer les tableaux de ton GDD en vraies structures de données JSON, prêtes à être utilisées par le code.

---

### 1. Objectif pédagogique de l’étape

- Comprendre la séparation **code / données**.
- Savoir concevoir des **schémas JSON** cohérents avec ton GDD.
- Faciliter l’équilibrage du jeu sans toucher au code Python.

---

### 2. `levels.json` — Niveaux et déblocages

**But** : décrire chaque niveau du joueur.

- **Schéma envisagé** :

```json
[
  {
    "level": 1,
    "xp_required": 150,
    "unlocks": []
  },
  {
    "level": 2,
    "xp_required": 200,
    "unlocks": ["dress_etoilee"]
  },
  {
    "level": 3,
    "xp_required": 250,
    "unlocks": ["xo_medium_difficulty"]
  }
]
```

- **Champs** :
  - `level` : numéro du niveau.
  - `xp_required` : XP nécessaire pour passer au niveau suivant.
  - `unlocks` : liste d’IDs de contenu débloqué à ce niveau.

---

### 3. `items.json` — Objets (vêtements, décors, etc.)

**But** : décrire tous les items disponibles dans le jeu.

- **Schéma envisagé** :

```json
[
  {
    "id": "dress_etoilee",
    "name": "Robe Étoilée",
    "type": "dress",
    "rarity": "rare",
    "cost_coins": 300,
    "cost_stars": 0,
    "min_level": 2
  },
  {
    "id": "hub_fountain",
    "name": "Fontaine Dorée",
    "type": "hub_decoration",
    "rarity": "epic",
    "cost_coins": 0,
    "cost_stars": 5,
    "min_level": 5
  }
]
```

- **Champs** :
  - `id` : identifiant unique (utilisé dans le code et les sauvegardes).
  - `name` : nom lisible pour l’UI.
  - `type` : catégorie (`dress`, `hat`, `accessory`, `hub_decoration`, …).
  - `rarity` : `common`, `rare`, `epic`, `legendary`.
  - `cost_coins`, `cost_stars` : coût d’achat.
  - `min_level` : niveau minimum pour pouvoir acheter/équiper.

---

### 4. `recipes.json` — Recettes de Cuisine Royale

**But** : définir les séquences d’actions pour le mini‑jeu Cuisine.

- **Schéma envisagé** :

```json
[
  {
    "id": "recipe_cake_01",
    "name": "Gâteau Fraise Or",
    "time_limit": 90,
    "steps": [
      { "action": "select_ingredient", "target": "flour" },
      { "action": "mix", "target": "bowl" },
      { "action": "select_ingredient", "target": "eggs" },
      { "action": "mix", "target": "bowl" },
      { "action": "bake", "duration": 30 }
    ]
  }
]
```

- **Champs** :
  - `time_limit` : temps total alloué en secondes.
  - `steps` : liste d’actions que le joueur doit réaliser dans l’ordre.

---

### 5. `golf_courses.json` — Parcours de Golf

**But** : définir les obstacles et la difficulté des parcours.

- **Schéma simplifié** :

```json
[
  {
    "id": "golf_course_1",
    "par": 3,
    "start": { "x": 100, "y": 300 },
    "hole": { "x": 700, "y": 320, "radius": 20 },
    "obstacles": [
      { "type": "wall", "x": 300, "y": 280, "width": 20, "height": 80 },
      { "type": "bumper", "x": 500, "y": 310, "radius": 15 }
    ]
  }
]
```

---

### 6. `piano_tracks.json` — Pistes de Piano

**But** : définir les notes et leur timing pour le mini‑jeu Piano.

- **Schéma simplifié** :

```json
[
  {
    "id": "piano_easy_1",
    "bpm": 100,
    "notes": [
      { "time_ms": 0, "column": 0 },
      { "time_ms": 500, "column": 1 },
      { "time_ms": 1000, "column": 2 },
      { "time_ms": 1500, "column": 3 },
      { "time_ms": 2000, "column": 4 }
    ]
  }
]
```

- **Convention** :
  - `column` correspond à une touche du clavier (ex : 0→A, 1→S, 2→D, etc.).

---

### 7. Convention de nommage des IDs

- Mini‑jeux : `xo`, `golf`, `piano`, `riding`, `cooking`, `studio`.
- Items :
  - Vêtements : `dress_*`, `hat_*`, `accessory_*`.
  - Décors hub : `hub_*`.
- Recettes : `recipe_*`.
- Parcours golf : `golf_course_*`.
- Pistes piano : `piano_*`.

---

### 8. Checklist de fin d’étape

Tu dois pouvoir :

1. Écrire un **exemple complet** pour chacun des fichiers JSON.
2. Expliquer comment modifier la difficulté (par ex. augmenter `xp_required`, changer `par`, densifier les notes de piano).
3. Comprendre que tu peux **équilibrer le jeu** en touchant seulement ces fichiers, sans modifier le Python.

---

### 9. Notes personnelles / questions

- …

