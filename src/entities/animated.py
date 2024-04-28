import arcade
from pyglet.math import Vec2


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
                    x=width*col,
                    y=height*row,
                    width=width,
                    height=height,
                    )
            textures[anim_seq[row]].append(texture)
    for key in anim_seq:
        textures[key] = reorder(textures[key])
    return textures, {key: [v[0]] for key, v in textures.items()}


class AnimatedSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.walking_textures = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
        self.staying_textures = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
        self.cur_texture_index = 0
        self.last_direction = DOWN
        self.last_center = Vec2(self.center_x, self.center_y)
        self.texture_change_distance = 20

    def update_animation(self, delta_time: float = 1 / 60):
        center = Vec2(self.center_x, self.center_y)
        textures = []
        change = center-self.last_center
        max_change = max(abs(change.x), abs(change.y))
        if abs(change.x) == max_change:
            if change.x > 0:
                textures = self.walking_textures[RIGHT]
                self.last_direction = RIGHT
            elif change.x < 0:
                textures = self.walking_textures[LEFT]
                self.last_direction = LEFT
        else:
            if change.y > 0:
                textures = self.walking_textures[UP]
                self.last_direction = UP
            elif change.y < 0:
                textures = self.walking_textures[DOWN]
                self.last_direction = DOWN

        if change.x == 0 and change.y == 0:
            textures = self.staying_textures[self.last_direction]

        if center.distance(self.last_center) >= self.texture_change_distance:
            print(change)
            self.texture = textures[self.cur_texture_index]
            self.cur_texture_index += 1
            self.cur_texture_index %= len(textures)
            self.last_center = center
         


