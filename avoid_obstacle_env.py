import gym
from gym import spaces
import numpy as np
import random

class AvoidObstacleEnv(gym.Env):
    def __init__(self):
        super(AvoidObstacleEnv, self).__init__()
        self.action_space = spaces.Discrete(3)  # 0 = balra, 1 = jobbra, 2 = marad
        self.observation_space = spaces.Box(low=0, high=1, shape=(16,), dtype=np.float32)  # Több információ

        self.reset()

    def reset(self):
        self.ai_x = 0.5  # AI kezdeti pozíció
        self.obstacles = []
        self.done = False
        return self._get_state()

    def create_obstacle(self):
        x_pos = random.uniform(0.5, 1.0)  # Csak az AI pályájára eső akadályok
        self.obstacles.append([x_pos, 1.0, random.uniform(0.01, 0.05)])  # X, Y, sebesség

    def step(self, action):
        reward = 0

        # Akció végrehajtása
        if action == 0:  # Balra
            self.ai_x = max(0.5, self.ai_x - 0.03)
        elif action == 1:  # Jobbra
            self.ai_x = min(1.0, self.ai_x + 0.03)

        # Akadályok mozgatása
        for obstacle in self.obstacles:
            obstacle[1] -= obstacle[2]

        # Jutalmazás
        for obstacle in self.obstacles:
            distance_x = abs(self.ai_x - obstacle[0])

            if distance_x < 0.1 and obstacle[1] < 0.2:  # Ütközés közeli helyzet
                reward -= 50
                self.done = True  # Játék vége
            elif 1.5 <= distance_x <= 0.05 and 0.05 < obstacle[1] < 1.5:  # Biztonságos távolság
                reward += 50
            else:
                reward -= 1  # Büntetés a felesleges mozgásért

        # Új akadály generálása
        if random.random() < 0.2:
            self.create_obstacle()

        # Akadályok eltávolítása
        self.obstacles = [ob for ob in self.obstacles if ob[1] > 0]

        return self._get_state(), reward, self.done, {}


    def _get_state(self):
        ai_x_normalized = (self.ai_x - 0.5) / 0.5
        state = [ai_x_normalized]

        # Az akadályok normalizált pozíciója és sebessége
        obstacles = sorted(self.obstacles, key=lambda x: x[1])[:5]
        for ob in obstacles:
            distance_x = (ob[0] - self.ai_x)  # Távolság az akadálytól X irányban
            state.extend([distance_x, ob[1], ob[2]])  # X távolság, Y pozíció, sebesség

        # Ha kevesebb akadály van, nullákkal töltjük fel
        while len(state) < 16:  # 1 AI pozíció + 5 akadály (3 adat/akadály)
            state.append(0.0)

        return np.array(state, dtype=np.float32)

