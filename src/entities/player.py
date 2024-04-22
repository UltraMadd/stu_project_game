import arcade
from os.path import abspath, join

from entities.entity import Entity

class Player(Entity, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.speed = 2
        self.texture = arcade.load_texture(abspath(join("textures", "player", "walkback1.png")))
        self.hit_box_algorithm = "Detailed"
        self.set_hit_box(self.texture.hit_box_points)

