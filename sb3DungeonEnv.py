import numpy as np
import Constants
import gym
from gym import spaces
import Cell
import pygame
import Agent
import Dungeon


class sb3DungeonEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        self.passive_loss = 1
        self.frames = 0
        self.max_frames = (Constants.CELL_HEIGHT * Constants.CELL_WIDTH) / 2

        pygame.init()
        self.screen = pygame.display.set_mode(
            (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)
        )

        self.reward = 0
        self.done = False

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(Constants.CELL_WIDTH, Constants.CELL_HEIGHT),
            dtype=np.float32,
        )
        self.agent = Agent.Agent()
        self.dungeon = Dungeon.Dungeon(self.agent, self.screen)
        self.dungeon.create_exit()
        self.dungeon.add_agent(self.agent)

        self.dungeon.create_brownian_path()
        self.dungeon.create_rocks()
        self.dungeon.build_goblins()
        self.dungeon.update()
        #pygame.display.flip()

    def step(self, action):
        self.frames += 1
        if self.frames > self.max_frames:
            self.done = True
            self.reward = -100
        agent_status = self.dungeon.move_agent(self.agent, action)
        goblin_status = None
        if agent_status != "no_move":
            goblin_status = self.dungeon.update()
        if agent_status == "no_move":
            self.reward += -1
        self.reward += self.dungeon.get_reward()
        if agent_status == "win":
            self.done = True
            self.reward += 500
        
        self.reward -= self.passive_loss
        if self.frames % 25 == 0:
            self.passive_loss += 1

        if goblin_status == "lose":
            self.done = True

        return self.dungeon.get_state(), self.reward, self.done, {}

    def reset(self):
        self.done = False
        self.reward = 0
        self.passive_loss = 1
        self.frames = 0 
        self.agent = Agent.Agent()
        self.dungeon = Dungeon.Dungeon(self.agent, self.screen)
        self.dungeon.create_exit()
        self.dungeon.add_agent(self.agent)

        self.dungeon.create_brownian_path()
        self.dungeon.create_rocks()
        self.dungeon.build_goblins()
        self.dungeon.update()
        #pygame.display.flip()
        return self.dungeon.get_state()

    def render(self, mode="human"):
        pygame.display.flip()   
