from os.path import abspath, join

import arcade
import pyglet.math as gmath

from entities.entity import Entity


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
        self.xp = 0
        self.max_xp = 1000
        self.acquired_upgrades_idf = set()

    def start_attacking(self):
        self.is_attacking = True
        self.attacking_timer = 0

    def update_attack(self, delta_time):
        if not self.is_attacking:
            return
        self.attacking_timer += delta_time
        if self.attacking_timer > 0.5:
            self.is_attacking = False
