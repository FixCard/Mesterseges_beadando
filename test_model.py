from stable_baselines3 import PPO
from avoid_obstacle_env import AvoidObstacleEnv

# Modell betöltése
model = PPO.load("optimized_obstacle_avoider_model")

# Környezet inicializálása
env = AvoidObstacleEnv()
obs = env.reset()

# Tesztfutás
for step in range(100):
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)

    # Debug adatok
    print(f"Lépés: {step}, Reward: {reward}, Akció: {action}, Pozíció (normalizált): {obs[0]:.2f}")

    for idx, obstacle in enumerate(env.obstacles):
        print(f"Akadály {idx}: X={obstacle[0]:.2f}, Y={obstacle[1]:.2f}, Sebesség={obstacle[2]:.4f}")
    
    if done:
        print("Ütközés történt!")
        obs = env.reset()
        print("Környezet újraindítva.")
