import gymnasium as gym
import numpy as np
from typing import *

from gymnasium.core import ActType


class PCGEnv(gym.Env):
    def __init__(self):
        # Set up the environment
        super().__init__()

        # self.action_space = gym.spaces.Discrete(10)

        # how much to increase or decrease each parameter
        self.action_space = gym.spaces.Box(low=np.array([]))    # 5 simultaneous continuous actions

        # damage dealt (avg per entity?), damage receive, current parameters
        self.observation_space = gym.spaces.Box()

    def step(self, action: ActType):
        pass

    def _min_skill_level(self):
        pass

