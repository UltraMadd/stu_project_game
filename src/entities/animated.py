import arcade
from pyglet.math import Vec2

from utils import EPS


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


def reorder(lst):
    return [lst[1], lst[0], lst[1], lst[2]]


def load_default_animated(filepath, width=32, height=32):
    anim_seq = (DOWN, LEFT, RIGHT, UP)  # Hardcoded is kinda ok
    textures = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
    for row in range(len(anim_seq)):
        for col in range(3):
            texture = arcade.load_texture(
                filepath,
                x=width * col,
                y=height * row,
                width=width,
                height=height,
            )
            textures[anim_seq[row]].append(texture)
    for key in anim_seq:
        textures[key] = reorder(textures[key])
    return textures, {key: [v[0]] for key, v in textures.items()}


class AnimatedSprite(arcade.Sprite):
    def __init__(self, *args, default_direction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.walking_textures = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
        self.staying_textures = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
        self.cur_texture_index = 0
        self.default_direction = default_direction
        self.last_direction = DOWN
        self.last_center = Vec2(self.center_x, self.center_y)
        self.first_change = True
        self.texture_change_distance = 20

    def update_animation(self, delta_time: float = 1 / 60):
        center = Vec2(self.center_x, self.center_y)
        textures = []
        change = center - self.last_center
        max_change = max(abs(change.x), abs(change.y))
        changed_direction = False
        if abs(change.x) == max_change:
            if change.x > EPS:
                textures = self.walking_textures[RIGHT]
                self.last_direction = RIGHT
                changed_direction = True
            elif change.x < -EPS:
                textures = self.walking_textures[LEFT]
                self.last_direction = LEFT
                changed_direction = True
        else:
            if change.y > EPS:
                textures = self.walking_textures[UP]
                self.last_direction = UP
                changed_direction = True
            elif change.y < -EPS:
                textures = self.walking_textures[DOWN]
                self.last_direction = DOWN
                changed_direction = True

        if not changed_direction:
            if self.default_direction is not None:
                self.last_direction = self.default_direction
            textures = self.staying_textures[self.last_direction]

        if (
            center.distance(self.last_center) >= self.texture_change_distance
            or self.first_change
        ):
            self.texture = textures[self.cur_texture_index]
            self.cur_texture_index += 1
            self.cur_texture_index %= len(textures)
            self.last_center = center
            self.first_change = False
