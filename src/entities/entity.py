from collections import deque
from time import time

import arcade


class Entity(arcade.Sprite):
    def __init__(self, *args, hitpoints=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_hitpoints = hitpoints
        self.hitpoints = hitpoints
        self.hit_box_algorithm = "Detailed"
        self.dead = False
        self.damaged_queue = deque()  # sorted by time

    def damage(self, amount: int):
        self.hitpoints -= amount
        self.damaged_queue.appendleft((amount, time()))
        if self.hitpoints <= 0:
            self.dead = True
