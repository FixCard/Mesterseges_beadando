from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from avoid_obstacle_env import AvoidObstacleEnv

env = DummyVecEnv([lambda: AvoidObstacleEnv()])

model = PPO(
    "MlpPolicy",
    env,
    learning_rate=0.000001,  
    n_steps=4096,         
    batch_size=1024,       
    gamma=0.99,            
    gae_lambda=1,
    clip_range=0.15,
    ent_coef=0.001,
    verbose=1,
)

print("Tréning elkezdődött...")
model.learn(total_timesteps=15000)  
model.save("optimized_obstacle_avoider_model")
print("A modell mentése kész.")
