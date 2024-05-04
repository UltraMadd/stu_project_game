import math
from os.path import abspath, join
from time import time

import arcade
import pyglet.math as gmath
from arcade.experimental.shadertoy import Shadertoy

from entities.entity import Entity
from entities.animated import AnimatedSprite, load_default_animated
from utils import get_color_from_gradient, mul_vec_const, sprite_pos


MIN_ENEMY_TP = 0
MAX_ENEMY_TP = 4

HP_BAR_WIDTH = 50
HP_BAR_HEIGHT = 10
DAMAGE_EFFECT_TIME_DISPLAY = 2

HP_BAR_HEALTH_GRADIENT = [
    arcade.color.PASTEL_RED,
    arcade.color.PASTEL_YELLOW,
    arcade.color.PASTEL_GREEN,
]

def sigmoid(x):
    return 1/(1 + math.exp(-x))


class EnemyAttack:
    def __init__(self, attack_range=128, damage=5, no_attack=False):
        self.attack_range = attack_range
        self.attack_start_range = attack_range // 2
        self.prepare_time = 0.5
        self.attack_time = 0.5 + self.prepare_time
        self.end_time = 0.3 + self.attack_time
        self.damage = damage
        self.no_attack = no_attack

    @classmethod
    def simple(cls):
        return cls(128)
    
    @classmethod
    def no_attack(cls, attack_range=128):
        return cls(no_attack=True, attack_range=attack_range)


def load_enemy_texture(fname):
    return load_default_animated(abspath(join("textures", "enemy", fname)))


class Enemy(Entity, AnimatedSprite):
    def __init__(
        self,
        scale=0.4,
        center_x=0,
        center_y=0,
        speed=128,
        kill_xp_reward=40,
        attack: EnemyAttack = EnemyAttack.simple(),
        textures=load_enemy_texture("Enemy 16-2.png"),
        tp=0,
        shadertoys=None,
        *args,
        **kwargs,
    ):
        if shadertoys is None:
            raise ValueError
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.speed = speed
        self.attack = attack
        self.is_attacking = False
        self.attacking_target = None
        self.damaged = False
        self.scale = 1.5
        self.attacking_timer = 0
        self.walking_textures, self.staying_textures = textures
        self.center_x = center_x
        self.center_y = center_y
        self.kill_xp_reward = kill_xp_reward
        self.tp = tp
        self.does_activate_shield = False
        self.shield_shadertoy = shadertoys['shield']
        if self.tp == 2:
            self.glowing_ball_shadertoy = shadertoys["glowing_ball"]
        elif self.tp == 4:
            self.does_activate_shield = True

    @classmethod
    def from_tp(cls, tp: int = 0, *args, **kwargs):
        if tp == 0:
            return cls(
                *args,
                attack=EnemyAttack(128, 5),
                kill_xp_reward=40,
                speed=128,
                tp=tp,
                hitpoints=90,
                **kwargs,
            )
        elif tp == 1:
            return cls(
                *args,
                attack=EnemyAttack(64, 15),
                kill_xp_reward=60,
                speed=96,
                textures=load_enemy_texture("Enemy 04-1.png"),
                tp=tp,
                hitpoints=120,
                **kwargs,
            )
        elif tp == 2:
            return cls(
                *args,
                attack=EnemyAttack(512, 10),
                kill_xp_reward=100,
                speed=69,
                textures=load_enemy_texture("Enemy 21.png"),
                tp=tp,
                hitpoints=50,
                **kwargs,
            )
        elif tp == 3:
            return cls(
                *args,
                attack=EnemyAttack(64, 50),
                kill_xp_reward=300,
                speed=89,
                textures=load_enemy_texture("Enemy 22.png"),
                tp=tp,
                hitpoints=500,
                **kwargs,
            )
        elif tp == 4:
            return cls(
                *args,
                attack=EnemyAttack.no_attack(512),
                kill_xp_reward=400,
                speed=105,
                textures=load_enemy_texture("Enemy 02-1.png"),
                tp=tp,
                hitpoints=750,
                **kwargs,
            )


    def update(self):
        self.update_animation()

    def start_attacking(self, target):
        self.is_attacking = True
        self.damaged = False
        self.attacking_timer = 0
        self.attacking_target = target

    def update_attack(self, delta_time):
        if self.attack.no_attack:
            return
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
            pass
        elif self.attacking_timer < self.attack.end_time:
            pass
        else:
            if not self.damaged:
                self.attacking_target.damage(self.attack.damage)
                self.damaged = True
            self.is_attacking = False

    def draw_attack(self, parent_view):
        if not self.is_attacking:
            return
        if self.tp == 2:
            time_fly = self.attacking_timer - self.attack.prepare_time
            if time_fly < 0:
                return
            time_fly_total = self.attack.end_time - self.attack.prepare_time
            ball_position = (
                mul_vec_const(
                    sprite_pos(self.attacking_target) - sprite_pos(self),
                    time_fly / time_fly_total,
                )
                + sprite_pos(self)
                - parent_view.camera.position
            )

            self.glowing_ball_shadertoy.program["pos"] = ball_position
            self.glowing_ball_shadertoy.program["color"] = arcade.color.VIOLET
            self.glowing_ball_shadertoy.program["radius"] = 10
            self.glowing_ball_shadertoy.render()

    def draw_shield(self, parent_view):
        self.shield_shadertoy.program["pos"] = sprite_pos(self) - parent_view.camera.position
        self.shield_shadertoy.program["color"] = arcade.get_three_float_color(arcade.color.LIGHT_BLUE)
        self.shield_shadertoy.program["radius"] = self.height * 3 / 4
        self.shield_shadertoy.render()

    # !!!!!! TRASH CODE ALERT !!!!!! 
    def draw_effects(self, parent_view):
        self.draw_attack(parent_view)
        if self.tp == 4:
            self.draw_shield(parent_view)
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
        if self.hitpoints < 0:
            return
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
