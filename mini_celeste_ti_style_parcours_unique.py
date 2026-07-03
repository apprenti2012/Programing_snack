import pygame
import sys
import math

pygame.init()

# ============================================================
# MINI CELESTE - STYLE CALCULATRICE TEXAS
# Jeu original inspiré des mécaniques de plateforme/dash.
# Commandes :
#   Q/D ou flèches gauche/droite : bouger
#   Z / haut / espace : sauter
#   X ou Shift : dash
#   R : recommencer le niveau
#   Echap : quitter
# ============================================================

SCALE = 4
TILE = 8
GRID_W, GRID_H = 40, 24
WIDTH, HEIGHT = GRID_W * TILE, GRID_H * TILE
SCREEN_W, SCREEN_H = WIDTH * SCALE, HEIGHT * SCALE
FPS = 60

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Mini Celeste TI Style")
clock = pygame.time.Clock()
canvas = pygame.Surface((WIDTH, HEIGHT))

# Palette noir/blanc/bleu style calculatrice rétro
BLACK = (7, 10, 18)
DARK = (18, 25, 45)
MID = (45, 65, 95)
LIGHT = (150, 185, 220)
WHITE = (235, 245, 255)
BLUE = (70, 150, 255)
CYAN = (80, 230, 255)
RED = (255, 70, 90)
PINK = (255, 120, 180)
GREEN = (100, 255, 160)
YELLOW = (255, 230, 90)
PURPLE = (185, 100, 255)
ORANGE = (255, 160, 70)

font = pygame.font.SysFont("consolas", 8, bold=True)
big_font = pygame.font.SysFont("consolas", 14, bold=True)

GRAVITY = 0.33
MOVE_ACCEL = 0.48
FRICTION = 0.78
MAX_SPEED = 1
JUMP_SPEED = -5.0
WALL_JUMP_X = 3.4
WALL_JUMP_Y = -5.2
WALL_SLIDE_SPEED = 1.15
DASH_SPEED = 5.8
DASH_TIME = 12
COYOTE_TIME = 8
JUMP_BUFFER = 8

