import arcade
from pyglet.math import Vec2


def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_w, rect_h):
    return (rect_x < point_x < rect_x + rect_w) and (rect_y < point_y < rect_y + rect_h)


def sprite_pos(sprite: arcade.Sprite) -> Vec2:
    return Vec2(sprite.center_x, sprite.center_y)


def mul_vec_const(vec: Vec2, const) -> Vec2:
    return Vec2(vec.x * const, vec.y * const)
