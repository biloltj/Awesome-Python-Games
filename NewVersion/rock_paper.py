import pygame
import random
import math
import sys
import time


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPSLS Neon Arcade")
clock = pygame.time.Clock()


title_font = pygame.font.SysFont("consolas", 42)
font = pygame.font.SysFont("consolas", 24)
big_font = pygame.font.SysFont("consolas", 32)


BG = (15, 15, 30)
WHITE = (240, 240, 240)
PURPLE = (180, 100, 255)
BLUE = (90, 180, 255)
GREEN = (90, 255, 150)
RED = (255, 90, 90)
GRAY = (80, 80, 100)


def tone(freq, duration=0.15):
    sample_rate = 44100
    n = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n):
        v = int(127 * math.sin(2 * math.pi * freq * i / sample_rate))
        buf.extend((v + 128, v + 128))
    return pygame.mixer.Sound(buffer=bytes(buf))

win_sound = tone(700)
lose_sound = tone(250)
tie_sound = tone(450, 0.1)

choices = ["rock", "Spock", "paper", "lizard", "scissors"]

win_map = {
    ("scissors", "paper"), ("paper", "rock"),
    ("rock", "lizard"), ("lizard", "Spock"),
    ("Spock", "scissors"), ("scissors", "lizard"),
    ("lizard", "paper"), ("paper", "Spock"),
    ("Spock", "rock"), ("rock", "scissors")
}

player_score = 0
computer_score = 0
win_streak = 0

player_choice = None
computer_choice = None
message = "Choose your move!"


def get_result(p, c):
    if p == c:
        return "tie"
    if (p, c) in win_map:
        return "player"
    return "computer"


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        glow = pygame.Surface((self.rect.width+12, self.rect.height+12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*BLUE, 60), glow.get_rect(), border_radius=14)
        screen.blit(glow, (self.rect.x-6, self.rect.y-6))

        pygame.draw.rect(screen, BLUE, self.rect, border_radius=10)
        label = font.render(self.text, True, WHITE)
        screen.blit(label, (
            self.rect.centerx - label.get_width() // 2,
            self.rect.centery - label.get_height() // 2
        ))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


buttons = []
start_x = 70
for i, c in enumerate(choices):
    buttons.append(Button(c, start_x + i * 130, 350, 120, 45))

running = True
thinking = False
think_timer = 0

while running:
    clock.tick(60)
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                player_score = computer_score = win_streak = 0
                message = "Game reset!"
                player_choice = computer_choice = None

        if event.type == pygame.MOUSEBUTTONDOWN and not thinking:
            for b in buttons:
                if b.clicked(event.pos):
                    player_choice = b.text
                    thinking = True
                    think_timer = pygame.time.get_ticks()

    if thinking:
        if pygame.time.get_ticks() - think_timer > 800:
            computer_choice = random.choice(choices)
            result = get_result(player_choice, computer_choice)

            if result == "player":
                player_score += 1
                win_streak += 1
                win_sound.play()
                message = "You win!"
            elif result == "computer":
                computer_score += 1
                win_streak = 0
                lose_sound.play()
                message = "Computer wins!"
            else:
                tie_sound.play()
                message = "It's a tie!"

            thinking = False

    
    title = title_font.render("Rock Paper Scissors Lizard Spock", True, PURPLE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    score = font.render(
        f"Player: {player_score}   Computer: {computer_score}   Streak: {win_streak}",
        True, WHITE
    )
    screen.blit(score, (WIDTH//2 - score.get_width()//2, 80))

    if player_choice:
        p = big_font.render(f"You chose: {player_choice}", True, GREEN)
        screen.blit(p, (60, 150))

    if computer_choice:
        c = big_font.render(f"Computer chose: {computer_choice}", True, RED)
        screen.blit(c, (60, 200))

    if thinking:
        think = big_font.render("Computer is thinking...", True, GRAY)
        screen.blit(think, (WIDTH//2 - think.get_width()//2, 260))
    else:
        msg = big_font.render(message, True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 260))

    for b in buttons:
        b.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()