# Symboles niveaux :
# # = mur / plateforme
# S = départ
# E = sortie
# ^ v < > = pics
# * = fraise
# R = recharge dash
# M = plateforme mobile horizontale
# T = trampoline
LEVELS = [
    # Niveau 1 : ligne simple, un seul chemin vers la sortie
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.............*........................#",
        "#............###.......................#",
        "#......................R...............#",
        "#.....................###..............#",
        "#..............................E.......#",
        "#.............................###......#",
        "#..................###.................#",
        "#......................................#",
        "#.........###..........................#",
        "#......................................#",
        "#.....###.....................^^^^.....#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 2 : montée en escalier, pas de bifurcation
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.................................E....#",
        "#................................###...#",
        "#............................###.......#",
        "#.......................R..............#",
        "#......................###.............#",
        "#.................###..................#",
        "#......................................#",
        "#............###.......................#",
        "#......................................#",
        "#.......###............................#",
        "#......................................#",
        "#...###................................#",
        "#......................................#",
        "#...................*..................#",
        "#..................###.................#",
        "#.........................^^^^.........#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 3 : couloir vertical avec wall jump obligatoire
    [
        "########################################",
        "#S.....................................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#######........R................#",
        "#......#.............###...............#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#.................*.............#",
        "#......#E...............###............#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#......#...............................#",
        "#..#####...............................#",
        "########################################",
    ],
    # Niveau 4 : dash horizontal, recharge au milieu
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#................R.....................#",
        "#...............###..............E.....#",
        "#...............................###....#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.......###............................#",
        "#......................................#",
        "#.....###..............*...............#",
        "#.....................###..............#",
        "#..........^^^^^^^^^^^^^^^^^^^^........#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 5 : trampoline puis dash
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#.................................E....#",
        "#................................###...#",
        "#..........................R...........#",
        "#.........................###..........#",
        "#......................................#",
        "#..................T...................#",
        "#.................###..................#",
        "#......................................#",
        "#............*.........................#",
        "#...........###........................#",
        "#......................................#",
        "#.......###............................#",
        "#......................................#",
        "#...###................................#",
        "#......................................#",
        "#......................................#",
        "#....................^^^^^^............#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 6 : petite plateforme mobile dans le chemin unique
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.................................E....#",
        "#................................###...#",
        "#...........................R..........#",
        "#..........................###.........#",
        "#....................M.................#",
        "#......................................#",
        "#...............###....................#",
        "#......................................#",
        "#..........###.........................#",
        "#......................................#",
        "#.....###..............................#",
        "#......................................#",
        "#..###............*....................#",
        "#................###...................#",
        "#.......................^^^^^^.........#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 7 : zigzag fermé, passage forcé
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#............###########################",
        "#......................................#",
        "###########################............#",
        "#......................................#",
        "#............###########################",
        "#......................................#",
        "###########################............#",
        "#......................................#",
        "#............###########################",
        "#......................................#",
        "#........R.............................#",
        "#.......###............................#",
        "#...................*..................#",
        "#..................###.................#",
        "#.................................E....#",
        "#................................###...#",
        "#.......................^^^^^^.........#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 8 : deux recharges en ligne droite technique
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.................................E....#",
        "#................................###...#",
        "#........................R.............#",
        "#.......................###............#",
        "#......................................#",
        "#................R.....................#",
        "#...............###....................#",
        "#......................................#",
        "#..........T...........................#",
        "#.........###..........................#",
        "#......................................#",
        "#.....###..............................#",
        "#......................................#",
        "#..###................*................#",
        "#....................###...............#",
        "#.............^^^^^^...................#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
    # Niveau 9 : montée mur + recharge + sortie
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#..............................E.......#",
        "#.............................###......#",
        "#......................................#",
        "#......................................#",
        "#....................*.................#",
        "#...................###................#",
        "#.........................R............#",
        "#........................###...........#",
        "#################......................#",
        "#......................^^^^^...........#",
        "#..............^^^^#####...............#",
        "#...............................####...#",
        "#...........###.^^^^^^^^^^^^^^.........#",
        "#......................................#",
        "#..#####...............................#",
        "########################################",
    ],
    # Niveau 10 : final, parcours unique avec toutes les mécaniques
    [
        "########################################",
        "#S.....................................#",
        "#......................................#",
        "#......................................#",
        "#......................................#",
        "#.................................E....#",
        "#................................###...#",
        "#...........................R..........#",
        "#..........................###.........#",
        "#....................T.................#",
        "#...................###................#",
        "#...............M......................#",
        "#......................................#",
        "#..........R...........................#",
        "#.........###..........................#",
        "#......................................#",
        "#.....###..............................#",
        "#......................................#",
        "#..###.............*...................#",
        "#.................###..................#",
        "#..........^^^^^^^^^^^^^^^^^^..........#",
        "#......................................#",
        "#......................................#",
        "########################################",
    ],
]

class Particle:
    def __init__(self, x, y, dx, dy, color, life=25):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.03
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.rect(surf, self.color, (int(self.x), int(self.y), 1, 1))

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 6, 7)
        self.dx = 0
        self.dy = 0
        self.on_ground = False
        self.on_wall = 0
        self.dashes = 1
        self.dashing = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.facing = 1
        self.coyote = 0
        self.jump_buffer = 0
        self.dead_timer = 0
        self.respawn_flash = 0

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.dx = 0
        self.dy = 0
        self.dashes = 1
        self.dashing = 0
        self.dead_timer = 0
        self.respawn_flash = 25

    def kill(self, particles):
        if self.dead_timer == 0:
            self.dead_timer = 25
            for i in range(18):
                a = i / 18 * math.pi * 2
                particles.append(Particle(self.rect.centerx, self.rect.centery, math.cos(a)*1.4, math.sin(a)*1.4, RED, 22))

