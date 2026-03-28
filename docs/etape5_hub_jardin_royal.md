## Étape 5 — Conception du Hub : le Jardin Royal

> **But de ce document**  
> Spécifier précisément comment fonctionne le Hub (Jardin Royal) dans Diva Land, sur le plan technique et UX.

---

### 1. Objectif pédagogique de l’étape

- Traduire la description artistique du GDD en **comportement concret** dans le jeu.
- Définir **layout**, interactions et données nécessaires pour le Hub.
- Préparer le Hub comme “centre nerveux” reliant tous les systèmes.

---

### 2. Rôle du Hub dans Diva Land

Depuis le Jardin Royal, le joueur peut :

- Accéder aux **6 mini‑jeux**.
- Voir ses **monnaies** et son **niveau**.
- Gérer son **inventaire** (tenues, accessoires).
- Voir les **décorations** débloquées et l’évolution visuelle du jardin.

Le Hub est un **état** (par ex. `HubState`) qui utilise :

- des données venant de `XPManager`,
- des monnaies de `EconomyManager`,
- des items de `Inventory`.

---

### 3. Layout (disposition à l’écran)

Description textuelle possible :

- **Bandeau haut (HUD)** :
  - Avatar du joueur.
  - Niveau + barre d’XP.
  - Affichage des Pièces, Étoiles, Couronnes.

- **Zone centrale** :
  - Personnage de la diva (idle animation).
  - Décor du jardin (fond + décorations).
  - Portails/entrées des mini‑jeux (ex. 6 arches avec symboles).

- **Bandeau bas** :
  - Bouton “Inventaire”.
  - Bouton “Boutique”.
  - Bouton “Menu / Options”.

Tu peux dessiner un petit schéma ASCII si tu veux, comme dans le GDD.

---

### 4. Interactions utilisateur dans le Hub

Liste les interactions possibles :

- **Clic sur un portail de mini‑jeu** :
  - → demande au `Game` de changer d’état vers le mini‑jeu correspondant.
- **Clic sur “Inventaire”** :
  - → ouvre un sous‑écran d’inventaire (ou un état `InventoryState`).
- **Clic sur “Boutique”** :
  - → ouvre un sous‑écran de boutique.
- **Clic sur un bouton retour/menu** :
  - → retour au `MenuState` (facultatif pour la démo).

> Important :  
> Chaque interaction doit être rendue **visible** (hover, surbrillance, icône claire).

---

### 5. Données et systèmes utilisés par le Hub

Le Hub lit :

- Le **niveau** et l’**XP** via `XPManager`.
- Les **monnaies** via `EconomyManager`.
- Les **items équipés** (tenue de la diva) via `Inventory`.
- Les **décorations débloquées** via une liste d’IDs (dans la sauvegarde ou un système dédié).

Le Hub **ne modifie pas** directement les monnaies ou l’XP (sauf achats) :  
il affiche surtout l’état courant et permet de lancer des actions (mini‑jeux, achats, changements de tenue).

---

### 6. Évolution visuelle du Jardin

Relie cette partie à ton GDD :

- Plus le joueur progresse, plus :
  - il y a de **nouvelles décorations** visibles (fontaine, lumières, fleurs, etc.).
  - de **zones** peuvent s’ouvrir (sans forcément toutes les implémenter pour la démo).

Idée :  
Associer certains IDs d’items décoratifs (`hub_fountain`, `hub_flowerbed_1`, etc.) au **niveau minimum** pour les afficher dans le Hub.

---

### 7. Checklist de fin d’étape

Tu dois pouvoir :

1. Faire un dessin du Hub sur papier (HUD, portails, boutons).
2. Expliquer comment le Hub utilise les infos de XP, d’économie et d’inventaire.
3. Décrire textuellement ce qui se passe quand le joueur :
   - arrive dans le Hub,
   - lance un mini‑jeu,
   - revient du mini‑jeu avec des récompenses.

---

### 8. Notes personnelles / questions

- …

