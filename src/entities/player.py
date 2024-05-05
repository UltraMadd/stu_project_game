from dataclasses import dataclass
from os.path import abspath, join
from time import time
import math

import arcade
from pyglet.math import Vec2

from entities.entity import Entity
from utils import mul_vec_const
from views.upgrade_tree import IDF2UPGRADE


LVL_GROWTH = 1.3


@dataclass
class Goto:
    idf: str
    x: int
    y: int


DEF_MAX_HP = 100
DEF_DAMAGE = 15
DEF_HEAL = 5


class Player(Entity, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.speed = 3
        self.attack_range = 100
        self.attack_damage = DEF_DAMAGE
        self.direction = Vec2(1, 1)
        self.texture = arcade.load_texture(
            abspath(join("textures", "player", "walkback1.png"))
        )
        self.hit_box_algorithm = "Detailed"
        self.set_hit_box(self.texture.hit_box_points)
        self.is_attacking = False
        self.attacking_timer = 0
        self.xp = 0

        self.max_xp = 100
        self.points = 0
        self.heal_speed = DEF_HEAL
        self.max_hitpoints = DEF_MAX_HP
        self.attack_speed = 1
        self.attack_time = 0.5
        self.acquired_upgrades_idf = set()
        self.last_heal = time()
        self.gotos = []

    def update(self):
        if time() - self.last_heal >= 1:
            self.hitpoints = min(self.hitpoints + self.heal_speed, self.max_hitpoints)
            self.last_heal = time()

    def start_attacking(self):
        self.is_attacking = True
        self.attacking_timer = 0

    def update_attack(self, delta_time):
        if not self.is_attacking:
            return
        self.attacking_timer += delta_time
        if self.attacking_timer * self.attack_speed > self.attack_time:
            self.is_attacking = False

    def update_stats(self):
        self.max_hitpoints = DEF_MAX_HP
        self.heal_speed = DEF_HEAL
        self.attack_damage = DEF_DAMAGE
        self.attack_speed = 1
        damage_mult = 1
        for idf in self.acquired_upgrades_idf:
            upgrade = IDF2UPGRADE[idf]
            if upgrade.hp_buff:
                self.max_hitpoints += upgrade.hp_buff
            if upgrade.heal_buff:
                self.heal_speed += upgrade.heal_buff
            if upgrade.damage_buff:
                damage_mult *= upgrade.damage_buff
            if upgrade.damage_add:
                self.attack_damage += upgrade.damage_add
            if upgrade.attack_speed_buff:
                self.attack_speed *= upgrade.attack_speed_buff
        self.attack_damage *= damage_mult

    def gain_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.points += 1
            self.max_xp *= LVL_GROWTH
            self.max_xp = int(self.max_xp)

    def add_goto(self, goto: Goto):
        self.gotos.append(goto)

    def remove_goto(self, idf: int) -> bool:
        index = None
        for cur_index, goto in enumerate(self.gotos):
            if goto.idf == idf:
                index = cur_index
        if index:
            self.gotos.pop(index)
            return True
        return False

    def can_attack(self, enemy_pos: Vec2) -> bool:
        player_pos = Vec2(self.center_x, self.center_y)
        attack_end_pos = player_pos + mul_vec_const(self.direction, self.attack_range)
        c = attack_end_pos.distance(enemy_pos)
        a = attack_end_pos.distance(player_pos)
        b = enemy_pos.distance(player_pos)
        player_enemy_angle = math.acos(
            max(min((a**2 + b**2 - c**2) / (2 * a * b), 1), -1)
        )
        return player_enemy_angle < math.pi / 2 and b < self.attack_range
