import pygame
from sys import exit, argv
import random
import math
import os

PHONE_SIM = "--phone" in argv

pygame.init()
screen_info = pygame.display.Info()

if PHONE_SIM:
    # Simulate a typical smartphone screen (412×915 scaled to fit monitor)
    _monitor_h = screen_info.current_h
    SCREEN_H = int(_monitor_h * 0.9)           # 90% of monitor height
    SCREEN_W = int(SCREEN_H * 0.45)            # ~9:20 aspect ratio (modern phone)
    window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Flappy Bird — Shadow World [PHONE MODE]")
else:
    SCREEN_W = screen_info.current_w
    SCREEN_H = screen_info.current_h
    window = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
    pygame.display.set_caption("Flappy Bird — Shadow World")

clock = pygame.time.Clock()

FPS = 60

S = min(SCREEN_W, SCREEN_H)
IS_LANDSCAPE = SCREEN_W > SCREEN_H

if IS_LANDSCAPE:
    BIRD_W = max(int(S * 0.055), 20)
    BIRD_H = max(int(BIRD_W * 0.7), 14)
    BIRD_START_X = SCREEN_W // 2
    PIPE_W = max(int(S * 0.09), 40)
    PIPE_SPEED = max(int(S * 0.004), 2)
    PIPE_INTERVAL = 1500
else:
    BIRD_W = max(int(SCREEN_W * 0.11), 34)
    BIRD_H = max(int(BIRD_W * 0.7), 24)
    BIRD_START_X = SCREEN_W // 5
    PIPE_W = max(int(SCREEN_W * 0.15), 50)
    PIPE_SPEED = max(int(SCREEN_W * 0.007), 3)
    PIPE_INTERVAL = 1300

BIRD_START_Y = SCREEN_H // 2
PIPE_H = int(SCREEN_H * 0.8)
PIPE_GAP = int(SCREEN_H * 0.30)

GRAVITY = SCREEN_H * 0.00055
FLAP_STRENGTH = -SCREEN_H * 0.012

BUTTON_W = max(int(S * 0.25), 120)
BUTTON_H = max(int(S * 0.07), 36)

# Shadow World
GLOW_RADIUS = max(int(S * 0.22), 100)
GLOW_RADIUS_MIN = max(int(S * 0.11), 50)
GLOW_SHRINK_RATE = 0.004
DARKNESS_RATE = 0.5
DARKNESS_RATE_MAX = 1.2
MAX_DARKNESS = 180
FLASH_RELIEF = 30
SHADOW_START_SCORE = 4
PULSE_SPEED = 0.04
PULSE_AMPLITUDE = 15

background_image = pygame.image.load("Backgroundfull.png").convert()
background_image = pygame.transform.smoothscale(background_image, (SCREEN_W, SCREEN_H))

bird_image = pygame.image.load("flappybird.png").convert_alpha()
bird_image = pygame.transform.smoothscale(bird_image, (BIRD_W, BIRD_H))

_bird_raw = pygame.image.load("flappybird.png").convert_alpha()
_splash_bird_w = max(int(S * 0.14), 60)
_splash_bird_h = max(int(_splash_bird_w * 0.7), 42)
splash_bird_img = pygame.transform.smoothscale(_bird_raw, (_splash_bird_w, _splash_bird_h))
_splash_glow_r = int(_splash_bird_w * 1.2)
_splash_glow_diam = _splash_glow_r * 2
splash_bird_glow = pygame.Surface((_splash_glow_diam, _splash_glow_diam), pygame.SRCALPHA)
for r in range(_splash_glow_r, 0, -1):
    t = r / _splash_glow_r
    a = int(50 * (1 - t ** 1.5))
    pygame.draw.circle(splash_bird_glow, (255, 220, 80, a), (_splash_glow_r, _splash_glow_r), r)

top_pipe_image = pygame.image.load("toppipe.png").convert_alpha()
top_pipe_image = pygame.transform.smoothscale(top_pipe_image, (PIPE_W, PIPE_H))

bottom_pipe_image = pygame.image.load("bottompipe.png").convert_alpha()
bottom_pipe_image = pygame.transform.smoothscale(bottom_pipe_image, (PIPE_W, PIPE_H))

# Dark mode parallax layers
CITY_BG_DIR = os.path.join("free-scrolling-city-backgrounds-pixel-art", "1 Backgrounds", "1", "Night")
PARALLAX_SPEEDS = [0.1, 0.25, 0.5, 0.75, 1.0]
dark_layers = []
dark_scroll_x = [0.0] * 5

