# ============================================================
#  fichier : scenes/studio_creatif.py
#  mini-jeu : Studio Créatif — Jeu de Mémoire Royal
#  mécanique : retourner des paires de cartes mode/bijoux
#  récompense : couronnes rares selon le score et la vitesse
#  auteure   : Doaa  |  jeu : DivaLandByDoaa
# ============================================================

import pygame    # bibliothèque principale pour affichage, événements, sons
import random    # pour mélanger les cartes à chaque partie
import math      # pour les animations (sin, cos)
import os        # pour construire les chemins des fichiers


# ─────────────────────────────────────────────────────────────
#  PALETTE DE COULEURS
# ─────────────────────────────────────────────────────────────

ROSE_PALE   = (255, 182, 213)    # fond doux de l'atelier
ROSE_VIF    = (255, 105, 180)    # titres, boutons principaux
VIOLET      = (180, 100, 220)    # dos des cartes, accents
VIOLET_CLAIR= (220, 180, 255)    # survol des cartes
OR          = (255, 215,   0)    # couronnes, paires trouvées
OR_FONCE    = (200, 160,   0)    # contour des paires validées
BLANC       = (255, 255, 255)    # textes sur fond coloré
NOIR        = (  0,   0,   0)    # contours et ombres légères
VERT_SUCCES = ( 80, 200, 120)    # flash quand une paire est trouvée
ROUGE_ECHEC = (220,  80,  80)    # flash quand les cartes ne matchent pas


# ─────────────────────────────────────────────────────────────
#  CONFIGURATION DU JEU
# ─────────────────────────────────────────────────────────────

COLS        = 4      # nombre de colonnes dans la grille
ROWS        = 4      # nombre de lignes dans la grille
NB_CARTES   = COLS * ROWS    # 16 cartes = 8 paires
CARTE_W     = 110    # largeur d'une carte en pixels
CARTE_H     = 130    # hauteur d'une carte en pixels
CARTE_MARGE = 14     # espace entre les cartes

# Position du coin haut-gauche de la grille (centrée sur 800x600)
GRILLE_X = (800 - (COLS * (CARTE_W + CARTE_MARGE))) // 2
GRILLE_Y = 110

DUREE_AFFICHAGE = 0.9    # secondes avant de recouvrir les cartes ratées
DUREE_FLASH     = 0.35   # secondes du flash vert/rouge

# Récompenses couronnes selon les erreurs
COURONNES_PARFAIT = 7    # 0 erreur
COURONNES_BIEN    = 4    # 1-3 erreurs
COURONNES_MOYEN   = 2    # 4-6 erreurs
COURONNES_MIN     = 1    # 7+ erreurs

# 8 symboles de mode (une paire par symbole)
SYMBOLES = ["Robe", "Couronne", "Collier", "Sac",
            "Chaussure", "Bague", "Chapeau", "Miroir"]

# Couleur de fond unique par symbole
COULEURS_SYMBOLES = {
    "Robe"     : (255, 180, 210),
    "Couronne" : (255, 230, 100),
    "Collier"  : (180, 230, 255),
    "Sac"      : (200, 255, 200),
    "Chaussure": (255, 200, 160),
    "Bague"    : (220, 180, 255),
    "Chapeau"  : (255, 160, 160),
    "Miroir"   : (200, 240, 230),
}


# ─────────────────────────────────────────────────────────────
#  CLASSE CARTE
# ─────────────────────────────────────────────────────────────

