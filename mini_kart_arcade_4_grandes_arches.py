import pygame, math, random, sys

# ============================================================
# MINI KART ARCADE 4 - Grandes arches
# - Route plus propre, sans gros cercles visibles
# - Bordures mieux dessinées
# - Checkpoints discrets et propres, sous forme de petits portiques
# - Vrai détecteur de tours conservé
#
# Commandes :
#   Z / Flèche haut      : accélérer
#   S / Flèche bas       : freiner / reculer
#   Q / Flèche gauche    : tourner gauche
#   D / Flèche droite    : tourner droite
#   ESPACE               : dérapage
#   R                    : recommencer
#   ECHAP                : quitter
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Kart Arcade 4")
clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)
big_font = pygame.font.SysFont(None, 72)

WHITE=(245,245,245)
BLACK=(8,8,12)
GRAY=(115,115,125)
DARK=(25,25,35)
ROAD=(58,58,64)
ROAD_DARK=(43,43,49)
GRASS=(34,118,54)
GRASS2=(29,103,48)
RED=(230,55,55)
BLUE=(55,120,245)
YELLOW=(255,220,70)
ORANGE=(255,150,45)
GREEN=(70,230,120)
PURPLE=(180,80,255)
CYAN=(80,230,255)
BROWN=(135,80,35)

TOTAL_LAPS = 3
TRACK_WIDTH = 104

# Parcours plus joli : moins rond, plus circuit avec virages variés.
track_points = [
    (190,560), (135,475), (130,350), (175,235),
    (300,155), (460,135), (640,160), (785,235),
    (845,350), (805,470), (690,545), (520,575),
    (350,555), (245,505)
]

# Points de contrôle plus courts, placés au centre de la route.
checkpoint_lines = [
    ((172,585), (210,535)),   # départ
    ((116,455), (165,455)),
    ((145,285), (190,305)),
    ((305,130), (315,178)),
    ((555,132), (545,184)),
    ((755,215), (725,255)),
    ((826,350), (775,350)),
    ((780,485), (742,452)),
    ((575,560), (575,512)),
    ((335,565), (352,518)),
]

boost_positions = [(165,370), (390,150), (735,230), (780,455), (505,560)]
banana_positions = [(240,515), (160,260), (650,175), (780,365), (390,555)]

def vec(p):
    return pygame.Vector2(p)

def dist_to_segment(p, a, b):
    p, a, b = vec(p), vec(a), vec(b)
    ab = b - a
    if ab.length_squared() == 0:
        return (p-a).length()
    t = max(0, min(1, (p-a).dot(ab) / ab.length_squared()))
    return (p - (a + ab*t)).length()

def on_road(pos):
    return any(
        dist_to_segment(pos, track_points[i], track_points[(i+1)%len(track_points)]) <= TRACK_WIDTH/2
        for i in range(len(track_points))
    )

def angle_to(src, dst):
    d = vec(dst) - vec(src)
    if d.length_squared() == 0:
        return 0
    return math.degrees(math.atan2(-d.y, d.x))

def draw_text(txt, x, y, col=WHITE, fnt=None, center=False):
    img = (fnt or font).render(txt, True, col)
    rect = img.get_rect()
    if center:
        rect.center = (x,y)
    else:
        rect.topleft = (x,y)
    screen.blit(img, rect)

def point_near_checkpoint(pos, index):
    a,b = checkpoint_lines[index]
    return dist_to_segment(pos, a, b) < 22