for i in range(1, 6):
    img_path = os.path.join(CITY_BG_DIR, f"{i}.png")
    img = pygame.image.load(img_path).convert_alpha()
    img = pygame.transform.smoothscale(img, (SCREEN_W, SCREEN_H))
    dark_layers.append(img)

ICON_SIZE = max(int(S * 0.05), 32) if IS_LANDSCAPE else max(int(SCREEN_W * 0.11), 40)
ICON_PAD = max(int(ICON_SIZE * 0.10), 3)
ICON_OUTER = ICON_SIZE + ICON_PAD * 2
ICON_MARGIN = max(int(S * 0.018), 10)

toggle_img_raw = pygame.image.load("day-and-night.png").convert_alpha()
toggle_img = pygame.transform.smoothscale(toggle_img_raw, (ICON_SIZE, ICON_SIZE))
toggle_btn = pygame.Rect(
    SCREEN_W - ICON_OUTER - ICON_MARGIN,
    ICON_MARGIN,
    ICON_OUTER,
    ICON_OUTER,
)
dark_mode = False

pause_img_raw = pygame.image.load("pause.png").convert_alpha()
pause_img = pygame.transform.smoothscale(pause_img_raw, (ICON_SIZE, ICON_SIZE))
play_img_raw = pygame.image.load("play-buttton.png").convert_alpha()
play_img = pygame.transform.smoothscale(play_img_raw, (ICON_SIZE, ICON_SIZE))
pause_btn = pygame.Rect(
    SCREEN_W - (ICON_OUTER + ICON_MARGIN) * 2,
    ICON_MARGIN,
    ICON_OUTER,
    ICON_OUTER,
)
game_paused = False

volume_img_raw = pygame.image.load("volume.png").convert_alpha()
volume_img = pygame.transform.smoothscale(volume_img_raw, (ICON_SIZE, ICON_SIZE))
settings_btn = pygame.Rect(ICON_MARGIN, ICON_MARGIN, ICON_OUTER, ICON_OUTER)
settings_open = False
music_enabled = True
sfx_enabled = True

_panel_w = max(int(S * 0.22), 140)
_panel_h = max(int(S * 0.14), 80)
_panel_x = ICON_MARGIN
_panel_y = ICON_MARGIN + ICON_OUTER + max(int(S * 0.008), 4)
settings_panel = pygame.Rect(_panel_x, _panel_y, _panel_w, _panel_h)

_row_h = _panel_h // 2
music_toggle_rect = pygame.Rect(_panel_x, _panel_y, _panel_w, _row_h)
sfx_toggle_rect   = pygame.Rect(_panel_x, _panel_y + _row_h, _panel_w, _row_h)

SOUND_DIR = os.path.join(os.path.dirname(__file__), "FlappySound")
pygame.mixer.init()

sfx_flap    = pygame.mixer.Sound(os.path.join(SOUND_DIR, "flap.mp3"))
sfx_point   = pygame.mixer.Sound(os.path.join(SOUND_DIR, "point.mp3"))
sfx_hit     = pygame.mixer.Sound(os.path.join(SOUND_DIR, "flappy-bird-hit-sound.mp3"))
sfx_die     = pygame.mixer.Sound(os.path.join(SOUND_DIR, "die.mp3"))
sfx_swoosh  = pygame.mixer.Sound(os.path.join(SOUND_DIR, "swoosh.mp3"))

_vol_flap = 0.4
_vol_point = 0.6
_vol_hit = 0.7
_vol_die = 0.7
_vol_swoosh = 0.5
sfx_flap.set_volume(_vol_flap)
sfx_point.set_volume(_vol_point)
sfx_hit.set_volume(_vol_hit)
sfx_die.set_volume(_vol_die)
sfx_swoosh.set_volume(_vol_swoosh)

def apply_sfx_volume():
    mult = 1.0 if sfx_enabled else 0.0
    sfx_flap.set_volume(_vol_flap * mult)
    sfx_point.set_volume(_vol_point * mult)
    sfx_hit.set_volume(_vol_hit * mult)
    sfx_die.set_volume(_vol_die * mult)
    sfx_swoosh.set_volume(_vol_swoosh * mult)

def apply_music_volume():
    pygame.mixer.music.set_volume(0.3 if music_enabled else 0.0)