class Carte:
    """
    Représente une carte individuelle dans la grille de mémoire.
    Gère son affichage (face ou dos), son animation de flip,
    et son état (retournée, validée, flash).
    """

    def __init__(self, symbole: str, col: int, row: int):
        """
        Crée une carte à sa position dans la grille.

        Paramètres :
            symbole → nom de l'objet de mode ("Robe", "Couronne"...)
            col     → colonne dans la grille (0 à COLS-1)
            row     → ligne dans la grille (0 à ROWS-1)
        """
        self.symbole = symbole    # identité de la carte pour trouver la paire

        # Calcul du rectangle à l'écran selon la position dans la grille
        x = GRILLE_X + col * (CARTE_W + CARTE_MARGE)
        y = GRILLE_Y + row * (CARTE_H + CARTE_MARGE)
        self.rect = pygame.Rect(x, y, CARTE_W, CARTE_H)

        # États de la carte
        self.retournee = False    # True = face visible (symbole affiché)
        self.validee   = False    # True = paire trouvée, reste visible définitivement
        self.flash     = None     # "succes" | "echec" | None

        # Animation de retournement
        self.anim_flip    = 0.0     # progression 0.0 → 1.0
        self.en_animation = False   # True pendant le flip

    def contient(self, pos) -> bool:
        """Retourne True si le point (x,y) est dans le rectangle de la carte."""
        return self.rect.collidepoint(pos)

    def demarrer_flip(self):
        """Lance l'animation de retournement."""
        self.en_animation = True
        self.anim_flip    = 0.0

    def update(self, dt: float):
        """
        Avance l'animation de flip.

        Paramètre :
            dt → delta time en secondes
        """
        if self.en_animation:
            self.anim_flip += dt / 0.25    # durée du flip = 0.25 secondes
            if self.anim_flip >= 1.0:
                self.anim_flip    = 1.0
                self.en_animation = False

    def draw(self, screen: pygame.Surface, font_sym, font_petit):
        """
        Dessine la carte sur l'écran.
        - Dos violet avec losange si face cachée
        - Fond coloré + symbole si face visible
        - Flash vert/rouge temporaire si résultat en cours

        Paramètres :
            screen     → surface pygame principale
            font_sym   → police du grand symbole
            font_petit → police du texte secondaire
        """
        # ── Calcul de la largeur animée (simulation de flip horizontal) ──
        if self.en_animation:
            # 1ère moitié : rétrécissement (1.0 → 0.0)
            # 2ème moitié : agrandissement (0.0 → 1.0)
            if self.anim_flip < 0.5:
                scale_x = 1.0 - self.anim_flip * 2
            else:
                scale_x = (self.anim_flip - 0.5) * 2
        else:
            scale_x = 1.0

        largeur_anim = max(2, int(CARTE_W * scale_x))
        offset_x     = (CARTE_W - largeur_anim) // 2
        rect_anim    = pygame.Rect(self.rect.x + offset_x, self.rect.y,
                                   largeur_anim, CARTE_H)

        # ── Choix face/dos pendant l'animation ───────────────────────
        montrer_face = self.retournee or self.validee
        if self.en_animation and self.anim_flip < 0.5:
            montrer_face = not montrer_face    # on inverse en première moitié

        if montrer_face:
            # ── FACE : fond coloré + symbole ──────────────────────────
            couleur = COULEURS_SYMBOLES.get(self.symbole, BLANC)
            pygame.draw.rect(screen, couleur, rect_anim, border_radius=12)

            # Contour doré si validée, violet sinon
            contour = OR_FONCE if self.validee else VIOLET
            epaisseur = 3 if self.validee else 2
            pygame.draw.rect(screen, contour, rect_anim, epaisseur, border_radius=12)

            # Flash de résultat
            if self.flash == "succes" and largeur_anim > 10:
                s = pygame.Surface((largeur_anim, CARTE_H), pygame.SRCALPHA)
                s.fill((*VERT_SUCCES, 120))
                screen.blit(s, rect_anim.topleft)
            elif self.flash == "echec" and largeur_anim > 10:
                s = pygame.Surface((largeur_anim, CARTE_H), pygame.SRCALPHA)
                s.fill((*ROUGE_ECHEC, 120))
                screen.blit(s, rect_anim.topleft)

            # Symbole texte centré
            if largeur_anim > 30:
                sym = font_sym.render(self.symbole[:5], True, NOIR)
                screen.blit(sym, (
                    rect_anim.centerx - sym.get_width() // 2,
                    rect_anim.centery - sym.get_height() // 2 - 8,
                ))
                sub = font_petit.render(self.symbole, True, (80, 60, 100))
                screen.blit(sub, (
                    rect_anim.centerx - sub.get_width() // 2,
                    rect_anim.centery + sym.get_height() // 2 - 4,
                ))

            # Étoile dorée en haut à gauche si validée
            if self.validee and largeur_anim > 20:
                star = font_petit.render("*", True, OR_FONCE)
                screen.blit(star, (rect_anim.x + 5, rect_anim.y + 4))

        else:
            # ── DOS : fond violet + losange décoratif ─────────────────
            pygame.draw.rect(screen, VIOLET, rect_anim, border_radius=12)
            pygame.draw.rect(screen, BLANC,  rect_anim, 2, border_radius=12)

            if largeur_anim > 40:
                cx, cy  = rect_anim.centerx, rect_anim.centery
                taille  = min(largeur_anim // 3, 28)
                points  = [(cx, cy - taille), (cx + taille, cy),
                           (cx, cy + taille), (cx - taille, cy)]
                pygame.draw.polygon(screen, VIOLET_CLAIR, points)
                pygame.draw.polygon(screen, BLANC, points, 1)

                if largeur_anim > 50:
                    q = font_petit.render("?", True, BLANC)
                    screen.blit(q, (cx - q.get_width() // 2,
                                    cy - q.get_height() // 2))


# ─────────────────────────────────────────────────────────────
#  CLASSE PRINCIPALE DU MINI-JEU
# ─────────────────────────────────────────────────────────────

class StudioCreatifState:
    """
    Mini-jeu Studio Créatif : Jeu de Mémoire Royal.

    Le joueur retourne 2 cartes à la fois.
    Même symbole → paire trouvée (cartes restent visibles).
    Symboles différents → les cartes se recouvrent après un délai.
    Victoire quand toutes les 8 paires sont trouvées.

    Interface publique attendue par game.py :
        handle_events(events)
        update(dt)
        render(screen)
    """

    def __init__(self, game):
        """
        Initialise le mini-jeu.

        Paramètre :
            game → objet Game principal (screen, economy, xp, sounds…)
        """
        self.game   = game
        self.screen = game.screen

        # Polices (SysFont = pas besoin de fichier .ttf externe)
        self.font_titre  = pygame.font.SysFont("Georgia", 34, bold=True)
        self.font_normal = pygame.font.SysFont("Georgia", 20)
        self.font_sym    = pygame.font.SysFont("Georgia", 22, bold=True)
        self.font_petit  = pygame.font.SysFont("Georgia", 13)

        # Création et mélange des cartes
        self.cartes = self._creer_cartes()    # liste de 16 objets Carte

        # Logique de jeu
        self.cartes_retournees = []    # max 2 cartes visibles à la fois
        self.nb_erreurs        = 0     # erreurs commises
        self.nb_paires_ok      = 0     # paires correctement trouvées
        self.paires_totales    = NB_CARTES // 2    # = 8

        # Timers
        self.timer_attente = 0.0     # décompte avant recouvrement
        self.en_attente    = False   # clics bloqués pendant l'attente
        self.timer_flash   = 0.0    # décompte du flash couleur
        self.en_flash      = False  # flash en cours

        # Chronomètre
        self.temps_ecoule = 0.0     # secondes depuis le début

        # Fin de jeu
        self.jeu_termine       = False
        self.couronnes_gagnees = 0
        self.anim_fin          = 0.0   # compteur pour animations de victoire

        # Boutons
        self.btn_quitter = pygame.Rect(20,  16, 130, 38)
        self.btn_rejouer = pygame.Rect(290, 460, 200, 50)
        self.btn_hub_fin = pygame.Rect(510, 460, 200, 50)

        # Flag retour Hub
        self.retour_hub = False

    # ─────────────────────────────────────────────────────────────────
    #  CRÉATION DES CARTES
    # ─────────────────────────────────────────────────────────────────

    def _creer_cartes(self) -> list:
        """
        Génère 16 cartes (2 par symbole = 8 paires) mélangées aléatoirement.

        Retourne :
            list de 16 objets Carte disposés en grille COLS × ROWS
        """
        symboles_doubles = SYMBOLES * 2    # chaque symbole apparaît 2 fois
        random.shuffle(symboles_doubles)   # mélange aléatoire

        cartes = []
        for index, symbole in enumerate(symboles_doubles):
            col = index % COLS      # colonne : 0,1,2,3,0,1,2,3,...
            row = index // COLS     # ligne   : 0,0,0,0,1,1,1,1,...
            cartes.append(Carte(symbole, col, row))
        return cartes

    # ─────────────────────────────────────────────────────────────────
    #  INTERFACE PUBLIQUE
    # ─────────────────────────────────────────────────────────────────

    def handle_events(self, events: list):
        """
        Traite les événements pygame (clics souris).
        Appelée par game.py avant update().
        """
        for event in events:
            self._gerer_evenement(event)

        if self.retour_hub:
            self._retourner_au_hub()

    def update(self, dt: float):
        """
        Met à jour la logique (timers, animations, fin de partie).
        Appelée par game.py après handle_events().

        Paramètre :
            dt → delta time en secondes
        """
        if self.jeu_termine:
            self.anim_fin += dt    # avance l'animation de célébration
            return

        self.temps_ecoule += dt    # chronomètre

        # Mise à jour des animations de chaque carte
        for carte in self.cartes:
            carte.update(dt)

        # Gestion du flash (vert ou rouge)
        if self.en_flash:
            self.timer_flash -= dt
            if self.timer_flash <= 0:
                # Flash terminé : on retire la couleur des cartes
                for carte in self.cartes_retournees:
                    carte.flash = None
                self.en_flash = False

        # Gestion de l'attente avant recouvrement
        if self.en_attente and not self.en_flash:
            self.timer_attente -= dt
            if self.timer_attente <= 0:
                self._recouvrir_cartes()
                self.en_attente = False

    def render(self, screen: pygame.Surface):
        """
        Dessine tout l'écran du mini-jeu.
        Appelée par game.py après update().

        Paramètre :
            screen → surface pygame principale (800 × 600)
        """
        self.screen = screen
        screen.fill(ROSE_PALE)
        pygame.draw.rect(screen, ROSE_VIF, pygame.Rect(0, 0, 800, 6))

        if self.jeu_termine:
            self._draw_grille(screen)
            self._draw_ecran_fin(screen)
        else:
            self._draw_hud(screen)
            self._draw_grille(screen)

    # ─────────────────────────────────────────────────────────────────
    #  GESTION DES ÉVÉNEMENTS
    # ─────────────────────────────────────────────────────────────────

    def _gerer_evenement(self, event):
        """
        Analyse un événement pygame et réagit aux clics gauche.

        Paramètre :
            event → pygame.event à analyser
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return    # on ne traite que les clics gauche

        pos = event.pos

        # Bouton Quitter
        if self.btn_quitter.collidepoint(pos):
            self.retour_hub = True
            return

        # Bouton Rejouer (écran de fin)
        if self.jeu_termine:
            if self.btn_rejouer.collidepoint(pos):
                self._reinitialiser()
                return
            if self.btn_hub_fin.collidepoint(pos):
                self.retour_hub = True
                return

        # Clic sur une carte (bloqué si on est en attente)
        if self.en_attente or self.en_flash:
            return

        for carte in self.cartes:
            if carte.contient(pos):
                self._cliquer_carte(carte)
                break

    def _cliquer_carte(self, carte: Carte):
        """
        Retourne une carte cliquée si elle est éligible.
        Vérifie la paire si c'est la 2ème carte retournée.

        Paramètre :
            carte → objet Carte cliqué
        """
        # Ignore si déjà validée, déjà visible, ou 2 cartes déjà retournées
        if carte.validee or carte.retournee:
            return
        if len(self.cartes_retournees) >= 2:
            return

        carte.retournee = True
        carte.demarrer_flip()
        self.cartes_retournees.append(carte)

        # Vérification de la paire si 2 cartes retournées
        if len(self.cartes_retournees) == 2:
            self._verifier_paire()

    def _verifier_paire(self):
        """
        Compare les 2 cartes retournées.
        Même symbole → paire validée (flash vert).
        Symboles différents → erreur (flash rouge, recouvrement).
        """
        c1, c2 = self.cartes_retournees[0], self.cartes_retournees[1]

        if c1.symbole == c2.symbole:
            # PAIRE TROUVÉE
            c1.flash   = "succes"
            c2.flash   = "succes"
            c1.validee = True
            c2.validee = True
            self.en_flash    = True
            self.timer_flash = DUREE_FLASH
            self.nb_paires_ok += 1

            try:
                self.game.sounds.play_ui_click()
            except Exception:
                pass

            # On vide les cartes_retournees après le flash
            self.en_attente    = True
            self.timer_attente = DUREE_FLASH + 0.1

        else:
            # PAS UNE PAIRE
            c1.flash   = "echec"
            c2.flash   = "echec"
            self.en_flash    = True
            self.timer_flash = DUREE_FLASH
            self.nb_erreurs += 1

            self.en_attente    = True
            self.timer_attente = DUREE_AFFICHAGE

    def _recouvrir_cartes(self):
        """
        Recouvre les cartes non-validées après l'attente.
        Vérifie si la partie est terminée.
        """
        for carte in self.cartes_retournees:
            if not carte.validee:
                carte.retournee = False
                carte.demarrer_flip()

        self.cartes_retournees = []

        # Toutes les paires trouvées ?
        if self.nb_paires_ok == self.paires_totales:
            self._terminer_jeu()

    def _terminer_jeu(self):
        """
        Calcule les récompenses et les crédite au joueur.
        Active l'écran de victoire.
        """
        # Couronnes selon les erreurs
        if self.nb_erreurs == 0:
            self.couronnes_gagnees = COURONNES_PARFAIT
        elif self.nb_erreurs <= 3:
            self.couronnes_gagnees = COURONNES_BIEN
        elif self.nb_erreurs <= 6:
            self.couronnes_gagnees = COURONNES_MOYEN
        else:
            self.couronnes_gagnees = COURONNES_MIN

        # XP bonus selon la vitesse (plus rapide = plus d'XP)
        xp_vitesse = max(50, 200 - int(self.temps_ecoule * 2))

        # Crédit dans les systèmes officiels du jeu
        try:
            self.game.economy.add_crowns(self.couronnes_gagnees)
            self.game.economy.add_coins(self.nb_paires_ok * 5)
            self.game.xp.add_xp(xp_vitesse)
        except Exception:
            pass

        self.jeu_termine = True
        self.anim_fin    = 0.0

    def _reinitialiser(self):
        """Remet le jeu à zéro pour une nouvelle partie."""
        self.cartes            = self._creer_cartes()
        self.cartes_retournees = []
        self.nb_erreurs        = 0
        self.nb_paires_ok      = 0
        self.timer_attente     = 0.0
        self.en_attente        = False
        self.timer_flash       = 0.0
        self.en_flash          = False
        self.temps_ecoule      = 0.0
        self.jeu_termine       = False
        self.couronnes_gagnees = 0
        self.anim_fin          = 0.0
        self.retour_hub        = False

    # ─────────────────────────────────────────────────────────────────
    #  DESSIN — HUD
    # ─────────────────────────────────────────────────────────────────

    def _draw_hud(self, screen: pygame.Surface):
        """
        Dessine la barre d'infos : titre, paires, erreurs, chrono, quitter.
        """
        # Titre centré
        titre = self.font_titre.render("Studio Creatif — Memoire Royale", True, ROSE_VIF)
        screen.blit(titre, (800 // 2 - titre.get_width() // 2, 12))

        # Paires trouvées
        txt_p = self.font_normal.render(
            f"Paires : {self.nb_paires_ok} / {self.paires_totales}", True, VIOLET)
        screen.blit(txt_p, (570, 20))

        # Erreurs (rouge si > 3)
        couleur_err = ROUGE_ECHEC if self.nb_erreurs > 3 else NOIR
        txt_e = self.font_normal.render(f"Erreurs : {self.nb_erreurs}", True, couleur_err)
        screen.blit(txt_e, (570, 46))

        # Chronomètre
        m = int(self.temps_ecoule) // 60
        s = int(self.temps_ecoule) % 60
        txt_t = self.font_normal.render(f"Temps : {m:01d}:{s:02d}", True, NOIR)
        screen.blit(txt_t, (570, 72))

        # Bouton Quitter
        pygame.draw.rect(screen, ROSE_VIF, self.btn_quitter, border_radius=10)
        pygame.draw.rect(screen, NOIR,     self.btn_quitter, 1, border_radius=10)
        txt_q = self.font_petit.render("< Retour Hub", True, BLANC)
        screen.blit(txt_q, (
            self.btn_quitter.centerx - txt_q.get_width() // 2,
            self.btn_quitter.centery - txt_q.get_height() // 2,
        ))

    # ─────────────────────────────────────────────────────────────────
    #  DESSIN — GRILLE DE CARTES
    # ─────────────────────────────────────────────────────────────────

    def _draw_grille(self, screen: pygame.Surface):
        """Dessine les 16 cartes de la grille."""
        for carte in self.cartes:
            carte.draw(screen, self.font_sym, self.font_petit)

    # ─────────────────────────────────────────────────────────────────
    #  DESSIN — ÉCRAN DE VICTOIRE
    # ─────────────────────────────────────────────────────────────────

    def _draw_ecran_fin(self, screen: pygame.Surface):
        """
        Overlay de victoire : couronnes gagnées, résumé, boutons.
        Animation de pulsation sur le texte des couronnes.
        """
        # Fond semi-transparent
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((255, 182, 213, 210))
        screen.blit(overlay, (0, 0))

        # Titre
        titre = self.font_titre.render("Bravo ! Toutes les paires trouvees !", True, ROSE_VIF)
        screen.blit(titre, (800 // 2 - titre.get_width() // 2, 95))

        # Couronnes avec pulsation
        pulse = 1.0 + 0.08 * math.sin(self.anim_fin * 5)
        font_c = pygame.font.SysFont("Georgia", int(36 * pulse), bold=True)
        txt_c  = font_c.render(
            f"+ {self.couronnes_gagnees} Couronne(s) Rare(s) !", True, OR)
        screen.blit(txt_c, (800 // 2 - txt_c.get_width() // 2, 165))

        # Étoiles clignotantes
        alpha = int(128 + 127 * math.sin(self.anim_fin * 3))
        etoiles = self.font_titre.render("* * * * * * * *", True, OR)
        etoiles.set_alpha(alpha)
        screen.blit(etoiles, (800 // 2 - etoiles.get_width() // 2, 225))

        # Résumé temps + erreurs
        m = int(self.temps_ecoule) // 60
        s = int(self.temps_ecoule) % 60
        resume = self.font_normal.render(
            f"Temps : {m:01d}:{s:02d}   |   Erreurs : {self.nb_erreurs}", True, NOIR)
        screen.blit(resume, (800 // 2 - resume.get_width() // 2, 285))

        # Message de performance
        if self.nb_erreurs == 0:
            msg, couleur_msg = "Performance PARFAITE ! Memoire de genie !", VERT_SUCCES
        elif self.nb_erreurs <= 3:
            msg, couleur_msg = "Tres bien ! Excellente memoire !", VIOLET
        elif self.nb_erreurs <= 6:
            msg, couleur_msg = "Bien joue ! Continue a t'entrainer !", (100, 100, 200)
        else:
            msg, couleur_msg = "Courage ! Tu feras mieux la prochaine fois !", (150, 80, 80)

        surf_msg = self.font_normal.render(msg, True, couleur_msg)
        screen.blit(surf_msg, (800 // 2 - surf_msg.get_width() // 2, 325))

        # Bouton Rejouer
        pygame.draw.rect(screen, VIOLET,   self.btn_rejouer, border_radius=14)
        pygame.draw.rect(screen, OR,       self.btn_rejouer, 3, border_radius=14)
        txt_r = self.font_normal.render("Rejouer", True, BLANC)
        screen.blit(txt_r, (
            self.btn_rejouer.centerx - txt_r.get_width() // 2,
            self.btn_rejouer.centery - txt_r.get_height() // 2,
        ))

        # Bouton Retour Hub
        pygame.draw.rect(screen, ROSE_VIF, self.btn_hub_fin, border_radius=14)
        pygame.draw.rect(screen, OR,       self.btn_hub_fin, 3, border_radius=14)
        txt_h = self.font_normal.render("Retour au Hub", True, BLANC)
        screen.blit(txt_h, (
            self.btn_hub_fin.centerx - txt_h.get_width() // 2,
            self.btn_hub_fin.centery - txt_h.get_height() // 2,
        ))

    # ─────────────────────────────────────────────────────────────────
    #  RETOUR AU HUB
    # ─────────────────────────────────────────────────────────────────

    def _retourner_au_hub(self):
        """
        Change l'état du jeu pour retourner au HubState.
        Import local pour éviter les imports circulaires.
        """
        from core.states import HubState
        self.game.change_state(HubState(self.game))


# ─────────────────────────────────────────────────────────────────────
#  INTÉGRATION DANS states.py — dans HubState._open_portal() :
#
#      if key == "studio":
#          from scenes.studio_creatif import StudioCreatifState
#          self.game.change_state(StudioCreatifState(self.game))
#          return
# ─────────────────────────────────────────────────────────────────────
