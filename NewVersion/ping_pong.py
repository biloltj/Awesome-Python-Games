import pygame
import random
import math
import sys


WIDTH, HEIGHT = 720, 480
FPS = 60
BALL_RADIUS = 10
PAD_WIDTH = 12
PAD_HEIGHT = 90
WIN_SCORE = 7

BG = (8, 8, 20)
WHITE = (245, 245, 245)
NEON_PURPLE = (190, 110, 255)
NEON_BLUE = (90, 190, 255)
NEON_RED = (255, 90, 110)

pygame.init()
pygame.mixer.init()
pygame.joystick.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Pong Arcade")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("consolas", 64)
font_small = pygame.font.SysFont("consolas", 22)


controller = None
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()


def tone(freq, duration=0.1):
    sample_rate = 44100
    n = int(sample_rate * duration)
    buf = bytearray()
    for x in range(n):
        v = int(127 * math.sin(2 * math.pi * freq * x / sample_rate))
        buf.extend((v + 128, v + 128))
    return pygame.mixer.Sound(buffer=bytes(buf))

bounce_sound = tone(600)
score_sound = tone(200, 0.25)

player = pygame.Rect(30, HEIGHT//2 - PAD_HEIGHT//2, PAD_WIDTH, PAD_HEIGHT)
ai = pygame.Rect(WIDTH - 42, HEIGHT//2 - PAD_HEIGHT//2, PAD_WIDTH, PAD_HEIGHT)

ball_pos = [WIDTH//2, HEIGHT//2]
ball_vel = [0, 0]

player_vel = 0
player_score = 0
ai_score = 0
game_over = False


particles = []

def spawn_particle():
    particles.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])

for _ in range(80):
    spawn_particle()


def spawn_ball(direction=None):
    global ball_pos, ball_vel
    ball_pos = [WIDTH//2, HEIGHT//2]
    angle = random.uniform(-0.4, 0.4)
    speed = random.randint(5, 6)
    dir = random.choice([-1, 1]) if direction is None else direction
    ball_vel = [dir * speed, speed * math.sin(angle)]

def reset_game():
    global player_score, ai_score, game_over
    player_score = ai_score = 0
    game_over = False
    spawn_ball()

def draw_glow_circle(pos, radius, color):
    for i in range(6, 0, -1):
        surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*color, 18),
            (radius*2, radius*2),
            radius + i*2
        )
        screen.blit(surf, (pos[0]-radius*2, pos[1]-radius*2))

def draw_glow_rect(rect, color):
    for i in range(5, 0, -1):
        surf = pygame.Surface((rect.width+i*6, rect.height+i*6), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, 20), surf.get_rect(), border_radius=8)
        screen.blit(surf, (rect.x-i*3, rect.y-i*3))


reset_game()
running = True

while running:
    clock.tick(FPS)
    screen.fill(BG)

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_w:
                player_vel = -7
            if event.key == pygame.K_s:
                player_vel = 7

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                player_vel = 0

    # Controller input
    if controller:
        axis = controller.get_axis(1)
        player_vel = int(axis * 8)

    if not game_over:
        # Player
        player.y += player_vel
        player.y = max(0, min(HEIGHT - PAD_HEIGHT, player.y))

        # AI (adaptive)
        ai_speed = 4.5 + (player_score - ai_score) * 0.4
        ai_speed = max(3, min(8, ai_speed))
        if ai.centery < ball_pos[1]:
            ai.y += ai_speed
        else:
            ai.y -= ai_speed
        ai.y = max(0, min(HEIGHT - PAD_HEIGHT, ai.y))

        # Ball
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]

        if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
            ball_vel[1] *= -1
            bounce_sound.play()

        ball_rect = pygame.Rect(
            ball_pos[0]-BALL_RADIUS,
            ball_pos[1]-BALL_RADIUS,
            BALL_RADIUS*2,
            BALL_RADIUS*2
        )

        # Spin physics
        if ball_rect.colliderect(player) and ball_vel[0] < 0:
            offset = (ball_pos[1] - player.centery) / (PAD_HEIGHT / 2)
            ball_vel[0] *= -1.1
            ball_vel[1] += offset * 4
            bounce_sound.play()

        if ball_rect.colliderect(ai) and ball_vel[0] > 0:
            offset = (ball_pos[1] - ai.centery) / (PAD_HEIGHT / 2)
            ball_vel[0] *= -1.1
            ball_vel[1] += offset * 3
            bounce_sound.play()

        # Score
        if ball_pos[0] < 0:
            ai_score += 1
            score_sound.play()
            spawn_ball(1)

        if ball_pos[0] > WIDTH:
            player_score += 1
            score_sound.play()
            spawn_ball(-1)

        if player_score >= WIN_SCORE or ai_score >= WIN_SCORE:
            game_over = True

    
    for p in particles:
        p[0] -= p[2]
        if p[0] < 0:
            p[0] = WIDTH
            p[1] = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, NEON_PURPLE, p[:2], p[2])

    for y in range(0, HEIGHT, 30):
        pygame.draw.line(screen, NEON_PURPLE, (WIDTH//2, y), (WIDTH//2, y+15), 2)

    draw_glow_rect(player, NEON_BLUE)
    draw_glow_rect(ai, NEON_RED)
    pygame.draw.rect(screen, WHITE, player, border_radius=6)
    pygame.draw.rect(screen, WHITE, ai, border_radius=6)

    draw_glow_circle(ball_pos, BALL_RADIUS, NEON_PURPLE)
    pygame.draw.circle(screen, WHITE, ball_pos, BALL_RADIUS)

    
    score = font_big.render(f"{player_score}   {ai_score}", True, WHITE)
    screen.blit(score, (WIDTH//2 - score.get_width()//2, 20))

    if game_over:
        text = "YOU WIN!" if player_score > ai_score else "AI WINS!"
        t = font_big.render(text, True, NEON_PURPLE)
        hint = font_small.render("Press R to Restart", True, WHITE)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
