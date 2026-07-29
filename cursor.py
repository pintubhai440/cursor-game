"""
CURSOR DODGE - ULTIMATE EDITION (Python / pygame)
--------------------------------------------------
Ek hi game mein dono versions ke best features combine kiye gaye hain:

    - Gradient background + floating bubbles (soft visual polish)
    - Blue side rails / border walls
    - Custom drawn cursor with a soft glowing TRAIL behind it
    - RED bouncing enemy orbs  -> touch = Game Over
    - BLUE bonus orbs          -> collect = +10 score
    - MISSILES with a blinking warning box before they fire
    - RED SWEEPING WALLS that appear once your score gets high
    - Progressive difficulty (more enemies, faster orbs, more missiles
      and walls as your score increases)
    - Menu + Game Over screens with hover buttons
    - High Score is remembered for the session

Controls:
    Mouse movement   -> move cursor
    Left Click       -> Start / Restart (on menu / game over screen)
    ESC              -> Quit

Run:
    pip install pygame
    python cursor_dodge_ultimate.py
"""

import pygame
import random
import math
import sys

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 560, 420
SIDE_BAR = 50          # blue side rails (from v1's border style)
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cursor Dodge - Ultimate Edition")
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)  # we draw our own custom cursor

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
BG_TOP = (168, 190, 250)
BG_BOTTOM = (215, 224, 252)
RAIL_BLUE = (0, 50, 200)
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
RED = (220, 20, 20)
RED_SOFT = (255, 100, 100)
BLUE_ORB = (30, 60, 200)
BLUE_ORB_SOFT = (100, 150, 255)
ORANGE = (255, 140, 0)
WARNING_COLOR = (255, 200, 0)
MISSILE_COLOR = (50, 50, 50)
GEAR_GRAY = (130, 140, 160)

font_title = pygame.font.SysFont("arial", 70, bold=True)
font_med = pygame.font.SysFont("arial", 34, bold=True)
font_small = pygame.font.SysFont("arial", 22, bold=True)
font_score = pygame.font.SysFont("arial", 36, bold=True)

# ---------------------------------------------------------------------------
# Background helpers
# ---------------------------------------------------------------------------
decorative_bubbles = [
    (random.randint(SIDE_BAR, WIDTH - SIDE_BAR), random.randint(0, HEIGHT), random.randint(15, 45))
    for _ in range(10)
]

_bg_cache = None


def build_background():
    """Pre-render the gradient once for performance."""
    global _bg_cache
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    _bg_cache = surf


build_background()


def draw_background(surf):
    surf.blit(_bg_cache, (0, 0))

    for bx, by, br in decorative_bubbles:
        s = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 40), (br, br), br)
        surf.blit(s, (bx - br, by - br))

    # Side rails (border walls)
    pygame.draw.rect(surf, RAIL_BLUE, (0, 0, SIDE_BAR, HEIGHT))
    pygame.draw.rect(surf, RAIL_BLUE, (WIDTH - SIDE_BAR, 0, SIDE_BAR, HEIGHT))


def draw_outlined_text(surf, text, font, pos, color=RAIL_BLUE, outline=BLACK, width=2):
    x, y = pos
    base = font.render(text, True, color)
    outline_surf = font.render(text, True, outline)
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx != 0 or dy != 0:
                surf.blit(outline_surf, (x + dx, y + dy))
    surf.blit(base, (x, y))


def draw_gear_icon(surf, center, radius=16):
    pygame.draw.circle(surf, WHITE, center, radius + 6, 0)
    pygame.draw.circle(surf, BLACK, center, radius + 6, 3)
    pygame.draw.circle(surf, GEAR_GRAY, center, radius)
    for i in range(8):
        ang = i * (math.pi / 4)
        x1 = center[0] + math.cos(ang) * (radius + 2)
        y1 = center[1] + math.sin(ang) * (radius + 2)
        x2 = center[0] + math.cos(ang) * (radius + 8)
        y2 = center[1] + math.sin(ang) * (radius + 8)
        pygame.draw.line(surf, GEAR_GRAY, (x1, y1), (x2, y2), 4)
    pygame.draw.circle(surf, BLACK, center, radius, 2)
    pygame.draw.circle(surf, WHITE, center, 5)