class Level:
    def __init__(self, data):
        self.data = [list(row) for row in data]
        self.walls = []
        self.spikes = []
        self.berries = []
        self.recharges = []
        self.trampolines = []
        self.movers = []
        self.exit = pygame.Rect(0, 0, 8, 8)
        self.start = (16, 16)
        self.collected = 0
        self.total_berries = 0
        self.parse()

    def parse(self):
        for y, row in enumerate(self.data):
            for x, ch in enumerate(row):
                rx, ry = x*TILE, y*TILE
                if ch == '#':
                    self.walls.append(pygame.Rect(rx, ry, TILE, TILE))
                elif ch == 'S':
                    self.start = (rx+1, ry+1)
                elif ch == 'E':
                    self.exit = pygame.Rect(rx+1, ry+1, 6, 6)
                elif ch in '^v<>':
                    self.spikes.append((pygame.Rect(rx, ry, TILE, TILE), ch))
                elif ch == '*':
                    self.berries.append({"rect": pygame.Rect(rx+2, ry+2, 4, 4), "got": False, "phase": (x+y)%20})
                    self.total_berries += 1
                elif ch == 'R':
                    self.recharges.append({"rect": pygame.Rect(rx+1, ry+1, 6, 6), "active": True, "timer": 0})
                elif ch == 'T':
                    self.trampolines.append(pygame.Rect(rx, ry+5, TILE, 3))
                elif ch == 'M':
                    self.movers.append({"rect": pygame.Rect(rx, ry, 18, 5), "base_x": rx, "dir": 1, "range": 44, "speed": 0.8})

    def solid_rects(self):
        return self.walls + [m["rect"] for m in self.movers]

    def update_movers(self, player):
        for m in self.movers:
            old_x = m["rect"].x
            m["rect"].x += m["dir"] * m["speed"]
            if abs(m["rect"].x - m["base_x"]) > m["range"]:
                m["dir"] *= -1
            move = m["rect"].x - old_x
            player_feet = pygame.Rect(player.rect.x, player.rect.bottom, player.rect.w, 2)
            if player_feet.colliderect(m["rect"]):
                player.rect.x += int(round(move))


def rect_collides(rect, solids):
    return [s for s in solids if rect.colliderect(s)]


def touching_wall(player, solids):
    left_probe = player.rect.move(-1, 0)
    right_probe = player.rect.move(1, 0)
    touch_left = any(left_probe.colliderect(s) for s in solids)
    touch_right = any(right_probe.colliderect(s) for s in solids)
    if touch_left and not player.on_ground:
        return -1
    if touch_right and not player.on_ground:
        return 1
    return 0


def move_axis(player, solids, axis):
    if axis == 'x':
        player.rect.x += int(round(player.dx))
        hits = rect_collides(player.rect, solids)
        for h in hits:
            if player.dx > 0:
                player.rect.right = h.left
                player.on_wall = 1
            elif player.dx < 0:
                player.rect.left = h.right
                player.on_wall = -1
            player.dx = 0
    else:
        player.rect.y += int(round(player.dy))
        hits = rect_collides(player.rect, solids)
        player.on_ground = False
        for h in hits:
            if player.dy > 0:
                player.rect.bottom = h.top
                player.on_ground = True
                player.coyote = COYOTE_TIME
                player.dashes = 1
            elif player.dy < 0:
                player.rect.top = h.bottom
            player.dy = 0


def draw_tile(surf, rect):
    pygame.draw.rect(surf, MID, rect)
    pygame.draw.line(surf, LIGHT, (rect.left, rect.top), (rect.right-1, rect.top))
    pygame.draw.line(surf, DARK, (rect.left, rect.bottom-1), (rect.right-1, rect.bottom-1))
    pygame.draw.rect(surf, BLACK, rect, 1)


def draw_spike(surf, rect, direction):
    if direction == '^':
        pts = [(rect.left, rect.bottom), (rect.centerx, rect.top), (rect.right, rect.bottom)]
    elif direction == 'v':
        pts = [(rect.left, rect.top), (rect.centerx, rect.bottom), (rect.right, rect.top)]
    elif direction == '<':
        pts = [(rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)]
    else:
        pts = [(rect.left, rect.top), (rect.right, rect.centery), (rect.left, rect.bottom)]
    pygame.draw.polygon(surf, RED, pts)
    pygame.draw.polygon(surf, WHITE, pts, 1)


def draw_player(surf, player, frame):
    r = player.rect
    if player.respawn_flash > 0 and frame % 6 < 3:
        return
    # Corps pixel-art
    pygame.draw.rect(surf, PINK, r)
    pygame.draw.rect(surf, WHITE, (r.x+1, r.y+1, 2, 2))
    # Cheveux / direction
    hx = r.x - 2 if player.facing < 0 else r.right
    pygame.draw.rect(surf, RED, (hx, r.y+1, 2, 3))
    # Indicateur dash disponible
    if player.dashes > 0:
        pygame.draw.rect(surf, CYAN, (r.x+2, r.y-2, 2, 1))


