import pygame
import sys
import math
import random

pygame.init()

# ─────────────────────────────────────────────
#  FENÊTRE
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Aearon Reforged")

# ─────────────────────────────────────────────
#  RESSOURCES
# ─────────────────────────────────────────────
background = pygame.image.load("img/bg.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

title = pygame.image.load("img/Aearon txt.png").convert_alpha()
title = pygame.transform.scale(title, (400, 400))

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 100))

retour_img     = pygame.transform.scale(
    pygame.image.load("img/retour.png").convert_alpha(), (256, 50)
)
retour_img_dim = retour_img.copy()
retour_img_dim.set_alpha(180)

title_jouer   = pygame.transform.scale(
    pygame.image.load("img/jouer.png").convert_alpha(), (400, 80)
)
title_options = pygame.transform.scale(
    pygame.image.load("img/options.png").convert_alpha(), (400, 80)
)

# ─────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────
font_large = pygame.font.SysFont("couriernew", 36, bold=True)
font_med   = pygame.font.SysFont("couriernew", 24)
font_small = pygame.font.SysFont("couriernew", 18)

version_text = font_small.render("v0.1 — Early Access", True, (140, 210, 190))

# ─────────────────────────────────────────────
#  COULEURS
# ─────────────────────────────────────────────
GOLD       = (80,  200, 160)
TEXT_COLOR = (140, 210, 190)
GRAY       = (80,  100, 95)
WHITE      = (255, 255, 255)

# ─────────────────────────────────────────────
#  GAME STATE
# ─────────────────────────────────────────────
class GameState:
    MENU     = "menu"
    PLAY     = "play"
    MULTI    = "multi"
    OPTIONS  = "options"
    CONTROLS = "controls"

state = GameState.MENU

# ─────────────────────────────────────────────
#  FONDU
# ─────────────────────────────────────────────
fade_alpha   = 255
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))

# ─────────────────────────────────────────────
#  PARTICULES
# ─────────────────────────────────────────────
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x     = random.randint(0, WIDTH)
        self.y     = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.3, 1.2)
        self.size  = random.randint(1, 3)
        self.alpha = random.randint(60, 180)

    def update(self):
        self.y -= self.speed
        self.x += math.sin(pygame.time.get_ticks() / 1000 + self.y) * 0.4
        if self.y < 0:
            self.reset()
            self.y = HEIGHT

    def draw(self, surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x, self.y))

particles = [Particle() for _ in range(60)]

