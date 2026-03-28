## Étape 7 — Mini‑jeu Golf : physique 2D et parcours

> **But de ce document**  
> Spécifier le mini‑jeu Golf pour apprendre la physique 2D simple, les collisions et un scoring basé sur la performance.

---

### 1. Objectif pédagogique de l’étape

- Manipuler des **vecteurs 2D** (position, vitesse).
- Comprendre friction, rebonds et trajectoires.
- Relier un système physique simple à un **système de scoring**.

---

### 2. Règles et déroulement d’une partie de Golf

- Le joueur voit un terrain avec :
  - une position de départ de la balle,
  - un trou (cible),
  - des obstacles (murs, bumpers, etc.).
- À chaque coup :
  - le joueur choisit un **angle** et une **force**,
  - la balle est lancée,
  - elle se déplace jusqu’à s’arrêter ou entrer dans le trou.
- Conditions de fin :
  - La balle est entrée dans le trou.
  - Eventuellement, nombre maximum de coups atteint.

---

### 3. Modèle physique simplifié

Tu travailles avec :

- **Position** de la balle : `(x, y)`.
- **Vitesse** : `(vx, vy)`.
- **Friction** : réduit la vitesse peu à peu.

Idée de mise à jour (conceptuelle) :

```text
position(t+1) = position(t) + vitesse(t) * dt
vitesse(t+1)  = vitesse(t) * (1 - friction)
si collision avec un mur :
    inverser la composante concernée de la vitesse (vx ou vy)
```

Les obstacles “rebondissants” (bumpers) peuvent multiplier la vitesse par un facteur (< 1 ou > 1 selon l’effet souhaité).

---

### 4. Choix de l’angle et de la force par le joueur

Plusieurs options possibles (à documenter ici) :

- **Option 1** : le joueur clique pour définir une direction (de la balle vers la souris), puis maintient pour charger la force.
- **Option 2** : le joueur utilise les touches gauche/droite pour régler l’angle, et une barre de puissance qui monte/descend pour la force.

Dans tous les cas :

- Angle → direction du vecteur vitesse.
- Force → norme initiale de la vitesse.

---

### 5. Parcours et obstacles (`golf_courses.json`)

Le mini‑jeu utilise les données décrites dans `golf_courses.json` :

- `start` : coordonnées de départ.
- `hole` : position et rayon d’un cercle.
- `obstacles` : liste d’objets, par exemple :
  - `type: "wall"` → rectangle solide.
  - `type: "bumper"` → cercle rebondissant.

Tu peux commencer par **un seul parcours simple**, puis en ajouter d’autres (jusqu’à 5 comme dans le GDD).

---

### 6. Scoring et multiplicateurs

Rappel du GDD :

| Performance          | Nom            | Multiplicateur |
|----------------------|----------------|----------------|
| 1 coup (Par -2)      | Albatros       | ×3             |
| 2 coups (Par -1)     | Eagle          | ×2             |
| 3 coups (Par)        | Par            | ×1             |
| 4 coups (Bogey)      | Bogey          | ×0,75          |
| 5 coups ou plus      | Double Bogey + | ×0,5           |

Idée de calcul :

1. Définir un **score de base** (par exemple basé sur le temps ou un score constant).
2. Calculer le nombre de coups utilisés.
3. Appliquer le multiplicateur correspondant.

Le résultat final sera ensuite **normalisé** et transformé en :

- Pièces gagnées,
- XP gagnée,
- éventuellement Étoiles si performance excellente.

---

### 7. Intégration Golf ↔ architecture globale

**Entrée** :

- L’état `MiniGameGolfState` est activé depuis le Hub.
- Il charge le parcours courant depuis `golf_courses.json`.

**Sortie** :

- À la fin, Golf produit un `result_dict` similaire à XO :

```text
{
  "minigame": "golf",
  "result": "success" / "fail",
  "strokes": nombre_de_coups,
  "score_raw": ...,
  "score_normalized": ...,
  "coins": ...,
  "stars": ...,
  "xp": ...
}
```

- `Game` transmet ensuite ces informations aux systèmes globaux (`XPManager`, `EconomyManager`, etc.).

---

### 8. Checklist de fin d’étape

Tu dois pouvoir :

1. Expliquer comment tu représentes la balle (position, vitesse) et comment tu mets à jour sa trajectoire.
2. Décrire un parcours simple (start, hole, mur) dans un schéma ou en JSON.
3. Expliquer le calcul du score et l’effet du nombre de coups sur les récompenses.

---

### 9. Notes personnelles / questions

- …