def draw_level(surf, level, frame):
    surf.fill(BLACK)
    # grille rétro
    for x in range(0, WIDTH, TILE):
        pygame.draw.line(surf, (10, 15, 28), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE):
        pygame.draw.line(surf, (10, 15, 28), (0, y), (WIDTH, y))

    for wall in level.walls:
        draw_tile(surf, wall)

    for m in level.movers:
        pygame.draw.rect(surf, PURPLE, m["rect"])
        pygame.draw.rect(surf, WHITE, m["rect"], 1)

    for sp, direction in level.spikes:
        draw_spike(surf, sp, direction)

    for t in level.trampolines:
        pygame.draw.rect(surf, GREEN, t)
        pygame.draw.line(surf, WHITE, t.topleft, t.topright)

    for b in level.berries:
        if not b["got"]:
            bob = int(math.sin((frame+b["phase"])*0.18)*1)
            rr = b["rect"].move(0, bob)
            pygame.draw.rect(surf, RED, rr)
            pygame.draw.rect(surf, WHITE, (rr.x+1, rr.y, 1, 1))

    for rc in level.recharges:
        if rc["active"]:
            pygame.draw.rect(surf, CYAN, rc["rect"])
            pygame.draw.rect(surf, WHITE, rc["rect"], 1)
        else:
            pygame.draw.rect(surf, DARK, rc["rect"], 1)

    pygame.draw.rect(surf, GREEN, level.exit)
    pygame.draw.rect(surf, WHITE, level.exit, 1)


def draw_hud(surf, level_index, level, player, deaths, total_berries):
    pygame.draw.rect(surf, BLACK, (0, 0, WIDTH, 10))
    txt = f"NIV {level_index+1}/{len(LEVELS)}  FRAISES {total_berries+level.collected}  MORTS {deaths}  DASH {'OK' if player.dashes else '--'}"
    surf.blit(font.render(txt, True, WHITE), (2, 1))


def make_level(index):
    level = Level(LEVELS[index])
    player = Player(level.start[0], level.start[1])
    return level, player

level_index = 0
level, player = make_level(level_index)
particles = []
frame = 0
deaths = 0
total_berries = 0
win = False
message_timer = 140

