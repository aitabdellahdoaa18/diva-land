## Étape 2 — Boucle de jeu Pygame et gestion des états

> **But de ce document**  
> Décrire clairement comment fonctionnera la boucle principale Pygame et le système d’états (écrans) de ton jeu Diva Land.

---

### 1. Objectif pédagogique de l’étape

- Comprendre le schéma classique d’un jeu 2D : **événements → mise à jour → rendu**.
- Savoir organiser ton code autour d’une **classe `Game`** et de **classes d’états** (`GameState`).
- Relier ce système à la **machine à états** décrite dans le GDD (navigation Hub / mini‑jeux / résultats).

---

### 2. Vue générale de la boucle de jeu

La boucle principale sera gérée par une classe `Game` (dans `core/game.py`).

Pseudo-code (en français) :

```text
initialiser pygame
créer la fenêtre
créer une horloge pour gérer les FPS
initialiser l'état courant (par ex. MenuState)

tant que le jeu tourne :
    récupérer les événements pygame
    les transmettre à l'état courant (handle_events)
    calculer dt (delta time = temps écoulé depuis la frame précédente)
    appeler update(dt) sur l'état courant
    demander à l'état courant de dessiner sur l'écran (render)
    rafraîchir l'affichage (pygame.display.flip)
    limiter la boucle à une fréquence stable (clock.tick(FPS))
```

Idée clé : **`Game` ne connaît pas les détails internes de XO, Golf, etc.**  
Il délègue tout au **GameState courant**.

---

### 3. La classe de base `GameState`

Dans `core/states.py`, tu définiras une classe abstraite (ou de base) :

- Attributs typiques :
  - une référence vers l’objet `Game` (pour pouvoir demander un changement d’état, accéder aux systèmes, etc.).
- Méthodes que chaque état devra redéfinir :
  - `handle_events(events)` : traite les entrées clavier/souris.
  - `update(dt)` : met à jour la logique du jeu.
  - `render(surface)` : dessine l’état sur la surface d’affichage.

**But pédagogique** :  
Tous les écrans du jeu partagent cette même interface, ce qui simplifie le code de `Game`.

---

### 4. Liste des états-écrans prévus

Tu peux prévoir par exemple :

- `MenuState` : menu principal.
- `HubState` : Jardin Royal (hub central).
- États de mini‑jeux :
  - `MiniGameXOState`
  - `MiniGameGolfState`
  - `MiniGamePianoState`
  - `MiniGameRidingState`
  - `MiniGameCookingState`
  - `MiniGameStudioState`
- `ResultState` : écran de résultats après un mini‑jeu.

> Remarque :  
> Tu peux regrouper les mini‑jeux dans une classe générique `MiniGameState` + des sous‑classes, mais ce n’est pas obligatoire. L’important est de **savoir qui dessine quoi** et **qui gère quelle logique**.

---

### 5. Diagramme des transitions entre états

Tu peux représenter le flux principal ainsi :

```text
[MenuState] --(Nouvelle Partie / Charger)--> [HubState]

[HubState] --(Portail XO)------------------> [MiniGameXOState]
[HubState] --(Portail Golf)----------------> [MiniGameGolfState]
[HubState] --(Portail Piano)---------------> [MiniGamePianoState]
[HubState] --(Portail Équitation)----------> [MiniGameRidingState]
[HubState] --(Portail Cuisine)-------------> [MiniGameCookingState]
[HubState] --(Portail Studio)--------------> [MiniGameStudioState]

[MiniGame*State] --(Fin de partie)---------> [ResultState]
[ResultState] --(Retour au Hub)------------> [HubState]

[HubState] --(Retour Menu)-----------------> [MenuState]
```

Idée : **seul `Game` peut changer l’état courant**, mais la demande vient souvent de l’état actif (par exemple le mini‑jeu qui signale qu’il est terminé).

---

### 6. Communication entre `Game` et les états

- `Game` possède :
  - une instance de l’état courant : `self.current_state`.
  - une méthode pour changer d’état : `change_state(new_state)`.
- Un état (par exemple `MiniGameXOState`) peut demander au `Game` de changer d’état, par exemple quand :
  - la partie est finie → aller vers `ResultState`.
  - le joueur quitte → revenir au `HubState`.

**Message important** :  
Tu évites les “import circulaires” et le chaos en centralisant les transitions d’états dans `Game`.

---

### 7. Checklist de fin d’étape

Tu dois pouvoir :

1. Expliquer **verbalement** ce qui se passe entre deux frames (events → update → render).
2. Nommer les **états principaux** de ton jeu et leur rôle.
3. Décrire comment on passe :
   - du Menu au Hub,
   - du Hub à un mini‑jeu,
   - d’un mini‑jeu à l’écran de résultats,
   - puis retour au Hub.

---

### 8. Notes personnelles / questions

> Utilise cette section pour noter les choses floues (par ex. : différence entre `Game` et `GameState`, gestion du temps `dt`, etc.).

- …

