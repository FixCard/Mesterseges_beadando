import pygame
import random
import sys
import numpy as np
from stable_baselines3 import PPO

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Autós Játék - AI ellen")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (105, 105, 105)

difficulty = "Könnyű"
sound_on = True

try:
    collision_sound = pygame.mixer.Sound("collision.wav")
    avoid_sound = pygame.mixer.Sound("avoid.wav")
    life_gain_sound = pygame.mixer.Sound("life_gain.wav")
except FileNotFoundError:
    print("Hangfájlok nem találhatóak. Hanghatások nem lesznek elérhetők.")
    sound_on = False

try:
    ai_model = PPO.load("optimized_obstacle_avoider_model.zip")
except FileNotFoundError:
    print("Az előre tanított AI modell nem található. Az AI nem fog működni.")
    ai_model = None

def show_menu():
    global difficulty, sound_on
    menu_running = True
    while menu_running:
        screen.fill(WHITE)
        
        font = pygame.font.SysFont(None, 48)
        title_text = font.render("Autós Játék - AI ellen", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        difficulty_text = font.render("Nehézségi szint: " + difficulty, True, BLACK)
        screen.blit(difficulty_text, (SCREEN_WIDTH // 2 - difficulty_text.get_width() // 2, 150))
        
        easy_text = font.render("Könnyű", True, BLACK)
        medium_text = font.render("Közepes", True, BLACK)
        hard_text = font.render("Nehéz", True, BLACK)
        screen.blit(easy_text, (SCREEN_WIDTH // 4 - easy_text.get_width() // 2, 250))
        screen.blit(medium_text, (SCREEN_WIDTH // 2 - medium_text.get_width() // 2, 250))
        screen.blit(hard_text, (3 * SCREEN_WIDTH // 4 - hard_text.get_width() // 2, 250))

        sound_status = "Be" if sound_on else "Ki"
        sound_text = font.render(f"Hang: {sound_status}", True, BLACK)
        screen.blit(sound_text, (SCREEN_WIDTH // 2 - sound_text.get_width() // 2, 350))

        start_text = font.render("Indítás", True, BLACK)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 450))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if easy_text.get_rect(center=(SCREEN_WIDTH // 4, 250)).collidepoint(x, y):
                    difficulty = "Könnyű"
                elif medium_text.get_rect(center=(SCREEN_WIDTH // 2, 250)).collidepoint(x, y):
                    difficulty = "Közepes"
                elif hard_text.get_rect(center=(3 * SCREEN_WIDTH // 4, 250)).collidepoint(x, y):
                    difficulty = "Nehéz"

                elif sound_text.get_rect(center=(SCREEN_WIDTH // 2, 350)).collidepoint(x, y):
                    sound_on = not sound_on

                elif start_text.get_rect(center=(SCREEN_WIDTH // 2, 450)).collidepoint(x, y):
                    menu_running = False

def update_ai_position(AI_x, AI_y, obstacles, AI_speed_x, AI_target_x, AI_left_lane, AI_right_lane):
    if ai_model:

        ai_obstacles = [ob for ob in obstacles if AI_left_lane <= ob.x <= AI_right_lane]
        obstacle_positions = [[(ob.x - AI_left_lane) / (AI_right_lane - AI_left_lane), ob.y / SCREEN_HEIGHT] for ob in sorted(ai_obstacles, key=lambda x: x.y)[:3]]

        ai_x_normalized = (AI_x - AI_left_lane) / (AI_right_lane - AI_left_lane) 
        state = [ai_x_normalized]
        for ob in obstacle_positions:
            state.extend(ob)

        while len(state) < 16:
            state.append(0.0)

        state = np.array(state, dtype=np.float32)

        action, _ = ai_model.predict(state)

        if action == 0:  
            AI_target_x = max(AI_target_x - AI_speed_x, AI_left_lane)
        elif action == 1:  
            AI_target_x = min(AI_target_x + AI_speed_x, AI_right_lane)

    return AI_target_x

def check_and_add_life(player_score, player_lives):
    if player_score > 0 and player_score % 3 == 0 and player_lives < 3:
        player_lives += 1
        if sound_on and life_gain_sound:
            life_gain_sound.play()
    return player_lives

def check_and_add_life(AI_score, AI_lives):
    if AI_score > 0 and AI_score % 3 == 0 and AI_lives < 3:
        AI_lives += 1
        if sound_on and life_gain_sound:
            life_gain_sound.play()
    return AI_lives

def start_game():
    global difficulty, sound_on

    player_lives = 3
    AI_lives = 3
    player_score = 0
    AI_score = 0

    start_time = pygame.time.get_ticks()

    if difficulty == "Könnyű":
        obstacle_speed = 5
        obstacle_frequency = 60
    elif difficulty == "Közepes":
        obstacle_speed = 7
        obstacle_frequency = 45
    elif difficulty == "Nehéz":
        obstacle_speed = 10
        obstacle_frequency = 30

    PLAYER_WIDTH = 50
    PLAYER_HEIGHT = 50
    player_x = SCREEN_WIDTH // 4
    player_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20
    player_speed = 8

    AI_x = (SCREEN_WIDTH // 4) * 3
    AI_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20
    AI_target_x = AI_x
    AI_speed_x = 10
    AI_left_lane = (SCREEN_WIDTH // 2) 
    AI_right_lane = SCREEN_WIDTH - 50 

    OBSTACLE_WIDTH = 40
    OBSTACLE_HEIGHT = 40
    obstacles = []

    def create_obstacle():
        x_pos = random.choice([random.randint(0, SCREEN_WIDTH // 2 - OBSTACLE_WIDTH), 
                               random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - OBSTACLE_WIDTH)])
        obstacles.append(pygame.Rect(x_pos, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(WHITE)

        for i in range(3):
            pygame.draw.circle(screen, RED if i < player_lives else GRAY, (30 + i * 40, 50), 15)
            pygame.draw.circle(screen, RED if i < AI_lives else GRAY, (SCREEN_WIDTH - (30 + i * 40), 50), 15)

        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)  
        pygame.draw.line(screen, RED, (SCREEN_WIDTH - 1, 0), (SCREEN_WIDTH - 1, SCREEN_HEIGHT), 2)  

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Idő: {elapsed_time} mp", True, BLACK)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))

        player_text = font.render(f"Játékos pontok: {player_score}", True, BLUE)
        AI_text = font.render(f"AI pontok: {AI_score}", True, RED)
        screen.blit(player_text, (10, 10))
        screen.blit(AI_text, (SCREEN_WIDTH - AI_text.get_width() - 10, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH / 2 - PLAYER_WIDTH:
            player_x += player_speed

        AI_target_x = update_ai_position(AI_x, AI_y, obstacles, AI_speed_x, AI_target_x, AI_left_lane, AI_right_lane)
        if AI_x < AI_target_x:
            AI_x += AI_speed_x
        elif AI_x > AI_target_x:
            AI_x -= AI_speed_x

        if random.randint(1, obstacle_frequency) == 1:
            create_obstacle()

        for obstacle in obstacles[:]:
            obstacle.y += obstacle_speed
            pygame.draw.rect(screen, BLACK, obstacle)
            player_car = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            AI_car = pygame.Rect(AI_x, AI_y, PLAYER_WIDTH, PLAYER_HEIGHT)

            if player_car.colliderect(obstacle):
                obstacles.remove(obstacle)
                player_lives -= 1
                if sound_on and collision_sound:
                    collision_sound.play()
                if player_lives <= 0:
                    print("A játékos elvesztette az életét. Az AI nyert!")
                    running = False

            elif AI_car.colliderect(obstacle):
                obstacles.remove(obstacle)
                AI_lives -= 1
                if sound_on and collision_sound:
                    collision_sound.play()
                if AI_lives <= 0:
                    print("Az AI elvesztette az életét. A játékos nyert!")
                    running = False

            elif obstacle.y > SCREEN_HEIGHT:
                obstacles.remove(obstacle)
                if obstacle.x < SCREEN_WIDTH // 2:
                    player_score += 1
                    player_lives = check_and_add_life(player_score, player_lives)
                    if sound_on and avoid_sound:
                        avoid_sound.play()
                else:
                    AI_score += 1
                    AI_lives = check_and_add_life(AI_score, AI_lives)

        pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        pygame.draw.rect(screen, RED, (AI_x, AI_y, PLAYER_WIDTH, PLAYER_HEIGHT))

        pygame.display.flip()
        clock.tick(30)

    show_menu()
    start_game()

show_menu()
start_game()
