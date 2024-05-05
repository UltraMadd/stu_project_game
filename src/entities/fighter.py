from dataclasses import dataclass
from os.path import abspath, join
from random import randint, random
import math

import arcade
from arcade.experimental.shadertoy import Shadertoy
from pyglet.math import Vec2

from entities.player import Player
from utils import EPS, get_random_direction, mul_vec_const, triange_area_3p, sprite_pos


def load_boss_textures(filepath, row, width=96, height=96):
    frames = []
    for col in range(3):
        frames.append(
            arcade.AnimationKeyframe(
                col,
                120,
                arcade.load_texture(
                    filepath, x=col * width, y=row * height, width=width, height=height
                ),
            )
        )
    return frames


class Fighter:
    def __init__(self) -> None:
        super().__init__()
        self.hitpoints = None
        self.max_hitpoints = None
        self.is_dead = False
        self.is_ready_to_hide = False
        self.parent_view = None

    def damage(self, amount: int):
        self.hitpoints -= amount
        if self.hitpoints < 0:
            self.is_dead = True
            self.hitpoints = 0

    def attack(self, player: Player, delta_time: float):
        raise NotImplementedError()

    def setup(self):
        raise NotImplementedError()


SHIELD_VISUAL_RADIUS = 45
SHIELD_VISUAL_RADIUS_VARY = 5
LIGHTNINGS_TIME_ACTIVE = 6


@dataclass
class Lightning:
    rot: float
    last_damage: float = 0.0
    rot_offset: float = 0.0
    damage: int = 50
    color: arcade.Color = arcade.color.WHITE


@dataclass
class Ball:
    pos: Vec2
    dir: Vec2
    speed: float
    radius: float
    color: arcade.Color
    visible: bool = True