while True:
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r and not win:
                player.kill(particles)
            if event.key in (pygame.K_z, pygame.K_UP, pygame.K_SPACE):
                player.jump_buffer = JUMP_BUFFER
            if event.key in (pygame.K_x, pygame.K_LSHIFT, pygame.K_RSHIFT) and not win:
                if player.dashes > 0 and player.dashing <= 0 and player.dead_timer == 0:
                    keys = pygame.key.get_pressed()
                    ax = (1 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_q] or keys[pygame.K_LEFT] else 0)
                    ay = (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_z] or keys[pygame.K_UP] else 0)
                    if ax == 0 and ay == 0:
                        ax = player.facing
                    length = math.hypot(ax, ay)
                    ax, ay = ax/length, ay/length
                    player.dashing = DASH_TIME
                    player.dash_dx = ax * DASH_SPEED
                    player.dash_dy = ay * DASH_SPEED
                    player.dx = player.dash_dx
                    player.dy = player.dash_dy
                    player.dashes -= 1
                    for i in range(12):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, -ax*1.5 + (i%3-1)*0.3, -ay*1.5 + (i//3-1)*0.2, CYAN, 18))

    if not win:
        keys = pygame.key.get_pressed()

        if player.dead_timer > 0:
            player.dead_timer -= 1
            if player.dead_timer == 0:
                deaths += 1
                # on garde les fraises prises dans le niveau actuel
                player.reset()
        else:
            level.update_movers(player)
            solids = level.solid_rects()
            player.on_wall = touching_wall(player, solids)

            left = keys[pygame.K_q] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            if left:
                player.dx -= MOVE_ACCEL
                player.facing = -1
            if right:
                player.dx += MOVE_ACCEL
                player.facing = 1
            if not left and not right and player.dashing <= 0:
                player.dx *= FRICTION
                if abs(player.dx) < 0.05:
                    player.dx = 0
            player.dx = max(-MAX_SPEED, min(MAX_SPEED, player.dx)) if player.dashing <= 0 else player.dx

            if player.jump_buffer > 0:
                player.jump_buffer -= 1
            if player.coyote > 0:
                player.coyote -= 1

            if player.dashing > 0:
                player.dashing -= 1
                if player.dashing == 0:
                    player.dx *= 0.45
                    player.dy *= 0.45
            else:
                player.dy += GRAVITY
                # Glissade sur les murs : on tombe lentement contre un mur.
                player.on_wall = touching_wall(player, solids)
                if player.on_wall != 0 and player.dy > WALL_SLIDE_SPEED and (left or right):
                    player.dy = WALL_SLIDE_SPEED
                    if frame % 5 == 0:
                        px = player.rect.left if player.on_wall < 0 else player.rect.right
                        particles.append(Particle(px, player.rect.centery, -player.on_wall*0.25, 0.35, LIGHT, 12))
                player.dy = min(player.dy, 5.5)

            # Saut normal ou wall jump avec buffer.
            # Le test du mur est fait AVANT le déplacement, donc le wall jump répond tout de suite.
            wall_now = touching_wall(player, solids)
            if player.jump_buffer > 0:
                if player.on_ground or player.coyote > 0:
                    player.dy = JUMP_SPEED
                    player.jump_buffer = 0
                    player.coyote = 0
                    for i in range(6):
                        particles.append(Particle(player.rect.centerx, player.rect.bottom, (i-3)*0.15, 0.8, WHITE, 14))
                elif wall_now != 0:
                    player.dx = -wall_now * WALL_JUMP_X
                    player.dy = WALL_JUMP_Y
                    player.jump_buffer = 0
                    player.dashes = 1
                    player.facing = -wall_now
                    for i in range(8):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, wall_now*0.4, (i-4)*0.15, CYAN, 16))

            move_axis(player, solids, 'x')
            player.on_wall = touching_wall(player, solids)
            move_axis(player, solids, 'y')

            # Trampolines
            for t in level.trampolines:
                if player.rect.colliderect(t) and player.dy >= 0:
                    player.rect.bottom = t.top
                    player.dy = -7.2
                    player.dashes = 1
                    for i in range(12):
                        particles.append(Particle(t.centerx, t.y, (i-6)*0.12, -1.2, GREEN, 18))

            # Pics
            for sp, direction in level.spikes:
                if player.rect.colliderect(sp):
                    player.kill(particles)
                    break

            # Hors écran
            if player.rect.top > HEIGHT:
                player.kill(particles)

            # Fraises
            for b in level.berries:
                if not b["got"] and player.rect.colliderect(b["rect"]):
                    b["got"] = True
                    level.collected += 1
                    for i in range(14):
                        a = i/14*math.pi*2
                        particles.append(Particle(b["rect"].centerx, b["rect"].centery, math.cos(a), math.sin(a), RED, 20))

            # Recharge dash
            for rc in level.recharges:
                if rc["active"] and player.rect.colliderect(rc["rect"]):
                    player.dashes = 1
                    rc["active"] = False
                    rc["timer"] = 150
                    for i in range(16):
                        a = i/16*math.pi*2
                        particles.append(Particle(rc["rect"].centerx, rc["rect"].centery, math.cos(a)*1.1, math.sin(a)*1.1, CYAN, 20))
                elif not rc["active"]:
                    rc["timer"] -= 1
                    if rc["timer"] <= 0:
                        rc["active"] = True

            # Sortie
            if player.rect.colliderect(level.exit):
                total_berries += level.collected
                level_index += 1
                if level_index >= len(LEVELS):
                    win = True
                else:
                    level, player = make_level(level_index)
                    message_timer = 90

        if player.respawn_flash > 0:
            player.respawn_flash -= 1

    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)

    draw_level(canvas, level, frame)
    for p in particles:
        p.draw(canvas)
    if not win and player.dead_timer == 0:
        draw_player(canvas, player, frame)
    draw_hud(canvas, level_index if not win else len(LEVELS)-1, level, player, deaths, total_berries)

    if message_timer > 0 and not win:
        message_timer -= 1
        msg = "X = DASH   MUR + SAUT = WALL JUMP"
        canvas.blit(font.render(msg, True, WHITE), (WIDTH//2 - 45, HEIGHT//2 - 4))

    if win:
        pygame.draw.rect(canvas, BLACK, (30, 55, WIDTH-60, 78))
        pygame.draw.rect(canvas, WHITE, (30, 55, WIDTH-60, 78), 1)
        canvas.blit(big_font.render("BRAVO !", True, WHITE), (WIDTH//2-32, 66))
        canvas.blit(font.render(f"Fraises : {total_berries}", True, RED), (WIDTH//2-38, 88))
        canvas.blit(font.render(f"Morts : {deaths}", True, WHITE), (WIDTH//2-30, 101))
        canvas.blit(font.render("ECHAP POUR QUITTER", True, CYAN), (WIDTH//2-55, 116))

    scaled = pygame.transform.scale(canvas, (SCREEN_W, SCREEN_H))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
