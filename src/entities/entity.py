from math import ceil
from time import time
from collections import deque

import arcade

from utils import get_color_from_gradient


HP_BAR_WIDTH = 50
HP_BAR_HEIGHT = 10
DAMAGE_EFFECT_TIME_DISPLAY = 2

HP_BAR_HEALTH_GRADIENT = [
    arcade.color.PASTEL_RED,
    arcade.color.PASTEL_YELLOW,
    arcade.color.PASTEL_GREEN,
]


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

    def draw_effects(self):
        pos_x, pos_y = self.center_x, self.top + HP_BAR_HEIGHT // 2
        to_pop = 0
        for damage, when_received in reversed(self.damaged_queue):
            elapsed = time() - when_received
            new_y = arcade.lerp(
                pos_y + HP_BAR_HEIGHT, pos_y + HP_BAR_HEIGHT * 3, elapsed
            )
            opacity = int(arcade.lerp(255, 0, elapsed))
            if opacity <= 0:
                to_pop += 1
            else:
                arcade.draw_text(
                    f"{-damage}",
                    pos_x,
                    new_y,
                    anchor_y="center",
                    bold=True,
                    color=arcade.color.RED + (opacity,),
                )
        for _ in range(to_pop):
            self.damaged_queue.pop()

    def draw_hp_bar(self):
        pos_x, pos_y = self.center_x, self.top + HP_BAR_HEIGHT // 2

        arcade.draw_rectangle_filled(
            pos_x,
            pos_y,
            HP_BAR_WIDTH,
            HP_BAR_HEIGHT,
            arcade.color.DARK_GREEN,
        )

        hp_bar_indicator_width = int(HP_BAR_WIDTH * self.hitpoints / self.max_hitpoints)

        arcade.draw_rectangle_filled(
            pos_x + (hp_bar_indicator_width - HP_BAR_WIDTH) / 2,
            pos_y,
            hp_bar_indicator_width,
            HP_BAR_HEIGHT,
            get_color_from_gradient(
                HP_BAR_HEALTH_GRADIENT, self.hitpoints, self.max_hitpoints
            ),
        )