def make_track_surface():
    """Prépare une piste propre sur une surface séparée."""
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pts = track_points + [track_points[0]]

    # Ombre extérieure
    pygame.draw.lines(surf, (0,0,0,120), True, [(x+5,y+5) for x,y in pts], TRACK_WIDTH+24)
    for p in pts[:-1]:
        pygame.draw.circle(surf, (0,0,0,120), (p[0]+5,p[1]+5), TRACK_WIDTH//2+12)

    # Bord extérieur clair
    pygame.draw.lines(surf, (220,220,220), True, pts, TRACK_WIDTH+16)
    for p in pts[:-1]:
        pygame.draw.circle(surf, (220,220,220), p, TRACK_WIDTH//2+8)

    # Vibreurs rouges/blancs le long de certains segments
    for i in range(len(track_points)):
        a = vec(track_points[i])
        b = vec(track_points[(i+1)%len(track_points)])
        d = b-a
        if d.length_squared() == 0:
            continue
        d = d.normalize()
        n = pygame.Vector2(-d.y, d.x)
        length = a.distance_to(b)
        steps = max(1, int(length//22))
        for s in range(steps):
            if s % 2 == 0:
                color = RED
            else:
                color = WHITE
            center = a + d*(s*22+11)
            for side in [-1, 1]:
                c = center + n*side*(TRACK_WIDTH//2+3)
                r = pygame.Rect(0,0,16,8)
                r.center = c
                pygame.draw.rect(surf, color, r, border_radius=2)

    # Route principale
    pygame.draw.lines(surf, ROAD, True, pts, TRACK_WIDTH)
    for p in pts[:-1]:
        pygame.draw.circle(surf, ROAD, p, TRACK_WIDTH//2)

    # Légère route intérieure plus sombre pour donner du relief
    pygame.draw.lines(surf, ROAD_DARK, True, pts, TRACK_WIDTH-18)
    for p in pts[:-1]:
        pygame.draw.circle(surf, ROAD_DARK, p, TRACK_WIDTH//2-9)

    # Couche centrale normale pour adoucir
    pygame.draw.lines(surf, ROAD, True, pts, TRACK_WIDTH-34)
    for p in pts[:-1]:
        pygame.draw.circle(surf, ROAD, p, TRACK_WIDTH//2-17)

    # Pointillés centraux propres
    for i in range(len(track_points)):
        a = vec(track_points[i])
        b = vec(track_points[(i+1)%len(track_points)])
        length = a.distance_to(b)
        if length == 0:
            continue
        direction = (b-a).normalize()
        steps = int(length//42)
        for s in range(steps):
            if s % 2 == 0:
                p1 = a + direction*(s*42+12)
                p2 = a + direction*(s*42+28)
                pygame.draw.line(surf, (205,205,205), p1, p2, 3)

    return surf

track_surface = make_track_surface()

class Kart:
    def __init__(self, x, y, color, is_player=False):
        self.pos = pygame.Vector2(x,y)
        self.vel = pygame.Vector2()
        self.angle = 0
        self.color = color
        self.is_player = is_player
        self.radius = 14
        self.max_speed = 6.4 if is_player else 5.15
        self.accel = 0.18 if is_player else 0.145
        self.friction = 0.966
        self.turn_speed = 3.5
        self.drift = False
        self.boost_timer = 0
        self.stun_timer = 0
        self.next_cp = 0
        self.cp_seen = [False] * len(checkpoint_lines)
        self.lap = 1
        self.finished = False
        self.finish_ms = None
        self.ai_target = 1

    def forward(self):
        return pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))

    def update_player(self, keys):
        if self.finished:
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel *= 0.93
            self.move()
            return

        f = self.forward()

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.vel += f * self.accel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel -= f * (self.accel * 0.68)

        speed = self.vel.length()
        self.drift = keys[pygame.K_SPACE] and speed > 2.1

        turn = 0
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            turn += 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            turn -= 1

        steer = min(1.0, speed / 2.3)
        self.angle += turn * self.turn_speed * steer * (1.55 if self.drift else 1.0)

        max_spd = self.max_speed + (3.1 if self.boost_timer > 0 else 0)
        if self.boost_timer > 0:
            self.boost_timer -= 1

        if self.vel.length() > max_spd:
            self.vel.scale_to_length(max_spd)

        self.surface_physics()
        self.move()
        self.update_checkpoints()

    def update_ai(self):
        if self.finished:
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel *= 0.94
            self.move()
            return

        target = pygame.Vector2(track_points[self.ai_target])
        wanted = angle_to(self.pos, target)
        diff = (wanted - self.angle + 180) % 360 - 180
        self.angle += max(-2.4, min(2.4, diff * 0.065))
        self.vel += self.forward() * self.accel

        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        if self.pos.distance_to(target) < 75:
            self.ai_target = (self.ai_target + 1) % len(track_points)

        self.surface_physics()
        self.move()
        self.update_checkpoints()

    def surface_physics(self):
        if not on_road(self.pos):
            self.vel *= 0.82
        else:
            self.vel *= 0.995

        if self.drift:
            side = pygame.Vector2(-self.forward().y, self.forward().x)
            self.vel += side * random.uniform(-0.09, 0.09)

    def move(self):
        self.pos += self.vel
        self.vel *= self.friction
        self.pos.x = max(18, min(WIDTH-18, self.pos.x))
        self.pos.y = max(70, min(HEIGHT-18, self.pos.y))

    def update_checkpoints(self):
        if point_near_checkpoint(self.pos, self.next_cp):
            if self.next_cp == 0:
                if all(self.cp_seen[1:]):
                    self.lap += 1
                    self.cp_seen = [False] * len(checkpoint_lines)
                    if self.lap > TOTAL_LAPS:
                        self.finished = True
                        self.finish_ms = pygame.time.get_ticks()
                        return
                self.cp_seen[0] = True
                self.next_cp = 1
            else:
                self.cp_seen[self.next_cp] = True
                self.next_cp += 1
                if self.next_cp >= len(checkpoint_lines):
                    self.next_cp = 0

    def draw(self):
        f = self.forward()
        side = pygame.Vector2(-f.y, f.x)
        p1 = self.pos + f*23
        p2 = self.pos - f*18 + side*14
        p3 = self.pos - f*18 - side*14

        shadow = pygame.Vector2(3,3)
        pygame.draw.polygon(screen, BLACK, [p1+shadow, p2+shadow, p3+shadow])
        pygame.draw.polygon(screen, self.color, [p1,p2,p3])
        pygame.draw.line(screen, WHITE, self.pos + side*8, self.pos - side*8, 3)
        pygame.draw.circle(screen, WHITE, self.pos + f*7, 5)
        pygame.draw.circle(screen, BLACK, self.pos + f*7, 2)

        for wheel in [
            self.pos + side*13 + f*8, self.pos - side*13 + f*8,
            self.pos + side*13 - f*10, self.pos - side*13 - f*10
        ]:
            pygame.draw.circle(screen, DARK, wheel, 4)

        if self.boost_timer > 0:
            flame = self.pos - f*24
            pygame.draw.circle(screen, ORANGE, flame, random.randint(7,11))
            pygame.draw.circle(screen, YELLOW, flame, random.randint(3,6))

        if self.drift:
            pygame.draw.circle(screen, GRAY, self.pos - f*18 + side*12, random.randint(4,8))
            pygame.draw.circle(screen, GRAY, self.pos - f*18 - side*12, random.randint(4,8))

class BoostPad:
    def __init__(self, x,y):
        self.rect = pygame.Rect(x-22,y-16,44,32)
        self.t = random.randint(0,50)
    def draw(self):
        self.t += 1
        col = CYAN if self.t % 20 < 10 else BLUE
        pygame.draw.rect(screen, (0,0,0), self.rect.move(3,3), border_radius=8)
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.polygon(screen, WHITE, [
            (self.rect.centerx-10,self.rect.centery+9),
            (self.rect.centerx,self.rect.centery-10),
            (self.rect.centerx+10,self.rect.centery+9)
        ])

class Banana:
    def __init__(self, x,y):
        self.pos = pygame.Vector2(x,y)
        self.radius = 11
    def draw(self):
        pygame.draw.circle(screen, YELLOW, self.pos, self.radius)
        pygame.draw.arc(screen, BROWN, (self.pos.x-9,self.pos.y-12,18,22), 0.4, 2.6, 3)
        pygame.draw.circle(screen, WHITE, self.pos, 3)

def draw_background():
    screen.fill(GRASS)
    for x in range(0, WIDTH, 50):
        for y in range(70, HEIGHT, 50):
            if (x+y)//50 % 2 == 0:
                pygame.draw.rect(screen, GRASS2, (x,y,50,50))
    # petits décors
    random.seed(4)
    for _ in range(90):
        x = random.randint(30, WIDTH-30)
        y = random.randint(90, HEIGHT-30)
        if not on_road((x,y)):
            pygame.draw.circle(screen, (45,145,65), (x,y), random.randint(2,4))

def draw_track():
    draw_background()
    screen.blit(track_surface, (0,0))

def draw_checkpoints():
    # Grandes arches propres sur toute la largeur de la piste.
    # Elles sont visuelles seulement : la détection reste précise au centre.
    for idx, (a,b) in enumerate(checkpoint_lines):
        aa, bb = pygame.Vector2(a), pygame.Vector2(b)
        mid = (aa + bb) * 0.5
        d = bb - aa
        if d.length_squared() == 0:
            continue

        d = d.normalize()
        n = pygame.Vector2(-d.y, d.x)

        col = YELLOW if idx == player.next_cp else (150,160,170)
        dark_col = (35,35,45)

        # Arche étendue sur toute la route
        half = TRACK_WIDTH * 0.50
        left = mid + d * half
        right = mid - d * half

        # Petite hauteur visuelle, orientée selon la piste
        lift = n * 10
        left_top = left + lift
        right_top = right + lift

        # Ombre
        pygame.draw.line(screen, BLACK, left + pygame.Vector2(3,3), right + pygame.Vector2(3,3), 9)
        pygame.draw.line(screen, BLACK, left_top + pygame.Vector2(3,3), right_top + pygame.Vector2(3,3), 7)

        # Barre au sol sur toute la largeur
        pygame.draw.line(screen, dark_col, left, right, 9)
        pygame.draw.line(screen, col, left, right, 5)

        # Barre supérieure de l'arche
        pygame.draw.line(screen, dark_col, left_top, right_top, 7)
        pygame.draw.line(screen, col, left_top, right_top, 4)

        # Poteaux aux deux extrémités
        pygame.draw.line(screen, dark_col, left, left_top, 8)
        pygame.draw.line(screen, dark_col, right, right_top, 8)
        pygame.draw.line(screen, col, left, left_top, 4)
        pygame.draw.line(screen, col, right, right_top, 4)

        # Petits capteurs lumineux
        pygame.draw.circle(screen, WHITE, left_top, 4)
        pygame.draw.circle(screen, WHITE, right_top, 4)

        if idx == 0:
            # Arche de départ en damier sur toute la largeur
            segments = 10
            for i in range(segments):
                t1 = i / segments
                t2 = (i + 1) / segments
                p1 = left.lerp(right, t1)
                p2 = left.lerp(right, t2)
                pygame.draw.line(screen, BLACK if i % 2 == 0 else WHITE, p1, p2, 8)

def handle_boosts(kart):
    for b in boosts:
        if b.rect.collidepoint(kart.pos):
            kart.boost_timer = 55
            kart.vel += kart.forward() * 1.0

def handle_bananas(kart):
    for ba in bananas[:]:
        if kart.pos.distance_to(ba.pos) < kart.radius + ba.radius:
            kart.stun_timer = 55
            kart.vel *= -0.35
            bananas.remove(ba)

def reset():
    global player, rivals, boosts, bananas, start_ms, game_over
    player = Kart(190,560, BLUE, True)
    player.angle = 60

    rivals = [
        Kart(165,585, RED),
        Kart(215,590, PURPLE),
        Kart(140,555, GREEN),
    ]
    for i,r in enumerate(rivals):
        r.angle = 55
        r.ai_target = 1+i

    boosts = [BoostPad(x,y) for x,y in boost_positions]
    bananas = [Banana(x,y) for x,y in banana_positions]
    start_ms = pygame.time.get_ticks()
    game_over = False

def draw_hud():
    elapsed = (pygame.time.get_ticks() - start_ms) / 1000
    pygame.draw.rect(screen, BLACK, (0,0,WIDTH,64))
    draw_text(f"Tour : {min(player.lap, TOTAL_LAPS)}/{TOTAL_LAPS}", 18, 15)
    draw_text(f"Checkpoint : {player.next_cp}/{len(checkpoint_lines)-1}", 150, 15)
    draw_text(f"Temps : {elapsed:.1f}s", 380, 15)
    draw_text("ZQSD/Fleches | ESPACE derapage | R restart", 560, 15)

    if player.next_cp == 0 and all(player.cp_seen[1:]):
        draw_text("Retourne a la ligne de depart !", 150, 40, YELLOW, small_font)
    else:
        draw_text("Passe les grandes arches dans l'ordre", 150, 40, GRAY, small_font)

def draw_minimap():
    scale = 0.16
    ox, oy = WIDTH-180, HEIGHT-125
    pygame.draw.rect(screen, BLACK, (ox-12,oy-12,165,112), border_radius=8)
    pts = [(ox+x*scale, oy+y*scale) for x,y in track_points]
    pygame.draw.lines(screen, GRAY, True, pts, 14)
    pygame.draw.lines(screen, WHITE, True, pts, 2)

    for i,line in enumerate(checkpoint_lines):
        a,b = line
        aa = (ox+a[0]*scale, oy+a[1]*scale)
        bb = (ox+b[0]*scale, oy+b[1]*scale)
        col = YELLOW if i == player.next_cp else (120,120,120)
        pygame.draw.line(screen, col, aa, bb, 2)

    pygame.draw.circle(screen, BLUE, (int(ox+player.pos.x*scale), int(oy+player.pos.y*scale)), 4)
    for r in rivals:
        pygame.draw.circle(screen, r.color, (int(ox+r.pos.x*scale), int(oy+r.pos.y*scale)), 4)

reset()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r:
                reset()

    keys = pygame.key.get_pressed()

    if not game_over:
        player.update_player(keys)
        handle_boosts(player)
        handle_bananas(player)

        for r in rivals:
            r.update_ai()
            handle_boosts(r)
            handle_bananas(r)

        if player.finished:
            game_over = True

    draw_track()
    draw_checkpoints()

    for b in boosts:
        b.draw()
    for ba in bananas:
        ba.draw()

    for r in sorted(rivals, key=lambda k: k.pos.y):
        r.draw()
    player.draw()

    # flèche vers prochain checkpoint
    if not player.finished:
        a,b = checkpoint_lines[player.next_cp]
        target = (pygame.Vector2(a)+pygame.Vector2(b))*0.5
        direction = target - player.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
            tip = player.pos + direction*42
            left = tip - direction*14 + pygame.Vector2(-direction.y, direction.x)*8
            right = tip - direction*14 - pygame.Vector2(-direction.y, direction.x)*8
            pygame.draw.polygon(screen, YELLOW, [tip,left,right])

    draw_hud()
    draw_minimap()

    if game_over:
        final_time = (player.finish_ms - start_ms) / 1000
        pygame.draw.rect(screen, BLACK, (175,230,650,210), border_radius=18)
        draw_text("COURSE TERMINEE !", WIDTH//2, 285, WHITE, big_font, True)
        draw_text(f"Temps final : {final_time:.1f}s", WIDTH//2, 355, YELLOW, font, True)
        draw_text("Appuie sur R pour recommencer", WIDTH//2, 395, WHITE, font, True)

    pygame.display.flip()
    clock.tick(FPS)