# ---------------------------------------------------------------------------
# Player (custom cursor + glowing trail)
# ---------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.radius = 10
        self.pos = list(pygame.mouse.get_pos())
        self.trail = []

    def update(self):
        mx, my = pygame.mouse.get_pos()
        mx = max(SIDE_BAR + self.radius, min(WIDTH - SIDE_BAR - self.radius, mx))
        my = max(self.radius, min(HEIGHT - self.radius, my))
        self.pos = [mx, my]

        self.trail.append(list(self.pos))
        if len(self.trail) > 12:
            self.trail.pop(0)

    def rect(self):
        return pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius,
                            self.radius * 2, self.radius * 2)

    def draw(self, surf):
        # Glowing trail
        for i, t_pos in enumerate(self.trail):
            alpha = int(120 * (i + 1) / len(self.trail))
            size = max(2, int(self.radius * (i + 1) / len(self.trail)))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (80, 120, 255, alpha), (size, size), size)
            surf.blit(s, (t_pos[0] - size, t_pos[1] - size))

        # Custom cursor arrow shape
        x, y = self.pos
        points = [
            (x, y - 10), (x, y + 12), (x + 4, y + 8),
            (x + 7, y + 15), (x + 10, y + 13), (x + 7, y + 7),
            (x + 12, y + 7),
        ]
        pygame.draw.polygon(surf, WHITE, points)
        pygame.draw.polygon(surf, BLACK, points, 2)
        pygame.draw.circle(surf, (50, 100, 255), (x, y), 4)


# ---------------------------------------------------------------------------
# Enemy - bouncing red orb (deadly, always on screen)
# ---------------------------------------------------------------------------
class Enemy:
    def __init__(self, speed_mult=1.0):
        self.radius = 10
        self.x = random.choice([SIDE_BAR + 20, WIDTH - SIDE_BAR - 20])
        self.y = random.randint(30, HEIGHT - 30)

        speed = random.uniform(2.5, 4.2) * speed_mult
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

        if self.x - self.radius <= SIDE_BAR or self.x + self.radius >= WIDTH - SIDE_BAR:
            self.dx *= -1
            self.x = max(SIDE_BAR + self.radius, min(WIDTH - SIDE_BAR - self.radius, self.x))
        if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
            self.dy *= -1
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, RED_SOFT, (int(self.x), int(self.y)), self.radius - 4)


# ---------------------------------------------------------------------------
# Bonus Orb - blue, gives extra score, drifts in then leaves
# ---------------------------------------------------------------------------
class BonusOrb:
    def __init__(self):
        self.radius = 9
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            self.x = random.randint(SIDE_BAR + 20, WIDTH - SIDE_BAR - 20)
            self.y = -20
        elif edge == "bottom":
            self.x = random.randint(SIDE_BAR + 20, WIDTH - SIDE_BAR - 20)
            self.y = HEIGHT + 20
        elif edge == "left":
            self.x = SIDE_BAR - 10
            self.y = random.randint(20, HEIGHT - 20)
        else:
            self.x = WIDTH - SIDE_BAR + 10
            self.y = random.randint(20, HEIGHT - 20)

        target_x = random.randint(SIDE_BAR + 40, WIDTH - SIDE_BAR - 40)
        target_y = random.randint(40, HEIGHT - 40)
        dx, dy = target_x - self.x, target_y - self.y
        dist = max(1, math.hypot(dx, dy))
        speed = random.uniform(1.3, 2.0)
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy

    def off_screen(self):
        return (self.x < -40 or self.x > WIDTH + 40 or
                self.y < -40 or self.y > HEIGHT + 40)

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(140 * (i + 1) / len(self.trail))
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*BLUE_ORB, alpha), (self.radius, self.radius), max(2, self.radius - 3))
            surf.blit(s, (tx - self.radius, ty - self.radius))
        pygame.draw.circle(surf, BLUE_ORB, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, BLUE_ORB_SOFT, (int(self.x), int(self.y)), self.radius - 4)


