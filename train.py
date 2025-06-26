# train the AI model here

# test

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

# from torch import nn

#from game import Game
import game


# class PolicyNetwork(nn.Module):
#     def __init__(self, input_dim, hidden_dim, output_dim, dropout):
#         super().__init__()
#         self.layer1 = nn.Linear(input_dim, hidden_dim)
#         self.layer2 = nn.Linear(hidden_dim, output_dim)
#         self.dropout = nn.Dropout(dropout)
#
#     def forward(self, x):
#         x = self.layer1(x)
#         x = self.dropout(x)
#         x = nn.functional.relu(x)
#         x = self.layer2(x)
#         return x


# env = gym.make('CartPole-v1', render_mode="rgb_array")
# print("observation space: ", env.observation_space)
# observation, info = env.reset()
# print("observation: ", observation)
# print("action space: ", env.action_space)
#
# print(env.render())

gym.register("GameEnv", entry_point="game:Game")

# Create the environment
env = gym.make("GameEnv")


# Parallel environments
vec_env = make_vec_env("FrozenLake-v1", n_envs=4)

model = PPO("MlpPolicy", vec_env, verbose=1)
model.learn(total_timesteps=25000)
# model.save("ppo_cartpole")

# del model # remove to demonstrate saving and loading

# model = PPO.load("ppo_cartpole")

obs = vec_env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = vec_env.step(action)
    vec_env.render("human")