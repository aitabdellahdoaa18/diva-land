## Étape 8 — Autres mini‑jeux : Piano, Équitation, Cuisine, Studio

> **But de ce document**  
> Décrire les 4 mini‑jeux restants de façon structurée, en réutilisant les idées et patterns appris avec XO et Golf.

---

### 1. Objectif pédagogique de l’étape

- Appliquer le même schéma de conception à plusieurs gameplays différents.
- Clarifier pour chaque mini‑jeu :
  - contrôles,
  - représentation des données,
  - flow de partie,
  - scoring et intégration.

---

### 2. Mini‑jeu Piano — Rythme et timing

**Fichier de scène** : `scenes/piano.py`  
**Données** : `assets/data/piano_tracks.json`

#### 2.1. Règles de base

- Des notes descendent sur 5 colonnes.
- Chaque colonne correspond à une touche du clavier (ex : A, S, D, J, K).
- Le joueur doit appuyer sur la bonne touche au bon moment, quand la note atteint la zone de frappe.

#### 2.2. Représentation des notes

- Chaque note est un objet avec :
  - `time_ms` : moment où la note doit être frappée.
  - `column` : indice de colonne (0 à 4).
- Les notes sont chargées depuis `piano_tracks.json`.

#### 2.3. Gestion du temps et précision

- Utiliser un temps global (ex : `pygame.time.get_ticks()` ou un compteur incrémenté par `dt`).
- Pour chaque note, comparer le temps réel d’appui avec `time_ms` :
  - `delta_t = |t_input - time_ms|`
  - Plus `delta_t` est petit, meilleure est la note (PERFECT, GREAT, GOOD, MISS).

#### 2.4. Scoring

- Reprendre le tableau de ton GDD (points par niveau de précision).
- Ajouter un **multiplicateur de combo** qui augmente quand le joueur enchaîne les notes correctes.

#### 2.5. Résultat renvoyé

- Score total.
- Nombre de notes correctes / ratées.
- XP + monnaies selon la performance.

---

### 3. Mini‑jeu Équitation — Runner infini

**Fichier de scène** : `scenes/riding.py`

#### 3.1. Règles de base

- Le cheval avance automatiquement.
- Le joueur peut :
  - **sauter** (touche, ex : Espace),
  - **se baisser** (touche, ex : flèche bas).
- Obstacles divers : haies, fossés, branches basses, rochers.
- La partie se termine après 3 collisions (3 “vies”).

#### 3.2. Représentation

- Position du cheval : `(x, y)` (x souvent fixe, y variable).
- Obstacles :
  - type (haut/bas),
  - position x défilante,
  - hitbox (rectangle ou autre).

#### 3.3. Vitesse et difficulté

- Vitesse qui augmente avec le temps.
- Fréquence de spawn des obstacles qui augmente progressivement.

#### 3.4. Scoring

- Fonction du temps de survie.
- Option : points pour chaque obstacle évité.

#### 3.5. Résultat renvoyé

- Temps total de survie.
- Nombre d’obstacles évités.
- XP + monnaies en conséquence.

---

### 4. Mini‑jeu Cuisine — FSM séquentielle

**Fichier de scène** : `scenes/cooking.py`  
**Données** : `assets/data/recipes.json`

#### 4.1. Règles de base

- Le jeu affiche une recette avec une séquence d’étapes.
- Le joueur doit reproduire cette séquence :
  - sélectionner les bons ingrédients,
  - effectuer les bonnes actions (couper, mélanger, cuire),
  - dans le temps imparti.

#### 4.2. Machine à états (FSM)

États possibles :

- `SHOW_RECIPE` : affiche la recette pour mémorisation.
- `SELECT_INGREDIENT` : attente de sélection.
- `PERFORM_ACTION` : animation / feedback de l’action.
- `VALIDATE_STEP` : vérifie si l’étape est correcte.
- `NEXT_DISH` ou `END` : passage à la recette suivante ou fin de partie.

Chaque recette est décrite par sa liste de `steps` dans `recipes.json`.

#### 4.3. Scoring

- Basé sur :
  - nombre d’étapes réussies sur le total,
  - respect du temps (bonus de vitesse),
  - pénalités en cas d’erreurs.

#### 4.4. Résultat renvoyé

- Score par recette et score global.
- XP + monnaies selon la qualité globale de la session.

---

### 5. Mini‑jeu Studio — Création et scoring pondéré

**Fichier de scène** : `scenes/studio.py`  
**Données** : `assets/data/items.json` (catégories de vêtements/décors)

#### 5.1. Règles de base

- Le joueur reçoit un thème (ex : “Tenue d’été”, “Look de soirée”).
- Il doit choisir :
  - une robe, un haut, un bas, des accessoires, etc.
- Le jeu calcule un **score créatif** selon plusieurs critères.

#### 5.2. Critères de scoring (rappel GDD)

- Cohérence thématique.
- Harmonie des couleurs.
- Originalité (utilisation d’items rares).
- Complétude (slots remplis).

Chaque critère donne un sous‑score (0–100), puis on calcule un score global pondéré.

#### 5.3. Résultat renvoyé

- Score créatif final (0–100).
- Si score > 90, possibilité de sauvegarder la création dans un “Portfolio”.
- XP + monnaies, éventuellement Étoiles bonus pour les très bonnes créations.

---

### 6. Checklist de fin d’étape

Tu dois pouvoir :

1. Décrire pour chaque mini‑jeu :
   - les contrôles,
   - le flow de partie,
   - les données nécessaires (JSON ou non),
   - ce que contient le résultat renvoyé au système global.
2. Montrer que tu réutilises les mêmes **idées d’architecture** :
   - une scène par mini‑jeu,
   - un contrat de résultat,
   - des systèmes globaux partagés (XP, économie, sauvegarde).

---

### 7. Notes personnelles / questions

- …