# ---------------------------------------------------------------------------
# Missile - warns before firing horizontally across the arena
# ---------------------------------------------------------------------------
class Missile:
    def __init__(self, speed_mult=1.0):
        self.width = 30
        self.height = 15
        self.y = random.randint(40, HEIGHT - 40)
        self.direction = random.choice([1, -1])

        if self.direction == 1:
            self.x = SIDE_BAR
            self.warning_x = SIDE_BAR + 10
        else:
            self.x = WIDTH - SIDE_BAR
            self.warning_x = WIDTH - SIDE_BAR - 40

        self.speed = 11 * speed_mult
        self.warning_timer = 75
        self.active = False

    def update(self):
        if self.warning_timer > 0:
            self.warning_timer -= 1
        else:
            self.active = True
            self.x += self.speed * self.direction

    def off_screen(self):
        return self.x < -60 or self.x > WIDTH + 60

    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                            self.width, self.height)

    def draw(self, surf):
        if self.warning_timer > 0:
            if self.warning_timer % 10 > 5:
                warn_rect = pygame.Rect(self.warning_x, self.y - 15, 30, 30)
                pygame.draw.rect(surf, WARNING_COLOR, warn_rect)
                pygame.draw.rect(surf, RED, warn_rect, 3)
        elif self.active:
            m_rect = self.rect()
            pygame.draw.rect(surf, MISSILE_COLOR, m_rect, border_radius=5)
            fire_x = self.x - (self.width // 2) if self.direction == 1 else self.x + (self.width // 2)
            pygame.draw.circle(surf, ORANGE, (int(fire_x), int(self.y)), 8)


# ---------------------------------------------------------------------------
# Sweeping wall - drops down with a gap to dodge through
# ---------------------------------------------------------------------------
class SweepWall:
    def __init__(self, speed):
        self.height = 30
        self.y = -self.height
        self.speed = speed
        self.gap_x = random.randint(SIDE_BAR + 80, WIDTH - SIDE_BAR - 80)
        self.gap_w = 130

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > HEIGHT

    def draw(self, surf):
        left_w = self.gap_x - SIDE_BAR - self.gap_w // 2
        if left_w > 0:
            pygame.draw.rect(surf, RED, (SIDE_BAR, self.y, left_w, self.height))
        right_start = self.gap_x + self.gap_w // 2
        right_w = (WIDTH - SIDE_BAR) - right_start
        if right_w > 0:
            pygame.draw.rect(surf, RED, (right_start, self.y, right_w, self.height))

    def collides(self, player_rect):
        left_w = self.gap_x - SIDE_BAR - self.gap_w // 2
        right_start = self.gap_x + self.gap_w // 2
        right_w = (WIDTH - SIDE_BAR) - right_start
        left_rect = pygame.Rect(SIDE_BAR, self.y, max(0, left_w), self.height)
        right_rect = pygame.Rect(right_start, self.y, max(0, right_w), self.height)
        return player_rect.colliderect(left_rect) or player_rect.colliderect(right_rect)


# ---------------------------------------------------------------------------
# Game state machine
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.state = "MENU"
        self.high_score = 0
        self.reset()

    def reset(self):
        self.player = Player()
        self.enemies = [Enemy(), Enemy()]
        self.orbs = []
        self.missiles = []
        self.walls = []
        self.score = 0
        self.frame_count = 0
        self.last_orb_spawn = 0
        self.last_wall_spawn = 0

    def difficulty_mult(self):
        return 1.0 + min(1.8, self.score / 250)

    def update(self):
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self.score += 1

        # More enemies over time
        if self.frame_count % 480 == 0 and len(self.enemies) < 8:
            self.enemies.append(Enemy(self.difficulty_mult()))

        # Bonus orbs
        orb_interval = max(50, 140 - int(self.score / 3))
        if self.frame_count - self.last_orb_spawn > orb_interval:
            self.orbs.append(BonusOrb())
            self.last_orb_spawn = self.frame_count

        # Missiles - random chance, gets more frequent with score
        missile_chance = max(120, 500 - int(self.score * 4))
        if random.randint(1, missile_chance) == 1:
            self.missiles.append(Missile(self.difficulty_mult()))

        # Sweep walls appear once score is decent
        if self.score > 30:
            wall_interval = max(140, 280 - int(self.score))
            if self.frame_count - self.last_wall_spawn > wall_interval:
                self.walls.append(SweepWall(speed=2.2 + min(3, self.score / 90)))
                self.last_wall_spawn = self.frame_count

        self.player.update()

        for e in self.enemies:
            e.update()

        for o in self.orbs:
            o.update()
        self.orbs = [o for o in self.orbs if not o.off_screen()]

        for m in self.missiles:
            m.update()
        self.missiles = [m for m in self.missiles if not m.off_screen()]

        for w in self.walls:
            w.update()
        self.walls = [w for w in self.walls if not w.off_screen()]

        p_rect = self.player.rect()

        # Collect bonus orbs
        remaining_orbs = []
        for o in self.orbs:
            if o.rect().colliderect(p_rect):
                self.score += 10
            else:
                remaining_orbs.append(o)
        self.orbs = remaining_orbs

        # Check death collisions
        game_over = False
        for e in self.enemies:
            if e.rect().colliderect(p_rect):
                game_over = True
        for m in self.missiles:
            if m.active and m.rect().colliderect(p_rect):
                game_over = True
        for w in self.walls:
            if w.collides(p_rect):
                game_over = True

        if game_over:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw(self, surf):
        for e in self.enemies:
            e.draw(surf)
        for o in self.orbs:
            o.draw(surf)
        for m in self.missiles:
            m.draw(surf)
        for w in self.walls:
            w.draw(surf)
        self.player.draw(surf)


game = Game()


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def draw_hud(surf):
    shadow = font_score.render(f"SCORE: {game.score}", True, BLACK)
    txt = font_score.render(f"SCORE: {game.score}", True, WHITE)
    surf.blit(shadow, (SIDE_BAR + 12, 12))
    surf.blit(txt, (SIDE_BAR + 10, 10))


def draw_menu(surf, mouse_pos):
    # Top-left score, top-right settings gear (like the dashboard reference)
    score_label = font_med.render(f"SCORE: {game.high_score}", True, RAIL_BLUE)
    surf.blit(score_label, (SIDE_BAR + 15, 15))

    draw_gear_icon(surf, (WIDTH - SIDE_BAR - 35, 35))

    # Big overlapping bubble title
    draw_outlined_text(surf, "CURSOR", font_title, (WIDTH // 2 - 155, 75))
    draw_outlined_text(surf, "DODGE", font_title, (WIDTH // 2 - 130, 140))

    # START + BEST SCORE buttons side by side
    btn_w, btn_h = 150, 55
    gap = 20
    total_w = btn_w * 2 + gap
    start_x = WIDTH // 2 - total_w // 2
    btn_y = HEIGHT // 2 + 70

    start_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
    best_rect = pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)

    for rect, label in [(start_rect, "START"), (best_rect, "BEST SCORE")]:
        hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(surf, (235, 240, 255) if hover else WHITE, rect, border_radius=14)
        pygame.draw.rect(surf, BLACK, rect, 3, border_radius=14)
        txt = font_small.render(label, True, BLACK)
        surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    game.player.pos = list(mouse_pos)
    game.player.draw(surf)
    return start_rect


def draw_gameover(surf, mouse_pos):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surf.blit(overlay, (0, 0))

    box = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 130, 340, 260)
    pygame.draw.rect(surf, WHITE, box, border_radius=16)
    pygame.draw.rect(surf, BLACK, box, 3, border_radius=16)

    title = font_med.render("GAME OVER", True, RED)
    surf.blit(title, (box.centerx - title.get_width() // 2, box.y + 20))

    score_txt = font_small.render(f"Score: {game.score}", True, BLACK)
    surf.blit(score_txt, (box.centerx - score_txt.get_width() // 2, box.y + 85))

    best_txt = font_small.render(f"Best: {game.high_score}", True, BLACK)
    surf.blit(best_txt, (box.centerx - best_txt.get_width() // 2, box.y + 118))

    restart_rect = pygame.Rect(box.centerx - 90, box.y + 170, 180, 55)
    hover = restart_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surf, (235, 240, 255) if hover else WHITE, restart_rect, border_radius=14)
    pygame.draw.rect(surf, BLACK, restart_rect, 3, border_radius=14)
    txt = font_small.render("RESTART", True, BLACK)
    surf.blit(txt, (restart_rect.centerx - txt.get_width() // 2, restart_rect.centery - txt.get_height() // 2))

    game.player.pos = list(mouse_pos)
    game.player.draw(surf)
    return restart_rect


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "MENU":
                    start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60)
                    if start_rect.collidepoint(mouse_pos):
                        game.reset()
                        game.state = "PLAY"
                elif game.state == "GAMEOVER":
                    box = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 130, 340, 260)
                    restart_rect = pygame.Rect(box.centerx - 90, box.y + 170, 180, 55)
                    if restart_rect.collidepoint(mouse_pos):
                        game.reset()
                        game.state = "PLAY"

        draw_background(screen)

        if game.state == "MENU":
            draw_menu(screen, mouse_pos)
        elif game.state == "PLAY":
            game.update()
            game.draw(screen)
            draw_hud(screen)
        elif game.state == "GAMEOVER":
            game.draw(screen)
            draw_hud(screen)
            draw_gameover(screen, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
