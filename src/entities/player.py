import arcade
from os.path import abspath, join


class Player(arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.5
        self.texture = arcade.load_texture(abspath(join("..", "textures", "player", "walkback1.png")))
        self.set_hit_box(self.texture.hit_box_points)
