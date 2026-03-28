## Étape 3 — Systèmes globaux : XP, économie, inventaire, sauvegarde

> **But de ce document**  
> Définir précisément les “services” centraux de ton jeu : progression, monnaies, inventaire, sauvegarde.

---

### 1. Objectif pédagogique de l’étape

- Comprendre que ces systèmes sont **indépendants des mini‑jeux**.
- Apprendre à décrire une **API de module** (fonctions, données, responsabilités).
- Faire le lien direct entre les **formules mathématiques** du GDD et le code.

---

### 2. EconomyManager — Système économique

**Fichier concerné** : `systems/economy_manager.py`

- **Données gérées** :
  - `coins` (Pièces)
  - `stars` (Étoiles)
  - `crowns` (Couronnes)

- **Opérations prévues** (en pseudo‑fonctions) :
  - `add_coins(amount)`
  - `add_stars(amount)`
  - `add_crowns(amount)`
  - `get_balances()` → retourne un dictionnaire avec les trois monnaies.
  - `can_afford(cost)` → vérifie si le joueur a assez de ressources pour un achat.
  - `spend(cost)` → retire les monnaies nécessaires (si possible).

- **Sources de revenus** :
  - Chaque mini‑jeu donne un certain nombre de Pièces / Étoiles / XP (voir tableau du GDD §8.2).
  - L’EconomyManager n’a pas besoin de connaître les détails du mini‑jeu, seulement **le résultat** qu’on lui transmet.

> **Idée clé**  
> Toutes les modifications de monnaies **passent par ce module**, pour éviter les incohérences.

---

### 3. XPManager — Progression et niveaux

**Fichier concerné** : `systems/xp_manager.py`

- **Données gérées** :
  - `level` (niveau actuel)
  - `xp` (expérience actuelle)
  - éventuellement `total_xp` (XP cumulée historique).

- **Formule de progression** (GDD) :
  - \(XP_{requise}(n) = 100 + 50 \times n\)

- **Fonctions prévues** :
  - `add_xp(source, amount)` : ajoute de l’XP (source = mini‑jeu ou événement).
  - `get_level()` / `get_xp()`.
  - `get_required_xp_for_next_level()`.
  - `check_level_up()` :
    - vérifie si l’XP dépasse le seuil,
    - augmente le niveau autant que nécessaire,
    - renvoie éventuellement une liste de déblocages.

- **Déblocages possibles** :
  - Nouveaux items,
  - Nouvelles difficultés,
  - Contenu du Hub, etc.  
  (cf. tableau du GDD §7.2).

---

### 4. Inventory — Objets possédés et équipés

**Fichier concerné** : `systems/inventory.py`

- **Données gérées** :
  - Liste d’IDs d’items possédés : `["dress_01", "hat_03", ...]`.
  - Équipement actuel :
    - `equipped = { "head": "hat_03", "dress": "dress_01", "accessory": "necklace_02" }`.

- **Fonctions prévues** :
  - `add_item(item_id)` : ajoute un objet à l’inventaire.
  - `has_item(item_id)` : vérifie la possession.
  - `equip(slot, item_id)` : équipe un item sur un slot donné (si possédé).
  - `get_equipped()` : retourne l’état actuel de l’équipement.

- **Lien avec EconomyManager et XPManager** :
  - Certains items sont achetés avec des monnaies.
  - Certains items sont débloqués automatiquement à certains niveaux.

---

### 5. SaveManager — Sauvegarde et chargement

**Fichier concerné** : `systems/save_manager.py`

- **Format de sauvegarde** :
  - Inspiré du JSON du GDD §11.4, par exemple :

```json
{
  "player_level": 5,
  "player_xp": 230,
  "coins": 450,
  "stars": 12,
  "crowns": 2,
  "inventory": ["dress_01", "hat_03", "accessory_07"],
  "equipped": {
    "head": "hat_03",
    "dress": "dress_01",
    "accessory": "accessory_07"
  },
  "unlocked_content": ["hub_fountain", "piano_advanced"],
  "minigame_scores": {
    "xo": 85,
    "golf": 72,
    "piano": 91,
    "riding": 64,
    "cooking": 78,
    "studio": 88
  }
}
```

- **Fonctions prévues** :
  - `save_game(global_state_dict)` :
    - reçoit un dictionnaire représentant l’état du jeu,
    - l’écrit dans un fichier JSON (par ex. `save.json`).
  - `load_game()` :
    - lit le fichier JSON,
    - renvoie un dictionnaire avec les données.
  - Gestion de backup :
    - possibilité de créer `save_backup.json` avant d’écraser la sauvegarde principale.

- **Quand sauvegarder ?** (idées)
  - À chaque retour au Hub.
  - Lors d’un achat important.
  - Lors d’un changement de niveau.

---

### 6. Diagramme simple d’interaction des systèmes

```text
[Mini-jeu] --(résultat : score, xp, monnaies)--> [Game]

[Game] --(add_xp)------------------> [XPManager]
[Game] --(add_coins/stars/crowns)--> [EconomyManager]
[Game] --(add_item/equip)----------> [Inventory]

[Game] --(sauvegarder)-------------> [SaveManager] --(écrit JSON)-->
```

**À retenir** :  
Les mini‑jeux eux‑mêmes ne parlent **pas directement** à la sauvegarde ni à l’économie.  
Ils renvoient un **résultat** que `Game` et les `systems/` interprètent.

---

### 7. Checklist de fin d’étape

Tu dois pouvoir :

1. Expliquer **ce que fait** chaque système (`EconomyManager`, `XPManager`, `Inventory`, `SaveManager`).
2. Montrer comment une victoire dans un mini‑jeu se transforme en :
   - XP gagnée,
   - monnaies gagnées,
   - sauvegarde mise à jour.
3. Dessiner un petit schéma fléché montrant le chemin :  
   `MiniJeu → Game → Systems → SaveManager`.

---

### 8. Notes personnelles / questions

- …