class FirstBoss(Fighter, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = load_boss_textures(
            abspath(join("textures", "boss", "Boss 01.png")), 0
        )
        self.max_hitpoints = 10000
        self.hitpoints = self.max_hitpoints
        self.cur_attack_type = None
        self.speed = 200
        self.attacking_time = 0
        self.is_shield_active = False
        self.dead_time = None
        self.shield_shadertoy = Shadertoy
        self.lightning_shadertoy = Shadertoy
        self.lightnings = []
        self.balls_shadertoy = Shadertoy
        self.balls = []
        self.last_spawned_ball_time = 0
        self.draw_cum_delta_time = 0

    def setup(self):
        self.shield_shadertoy = Shadertoy.create_from_file(
            self.parent_view.window.get_size(), "src/shader/shield.glsl"
        )
        self.lightning_shadertoy = Shadertoy.create_from_file(
            self.parent_view.window.get_size(), "src/shader/lightning.glsl"
        )
        self.balls_shadertoy = Shadertoy.create_from_file(
            self.parent_view.window.get_size(), "src/shader/glowing_ball.glsl"
        )
        self.boss_kill_shadertoy = Shadertoy.create_from_file(
            self.parent_view.window.get_size(), "src/shader/boss_kill.glsl"
        )

    def draw_attack(self):
        if self.is_shield_active:
            self.shield_shadertoy.program["pos"] = (
                sprite_pos(self) - self.parent_view.camera.position
            )
            self.shield_shadertoy.program["color"] = arcade.get_three_float_color(
                arcade.color.LIGHT_BLUE
            )
            self.shield_shadertoy.program["radius"] = (
                math.cos(self.draw_cum_delta_time) * SHIELD_VISUAL_RADIUS_VARY
                + SHIELD_VISUAL_RADIUS
            )

            self.shield_shadertoy.render()

        for lightning in self.lightnings:
            self.lightning_shadertoy.program["pos"] = (
                sprite_pos(self) - self.parent_view.camera.position
            )
            self.lightning_shadertoy.program["rot"] = lightning.rot
            self.lightning_shadertoy.program["radius"] = 40
            self.lightning_shadertoy.program["color"] = lightning.color

            self.lightning_shadertoy.render()

        for ball in self.balls:
            if not ball.visible:
                continue
            self.balls_shadertoy.program["pos"] = (
                ball.pos - self.parent_view.camera.position
            )
            self.balls_shadertoy.program["color"] = arcade.color.ORANGE_RED
            self.balls_shadertoy.program["radius"] = ball.radius

            self.balls_shadertoy.render()

    def draw_death(self):
        self.boss_kill_shadertoy.program["pos"] = (
            sprite_pos(self) - self.parent_view.camera.position
        )
        self.boss_kill_shadertoy.program["color"] = arcade.color.ANTI_FLASH_WHITE
        since_death = self.draw_cum_delta_time - self.dead_time
        if since_death == 0:
            since_death = EPS
        radius = math.exp(since_death**4)
        self.boss_kill_shadertoy.program["radius"] = radius
        if radius > self.parent_view.camera.viewport_width:
            self.is_ready_to_hide = True

        self.boss_kill_shadertoy.render()

    def draw_ui(self):
        if self.is_dead and self.dead_time is not None:
            self.draw_death()

    def on_draw(self):
        if not self.is_dead or self.dead_time is None:
            self.draw_attack()
        self.draw()

    def activate_shield(self):
        self.is_shield_active = True

    def deactivate_shield(self):
        self.is_shield_active = False

    def on_update(self, delta_time: float = 1 / 60):
        self.draw_cum_delta_time += delta_time
        if not self.is_dead:
            self.update_animation(delta_time)
        else:
            self.visible = False
            if self.dead_time is None:
                self.dead_time = self.draw_cum_delta_time

    def damage(self, amount: int):
        if not self.is_shield_active:
            return super().damage(amount)

    def attack(self, player: Player, delta_time: float):
        if self.is_dead:
            self.balls.clear()
            self.lightnings.clear()
            return
        self.update_balls(player, delta_time)
        if self.cur_attack_type is None:
            self.attacking_time = 0
            self.cur_attack_type = randint(0, 2)
        else:
            self.attacking_time += delta_time
        # Shield
        if self.cur_attack_type == 0:
            self.activate_shield()
            if not self.lightnings:
                self.lightnings = [
                    Lightning(0),
                    Lightning(0, rot_offset=math.pi / 2),
                    Lightning(0, rot_offset=math.pi / 4),
                    Lightning(0, rot_offset=math.pi * 3 / 4),
                ]
            for lightning in self.lightnings:
                time_active = self.attacking_time
                lightning.rot = (
                    arcade.lerp(0, 2 * math.pi, time_active / 6) + lightning.rot_offset
                )
                if (
                    self.draw_cum_delta_time - lightning.last_damage > 0.2
                    and triange_area_3p(
                        sprite_pos(player),
                        sprite_pos(self),
                        Vec2(
                            self.center_x + math.cos(lightning.rot),
                            self.center_y + math.sin(lightning.rot),
                        ),
                    )
                    < 10
                ):
                    lightning.last_damage = self.draw_cum_delta_time
                    player.damage(lightning.damage)
            if self.attacking_time > LIGHTNINGS_TIME_ACTIVE:
                self.lightnings.clear()
                self.deactivate_shield()
                self.cur_attack_type = None
                self.last_lightnings_toggle = 0
        # Give a player time to attack
        elif self.cur_attack_type == 1:
            if self.attacking_time > 3:
                self.cur_attack_type = None
        elif self.cur_attack_type == 2:
            if (
                self.attacking_time - self.last_spawned_ball_time > 0.5
            ):  # attacking time is a FLOAT, ok to mod here
                player2boss_dist = sprite_pos(player).distance(sprite_pos(self))
                self.balls.append(
                    Ball(
                        sprite_pos(self),
                        (
                            mul_vec_const(get_random_direction(), 1 / 3)
                            + (sprite_pos(player) - sprite_pos(self)).normalize()
                        ).normalize(),
                        player2boss_dist,
                        randint(5, 15),
                        arcade.color.DARK_ORANGE,
                    )
                )
                self.last_spawned_ball_time = self.attacking_time
            if self.attacking_time > 10:
                self.last_spawned_ball_time = 0
                self.cur_attack_type = None

    def update_balls(self, player: Player, delta_time: float):
        for candidate_pos, candidate_ball in enumerate(reversed(self.balls)):
            if not candidate_ball.visible:
                self.balls.pop(len(self.balls) - candidate_pos - 1)
        for ball in self.balls:
            if not ball.visible:
                continue
            if ball.pos.distance(sprite_pos(player)) <= ball.radius + min(
                player.width, player.height
            ):
                player.damage(50 + int(500 / ball.radius))
                ball.visible = False
            ball2center_dist = ball.pos.distance(sprite_pos(self))
            if ball2center_dist > self.parent_view.arena_width:
                ball.visible = False
            ball.speed += ball2center_dist * delta_time

            ball.pos += mul_vec_const(ball.dir, ball.speed * delta_time)
