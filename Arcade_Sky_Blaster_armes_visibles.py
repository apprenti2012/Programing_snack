import pygame, pygame.gfxdraw as gfxdraw, random, sys, math

pygame.init()

WIDTH, HEIGHT = 600, 700
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Sky Blaster - Animations completes")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22, bold=True)
font_small = pygame.font.SysFont("arial", 17, bold=True)
big_font = pygame.font.SysFont("arial", 74, bold=True)

WHITE=(245,245,255); BLACK=(5,6,18); BLUE=(45,150,255); DARK_BLUE=(20,70,150)
CYAN=(70,230,255); RED=(240,55,65); DARK_RED=(120,20,35); YELLOW=(255,230,70)
ORANGE=(255,140,35); GREEN=(70,255,140); PURPLE=(185,80,255); PINK=(255,90,180)
GRAY=(120,130,160); DARK_GRAY=(55,60,80); ELECTRIC=(130,245,255)

player = pygame.Rect(WIDTH//2-24, HEIGHT-85, 48, 58)
player_speed = 10
player_hp = 100
max_hp = 100
invincible_timer = 0

bullets=[]; enemy_bullets=[]; enemies=[]; bombs=[]; particles=[]; smokes=[]; shockwaves=[]; stars=[]
weapon_effects=[]; heal_effects=[]

score = 0
weapon = 1
previous_weapon = 1
weapon_anim = 0
weapon_anim_max = 24
weapon_changing = False

# Timers visuels par arme : ils permettent d'avoir de vraies animations
fan_cannon_anim = 0      # arme 2 : mini canons des ailes
nose_cannon_anim = 0     # arme 3 : deux canons sur le nez
laser_open_anim = 0      # arme 4 : nez qui s'ouvre en deux + tube electrique
bomb_fusion_anim = 0     # arme 5 : pods gris qui avancent et fusionnent
heal_anim = 0            # arme 6 : soin

# Position de lancement de la bombe fusionnee
pending_fused_bomb = None

game_over = False
paused = False
start_countdown = 180

spawn_timer = 0
shoot_timer = 0
enemy_shoot_timer = 0
shoot_delay = 6

base_enemy_speed = 1.4
base_spawn_delay = 95
base_enemy_shoot_delay = 135
difficulty_level = 1

ammo_2, ammo_3, ammo_5, ammo_6 = 20, 12, 2, 3
max_ammo_2, max_ammo_3, max_ammo_5, max_ammo_6 = 20, 12, 2, 3

reload_2 = reload_3 = reload_5 = reload_6 = 0
reload_time_2 = 420
reload_time_3 = 480
reload_time_5 = 540
reload_time_6 = 720

laser_active = False
laser_timer = 0
laser_duration = 180
laser_reload = 0
laser_reload_time = 540

bomb_radius = 155
bomb_speed = 7
shake_timer = 0
frame_count = 0

# ---------------------------------------------------------------------------
# OUTILS VISUELS : lueurs (glow), formes lissees, degrades, vignette
# ---------------------------------------------------------------------------

glow_cache = {}

def get_glow(radius, color, max_alpha=170):
    radius = max(2, int(radius))
    key = (radius, color, max_alpha)
    surf = glow_cache.get(key)
    if surf is None:
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            t = r / radius
            alpha = int(max_alpha * (1 - t) ** 2)
            if alpha <= 0:
                continue
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        glow_cache[key] = surf
    return surf

def blit_glow(pos, radius, color, max_alpha=170):
    g = get_glow(radius, color, max_alpha)
    r = g.get_width() // 2
    screen.blit(g, (int(pos[0]-r), int(pos[1]-r)), special_flags=pygame.BLEND_RGBA_ADD)

def draw_poly(color, points):
    ipoints = [(int(x), int(y)) for x, y in points]
    try:
        gfxdraw.filled_polygon(screen, ipoints, color)
        gfxdraw.aapolygon(screen, ipoints, color)
    except Exception:
        pygame.draw.polygon(screen, color, ipoints)

def draw_circle(color, pos, r):
    x, y = int(pos[0]), int(pos[1])
    r = max(1, int(r))
    gfxdraw.filled_circle(screen, x, y, r, color)
    gfxdraw.aacircle(screen, x, y, r, color)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))

def make_vertical_gradient(w, h, c1, c2):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        pygame.draw.line(surf, lerp_color(c1, c2, t), (0, y), (w, y))
    return surf

def make_vignette(w, h, color=(0, 0, 0), max_alpha=150):
    sw, sh = 90, 105
    small = pygame.Surface((sw, sh), pygame.SRCALPHA)
    cx, cy = sw/2, sh/2
    maxd = math.hypot(cx, cy)
    for y in range(sh):
        for x in range(sw):
            d = math.hypot(x-cx, y-cy) / maxd
            a = max(0.0, (d - 0.32) / 0.68)
            alpha = int(max_alpha * min(1.0, a) ** 1.6)
            small.set_at((x, y), (*color, alpha))
    return pygame.transform.smoothscale(small, (w, h))

