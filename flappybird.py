# Author : Nguyen Vu Xuan Kien | 17/02/2004 | kien1722004@gmail.com
import pygame
import random
import sys
import sqlite3

pygame.init()

# ================== SETTINGS ==================
WIDTH, HEIGHT = 400, 600
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -10

PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 3

# ================== SETUP ==================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird by Xuân Kiên")
clock = pygame.time.Clock()

font = pygame.font.SysFont("sans", 30)

# ================== DATABASE ==================
conn = sqlite3.connect("flappy.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER
)
""")
conn.commit()

# ================== LOAD IMAGES ==================
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

bird_img = pygame.image.load("bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (40, 40))

pipe_img = pygame.image.load("column.png").convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, 400))
pipe_img_flip = pygame.transform.flip(pipe_img, False, True)

# ================== CLASSES ==================

class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.velocity = 0
        self.image = bird_img
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def draw(self):
        screen.blit(self.image, self.rect)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(120, 400)
        self.passed = False

        self.top_rect = pipe_img.get_rect()
        self.bottom_rect = pipe_img.get_rect()

    def update(self):
        self.x -= PIPE_SPEED

        self.top_rect.topleft = (self.x, self.height - pipe_img.get_height())
        self.bottom_rect.topleft = (self.x, self.height + PIPE_GAP)

    def draw(self):
        screen.blit(pipe_img_flip, self.top_rect)
        screen.blit(pipe_img, self.bottom_rect)

    def collide(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or \
               self.bottom_rect.colliderect(bird_rect)

# ================== MENU ==================

def show_menu():
    while True:
        screen.blit(background, (0, 0))

        title = font.render("FLAPPY BIRD", True, (0, 0, 0))
        start = font.render("Press SPACE to Start", True, (0, 0, 0))
        quit_txt = font.render("Press ESC to Quit", True, (0, 0, 0))

        screen.blit(title, (90, 200))
        screen.blit(start, (50, 300))
        screen.blit(quit_txt, (70, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# ================== GAME FUNCTIONS ==================

def reset_game():
    bird = Bird()
    pipes = [Pipe(500), Pipe(700), Pipe(900)]
    score = 0
    return bird, pipes, score

def save_score(score):
    cursor.execute("INSERT INTO scores (score) VALUES (?)", (score,))
    conn.commit()

def get_high_score():
    cursor.execute("SELECT MAX(score) FROM scores")
    result = cursor.fetchone()[0]
    if result is None:
        return 0
    return result

# ================== START ==================

show_menu()

bird, pipes, score = reset_game()
game_over = False

# ================== MAIN LOOP ==================

running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    save_score(score)
                    bird, pipes, score = reset_game()
                    game_over = False
                else:
                    bird.jump()

    if not game_over:
        bird.update()

        for pipe in pipes:
            pipe.update()

            # Score
            if pipe.x + PIPE_WIDTH < bird.x and not pipe.passed:
                score += 1
                pipe.passed = True

            # Collision
            if pipe.collide(bird.rect):
                game_over = True

        # Remove old pipe
        if pipes[0].x < -PIPE_WIDTH:
            pipes.pop(0)
            pipes.append(Pipe(pipes[-1].x + 250))

        # Check out of screen
        if bird.y > HEIGHT or bird.y < 0:
            game_over = True

    # Draw
    bird.draw()

    for pipe in pipes:
        pipe.draw()

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    high_score = get_high_score()
    hs_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(hs_text, (10, 40))

    if game_over:
        over_text = font.render("Game Over - Press SPACE", True, (255, 0, 0))
        screen.blit(over_text, (30, HEIGHT // 2))

    pygame.display.update()