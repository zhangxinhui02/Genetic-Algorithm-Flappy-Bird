import time
import random
import asyncio
import json

from FlapPyBird.src.flappy import Flappy
import config


class Bird:
    def __init__(self):
        self.generation = None
        self.wait_times = None
        self.score = 0
        self.last_time = None
        self.index = 0

    def score_add(self):
        self.score += 1

    def tick(self):
        now = time.time()
        if self.index >= len(self.wait_times):
            self.wait_times.append(random.random() * config.time_range_sec)
        if now - self.last_time >= self.wait_times[self.index]:
            self.last_time = now
            self.index += 1
            return True
        else:
            return False

    def start(self):
        self.last_time = time.time()

    def game_over(self):
        print(json.dumps([self.score, self.wait_times]))

    def simulate(self):
        asyncio.run(Flappy(self).start())
