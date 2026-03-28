## Étape 9 — Intégration globale et sauvegardes

> **But de ce document**  
> Définir comment tous les éléments de Diva Land (Hub, mini‑jeux, systèmes globaux, sauvegarde) travaillent ensemble.

---

### 1. Objectif pédagogique de l’étape

- Voir le jeu comme un **système complet**, pas seulement une collection de mini‑jeux.
- Comprendre le chemin des données : du mini‑jeu jusqu’au fichier de sauvegarde.
- Préparer un comportement robuste en cas d’erreur (sauvegarde, retour menu, etc.).

---

### 2. Contrat de résultat d’un mini‑jeu

Tous les mini‑jeux renverront un **objet résultat** avec une structure similaire.  
Par exemple :

```text
{
  "minigame": "xo" / "golf" / "piano" / ...,
  "result": "win" / "lose" / "draw" / "success" / "fail",
  "score_raw": nombre,
  "score_normalized": nombre_de_0_a_100,
  "coins": nombre,
  "stars": nombre,
  "xp": nombre,
  "extra": { ... }  # infos spécifiques au mini‑jeu (facultatif)
}
```

**But** :  
`Game` n’a pas besoin de connaître les détails internes de chaque mini‑jeu, il sait seulement traiter ce résultat standard.

---

### 3. Enchaînement logique après une partie

1. Le mini‑jeu se termine et construit son `result_dict`.
2. `MiniGame*State` signale à `Game` que la partie est finie, en passant ce résultat.
3. `Game` appelle :
   - `XPManager.add_xp(result["minigame"], result["xp"])`
   - `EconomyManager.add_coins(result["coins"])`
   - `EconomyManager.add_stars(result["stars"])`
4. `Game` peut aussi mettre à jour :
   - meilleures performances dans une structure `minigame_scores`.
5. `Game` demande à `SaveManager.save_game(...)` de sauvegarder l’état.
6. `Game` change d’état vers :
   - un écran `ResultState` (affiche score, récompenses, etc.), puis
   - retour au `HubState`.

---

### 4. Contenu de l’état global du jeu

Avant sauvegarde, `Game` doit assembler un **état global** (un gros dictionnaire) contenant :

- Infos joueur :
  - niveau, xp, xp cumulée,
  - monnaies (coins, stars, crowns).
- Inventaire :
  - items possédés,
  - items équipés.
- Déblocages :
  - contenu débloqué (items, décos de Hub, difficultés de mini‑jeux).
- Scores :
  - meilleurs scores par mini‑jeu.

Cet état global est ensuite transmis à `SaveManager.save_game(state_dict)`.

---

### 5. Flux “Chargement d’une partie”

Au lancement du jeu :

1. `Game` appelle `SaveManager.load_game()`.
2. Si une sauvegarde existe :
   - `XPManager`, `EconomyManager`, `Inventory` et autres systèmes se mettent à jour en fonction des données chargées.
3. Sinon :
   - démarrer une nouvelle partie avec des valeurs par défaut.

But : le joueur retrouve **son Hub**, ses **décos**, ses **niveaux** et ses **monnaies**.

---

### 6. Gestion d’erreurs basique

Quelques cas à prévoir (au niveau conceptuel) :

- Fichier de sauvegarde introuvable :
  - commencer une nouvelle partie.
- Fichier corrompu :
  - tenter de charger une **sauvegarde de secours** (backup),
  - sinon, informer l’utilisateur et démarrer une partie neuve.

> Même si tu n’implémentes pas toutes ces protections, montrer que tu y as pensé est très positif pour un projet académique.

---

### 7. Exemple de scénario complet

**Scénario : le joueur lance XO, gagne, et revient au Hub.**

1. Depuis le Hub, clic sur portail XO → `Game` passe en `MiniGameXOState`.
2. Le joueur joue, gagne :
   - XO calcule `result_dict` (score, coins, xp…).
3. XO signale la fin à `Game` avec ce `result_dict`.
4. `Game` :
   - met à jour XP et monnaies via les `systems/`,
   - met à jour les meilleurs scores,
   - appelle `SaveManager.save_game(...)`.
5. `Game` passe à `ResultState` :
   - affiche les scores et récompenses,
   - propose “Rejouer” ou “Retour Hub”.
6. Si “Retour Hub” :
   - `Game` passe en `HubState`.
   - Le Hub affiche le nouveau niveau/XP/monnaies.

---

### 8. Checklist de fin d’étape

Tu dois pouvoir :

1. Expliquer ce qu’est un **contrat de résultat** de mini‑jeu.
2. Tracer le chemin “données” :
   - `Mini-jeu → Game → Systems → SaveManager → Fichier`.
3. Décrire au moins un scénario complet comme celui ci‑dessus, en détaillant qui fait quoi.

---

### 9. Notes personnelles / questions

- …

