from os.path import abspath, join
from time import time

import arcade
import pyglet.math as gmath

from entities.entity import Entity
from views.upgrade_tree import IDF2UPGRADE


LVL_GROWTH = 1.2


class Player(Entity, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.speed = 3
        self.attack_range = 100
        self.attack_damage = 10
        self.direction = gmath.Vec2(1, 1)
        self.texture = arcade.load_texture(
            abspath(join("textures", "player", "walkback1.png"))
        )
        self.hit_box_algorithm = "Detailed"
        self.set_hit_box(self.texture.hit_box_points)
        self.is_attacking = False
        self.attacking_timer = 0
        self.xp = 10000
        self.max_xp = 100
        self.points = 0
        self.heal_speed = 0
        self.attack_speed = 1
        self.attack_time = 0.5
        self.acquired_upgrades_idf = set()
        self.last_heal = time()

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
        self.max_hitpoints = 100
        self.heal_speed = 0
        self.attack_damage = 10
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
