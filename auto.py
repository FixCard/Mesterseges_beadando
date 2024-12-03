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
