## Étape 6 — Mini‑jeu XO : logique, IA et intégration

> **But de ce document**  
> Spécifier complètement le mini‑jeu XO (morpion) comme un “laboratoire” pour apprendre Pygame et l’intégration dans Diva Land.

---

### 1. Objectif pédagogique de l’étape

- Comprendre comment concevoir un mini‑jeu **de A à Z** : règles, interface, IA, scoring.
- Apprendre à **intégrer** un mini‑jeu dans l’architecture globale (états, systèmes globaux).
- Se familiariser avec la gestion de la souris et d’une grille 2D.

---

### 2. Règles et déroulement d’une partie

Résumé des règles (adapté du GDD) :

- Plateau 3×3.
- Le joueur joue les **“X”**, l’IA joue les **“O”**.
- Les joueurs jouent à tour de rôle.
- Conditions de fin :
  - Victoire : aligner 3 symboles horizontalement, verticalement ou en diagonale.
  - Match nul : plateau rempli sans alignement de 3.

**Flow d’une partie** :

```text
Initialisation du plateau vide
Choix de la difficulté IA (Facile / Moyen / Difficile)

Répéter tant que la partie n'est pas terminée :
    - Si c'est au tour du joueur :
        attendre un clic sur une case valide
        placer un "X"
    - Si c'est au tour de l'IA :
        calculer le meilleur coup selon le niveau de difficulté
        placer un "O"
    - Vérifier si un joueur a gagné ou si le plateau est plein

Afficher le résultat (Victoire / Défaite / Nul)
Calculer score, Pièces, XP
Retourner le résultat au système global
```

---

### 3. Représentation des données (grille et état)

**Grille** :

- Représentée en Python par :
  - une liste de listes 3×3 : `grid[row][col]`,
  - ou une liste simple de 9 cases : `cells[0..8]`.
- Valeurs possibles :
  - `0` = vide
  - `1` = joueur (X)
  - `2` = IA (O)

**Autres variables d’état** :

- `current_player` : `"player"` ou `"ai"`.
- `game_over` : booléen.
- `winner` : `None`, `"player"`, `"ai"`, `"draw"`.

---

### 4. Interface utilisateur (XO en Pygame)

**Affichage de la grille** :

- La fenêtre XO contiendra :
  - Fond uni ou image légère.
  - Grille 3×3 dessinée avec des lignes (`pygame.draw.line`).
  - X et O dessinés soit avec :
    - du texte (police Pygame),
    - ou des sprites.

**Interaction souris** :

- Lors d’un clic :
  - Convertir la position du clic (x, y) en indices de case `(row, col)`.
  - Vérifier que la case est **vide**.
  - Si oui, placer un `X` et passer au tour de l’IA.

**Feedback** :

- Survol possible (facultatif) : surbrillance de la case.
- Message de fin de partie : texte centré (Victoire / Défaite / Nul).

---

### 5. IA : 3 niveaux de difficulté

**Niveau Facile (aléatoire)** :

- Algorithme :
  - Lister toutes les cases vides.
  - Choisir une case au hasard.
- Comportement :
  - Aucune stratégie, facile à battre.

**Niveau Moyen (heuristique)** :

- Algorithme (en français) :
  1. Si l’IA peut gagner en un coup, jouer ce coup.
  2. Sinon, si le joueur peut gagner en un coup, bloquer ce coup.
  3. Sinon, jouer une case “intelligente” :
     - centre si libre, sinon un coin, sinon une case quelconque.

**Niveau Difficile (minimax simplifié)** :

- Algorithme (idée générale) :
  - Simuler tous les coups possibles jusqu’à une certaine profondeur.
  - Évaluer le plateau :
    - +score si l’IA gagne,
    - –score si le joueur gagne,
    - 0 pour nul.
  - Choisir le coup qui maximise les chances de l’IA.
- Simplification :
  - Limiter la profondeur (par exemple ne pas explorer 100% de l’arbre si ce n’est pas nécessaire).

> **But pédagogique**  
> Tu montres au jury que tu sais appliquer un **algorithme d’IA** simple, avec plusieurs niveaux de difficulté.

---

### 6. Scoring et récompenses

Rappel du GDD :

| Résultat   | Pièces | XP |
|-----------|--------|----|
| Victoire  | 30     | 50 |
| Match nul | 15     | 25 |
| Défaite   | 10     | 10 |

Au moment où la partie se termine, le mini‑jeu XO doit produire une **structure de résultat**, par exemple :

```text
{
  "minigame": "xo",
  "result": "win" / "draw" / "lose",
  "score_raw": ...,
  "score_normalized": ...,
  "coins": ...,
  "stars": 0,
  "xp": ...
}
```

Ce résultat sera :

- utilisé par `EconomyManager` (Pièces),
- utilisé par `XPManager` (XP),
- éventuellement stocké par `SaveManager` (meilleurs scores).

---

### 7. Intégration XO ↔ architecture globale

**Entrée** :

- XO est lancé depuis le Hub (`HubState`) lorsque le joueur clique sur le portail XO.
- L’état de jeu change vers `MiniGameXOState`.

**Sortie** :

- À la fin, XO renvoie son `result_dict` à `Game`.
- `Game` appelle :
  - `XPManager.add_xp(...)`,
  - `EconomyManager.add_coins(...)`, etc.
- `Game` change d’état vers `ResultState` ou directement vers le `HubState` selon ta conception.

---

### 8. Checklist de fin d’étape

Tu dois pouvoir :

1. Expliquer le déroulement complet d’une partie de XO **en termes de variables** (grille, current_player, winner…).
2. Décrire simplement les 3 IA (Facile / Moyen / Difficile).
3. Dire comment XO se connecte au reste du jeu (résultats → systèmes globaux → sauvegarde).

---

### 9. Notes personnelles / questions

- …

