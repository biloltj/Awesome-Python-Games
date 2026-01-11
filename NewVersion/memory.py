import pygame
import random
import sys

WIDTH, HEIGHT = 800, 500
CARD_WIDTH, CARD_HEIGHT = 80, 120
MARGIN = 10
ROWS, COLS = 2, 8
FPS = 60

BG_COLOR = (25, 28, 40)
CARD_BACK = (70, 90, 140)
CARD_FRONT = (240, 240, 240)
TEXT_COLOR = (30, 30, 30)
ACCENT = (255, 200, 70)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory — Card Matching Game")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 36)
SMALL_FONT = pygame.font.SysFont("arial", 24)

def new_game():
    global deck, exposed, state, first_card, second_card, turns

    deck = list(range(8)) * 2
    random.shuffle(deck)

    exposed = [False] * 16
    state = 0
    first_card = None
    second_card = None
    turns = 0

def draw_card(x, y, value, is_exposed):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    if is_exposed:
        pygame.draw.rect(screen, CARD_FRONT, rect, border_radius=10)
        text = FONT.render(str(value), True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
    else:
        pygame.draw.rect(screen, CARD_BACK, rect, border_radius=10)

    pygame.draw.rect(screen, ACCENT, rect, 2, border_radius=10)


def main():
    global state, first_card, second_card, turns

    new_game()
    running = True
    hide_timer = 0

    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and hide_timer == 0:
                mx, my = event.pos

                for i in range(16):
                    row = i // COLS
                    col = i % COLS
                    x = col * (CARD_WIDTH + MARGIN) + MARGIN
                    y = row * (CARD_HEIGHT + MARGIN) + 60

                    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

                    if rect.collidepoint(mx, my) and not exposed[i]:
                        exposed[i] = True

                        if state == 0:
                            first_card = i
                            state = 1

                        elif state == 1:
                            second_card = i
                            state = 2
                            turns += 1

                            if deck[first_card] != deck[second_card]:
                                hide_timer = pygame.time.get_ticks()

                        break

        if state == 2 and hide_timer:
            if pygame.time.get_ticks() - hide_timer > 800:
                exposed[first_card] = False
                exposed[second_card] = False
                state = 0
                hide_timer = 0

        elif state == 2 and hide_timer == 0:
            state = 0

        
        for i in range(16):
            row = i // COLS
            col = i % COLS
            x = col * (CARD_WIDTH + MARGIN) + MARGIN
            y = row * (CARD_HEIGHT + MARGIN) + 60
            draw_card(x, y, deck[i], exposed[i])

        title = FONT.render("MEMORY", True, ACCENT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

        turns_text = SMALL_FONT.render(f"Turns: {turns}", True, (200, 200, 200))
        screen.blit(turns_text, (20, 20))

        reset_text = SMALL_FONT.render("Press R to Reset", True, (150, 150, 150))
        screen.blit(reset_text, (WIDTH - 180, 20))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            new_game()

        pygame.display.flip()


if __name__ == "__main__":
    main()