_bgm_day   = [os.path.join(SOUND_DIR, f) for f in ("2-bgm-1.mp3", "3-bgm-2.mp3")]
_bgm_night = [os.path.join(SOUND_DIR, f) for f in ("4-bgm-3.mp3", "5-bgm-4.mp3", "6-bgm-5.mp3")]
_current_bgm = None

def play_bgm(force_restart=False):
    global _current_bgm
    pool = _bgm_night if dark_mode else _bgm_day
    pick = random.choice(pool)
    if pick == _current_bgm and not force_restart:
        return
    _current_bgm = pick
    pygame.mixer.music.load(pick)
    pygame.mixer.music.set_volume(0.3 if music_enabled else 0.0)
    pygame.mixer.music.play(-1)

def stop_bgm():
    global _current_bgm
    pygame.mixer.music.fadeout(500)
    _current_bgm = None

# Glow mask (half-res for performance)
_SHADOW_SCALE = 2
_half_w = SCREEN_W // _SHADOW_SCALE
_half_h = SCREEN_H // _SHADOW_SCALE
_glow_radius_half = GLOW_RADIUS // _SHADOW_SCALE
_glow_diam = _glow_radius_half * 2
_glow_center = _glow_diam // 2
glow_mask = pygame.Surface((_glow_diam, _glow_diam), pygame.SRCALPHA)
glow_mask.fill((0, 0, 0, 255))
for r in range(_glow_center, 0, -1):
    t = r / _glow_center
    a = int(255 * (t ** 1.8))
    pygame.draw.circle(glow_mask, (0, 0, 0, a), (_glow_center, _glow_center), r)

_glow_cache = {}
def _get_scaled_glow(diam):
    if diam not in _glow_cache:
        _glow_cache[diam] = pygame.transform.scale(glow_mask, (diam, diam))
    return _glow_cache[diam]

# Bird aura glow
_aura_radius = max(int(BIRD_W * 2.5), 40)
_aura_diam = _aura_radius * 2
_aura_center = _aura_diam // 2
bird_aura = pygame.Surface((_aura_diam, _aura_diam), pygame.SRCALPHA)
for r in range(_aura_center, 0, -1):
    t = r / _aura_center
    a = int(30 * (1 - t ** 1.5))
    pygame.draw.circle(bird_aura, (255, 220, 120, a), (_aura_center, _aura_center), r)

_dark_surf = pygame.Surface((_half_w, _half_h), pygame.SRCALPHA)



MEDAL_THRESHOLDS = [
    (30, "PLATINUM", (200, 230, 255)),
    (20, "GOLD",     (255, 215, 0)),
    (10, "SILVER",   (200, 200, 210)),
    (5,  "BRONZE",   (205, 127, 50)),
]

def get_medal(sc):
    for threshold, name, color in MEDAL_THRESHOLDS:
        if sc >= threshold:
            return name, color
    return None

font_big = pygame.font.SysFont("Arial", max(int(S * 0.07), 28), bold=True)
font_score_pop = pygame.font.SysFont("Arial", max(int(S * 0.10), 40), bold=True)
font_medium = pygame.font.SysFont("Arial", max(int(S * 0.05), 22), bold=True)
font_title = pygame.font.SysFont("Arial", max(int(S * 0.09), 36), bold=True)
font_button = pygame.font.SysFont("Arial", max(int(S * 0.04), 18), bold=True)
font_small = pygame.font.SysFont("Arial", max(int(S * 0.032), 16))

_pop_font_cache = {}
_base_pop_h = font_big.get_height()
SCORE_POP_DURATION = 15
for _frac in range(0, SCORE_POP_DURATION + 1):
    _t = _frac / SCORE_POP_DURATION
    _sc = 1.0 + 0.4 * _t
    _sz = int(_base_pop_h * _sc)
    if _sz not in _pop_font_cache:
        _pop_font_cache[_sz] = pygame.font.SysFont("Arial", _sz, bold=True)


