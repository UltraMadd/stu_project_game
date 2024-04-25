from os.path import abspath, join

import arcade
import pyglet.math as gmath

from entities.entity import Entity


class Player(Entity, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.speed = 3
        self.attack_radius = 100
        self.direction = gmath.Vec2(1, 1)
        self.texture = arcade.load_texture(
            abspath(join("textures", "player", "walkback1.png"))
        )
        self.hit_box_algorithm = "Detailed"
        self.set_hit_box(self.texture.hit_box_points)
