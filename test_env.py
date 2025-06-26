import gymnasium as gym
from game import Game

gym.register(
    id="Talakat-v0",
    entry_point=Game,
)
env = gym.make("Talakat-v0")

print("observation space: ", env.observation_space)
observation, info = env.reset()
print("observation: ", observation)
print("action space: ", env.action_space)

for i in range(100):
    observation = env.step(env.action_space.sample())
    print("observation: ", observation)
    # add in however you want to render/display the current state
    print("-----")