class Bird(pygame.Rect):
    def __init__(self, img):
        super().__init__(BIRD_START_X, BIRD_START_Y, BIRD_W, BIRD_H)
        self.img = img
        self.vel_y = 0.0

    def flap(self):
        self.vel_y = FLAP_STRENGTH
        sfx_flap.play()

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.y = max(self.y, 0)

    _rot_cache = {}

    def draw(self, surface, show_aura=False, dying=False, death_spin=0):
        if show_aura:
            ax = int(self.centerx - _aura_diam // 2)
            ay = int(self.centery - _aura_diam // 2)
            surface.blit(bird_aura, (ax, ay))

        if dying:
            angle = death_spin
        else:
            angle = max(-25, min(15, -self.vel_y * 3))
        angle_key = round(angle / 2) * 2
        if angle_key not in Bird._rot_cache:
            Bird._rot_cache[angle_key] = pygame.transform.rotate(self.img, angle_key)
        rotated = Bird._rot_cache[angle_key]
        rect = rotated.get_rect(center=self.center)
        surface.blit(rotated, rect)


class Pipe(pygame.Rect):
    def __init__(self, img, x, y):
        super().__init__(x, y, PIPE_W, PIPE_H)
        self.img = img
        self.passed = False


bird = Bird(bird_image)
pipes: list[Pipe] = []
score = 0
best_score = 0
game_over = False
game_started = False
show_splash = True

dying = False
death_timer = 0.0
death_spin = 0.0
DEATH_DURATION = 60

shake_x = 0
shake_y = 0
shake_timer = 0
SHAKE_DURATION = 18
SHAKE_INTENSITY = max(int(S * 0.025), 12)

score_pop_timer = 0.0
last_displayed_score = 0

darkness = 0.0
shadow_active = False

create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, PIPE_INTERVAL)

restart_button = pygame.Rect(
    (SCREEN_W - BUTTON_W) // 2,
    SCREEN_H // 2 + int(S * 0.09),
    BUTTON_W,
    BUTTON_H,
)


def reset_game():
    global score, game_over, game_started, darkness, shadow_active
    global dying, death_timer, death_spin, score_pop_timer, last_displayed_score, show_splash
    global shake_timer, shake_x, shake_y, game_paused
    bird.x, bird.y = BIRD_START_X, BIRD_START_Y
    bird.vel_y = 0.0
    pipes.clear()
    score = 0
    game_over = False
    game_started = False
    show_splash = False
    sfx_swoosh.play()
    darkness = 0.0
    shadow_active = False
    dying = False
    death_timer = 0
    death_spin = 0
    score_pop_timer = 0
    last_displayed_score = 0
    shake_timer = 0
    shake_x = 0
    shake_y = 0
    game_paused = False


def create_pipes():
    min_top = -PIPE_H + int(SCREEN_H * 0.1)
    max_top = -PIPE_H + int(SCREEN_H * 0.65)
    top_y = random.randint(min_top, max_top)
    pipes.append(Pipe(top_pipe_image, SCREEN_W, top_y))
    pipes.append(Pipe(bottom_pipe_image, SCREEN_W, top_y + PIPE_H + PIPE_GAP))


def start_death():
    global dying, death_timer, death_spin, shake_timer
    if dying:
        return
    dying = True
    death_timer = 0
    death_spin = 0
    shake_timer = SHAKE_DURATION
    bird.vel_y = FLAP_STRENGTH * 0.7
    sfx_hit.play()


def update_death():
    global dying, game_over, death_timer, death_spin, shake_timer, shake_x, shake_y
    death_timer += 1
    death_spin -= 8
    bird.vel_y += GRAVITY * 2.5
    bird.y += bird.vel_y

    if shake_timer > 0:
        shake_timer -= 1
        intensity = int(SHAKE_INTENSITY * (shake_timer / SHAKE_DURATION))
        shake_x = random.randint(-intensity, intensity)
        shake_y = random.randint(-intensity, intensity)
    else:
        shake_x = 0
        shake_y = 0

    if death_timer >= DEATH_DURATION or bird.y > SCREEN_H + BIRD_H:
        dying = False
        game_over = True
        shake_x = 0
        shake_y = 0
        sfx_die.play()
        stop_bgm()


def move():
    global score, darkness, shadow_active, score_pop_timer, last_displayed_score
    bird.update()

    if bird.y > SCREEN_H:
        start_death()
        return

    for pipe in pipes:
        pipe.x -= PIPE_SPEED

        if not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 0.5
            pipe.passed = True
            if int(score) != last_displayed_score:
                last_displayed_score = int(score)
                score_pop_timer = SCORE_POP_DURATION
                sfx_point.play()
            if not shadow_active and int(score) >= SHADOW_START_SCORE:
                shadow_active = True
            if shadow_active and int(score * 2) % 2 == 0:
                darkness = max(0, darkness - FLASH_RELIEF)

        if bird.colliderect(pipe):
            start_death()
            return

    while pipes and pipes[0].x < -PIPE_W:
        pipes.pop(0)

    if shadow_active:
        score_above = max(0, int(score) - SHADOW_START_SCORE)
        current_rate = min(DARKNESS_RATE + score_above * 0.03, DARKNESS_RATE_MAX)
        darkness = min(MAX_DARKNESS, darkness + current_rate)

    if score_pop_timer > 0:
        score_pop_timer -= 1


def draw_shadow_overlay():
    if darkness < 1:
        return

    pulse = math.sin(pygame.time.get_ticks() * PULSE_SPEED * 0.06) * PULSE_AMPLITUDE
    effective_darkness = max(1, min(255, int(darkness + pulse)))

    dark_alpha = effective_darkness
    _dark_surf.fill((0, 0, 0, dark_alpha))

    score_above = max(0, int(score) - SHADOW_START_SCORE)
    shrink = 1.0 - score_above * GLOW_SHRINK_RATE
    shrink = max(GLOW_RADIUS_MIN / GLOW_RADIUS, min(1.0, shrink))
    current_glow_r = int(GLOW_RADIUS * shrink) // _SHADOW_SCALE
    current_glow_diam = current_glow_r * 2

    if current_glow_diam != _glow_diam:
        scaled_glow = _get_scaled_glow(current_glow_diam)
    else:
        scaled_glow = glow_mask

    glow_x = int(bird.centerx // _SHADOW_SCALE - current_glow_diam // 2)
    glow_y = int(bird.centery // _SHADOW_SCALE - current_glow_diam // 2)
    _dark_surf.blit(scaled_glow, (glow_x, glow_y), special_flags=pygame.BLEND_RGBA_MIN)

    scaled = pygame.transform.scale(_dark_surf, (SCREEN_W, SCREEN_H))
    window.blit(scaled, (0, 0))


def draw_score_live():
    score_str = str(int(score))
    if score_pop_timer > 0:
        t = score_pop_timer / SCORE_POP_DURATION
        scale = 1.0 + 0.4 * t
        pop_font_size = int(_base_pop_h * scale)
        pop_font = _pop_font_cache.get(pop_font_size)
        if pop_font is None:
            pop_font = font_big
        txt = pop_font.render(score_str, True, (255, 255, 100))
        shd = pop_font.render(score_str, True, (0, 0, 0))
    else:
        txt = font_big.render(score_str, True, (255, 255, 255))
        shd = font_big.render(score_str, True, (0, 0, 0))
    sx = (SCREEN_W - txt.get_width()) // 2
    sy = max(10, 10 - int((txt.get_height() - font_big.get_height()) / 2))
    window.blit(shd, (sx + 2, sy + 2))
    window.blit(txt, (sx, sy))

    if game_started and not game_over:
        if shadow_active:
            pct = min(int(darkness / MAX_DARKNESS * 100), 100)
            ind = font_small.render(f"Shadow: {pct}%", True, (200, 200, 200))
            window.blit(ind, (10, SCREEN_H - ind.get_height() - 10))
        elif int(score) >= SHADOW_START_SCORE - 3:
            warn = font_small.render(f"Shadow in {SHADOW_START_SCORE - int(score)}...", True, (255, 180, 80))
            window.blit(warn, (10, SCREEN_H - warn.get_height() - 10))


def draw_game_over_screen():
    global best_score
    if int(score) > best_score:
        best_score = int(score)

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    window.blit(overlay, (0, 0))

    title = font_medium.render("GAME OVER", True, (255, 80, 80))
    window.blit(title, ((SCREEN_W - title.get_width()) // 2,
                         SCREEN_H // 2 - int(S * 0.14)))

    sc = font_small.render(f"Score:  {int(score)}", True, (255, 255, 255))
    window.blit(sc, ((SCREEN_W - sc.get_width()) // 2,
                      SCREEN_H // 2 - int(S * 0.06)))

    bs = font_small.render(f"Best:   {best_score}", True, (255, 215, 0))
    window.blit(bs, ((SCREEN_W - bs.get_width()) // 2,
                      SCREEN_H // 2 - int(S * 0.02)))

    medal = get_medal(int(score))
    if medal:
        medal_name, medal_col = medal
        medal_surf = font_medium.render(medal_name, True, medal_col)
        medal_shd = font_medium.render(medal_name, True, (0, 0, 0))
        mx = (SCREEN_W - medal_surf.get_width()) // 2
        my = SCREEN_H // 2 + int(S * 0.02)
        window.blit(medal_shd, (mx + 1, my + 1))
        window.blit(medal_surf, (mx, my))

    mouse_pos = pygame.mouse.get_pos()
    hovered = restart_button.collidepoint(mouse_pos)
    btn_col = (80, 200, 80) if hovered else (50, 170, 50)
    pygame.draw.rect(window, btn_col, restart_button, border_radius=12)
    pygame.draw.rect(window, (255, 255, 255), restart_button, width=2, border_radius=12)
    bt = font_button.render("RESTART", True, (255, 255, 255))
    window.blit(bt, (
        restart_button.x + (BUTTON_W - bt.get_width()) // 2,
        restart_button.y + (BUTTON_H - bt.get_height()) // 2,
    ))


def draw_splash_screen():
    # Dim overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    window.blit(overlay, (0, 0))

    # Title
    title = font_title.render("FLAPPY BIRD", True, (255, 220, 50))
    title_shd = font_title.render("FLAPPY BIRD", True, (0, 0, 0))
    tx = (SCREEN_W - title.get_width()) // 2
    ty = SCREEN_H // 2 - int(S * 0.20)
    window.blit(title_shd, (tx + 2, ty + 2))
    window.blit(title, (tx, ty))

    # Subtitle — Shadow World
    sub = font_medium.render("— SHADOW WORLD —", True, (200, 150, 255))
    sub_shd = font_medium.render("— SHADOW WORLD —", True, (0, 0, 0))
    sx = (SCREEN_W - sub.get_width()) // 2
    sy = ty + title.get_height() + int(S * 0.01)
    window.blit(sub_shd, (sx + 1, sy + 1))
    window.blit(sub, (sx, sy))

    bob = math.sin(pygame.time.get_ticks() / 300.0) * int(S * 0.015)
    tilt = math.sin(pygame.time.get_ticks() / 500.0) * 8
    rotated_splash_bird = pygame.transform.rotate(splash_bird_img, tilt)
    # Glow behind bird
    glow_x = (SCREEN_W - _splash_glow_diam) // 2
    glow_y = SCREEN_H // 2 + int(S * 0.04) + int(bob) - (_splash_glow_diam - _splash_bird_h) // 2
    window.blit(splash_bird_glow, (glow_x, glow_y))
    # Bird
    bird_rect = rotated_splash_bird.get_rect(
        center=(SCREEN_W // 2, SCREEN_H // 2 + int(S * 0.04) + int(bob))
    )
    window.blit(rotated_splash_bird, bird_rect)

    # Tap to start
    if IS_LANDSCAPE:
        start_text = "Tap or press SPACE to start"
    else:
        start_text = "Tap to start"

    pulse = int(180 + 75 * math.sin(pygame.time.get_ticks() / 400.0))
    start_surf = font_small.render(start_text, True, (255, 255, 255))
    start_shd = font_small.render(start_text, True, (0, 0, 0))
    start_surf.set_alpha(pulse)
    start_shd.set_alpha(pulse)
    px = (SCREEN_W - start_surf.get_width()) // 2
    py = SCREEN_H // 2 + int(S * 0.10)
    window.blit(start_shd, (px + 1, py + 1))
    window.blit(start_surf, (px, py))

    # Twist hint
    twist_text = "Twist: Shadow World — survive the darkness!" if IS_LANDSCAPE else "Twist: Shadow World!"
    tw = font_small.render(twist_text, True, (255, 200, 50))
    window.blit(tw, ((SCREEN_W - tw.get_width()) // 2, py + int(S * 0.04)))


def draw_start_prompt():
    if IS_LANDSCAPE:
        start_text = "Tap or press SPACE to start"
    else:
        start_text = "Tap to start"

    msg = font_small.render(start_text, True, (255, 255, 255))
    shd = font_small.render(start_text, True, (0, 0, 0))
    px = (SCREEN_W - msg.get_width()) // 2
    py = SCREEN_H // 2 + int(S * 0.06)
    window.blit(shd, (px + 1, py + 1))
    window.blit(msg, (px, py))


def update_parallax():
    for i in range(5):
        dark_scroll_x[i] -= PIPE_SPEED * PARALLAX_SPEEDS[i]
        if dark_scroll_x[i] <= -SCREEN_W:
            dark_scroll_x[i] += SCREEN_W


def draw_parallax_bg():
    for i, layer in enumerate(dark_layers):
        x = int(dark_scroll_x[i])
        window.blit(layer, (x, 0))
        window.blit(layer, (x + SCREEN_W, 0))


def _draw_icon_bg(surface, rect, hovered=False, active=False):
    bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    if active:
        col = (255, 255, 255, 45)
    elif hovered:
        col = (255, 255, 255, 30)
    else:
        col = (0, 0, 0, 60)
    radius = max(rect.h // 4, 6)
    pygame.draw.rect(bg, col, bg.get_rect(), border_radius=radius)
    surface.blit(bg, rect.topleft)


def draw_toggle_button():
    mouse_pos = pygame.mouse.get_pos()
    hovered = toggle_btn.collidepoint(mouse_pos)

    _draw_icon_bg(window, toggle_btn, hovered=hovered)
    ix = toggle_btn.x + ICON_PAD
    iy = toggle_btn.y + ICON_PAD
    window.blit(toggle_img, (ix, iy))

    cx = toggle_btn.centerx
    label = font_small.render("NIGHT" if dark_mode else "DAY", True, (255, 255, 255))
    lx = cx - label.get_width() // 2
    ly = toggle_btn.bottom + 2
    label_shd = font_small.render("NIGHT" if dark_mode else "DAY", True, (0, 0, 0))
    window.blit(label_shd, (lx + 1, ly + 1))
    window.blit(label, (lx, ly))


def draw_pause_button():
    mouse_pos = pygame.mouse.get_pos()
    hovered = pause_btn.collidepoint(mouse_pos)
    _draw_icon_bg(window, pause_btn, hovered=hovered, active=game_paused)
    icon = play_img if game_paused else pause_img
    ix = pause_btn.x + ICON_PAD
    iy = pause_btn.y + ICON_PAD
    window.blit(icon, (ix, iy))


def draw_pause_overlay():
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    window.blit(overlay, (0, 0))
    txt = font_medium.render("PAUSED", True, (255, 255, 255))
    shd = font_medium.render("PAUSED", True, (0, 0, 0))
    tx = (SCREEN_W - txt.get_width()) // 2
    ty = SCREEN_H // 2 - txt.get_height() // 2
    window.blit(shd, (tx + 2, ty + 2))
    window.blit(txt, (tx, ty))
    hint = font_small.render("Tap or press P to resume", True, (200, 200, 200))
    hx = (SCREEN_W - hint.get_width()) // 2
    hy = ty + txt.get_height() + int(S * 0.02)
    window.blit(hint, (hx, hy))


def draw_settings():
    mouse_pos = pygame.mouse.get_pos()
    hovered = settings_btn.collidepoint(mouse_pos)

    _draw_icon_bg(window, settings_btn, hovered=hovered, active=settings_open)
    ix = settings_btn.x + ICON_PAD
    iy = settings_btn.y + ICON_PAD
    window.blit(volume_img, (ix, iy))

    if not music_enabled and not sfx_enabled:
        lw = max(2, ICON_SIZE // 10)
        x1, y1 = settings_btn.x + ICON_PAD // 2, settings_btn.y + ICON_PAD // 2
        x2, y2 = settings_btn.right - ICON_PAD // 2, settings_btn.bottom - ICON_PAD // 2
        pygame.draw.line(window, (255, 60, 60), (x1, y1), (x2, y2), lw)
        pygame.draw.line(window, (255, 60, 60), (x1, y2), (x2, y1), lw)

    if not settings_open:
        return

    pygame.draw.rect(window, (20, 20, 30), settings_panel, border_radius=6)
    pygame.draw.rect(window, (200, 200, 200), settings_panel, width=2, border_radius=6)

    _draw_toggle_row(window, music_toggle_rect, "Music", music_enabled, mouse_pos)
    _draw_toggle_row(window, sfx_toggle_rect, "SFX", sfx_enabled, mouse_pos)


def _draw_toggle_row(surface, rect, label_text, is_on, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    if hovered:
        hl = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 25))
        surface.blit(hl, rect.topleft)

    # Label
    lbl = font_small.render(label_text, True, (255, 255, 255))
    lx = rect.x + max(int(S * 0.012), 8)
    ly = rect.y + (rect.h - lbl.get_height()) // 2
    surface.blit(lbl, (lx, ly))

    # ON/OFF pill
    pill_w = max(int(S * 0.05), 36)
    pill_h = max(int(S * 0.022), 16)
    pill_x = rect.right - pill_w - max(int(S * 0.012), 8)
    pill_y = rect.y + (rect.h - pill_h) // 2
    pill_r = pill_h // 2

    bg_col = (60, 180, 80) if is_on else (120, 60, 60)
    pygame.draw.rect(surface, bg_col, (pill_x, pill_y, pill_w, pill_h), border_radius=pill_r)

    # Knob
    knob_r = pill_r - 2
    knob_x = pill_x + pill_w - pill_r if is_on else pill_x + pill_r
    knob_y = pill_y + pill_r
    pygame.draw.circle(surface, (255, 255, 255), (knob_x, knob_y), max(knob_r, 4))

    # Status text
    status = font_small.render("ON" if is_on else "OFF", True, (200, 200, 200))
    sx = pill_x - status.get_width() - max(int(S * 0.006), 4)
    sy = rect.y + (rect.h - status.get_height()) // 2
    surface.blit(status, (sx, sy))


def draw():
    show_aura = (game_started and not game_over and not dying
                 and shadow_active and darkness >= 1)

    if dark_mode:
        draw_parallax_bg()
    else:
        window.blit(background_image, (0, 0))

    for pipe in pipes:
        window.blit(pipe.img, pipe)
    bird.draw(window, show_aura=show_aura, dying=dying, death_spin=death_spin)

    if game_started and not game_over and not dying and shadow_active:
        draw_shadow_overlay()

    draw_score_live()
    if not game_over:
        draw_toggle_button()
        draw_pause_button()
        draw_settings()

    if game_paused and game_started and not game_over and not dying:
        draw_pause_overlay()

    if not game_started and show_splash:
        draw_splash_screen()
    elif not game_started:
        draw_start_prompt()
    if game_over:
        draw_game_over_screen()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer and game_started and not game_over and not game_paused:
            create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_paused:
                    game_paused = False
                else:
                    pygame.quit()
                    exit()
            if event.key == pygame.K_p and game_started and not game_over and not dying:
                game_paused = not game_paused
                if game_paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                if game_paused:
                    pass
                elif dying:
                    pass
                elif game_over:
                    reset_game()
                else:
                    if not game_started:
                        game_started = True
                        show_splash = False
                        sfx_swoosh.play()
                        play_bgm()
                    bird.flap()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pause_btn.collidepoint(event.pos) and game_started and not game_over and not dying:
                game_paused = not game_paused
                if game_paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                continue
            if game_paused:
                continue
            if settings_open and settings_panel.collidepoint(event.pos):
                if music_toggle_rect.collidepoint(event.pos):
                    music_enabled = not music_enabled
                    apply_music_volume()
                elif sfx_toggle_rect.collidepoint(event.pos):
                    sfx_enabled = not sfx_enabled
                    apply_sfx_volume()
                continue
            if settings_btn.collidepoint(event.pos):
                settings_open = not settings_open
                continue
            if settings_open:
                settings_open = False
            if toggle_btn.collidepoint(event.pos):
                dark_mode = not dark_mode
                play_bgm(force_restart=True)
            elif dying:
                pass
            elif game_over:
                if restart_button.collidepoint(event.pos):
                    reset_game()
            else:
                if not game_started:
                    game_started = True
                    show_splash = False
                    sfx_swoosh.play()
                    play_bgm()
                bird.flap()

        if event.type == pygame.FINGERDOWN:
            tx = int(event.x * SCREEN_W)
            ty = int(event.y * SCREEN_H)
            if pause_btn.collidepoint(tx, ty) and game_started and not game_over and not dying:
                game_paused = not game_paused
                if game_paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                continue
            if game_paused:
                continue
            if settings_open and settings_panel.collidepoint(tx, ty):
                if music_toggle_rect.collidepoint(tx, ty):
                    music_enabled = not music_enabled
                    apply_music_volume()
                elif sfx_toggle_rect.collidepoint(tx, ty):
                    sfx_enabled = not sfx_enabled
                    apply_sfx_volume()
                continue
            if settings_btn.collidepoint(tx, ty):
                settings_open = not settings_open
                continue
            if settings_open:
                settings_open = False
            if toggle_btn.collidepoint(tx, ty):
                dark_mode = not dark_mode
                play_bgm(force_restart=True)
            elif dying:
                pass
            elif game_over:
                if restart_button.collidepoint(tx, ty):
                    reset_game()
            else:
                if not game_started:
                    game_started = True
                    show_splash = False
                    sfx_swoosh.play()
                    play_bgm()
                bird.flap()

    if game_paused:
        pass
    elif dying:
        update_death()
    elif game_started and not game_over:
        move()
        if dark_mode:
            update_parallax()

    draw()

    if shake_x != 0 or shake_y != 0:
        shaken = window.copy()
        window.fill((0, 0, 0))
        window.blit(shaken, (shake_x, shake_y))

    pygame.display.update()
    clock.tick(FPS)

