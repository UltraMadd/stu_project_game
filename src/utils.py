from math import ceil
from random import random

import arcade
from pyglet.math import Vec2


EPS = 1e-3


def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_w, rect_h):
    return (rect_x < point_x < rect_x + rect_w) and (rect_y < point_y < rect_y + rect_h)


def sprite_pos(sprite: arcade.Sprite) -> Vec2:
    return Vec2(sprite.center_x, sprite.center_y)


def mul_vec_const(vec: Vec2, const) -> Vec2:
    return Vec2(vec.x * const, vec.y * const)


def get_color_from_gradient(gradient, value, max_value):
    return gradient[ceil(value / max_value * len(gradient)) - 1]


def triange_area_3p(p1: Vec2, p2: Vec2, p3: Vec2):
    return (
        1 / 2 * abs(p1.y * (p2.x - p3.x) + p2.y * (p3.x - p1.x) + p3.y * (p1.x - p2.x))
    )


def get_random_direction() -> Vec2:
    x = random() - 0.5
    y = random() - 0.5
    return Vec2(x, y).normalize()  # I know you can do it without the method