def vertical_gradient_rect(rect, c1, c2, radius=0):
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height)
        pygame.draw.line(surf, (*lerp_color(c1, c2, t), 255), (0, y), (rect.width, y))
    if radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=radius)
        surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(surf, rect.topleft)

BG_TOP = (6, 9, 26)
BG_BOTTOM = (14, 22, 48)
bg_gradient = make_vertical_gradient(WIDTH, HEIGHT, BG_TOP, BG_BOTTOM)

for i in range(150):
    layer = random.choice([0,0,1,1,2])
    speed = [0.5, 1.3, 2.6][layer] + random.uniform(-0.15, 0.25)
    size = [1, 2, 3][layer]
    stars.append({"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": speed,
                  "size": size, "layer": layer, "phase": random.uniform(0, math.pi*2)})

def clamp(v, a, b):
    return max(a, min(b, v))

def distance(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def set_weapon(new_weapon):
    global weapon, previous_weapon, weapon_anim, weapon_changing
    if new_weapon != weapon:
        previous_weapon = weapon
        weapon = new_weapon
        weapon_anim = weapon_anim_max
        weapon_changing = True

def add_sparks(x,y,color,amount=30,power=7):
    for _ in range(amount):
        a=random.uniform(0,math.pi*2); s=random.uniform(1.5,power)
        particles.append({"x":x,"y":y,"dx":math.cos(a)*s,"dy":math.sin(a)*s,"life":random.randint(18,45),"size":random.randint(2,7),"color":random.choice([color,ORANGE,YELLOW,WHITE])})

def add_smoke(x,y,amount=10):
    for _ in range(amount):
        smokes.append({"x":x+random.randint(-8,8),"y":y+random.randint(-8,8),"dx":random.uniform(-1,1),"dy":random.uniform(-1.5,0.8),"life":random.randint(25,55),"size":random.randint(8,18)})

def big_explosion(x,y,color=ORANGE):
    global shake_timer
    shake_timer=12
    add_sparks(x,y,color,75,10)
    add_smoke(x,y,16)
    shockwaves.append({"x":x,"y":y,"r":8,"max":100,"life":25,"color":color})

def damage_player(amount):
    global player_hp, game_over, invincible_timer
    if invincible_timer > 0 or game_over:
        return
    player_hp -= amount
    invincible_timer = 45
    big_explosion(player.centerx, player.centery, BLUE)
    if player_hp <= 0:
        player_hp = 0
        game_over = True

def heal_player(amount):
    global player_hp, heal_anim, shake_timer
    old_hp = player_hp
    player_hp = min(max_hp, player_hp + amount)
    heal_anim = 70
    shake_timer = 5
    heal_effects.append({"x": player.centerx, "y": player.centery, "life": 70, "gain": player_hp-old_hp})
    for _ in range(40):
        a = random.uniform(0, math.pi*2)
        s = random.uniform(1, 4)
        particles.append({"x":player.centerx,"y":player.centery,"dx":math.cos(a)*s,"dy":math.sin(a)*s,"life":random.randint(20,45),"size":random.randint(2,5),"color":random.choice([GREEN,CYAN,WHITE])})

def explode_bomb(x,y):
    global score, shake_timer
    shake_timer=18
    shockwaves.append({"x":x,"y":y,"r":10,"max":bomb_radius,"life":32,"color":ORANGE})
    add_sparks(x,y,ORANGE,100,13)
    add_smoke(x,y,25)

    for enemy in enemies[:]:
        if distance((x,y), enemy.center) <= bomb_radius:
            big_explosion(enemy.centerx, enemy.centery, RED)
            enemies.remove(enemy)
            score += 1

    for eb in enemy_bullets[:]:
        if distance((x,y), eb.center) <= bomb_radius:
            enemy_bullets.remove(eb)
            add_sparks(eb.centerx, eb.centery, GREEN, 12, 5)

def draw_background(offset):
    screen.blit(bg_gradient, (0,0))

    for i in range(0, HEIGHT, 90):
        pygame.draw.line(screen, (12,22,50), (0,i), (WIDTH,i), 1)

    for s in stars:
        if not paused:
            s["y"] += s["speed"]
            s["phase"] += 0.06
        if s["y"] > HEIGHT:
            s["x"] = random.randint(0, WIDTH)
            s["y"] = 0
        twinkle = 0.65 + 0.35 * math.sin(s["phase"])
        base_col = WHITE if s["layer"] == 2 else (170,190,255) if s["layer"] == 1 else (110,125,180)
        col = tuple(int(c*twinkle) for c in base_col)
        px, py = int(s["x"]+offset[0]), int(s["y"]+offset[1])
        pygame.draw.circle(screen, col, (px, py), s["size"])

def draw_electric_line(start, end, color=ELECTRIC, width=2, chaos=7, segments=7):
    sx, sy = start; ex, ey = end
    pts = []
    for i in range(segments+1):
        t = i / segments
        px = sx + (ex-sx)*t + random.randint(-chaos, chaos)
        py = sy + (ey-sy)*t + random.randint(-chaos, chaos)
        if i == 0: px, py = sx, sy
        if i == segments: px, py = ex, ey
        pts.append((px, py))
    pygame.draw.lines(screen, color, False, pts, width)
    pygame.draw.lines(screen, WHITE, False, pts, 1)

def deploy_amount(timer, max_timer=28):
    return clamp(timer / max_timer, 0, 1)

def draw_player(offset):
    if game_over and player_hp <= 0:
        return
    if invincible_timer > 0 and invincible_timer % 8 < 4:
        return

    x, y = player.centerx + offset[0], player.centery + offset[1]

    # Deploiement persistant : quand une arme est selectionnee, elle reste sortie
    # jusqu'a epuisement de ses munitions. Le laser reste ouvert tant qu'il tire.
    a2 = 1 if (weapon == 2 and ammo_2 > 0 and reload_2 == 0) else deploy_amount(fan_cannon_anim)
    a3 = 1 if (weapon == 3 and ammo_3 > 0 and reload_3 == 0) else deploy_amount(nose_cannon_anim)
    a4 = 1 if laser_active else deploy_amount(laser_open_anim)
    a5 = 1 if (weapon == 5 and ammo_5 > 0 and reload_5 == 0) else deploy_amount(bomb_fusion_anim, 36)
    a6 = 1 if (weapon == 6 and ammo_6 > 0 and reload_6 == 0) else deploy_amount(heal_anim, 70)

    # Ailes principales
    draw_poly(DARK_BLUE, [(x-6,y-8),(x-58,y+18),(x-34,y+29),(x-12,y+20)])
    draw_poly(DARK_BLUE, [(x+6,y-8),(x+58,y+18),(x+34,y+29),(x+12,y+20)])
    pygame.draw.line(screen, CYAN, (x-12,y-4), (x-54,y+17), 2)
    pygame.draw.line(screen, CYAN, (x+12,y-4), (x+54,y+17), 2)

    # Pods gris permanents sous les ailes. Pour l'arme 5 ils avancent et fusionnent.
    left_pod_x = x - 48 + int(36 * a5)
    right_pod_x = x + 38 - int(36 * a5)
    pod_y = y + 24 - int(48 * a5)
    pygame.draw.rect(screen, GRAY, (left_pod_x, pod_y, 11, 24), border_radius=5)
    pygame.draw.rect(screen, GRAY, (right_pod_x, pod_y, 11, 24), border_radius=5)
    pygame.draw.rect(screen, DARK_GRAY, (left_pod_x+2, pod_y+4, 7, 13), border_radius=3)
    pygame.draw.rect(screen, DARK_GRAY, (right_pod_x+2, pod_y+4, 7, 13), border_radius=3)
    if a5 > 0.05:
        pygame.draw.line(screen, ORANGE, (left_pod_x+5, pod_y+2), (x, y-64), 3)
        pygame.draw.line(screen, ORANGE, (right_pod_x+5, pod_y+2), (x, y-64), 3)
        if a5 > 0.65:
            draw_circle(ORANGE, (x, y-64), int(8 + 12*a5))
            draw_circle(YELLOW, (x, y-64), int(4 + 6*a5))
            draw_circle(WHITE, (x, y-64), 3)

    # Arme 2 : mini canons qui sortent des ailes et crachent en eventail.
    if a2 > 0:
        left_base = (x-49, y+12)
        right_base = (x+49, y+12)
        out = int(22 * a2)
        for side, base in [(-1,left_base),(1,right_base)]:
            bx, by = base
            for k, ang in enumerate([-0.55, 0, 0.55]):
                spread = ang * a2
                length = 15 + int(8*a2)
                sx = bx + side*out
                sy = by + k*5 - 5
                ex = sx + int(math.sin(spread)*length*side)
                ey = sy - int(math.cos(spread)*length)
                pygame.draw.line(screen, DARK_GRAY, (sx, sy), (ex, ey), 6)
                pygame.draw.line(screen, YELLOW, (sx, sy), (ex, ey), 2)
                if fan_cannon_anim > 20 and random.random() < 0.35:
                    draw_circle(WHITE, (ex, ey), random.randint(3,6))
                    draw_circle(YELLOW, (ex, ey), random.randint(2,4))

    # Ailettes arriere
    draw_poly(BLUE, [(x-9,y+20),(x-34,y+43),(x-12,y+38)])
    draw_poly(BLUE, [(x+9,y+20),(x+34,y+43),(x+12,y+38)])

    # Corps central
    draw_poly(BLUE, [(x,y-42),(x-17,y+29),(x,y+46),(x+17,y+29)])

    # Arme 4 : nez qui s'ouvre en deux + tuyau electrique qui sort.
    nose_split = int(14 * a4)
    if a4 > 0:
        draw_poly(CYAN, [(x-nose_split,y-42),(x-13-nose_split,y-16),(x-3-nose_split,y-14)])
        draw_poly(CYAN, [(x+nose_split,y-42),(x+13+nose_split,y-16),(x+3+nose_split,y-14)])
        tube_end = (x, y-70-int(12*a4))
        pygame.draw.line(screen, DARK_GRAY, (x, y-35), tube_end, 9)
        pygame.draw.line(screen, ELECTRIC, (x, y-35), tube_end, 4)
        for _ in range(2):
            draw_electric_line((x-nose_split, y-35), tube_end, chaos=4, segments=4)
            draw_electric_line((x+nose_split, y-35), tube_end, chaos=4, segments=4)
        draw_circle(WHITE, tube_end, 6)
        draw_circle(CYAN, tube_end, 3)
    else:
        draw_poly(CYAN, [(x,y-42),(x-8,y-14),(x+8,y-14)])

    # Cockpit
    pygame.draw.ellipse(screen, WHITE, (x-9,y-20,18,26))
    pygame.draw.ellipse(screen, CYAN, (x-5,y-16,10,17))

    # Arme 3 : deux canons deployes sur le nez de l'avion, gauche et droite.
    if a3 > 0:
        extend = int(24 * a3)
        for side in [-1, 1]:
            base_x = x + side * (8 + int(6*a3))
            base_y = y - 28
            tip = (base_x + side*3, base_y - extend)
            pygame.draw.line(screen, DARK_GRAY, (base_x, base_y), tip, 7)
            pygame.draw.line(screen, PURPLE, (base_x, base_y), tip, 3)
            draw_circle(WHITE, tip, 3)
            if nose_cannon_anim > 18 and random.random() < 0.25:
                draw_circle(PURPLE, (tip[0], tip[1]-5), 6)

    # Arme 6 : halo de soin autour du joueur.
    if a6 > 0:
        r = int(30 + 35 * math.sin((70-heal_anim)/70*math.pi))
        pygame.draw.circle(screen, GREEN, (x, y), max(8,r), 3)
        pygame.draw.circle(screen, CYAN, (x, y), max(5,r//2), 2)
        pygame.draw.line(screen, WHITE, (x-10,y), (x+10,y), 4)
        pygame.draw.line(screen, WHITE, (x,y-10), (x,y+10), 4)

    # Reacteurs
    pygame.draw.rect(screen, GRAY, (x-18,y+30,8,15), border_radius=3)
    pygame.draw.rect(screen, GRAY, (x+10,y+30,8,15), border_radius=3)
    pygame.draw.line(screen, WHITE, (x,y-38), (x,y+38), 2)
    pygame.draw.line(screen, CYAN, (x-42,y+22), (x-16,y+26), 2)
    pygame.draw.line(screen, CYAN, (x+42,y+22), (x+16,y+26), 2)

    if start_countdown <= 0 and not game_over and not paused:
        flame = random.randint(18,34)
        draw_poly(ORANGE, [(x-17,y+44),(x-9,y+44),(x-13,y+44+flame)])
        draw_poly(ORANGE, [(x+9,y+44),(x+17,y+44),(x+13,y+44+flame)])
        draw_poly(YELLOW, [(x-15,y+44),(x-11,y+44),(x-13,y+56)])
        draw_poly(YELLOW, [(x+11,y+44),(x+15,y+44),(x+13,y+56)])
        if random.random() < 0.4:
            add_smoke(x, y+48, 1)

def draw_enemy(enemy, offset):
    x, y = enemy.centerx + offset[0], enemy.centery + offset[1]
    draw_poly(DARK_RED, [(x-8,y+4),(x-42,y-16),(x-16,y-24)])
    draw_poly(DARK_RED, [(x+8,y+4),(x+42,y-16),(x+16,y-24)])
    draw_poly(RED, [(x,y+36),(x-15,y-24),(x,y-36),(x+15,y-24)])
    draw_poly(PINK, [(x,y+36),(x-6,y+10),(x+6,y+10)])
    pygame.draw.ellipse(screen, WHITE, (x-7,y-7,14,20))
    pygame.draw.ellipse(screen, PINK, (x-4,y-4,8,13))
    pygame.draw.rect(screen, GRAY, (x-16,y-34,7,12), border_radius=3)
    pygame.draw.rect(screen, GRAY, (x+9,y-34,7,12), border_radius=3)
    flame = random.randint(8,18) if not paused else 10
    draw_poly(ORANGE, [(x-16,y-36),(x-9,y-36),(x-12,y-36-flame)])
    draw_poly(ORANGE, [(x+9,y-36),(x+16,y-36),(x+12,y-36-flame)])
    pygame.draw.line(screen, WHITE, (x,y+32), (x,y-30), 2)

def draw_particles(offset):
    for p in particles[:]:
        if not paused:
            p["x"] += p["dx"]; p["y"] += p["dy"]; p["dy"] += 0.05
            p["life"] -= 1; p["size"] *= 0.96
        if p["life"] <= 0 or p["size"] <= 1:
            particles.remove(p)
        else:
            pos = (int(p["x"]+offset[0]), int(p["y"]+offset[1]))
            draw_circle(p["color"], pos, p["size"])

def draw_smoke(offset):
    for s in smokes[:]:
        if not paused:
            s["x"] += s["dx"]; s["y"] += s["dy"]; s["life"] -= 1; s["size"] *= 1.01
        if s["life"] <= 0:
            smokes.remove(s)
        else:
            shade = max(30, min(100, s["life"]*2))
            pos = (int(s["x"]+offset[0]), int(s["y"]+offset[1]))
            alpha = clamp(s["life"]*4, 0, 160)
            surf = pygame.Surface((int(s["size"]*2), int(s["size"]*2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (shade,shade,shade,int(alpha)), (int(s["size"]), int(s["size"])), int(s["size"]))
            screen.blit(surf, (pos[0]-int(s["size"]), pos[1]-int(s["size"])))

def draw_shockwaves(offset):
    for w in shockwaves[:]:
        if not paused:
            w["r"] += 7; w["life"] -= 1
        if w["life"] <= 0 or w["r"] >= w["max"]:
            shockwaves.remove(w)
        else:
            pos = (int(w["x"]+offset[0]), int(w["y"]+offset[1]))
            alpha_factor = clamp(w["life"]/25, 0, 1)
            ring = pygame.Surface((w["r"]*2+8, w["r"]*2+8), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*w["color"], int(220*alpha_factor)), (ring.get_width()//2, ring.get_height()//2), int(w["r"]), 3)
            screen.blit(ring, (pos[0]-ring.get_width()//2, pos[1]-ring.get_height()//2))

def spawn_enemy():
    x = random.randint(45, WIDTH-90)
    enemies.append(pygame.Rect(x, -60, 52, 60))

def shoot():
    global weapon, shoot_delay, ammo_2, ammo_3, ammo_5, ammo_6
    global reload_2, reload_3, reload_5, reload_6
    global laser_active, laser_timer, fan_cannon_anim, nose_cannon_anim, laser_open_anim, bomb_fusion_anim, pending_fused_bomb

    if weapon == 1:
        bullets.append({"rect":pygame.Rect(player.centerx-4, player.top, 8, 20), "dx":0, "dy":-10, "color":YELLOW})
        shoot_delay = 6

    elif weapon == 2:
        if ammo_2 > 0:
            fan_cannon_anim = 34
            # Canons qui sortent des deux ailes puis tirent en eventail.
            origins = [(player.centerx-54, player.centery+8), (player.centerx+54, player.centery+8)]
            for ox, oy in origins:
                for dx, dy in [(-6,-8),(-3,-10),(0,-11),(3,-10),(6,-8)]:
                    bullets.append({"rect":pygame.Rect(ox-4, oy-8, 8, 20), "dx":dx, "dy":dy, "color":YELLOW, "type":"fan"})
            ammo_2 -= 1
            shoot_delay = 13
        if ammo_2 <= 0:
            reload_2 = reload_time_2
            set_weapon(1)

    elif weapon == 3:
        if ammo_3 > 0:
            nose_cannon_anim = 38
            for ox in [player.centerx-13, player.centerx+13]:
                bullets.append({"rect":pygame.Rect(ox-4, player.top-22, 8, 26), "dx":-1 if ox < player.centerx else 1, "dy":-13, "color":PURPLE, "type":"nose"})
                bullets.append({"rect":pygame.Rect(ox-4, player.top-22, 8, 26), "dx":0, "dy":-14, "color":WHITE, "type":"nose"})
            ammo_3 -= 1
            shoot_delay = 15
        if ammo_3 <= 0:
            reload_3 = reload_time_3
            set_weapon(1)

    elif weapon == 4:
        if laser_reload == 0 and not laser_active:
            laser_open_anim = 45
            laser_active = True
            laser_timer = laser_duration
        # L'arme 4 reste visible pendant toute la duree du laser.

    elif weapon == 5:
        if ammo_5 > 0 and reload_5 == 0:
            # La vraie bombe n'apparait qu'apres la fusion des deux pods devant l'avion.
            bomb_fusion_anim = 48
            pending_fused_bomb = {"x": player.centerx, "y": player.top-62, "timer": 20}
            ammo_5 -= 1
            shoot_delay = 42
            if ammo_5 <= 0:
                reload_5 = reload_time_5
                set_weapon(1)
        # Sinon l'arme 5 reste visible tant qu'il reste des bombes.

    elif weapon == 6:
        if ammo_6 > 0 and reload_6 == 0 and player_hp < max_hp:
            heal_player(20)
            ammo_6 -= 1
            shoot_delay = 30
            if ammo_6 <= 0:
                reload_6 = reload_time_6
                set_weapon(1)
        # Sinon l'arme 6 reste visible tant qu'il reste des soins.

def recharge_weapons():
    global ammo_2, ammo_3, ammo_5, ammo_6
    global reload_2, reload_3, reload_5, reload_6
    global laser_active, laser_timer, laser_reload
    global fan_cannon_anim, nose_cannon_anim, laser_open_anim, bomb_fusion_anim, heal_anim, pending_fused_bomb

    if reload_2 > 0:
        reload_2 -= 1
        if reload_2 == 0: ammo_2 = max_ammo_2
    if reload_3 > 0:
        reload_3 -= 1
        if reload_3 == 0: ammo_3 = max_ammo_3
    if reload_5 > 0:
        reload_5 -= 1
        if reload_5 == 0: ammo_5 = max_ammo_5
    if reload_6 > 0:
        reload_6 -= 1
        if reload_6 == 0: ammo_6 = max_ammo_6

    if fan_cannon_anim > 0: fan_cannon_anim -= 1
    if nose_cannon_anim > 0: nose_cannon_anim -= 1
    if laser_open_anim > 0: laser_open_anim -= 1
    if bomb_fusion_anim > 0: bomb_fusion_anim -= 1
    if heal_anim > 0: heal_anim -= 1

    if pending_fused_bomb:
        pending_fused_bomb["timer"] -= 1
        if pending_fused_bomb["timer"] <= 0:
            bombs.append({"rect": pygame.Rect(int(pending_fused_bomb["x"])-13, int(pending_fused_bomb["y"])-13, 26, 26), "born": 16})
            add_sparks(pending_fused_bomb["x"], pending_fused_bomb["y"], ORANGE, 35, 8)
            pending_fused_bomb = None

    if laser_active:
        laser_timer -= 1
        # Hitbox du laser qui part du tube sorti du nez.
        bullets.append({"rect":pygame.Rect(player.centerx-12, 0, 24, player.top-64), "dx":0, "dy":0, "color":PURPLE, "laser":True})
        if laser_timer <= 0:
            laser_active = False
            laser_reload = laser_reload_time
            if weapon == 4:
                set_weapon(1)
    if laser_reload > 0:
        laser_reload -= 1

def ammo_text(value, reload):
    return 'R'+str(reload//60+1) if reload>0 else str(value)

WEAPON_COLORS = {1: YELLOW, 2: YELLOW, 3: PURPLE, 4: ELECTRIC, 5: ORANGE, 6: GREEN}

def draw_weapon_slot(cx, cy, num, ammo, maxammo, reload, active):
    color = WEAPON_COLORS[num]
    ready = reload == 0 and (ammo is None or ammo > 0)
    box = pygame.Rect(0,0,46,46); box.center = (cx,cy)
    bg = color if ready else DARK_GRAY
    panel_col = (*[c//4 for c in bg], 255) if not active else (*[min(255,c//2+40) for c in bg], 255)
    pygame.draw.rect(screen, (18,20,40), box, border_radius=10)
    pygame.draw.rect(screen, bg if ready else GRAY, box, 2 if not active else 3, border_radius=10)
    label = font_small.render(str(num), True, WHITE if ready else GRAY)
    screen.blit(label, label.get_rect(center=(cx, cy-9)))
    if ammo is None:
        txt = "ON" if reload == -1 else ("OK" if ready else "R"+str(max(1,reload//60+1)))
    else:
        txt = ammo_text(ammo, reload)
    txt_surf = font_small.render(txt, True, color if ready else GRAY)
    screen.blit(txt_surf, txt_surf.get_rect(center=(cx, cy+11)))
    if ammo is not None and maxammo:
        bar = pygame.Rect(0,0,34,4); bar.center=(cx, cy+21)
        pygame.draw.rect(screen, (30,30,45), bar, border_radius=2)
        fill = bar.copy(); fill.width = int(34 * clamp(ammo/maxammo,0,1))
        pygame.draw.rect(screen, color if ready else GRAY, fill, border_radius=2)

def draw_hud():
    panel = pygame.Rect(8,8,WIDTH-16,64)
    vertical_gradient_rect(panel, (14,16,42), (8,9,26), radius=10)
    pygame.draw.rect(screen, (90,105,170), panel, 2, border_radius=10)

    screen.blit(font.render(f"Score {score}", True, WHITE), (18,14))
    screen.blit(font_small.render(f"Difficulte {difficulty_level}", True, (170,180,220)), (18,40))

    bar_rect = pygame.Rect(150,17,150,18)
    pygame.draw.rect(screen, (50,15,22), bar_rect, border_radius=9)
    hp_width = int(150 * player_hp / max_hp)
    hp_color = GREEN if player_hp > 45 else ORANGE if player_hp > 20 else RED
    if hp_width > 0:
        fill_rect = pygame.Rect(150,17,hp_width,18)
        vertical_gradient_rect(fill_rect, tuple(min(255,c+40) for c in hp_color), tuple(c//2 for c in hp_color), radius=9)
    pygame.draw.rect(screen, WHITE, bar_rect, 1, border_radius=9)
    screen.blit(font_small.render(f"Vie {player_hp}/{max_hp}", True, WHITE), (150,42))

    slots_x = [355, 400, 445, 490, 535]
    weapon_nums = [2,3,4,5,6]
    ammos = [ammo_2, ammo_3, None, ammo_5, ammo_6]
    maxammos = [max_ammo_2, max_ammo_3, None, max_ammo_5, max_ammo_6]
    reloads = [reload_2, reload_3, (-1 if laser_active else laser_reload), reload_5, reload_6]
    for i, num in enumerate(weapon_nums):
        draw_weapon_slot(slots_x[i], 39, num, ammos[i], maxammos[i], reloads[i], weapon == num)

    hint = font_small.render("ZQSD deplacer   ESPACE tirer   1-6 armes   P pause", True, (150,160,200))
    screen.blit(hint, (18, 76 if False else 76))

def reset_game():
    global score, weapon, previous_weapon, weapon_anim, weapon_changing
    global game_over, paused, start_countdown, player_hp, invincible_timer
    global spawn_timer, shoot_timer, enemy_shoot_timer
    global ammo_2, ammo_3, ammo_5, ammo_6, reload_2, reload_3, reload_5, reload_6
    global laser_active, laser_timer, laser_reload, difficulty_level
    global fan_cannon_anim, nose_cannon_anim, laser_open_anim, bomb_fusion_anim, heal_anim, pending_fused_bomb

    bullets.clear(); enemy_bullets.clear(); enemies.clear(); bombs.clear()
    particles.clear(); smokes.clear(); shockwaves.clear(); heal_effects.clear()
    player.x = WIDTH//2-24; player.y = HEIGHT-85
    player_hp = max_hp; invincible_timer = 0; score = 0
    weapon = 1; previous_weapon = 1; weapon_anim = 0; weapon_changing = False
    game_over = False; paused = False; start_countdown = 180
    spawn_timer = shoot_timer = enemy_shoot_timer = 0
    ammo_2, ammo_3, ammo_5, ammo_6 = max_ammo_2, max_ammo_3, max_ammo_5, max_ammo_6
    reload_2 = reload_3 = reload_5 = reload_6 = 0
    laser_active = False; laser_timer = 0; laser_reload = 0; difficulty_level = 1
    fan_cannon_anim = nose_cannon_anim = laser_open_anim = bomb_fusion_anim = heal_anim = 0
    pending_fused_bomb = None

while True:
    frame_count += 1
    offset = [0,0]
    if shake_timer > 0 and not paused:
        offset = [random.randint(-5,5), random.randint(-5,5)]
        shake_timer -= 1

    draw_background(offset)
    difficulty_level = max(1, 1 + score//10)
    enemy_speed = min(7, base_enemy_speed + difficulty_level*0.35)
    spawn_delay = max(18, base_spawn_delay - difficulty_level*4)
    enemy_shoot_delay = max(25, base_enemy_shoot_delay - difficulty_level*6)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not game_over and start_countdown <= 0:
                paused = not paused
            if game_over and event.key == pygame.K_r:
                reset_game()
            if not game_over and not paused and start_countdown <= 0:
                if event.key == pygame.K_1: set_weapon(1)
                elif event.key == pygame.K_2 and ammo_2 > 0 and reload_2 == 0: set_weapon(2)
                elif event.key == pygame.K_3 and ammo_3 > 0 and reload_3 == 0: set_weapon(3)
                elif event.key == pygame.K_4 and laser_reload == 0 and not laser_active: set_weapon(4)
                elif event.key == pygame.K_5 and ammo_5 > 0 and reload_5 == 0: set_weapon(5)
                elif event.key == pygame.K_6 and ammo_6 > 0 and reload_6 == 0: set_weapon(6)

    keys = pygame.key.get_pressed()

    if not game_over and not paused and start_countdown <= 0:
        recharge_weapons()
        if weapon_anim > 0:
            weapon_anim -= 1
            if weapon_anim <= 0: weapon_changing = False
        if invincible_timer > 0: invincible_timer -= 1

        if keys[pygame.K_q] and player.left > 0: player.x -= player_speed
        if keys[pygame.K_d] and player.right < WIDTH: player.x += player_speed
        if keys[pygame.K_z] and player.top > 80: player.y -= player_speed
        if keys[pygame.K_s] and player.bottom < HEIGHT: player.y += player_speed

        shoot_timer += 1
        if keys[pygame.K_SPACE] and shoot_timer >= shoot_delay:
            shoot(); shoot_timer = 0

        spawn_timer += 1
        if spawn_timer > spawn_delay:
            spawn_enemy(); spawn_timer = 0

        enemy_shoot_timer += 1
        if enemies and enemy_shoot_timer >= enemy_shoot_delay:
            enemy = random.choice(enemies)
            enemy_bullets.append(pygame.Rect(enemy.centerx-5, enemy.bottom, 10, 17))
            enemy_shoot_timer = 0

        for bomb in bombs[:]:
            bomb["rect"].y -= bomb_speed
            if bomb.get("born",0) > 0: bomb["born"] -= 1
            add_smoke(bomb["rect"].centerx, bomb["rect"].centery+8, 1)
            if bomb["rect"].bottom < 0:
                explode_bomb(bomb["rect"].centerx, bomb["rect"].centery)
                bombs.remove(bomb); continue
            for enemy in enemies[:]:
                if bomb["rect"].colliderect(enemy):
                    explode_bomb(bomb["rect"].centerx, bomb["rect"].centery)
                    if bomb in bombs: bombs.remove(bomb)
                    break

        for bullet in bullets[:]:
            if not bullet.get("laser", False):
                bullet["rect"].x += bullet["dx"]
                bullet["rect"].y += bullet["dy"]
            if bullet["rect"].bottom < 0 or bullet["rect"].right < 0 or bullet["rect"].left > WIDTH:
                if bullet in bullets: bullets.remove(bullet)

        for eb in enemy_bullets[:]:
            eb.y += 7
            if eb.top > HEIGHT:
                enemy_bullets.remove(eb)
            elif eb.colliderect(player):
                enemy_bullets.remove(eb); damage_player(20)

        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.top > HEIGHT:
                enemies.remove(enemy); score -= 1
            elif enemy.colliderect(player):
                big_explosion(enemy.centerx, enemy.centery, RED)
                enemies.remove(enemy); damage_player(35)

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet["rect"].colliderect(enemy):
                    add_sparks(enemy.centerx, enemy.centery, RED, 30, 7)
                    add_smoke(enemy.centerx, enemy.centery, 4)
                    if not bullet.get("laser", False) and bullet in bullets: bullets.remove(bullet)
                    if enemy in enemies: enemies.remove(enemy)
                    score += 1
                    break

        for bullet in bullets[:]:
            for eb in enemy_bullets[:]:
                if bullet["rect"].colliderect(eb):
                    add_sparks(eb.centerx, eb.centery, GREEN, 12, 5)
                    if not bullet.get("laser", False) and bullet in bullets: bullets.remove(bullet)
                    if eb in enemy_bullets: enemy_bullets.remove(eb)
                    break

        bullets[:] = [b for b in bullets if not b.get("laser", False)]

    draw_smoke(offset)
    draw_shockwaves(offset)

    # Bombe en fusion avant lancement
    if pending_fused_bomb:
        fx = int(pending_fused_bomb["x"] + offset[0])
        fy = int(pending_fused_bomb["y"] + offset[1])
        draw_circle(ORANGE, (fx, fy), 17)
        draw_circle(YELLOW, (fx, fy), 9)
        draw_circle(WHITE, (fx, fy), 4)
        if random.random() < 0.5:
            add_sparks(fx, fy, ORANGE, 2, 4)

    for bullet in bullets:
        r = bullet["rect"].move(offset)
        color = bullet["color"]
        if bullet.get("laser", False):
            continue
        width = 6 if bullet.get("type") in ("fan","nose") else 5
        pygame.draw.line(screen, color, r.midbottom, r.midtop, width)
        draw_circle(WHITE, r.midtop, 3)

    for bomb in bombs:
        b = bomb["rect"].move(offset)
        extra = bomb.get("born",0)
        draw_circle(ORANGE, b.center, 15 + extra//3)
        draw_circle(YELLOW, b.center, 8)
        draw_circle(WHITE, b.center, 3)

    if laser_active and not game_over:
        tube_y = player.top - 22
        width = random.randint(14,24) if not paused else 18
        laser_rect = pygame.Rect(player.centerx-width//2+offset[0], 0, width, tube_y)
        glow_surf = pygame.Surface((width+50, tube_y), pygame.SRCALPHA)
        screen.blit(glow_surf, (laser_rect.x-25, 0), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.rect(screen, WHITE, (player.centerx-3+offset[0], 0, 6, tube_y))
        for _ in range(4):
            draw_electric_line((player.centerx+offset[0], tube_y+offset[1]), (player.centerx+random.randint(-35,35)+offset[0], random.randint(0, tube_y)+offset[1]), CYAN, 2, 10, 8)

    for eb in enemy_bullets:
        e = eb.move(offset)
        draw_circle(GREEN, e.center, 7)
        draw_circle(WHITE, e.center, 3)

    for enemy in enemies:
        draw_enemy(enemy, offset)

    draw_player(offset)
    draw_particles(offset)

    draw_hud()

    if start_countdown > 0 and not game_over and not paused:
        number = min(3, start_countdown//60 + 1)
        txt = big_font.render(str(number), True, WHITE)
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        start_countdown -= 1

    if paused:
        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        screen.blit(overlay, (0,0))
        txt = big_font.render("PAUSE", True, WHITE)
        small = font.render("Appuie sur P pour reprendre", True, (200,210,240))
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2-25)))
        screen.blit(small, small.get_rect(center=(WIDTH//2, HEIGHT//2+35)))

    if game_over:
        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((20,0,0,140))
        screen.blit(overlay, (0,0))
        txt = big_font.render("GAME OVER", True, WHITE)
        restart = font.render("Appuie sur R pour recommencer", True, (220,190,190))
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2-30)))
        screen.blit(restart, restart.get_rect(center=(WIDTH//2, HEIGHT//2+35)))

    pygame.display.flip()
    clock.tick(FPS)