# ─────────────────────────────────────────────
#  BOUTON IMAGE
# ─────────────────────────────────────────────
class Button:
    def __init__(self, img_path, center_y, action, size=(256, 50)):
        self.action = action
        self.image  = pygame.transform.scale(
            pygame.image.load(img_path).convert_alpha(), size
        )
        self.rect       = self.image.get_rect(center=(WIDTH // 2, center_y))
        self.img_normal = self.image.copy()
        self.img_normal.set_alpha(180)

    def draw(self, is_selected):
        if is_selected:
            w, h   = self.image.get_size()
            scaled = pygame.transform.scale(self.image, (int(w * 1.07), int(h * 1.07)))
            screen.blit(scaled, scaled.get_rect(center=self.rect.center))
        else:
            screen.blit(self.img_normal, self.rect)

# ─────────────────────────────────────────────
#  BOUTONS MENU PRINCIPAL
# ─────────────────────────────────────────────
buttons = [
    Button("img/jouer.png",   400, "new"),
    Button("img/options.png", 470, "options"),
    Button("img/quitter.png", 540, "quit"),
]
selected_btn = 0

# ─────────────────────────────────────────────
#  BOUTONS ÉCRAN JOUER
# ─────────────────────────────────────────────
play_buttons = [
    Button("img/solo.png",  HEIGHT // 2 - 40, "solo",  size=(380, 70)),
    Button("img/multi.png", HEIGHT // 2 + 60, "multi", size=(380, 70)),
]
play_selected = 0   # 0 Solo | 1 Multi | 2 Retour

# ─────────────────────────────────────────────
#  SLIDER
# ─────────────────────────────────────────────
class Slider:
    def __init__(self, label, x, y, width, min_val, max_val, value):
        self.label    = label
        self.x        = x
        self.y        = y
        self.width    = width
        self.min_val  = min_val
        self.max_val  = max_val
        self.value    = value
        self.dragging = False
        self.track_rect  = pygame.Rect(x, y + 18, width, 6)
        self.handle_rect = pygame.Rect(0, y + 10, 20, 22)
        self._update_handle()

    def _update_handle(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = int(self.x + ratio * self.width)
        self.handle_rect.y       = self.y + 10

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])

    def adjust(self, delta):
        self.value = max(self.min_val, min(self.max_val, self.value + delta))
        self._update_handle()

    def _set_from_mouse(self, mx):
        ratio      = max(0, min(1, (mx - self.x) / self.width))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        self._update_handle()

    def draw(self, surface, is_selected=False):
        color      = GOLD if is_selected else GRAY
        label_surf = font_med.render(f"{self.label} : {int(self.value)}%", True, TEXT_COLOR)
        surface.blit(label_surf, (self.x, self.y - 30))
        pygame.draw.rect(surface, GRAY,  self.track_rect,  border_radius=3)
        filled = pygame.Rect(self.x, self.y + 18, self.handle_rect.centerx - self.x, 6)
        pygame.draw.rect(surface, color, filled,            border_radius=3)
        pygame.draw.rect(surface, color, self.handle_rect,  border_radius=4)

slider_music = Slider("Volume musique", WIDTH // 2 - 400, 220, 800, 0, 100, 80)

# ─────────────────────────────────────────────
#  CONTRÔLES CONFIGURABLES
# ─────────────────────────────────────────────
ACTIONS = ["Haut", "Bas", "Gauche", "Droite", "Attaque", "Interaction"]
controls = {
    "Haut":        pygame.K_UP,
    "Bas":         pygame.K_DOWN,
    "Gauche":      pygame.K_LEFT,
    "Droite":      pygame.K_RIGHT,
    "Attaque":     pygame.K_SPACE,
    "Interaction": pygame.K_e,
}
waiting_for_key = None

def key_name(k):
    name = pygame.key.name(k)
    return name.upper() if len(name) == 1 else name.capitalize()

# ─────────────────────────────────────────────
#  OPTIONS — indices
# ─────────────────────────────────────────────
OPT_MUSIC    = 0
OPT_CTRL     = 1
OPT_BACK     = 2
opt_selected  = OPT_MUSIC
ctrl_selected = 0

# ─────────────────────────────────────────────
#  MULTI — état
# ─────────────────────────────────────────────
# multi_selected : 0 = Héberger | 1 = Rentrer un code | 2 = Retour (pied de page)
multi_selected  = 0
code_input      = ""      # texte saisi par le joueur
saisie_active   = False   # True quand le champ de saisie est ouvert
is_hosting      = False
ip              = "ip_address"
# ─────────────────────────────────────────────
#  ZONE CLIQUABLE PIED DE PAGE (partagée)
# ─────────────────────────────────────────────
FOOTER_BACK_RECT = pygame.Rect(60, HEIGHT - 75, 256, 50)

# ─────────────────────────────────────────────
#  HELPERS DE RENDU
# ─────────────────────────────────────────────
def draw_fullscreen_bg():
    dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dark.fill((4, 8, 6, 245))
    screen.blit(background, (0, 0))
    screen.blit(dark, (0, 0))

def draw_title_img(img):
    screen.blit(img, img.get_rect(center=(WIDTH // 2, 65)))
    pygame.draw.line(screen, GOLD,
                     (WIDTH // 2 - 300, 115),
                     (WIDTH // 2 + 300, 115), 1)

def draw_title_text(text):
    t = font_large.render(text, True, GOLD)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 45))
    pygame.draw.line(screen, GOLD,
                     (WIDTH // 2 - 300, 95),
                     (WIDTH // 2 + 300, 95), 1)

def draw_footer(is_selected):
    pygame.draw.line(screen, GOLD, (60, HEIGHT - 90), (WIDTH - 60, HEIGHT - 90), 1)
    if is_selected:
        scaled = pygame.transform.scale(retour_img, (int(256 * 1.07), int(50 * 1.07)))
        screen.blit(scaled, scaled.get_rect(midleft=(60, HEIGHT - 50)))
    else:
        screen.blit(retour_img_dim, retour_img_dim.get_rect(midleft=(60, HEIGHT - 50)))

def draw_hint(text):
    hint = font_small.render(text, True, GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 28))

# ─────────────────────────────────────────────
#  ÉCRANS
# ─────────────────────────────────────────────
def draw_play():
    draw_fullscreen_bg()
    draw_title_img(title_jouer)

    for i, btn in enumerate(play_buttons):
        btn.draw(i == play_selected)

    draw_footer(play_selected == 2)
    draw_hint("↑↓ naviguer   Entrée valider   Échap retour")


def draw_multi():
    draw_fullscreen_bg()
    draw_title_text("MULTIJOUEUR")
    cx = WIDTH // 2

    # ── Option Héberger ──────────────────────
    heberg_color = GOLD if multi_selected == 0 else TEXT_COLOR
    heberg_surf  = font_large.render("Héberger une partie", True, heberg_color)
    heberg_y     = HEIGHT // 2 - 90
    screen.blit(heberg_surf, (cx - heberg_surf.get_width() // 2, heberg_y))
    if multi_selected == 0:
        pygame.draw.line(screen, GOLD,
                         (cx - heberg_surf.get_width() // 2, heberg_y + heberg_surf.get_height() + 2),
                         (cx + heberg_surf.get_width() // 2, heberg_y + heberg_surf.get_height() + 2), 1)

    # ── Boîte IP (visible uniquement si on héberge) ──
    if is_hosting:
        box_w, box_h = 520, 100
        box_x = cx - box_w // 2
        box_y = HEIGHT // 2 - 30
        pygame.draw.rect(screen, (10, 20, 16), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, GOLD,         (box_x, box_y, box_w, box_h), 2, border_radius=8)
        label = font_small.render("En attente d'un joueur…", True, GRAY)
        screen.blit(label, (cx - label.get_width() // 2, box_y + 12))
        ip_surf = font_large.render(f"IP : {ip}", True, GOLD)
        screen.blit(ip_surf, (cx - ip_surf.get_width() // 2, box_y + 44))

        # ── Option Rentrer un code ────────────────
    code_color = GOLD if multi_selected == 1 else TEXT_COLOR
    code_label = font_large.render("Rentrer un code", True, code_color)
    code_y = HEIGHT // 2 + 110 if is_hosting else HEIGHT // 2  # ← décalage si hosting
    screen.blit(code_label, (cx - code_label.get_width() // 2, code_y))
    if multi_selected == 1:
        pygame.draw.line(screen, GOLD,
                         (cx - code_label.get_width() // 2, code_y + code_label.get_height() + 2),
                         (cx + code_label.get_width() // 2, code_y + code_label.get_height() + 2), 1)

    # ── Champ de saisie ───
    if saisie_active:
        field_y = code_y + 60
        field_w = 500
        field_h = 52
        field_x = cx - field_w // 2
        field_y = HEIGHT // 2 + 80

        # Fond du champ
        pygame.draw.rect(screen, (10, 20, 16),
                         (field_x, field_y, field_w, field_h), border_radius=6)
        pygame.draw.rect(screen, GOLD,
                         (field_x, field_y, field_w, field_h), 2, border_radius=6)

        # Curseur clignotant
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        display_text = code_input + ("|" if blink else " ")
        txt_surf = font_large.render(display_text, True, GOLD)
        screen.blit(txt_surf, (field_x + 16, field_y + field_h // 2 - txt_surf.get_height() // 2))

        # Label au-dessus
        label = font_small.render("Entrez le code de la partie :", True, GRAY)
        screen.blit(label, (field_x, field_y - 26))

        hint_txt = "Entrée : valider   Échap : annuler"
    else:
        hint_txt = "↑↓ naviguer   Entrée valider   Échap retour"

    draw_footer(multi_selected == 2)
    draw_hint(hint_txt)



def draw_options():
    draw_fullscreen_bg()
    draw_title_img(title_options)

    slider_music.x     = WIDTH // 2 - 400
    slider_music.y     = 220
    slider_music.width = 800
    slider_music.track_rect = pygame.Rect(slider_music.x, slider_music.y + 18, slider_music.width, 6)
    slider_music._update_handle()
    slider_music.draw(screen, opt_selected == OPT_MUSIC)

    ctrl_color = GOLD if opt_selected == OPT_CTRL else TEXT_COLOR
    ctrl_surf  = font_large.render("Configurer les controles", True, ctrl_color)
    screen.blit(ctrl_surf, (WIDTH // 2 - ctrl_surf.get_width() // 2, 370))

    draw_footer(opt_selected == OPT_BACK)
    draw_hint("↑↓ naviguer   ←→ modifier   Entrée valider   Échap retour")


def draw_controls():
    draw_fullscreen_bg()
    draw_title_text("CONTRÔLES")

    col_left  = WIDTH // 2 - 250
    col_right = WIDTH // 2 + 80

    screen.blit(font_small.render("ACTION", True, GRAY), (col_left,  110))
    screen.blit(font_small.render("TOUCHE", True, GRAY), (col_right, 110))
    pygame.draw.line(screen, GRAY, (col_left - 10, 132), (col_right + 150, 132), 1)

    for i, action in enumerate(ACTIONS):
        y       = 145 + i * 50
        is_sel  = (i == ctrl_selected)
        is_wait = (waiting_for_key == action)
        color   = GOLD if is_sel else TEXT_COLOR

        if is_sel:
            hl = pygame.Surface((col_right - col_left + 160, 38), pygame.SRCALPHA)
            hl.fill((80, 200, 160, 28))
            screen.blit(hl, (col_left - 10, y - 4))

        screen.blit(font_med.render(action, True, color), (col_left, y))

        if is_wait:
            key_s = font_med.render("[ Appuie sur une touche... ]", True, (255, 220, 80))
        else:
            key_s = font_med.render(key_name(controls[action]), True, color)
        screen.blit(key_s, (col_right, y))

        pygame.draw.line(screen, (60, 80, 75),
                         (col_left - 10, y + 38),
                         (col_right + key_s.get_width() + 10, y + 38), 1)

    draw_footer(ctrl_selected == len(ACTIONS))
    draw_hint("↑↓ naviguer   Entrée : rebind   Échap retour")


# ─────────────────────────────────────────────
#  HANDLE ACTION MENU
# ─────────────────────────────────────────────
def handle_action(action):
    global state, running
    if action == "new":
        state = GameState.PLAY
    elif action == "options":
        state = GameState.OPTIONS
    elif action == "quit":
        running = False

# ─────────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ─────────────────────────────────────────────
fullscreen = True
running    = True
clock      = pygame.time.Clock()
debug      = False

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ── Rebind en attente ─────────────────
        elif waiting_for_key and event.type == pygame.KEYDOWN:
            if event.key != pygame.K_ESCAPE:
                controls[waiting_for_key] = event.key
            waiting_for_key = None

        # ── Saisie de code multijoueur ────────
        elif saisie_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print(f"Code de partie : {code_input}")
                saisie_active = False
                code_input = ""
            elif event.key == pygame.K_ESCAPE:
                saisie_active = False
                code_input = ""
            elif event.key == pygame.K_BACKSPACE:
                code_input = code_input[:-1]
            elif event.key == pygame.K_UP:
                saisie_active = False
                code_input = ""
                multi_selected = 0
            elif event.key == pygame.K_DOWN:
                saisie_active = False
                code_input = ""
                multi_selected = 2
            else:
                if len(code_input) < 20:
                    code_input += event.unicode

        elif event.type == pygame.KEYDOWN:

            # ── Touches globales ──────────────
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                flag = (pygame.FULLSCREEN | pygame.SCALED) if fullscreen else pygame.SCALED
                screen = pygame.display.set_mode((WIDTH, HEIGHT), flag)

            elif event.key == pygame.K_F3:
                debug = not debug

            elif event.key == pygame.K_ESCAPE:
                if saisie_active:
                    saisie_active = False
                    code_input = ""
                elif is_hosting:
                    is_hosting = False
                elif state == GameState.CONTROLS:
                    state = GameState.OPTIONS
                elif state == GameState.MULTI:
                    is_hosting = False
                    state = GameState.PLAY
                elif state in (GameState.OPTIONS, GameState.PLAY):
                    state = GameState.MENU
                elif state == GameState.MENU:
                    running = False

            # ── Menu ──────────────────────────
            elif state == GameState.MENU:
                if event.key == pygame.K_DOWN:
                    selected_btn = (selected_btn + 1) % len(buttons)
                elif event.key == pygame.K_UP:
                    selected_btn = (selected_btn - 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    handle_action(buttons[selected_btn].action)

            # ── Jouer ─────────────────────────
            elif state == GameState.PLAY:
                if event.key == pygame.K_DOWN:
                    play_selected = (play_selected + 1) % 3
                elif event.key == pygame.K_UP:
                    play_selected = (play_selected - 1) % 3
                elif event.key == pygame.K_RETURN:
                    if play_selected == 0:
                        print("Lancement Solo"); pygame.quit(); sys.exit()
                    elif play_selected == 1:
                        state = GameState.MULTI
                    elif play_selected == 2:
                        state = GameState.MENU

            # ── Multi ─────────────────────────
            elif state == GameState.MULTI:
                if event.key == pygame.K_DOWN:
                    multi_selected = (multi_selected + 1) % 3
                elif event.key == pygame.K_UP:
                    multi_selected = (multi_selected - 1) % 3
                elif event.key == pygame.K_RETURN:
                    if multi_selected == 0:
                        is_hosting = True
                        saisie_active = False
                        code_input = ""
                    elif multi_selected == 1:
                        saisie_active = True
                        is_hosting = False
                        code_input = ""
                    elif multi_selected == 2:
                        is_hosting = False
                        saisie_active = False
                        state = GameState.PLAY

            # ── Options ───────────────────────
            elif state == GameState.OPTIONS:
                if event.key == pygame.K_DOWN:
                    opt_selected = (opt_selected + 1) % 3
                elif event.key == pygame.K_UP:
                    opt_selected = (opt_selected - 1) % 3
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if opt_selected == OPT_MUSIC:
                        slider_music.adjust(5 if event.key == pygame.K_RIGHT else -5)
                elif event.key == pygame.K_RETURN:
                    if opt_selected == OPT_CTRL:
                        state = GameState.CONTROLS
                    elif opt_selected == OPT_BACK:
                        state = GameState.MENU

            # ── Contrôles ─────────────────────
            elif state == GameState.CONTROLS:
                nb = len(ACTIONS) + 1
                if event.key == pygame.K_DOWN:
                    ctrl_selected = (ctrl_selected + 1) % nb
                elif event.key == pygame.K_UP:
                    ctrl_selected = (ctrl_selected - 1) % nb
                elif event.key == pygame.K_RETURN:
                    if ctrl_selected == len(ACTIONS):
                        state = GameState.OPTIONS
                    else:
                        waiting_for_key = ACTIONS[ctrl_selected]

        # ── Clics souris ──────────────────────
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if state == GameState.MENU:
                for btn in buttons:
                    if btn.rect.collidepoint(event.pos):
                        handle_action(btn.action)

            elif state == GameState.PLAY:
                for i, btn in enumerate(play_buttons):
                    if btn.rect.collidepoint(event.pos):
                        play_selected = i
                        if i == 0:
                            print("Lancement Solo"); pygame.quit(); sys.exit()
                        elif i == 1:
                            state = GameState.MULTI
                if FOOTER_BACK_RECT.collidepoint(event.pos):
                    state = GameState.MENU

            elif state == GameState.MULTI:
                cx = WIDTH // 2
                heberg_surf = font_large.render("Héberger une partie", True, GOLD)
                heberg_rect = heberg_surf.get_rect(center=(cx, HEIGHT // 2 - 90 + heberg_surf.get_height() // 2))
                code_surf = font_large.render("Rentrer un code", True, GOLD)
                code_y = HEIGHT // 2 + 110 if is_hosting else HEIGHT // 2
                code_rect = code_surf.get_rect(center=(cx, code_y + code_surf.get_height() // 2))
                if heberg_rect.collidepoint(event.pos):
                    multi_selected = 0
                    is_hosting = True
                    saisie_active = False
                    code_input = ""
                elif code_rect.collidepoint(event.pos):
                    multi_selected = 1
                    saisie_active = True
                    is_hosting = False
                    code_input = ""
                elif FOOTER_BACK_RECT.collidepoint(event.pos):
                    is_hosting = False
                    saisie_active = False
                    code_input = ""
                    state = GameState.PLAY

            elif state == GameState.OPTIONS:
                ctrl_rect = pygame.Rect(WIDTH // 2 - 250, 360, 500, 44)
                if ctrl_rect.collidepoint(event.pos):
                    state = GameState.CONTROLS
                if FOOTER_BACK_RECT.collidepoint(event.pos):
                    state = GameState.MENU

            elif state == GameState.CONTROLS:
                col_left = WIDTH // 2 - 260
                for i, action in enumerate(ACTIONS):
                    y = 145 + i * 50
                    if pygame.Rect(col_left, y - 4, 500, 40).collidepoint(event.pos):
                        ctrl_selected   = i
                        waiting_for_key = action
                if FOOTER_BACK_RECT.collidepoint(event.pos):
                    state = GameState.OPTIONS

        # Slider souris
        if state == GameState.OPTIONS:
            slider_music.handle_event(event)

    # ─────────────────────────────────────────
    #  RENDU
    # ─────────────────────────────────────────
    if state == GameState.MENU:
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))

        for p in particles:
            p.update()
            p.draw(screen)

        for i, btn in enumerate(buttons):
            if btn.rect.collidepoint(mouse_pos):
                selected_btn = i

        offset_y = int(math.sin(pygame.time.get_ticks() / 600) * 6)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30 + offset_y))

        for i, btn in enumerate(buttons):
            btn.draw(i == selected_btn)

        screen.blit(version_text, (20, HEIGHT - 30))

    elif state == GameState.PLAY:
        for i, btn in enumerate(play_buttons):
            if btn.rect.collidepoint(mouse_pos):
                play_selected = i
        draw_play()

    elif state == GameState.MULTI:
        draw_multi()

    elif state == GameState.OPTIONS:
        draw_options()

    elif state == GameState.CONTROLS:
        draw_controls()

    # Fondu au démarrage
    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
        fade_alpha -= 4

    # Debug FPS
    if debug:
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (WIDTH - 80, 10))

    pygame.display.flip()

pygame.quit()
print("Fermeture du jeu")
