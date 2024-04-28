from os.path import abspath, join
from time import time

import arcade
import pyglet.math as gmath

from entities.entity import Entity
from utils import get_color_from_gradient


HP_BAR_WIDTH = 50
HP_BAR_HEIGHT = 10
DAMAGE_EFFECT_TIME_DISPLAY = 2

HP_BAR_HEALTH_GRADIENT = [
    arcade.color.PASTEL_RED,
    arcade.color.PASTEL_YELLOW,
    arcade.color.PASTEL_GREEN,
]


class EnemyAttack:
    def __init__(self, attack_range):
        self.attack_range = attack_range
        self.attack_start_range = attack_range // 2
        self.prepare_time = 0.5
        self.attack_time = 0.5 + self.prepare_time
        self.end_time = 0.3 + self.attack_time

    @classmethod
    def simple(cls):
        return cls(128)


class Enemy(Entity):
    def __init__(
        self,
        scale=0.4,
        center_x=0,
        center_y=0,
        speed=128,
        kill_xp_reward=40,
        attack: EnemyAttack = EnemyAttack.simple(),
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.speed = speed
        self.attack = attack
        self.is_attacking = False
        self.attacking_target = None
        self.damaged = False
        self.attacking_timer = 0
        self.scale = 2
        self.hit_box_algorithm = "Detailed"
        self.texture = arcade.load_texture(
            abspath(join("textures", "enemy", "Enemy 16-2.png")),
            width=32,
            height=32,
        )
        self.set_hit_box(self.texture.hit_box_points)
        self.center_x = center_x
        self.center_y = center_y
        self.kill_xp_reward = kill_xp_reward

    def start_attacking(self, target):
        self.is_attacking = True
        self.damaged = False
        self.attacking_timer = 0
        self.attacking_target = target

    def update_attack(self, delta_time):
        self.attacking_timer += delta_time
        target_pos = gmath.Vec2(
            self.attacking_target.center_x, self.attacking_target.center_y
        )
        enemy_pos = gmath.Vec2(self.center_x, self.center_y)
        enemy2target_distance = target_pos.distance(enemy_pos)

        if (
            self.attacking_timer < self.attack.end_time
            and enemy2target_distance > self.attack.attack_range
        ):
            self.attacking_timer = self.attack.end_time
        if self.attacking_timer < self.attack.prepare_time:
            pass
        elif self.attacking_timer < self.attack.attack_time:
            if not self.damaged:
                self.attacking_target.damage(5)
                self.damaged = True
        elif self.attacking_timer < self.attack.end_time:
            pass
        else:
            self.is_attacking = False

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
                    f"{-damage:.1f}",
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

