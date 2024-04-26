import math
from os.path import abspath, join
from random import randint

import arcade
import pyglet.math as gmath
from pyglet.math import Vec2

from entities.player import Player
from entities.enemy import Enemy
from utils import mul_vec_const, is_point_in_rect, sprite_pos


HP_BAR_WIDTH = 500
HP_BAR_HEIGHT = 50
HP_TEXT_SIZE = 20


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = None
        self.scene = None
        self.player = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False
        self.physics_engine = None
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.scene = None
        self.attacks_list = None

    def setup(self):
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player.center_x = 2000
        self.player.center_y = 2000
        self.attacks_list = arcade.SpriteList()

        self.tiled_map = arcade.load_tilemap(abspath(join("map", "map1.tmx")), 1)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player)
        self.setup_animations()
        self.setup_physics()

        self.enemies = arcade.SpriteList()
        self.enemies.append(Enemy(center_x=1500, center_y=1500))

    def load_player_animation_frames(self, all_frames: str):
        res = []
        for i in (1, 0, 1, 2):
            texturee = arcade.load_texture(
                abspath(join("textures", "player", all_frames)),
                x=i * 32,
                y=0,
                width=32,
                height=32,
            )
            anim = arcade.AnimationKeyframe(i, 120, texturee)
            res.append(anim)
        return res

    def setup_animations(self):
        if self.player.change_x == 0 and self.player.change_y == 0:
            self.player.frames = [
                arcade.AnimationKeyframe(0, 120, self.player.texture)
            ] * 4  # FIXME Костыль*3?
        if self.player.change_x < 0:
            self.player.frames = self.load_player_animation_frames("walkleft.png")
        elif self.player.change_x > 0:
            self.player.frames = self.load_player_animation_frames("walkright.png")
        if self.player.change_y < 0:
            self.player.frames = self.load_player_animation_frames("walkdown.png")
        elif self.player.change_y > 0:
            self.player.frames = self.load_player_animation_frames("walkup.png")

    def setup_physics(self):
        self.player_list.append(self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, walls=[self.scene["water"], self.scene["groundcollision1"]]
        )

    def center_camera_to_player(self):
        scr_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        scr_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        if scr_center_x < 0:
            scr_center_x = 0
        if scr_center_y < 0:
            scr_center_y = 0

        player_centered = [scr_center_x, scr_center_y]

        self.camera.move_to(player_centered)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def draw_hp(self):
        centx = self.camera.position.x + self.camera.viewport_width // 2
        centy = self.camera.position.y + HP_BAR_HEIGHT

        arcade.draw_rectangle_filled(
            centx, centy, HP_BAR_WIDTH, HP_BAR_HEIGHT, arcade.color.DARK_GREEN
        )
        arcade.draw_rectangle_outline(
            centx, centy, HP_BAR_WIDTH, HP_BAR_HEIGHT, arcade.color.BLACK
        )

        hp_bar_indicator_width = int(
            HP_BAR_WIDTH * self.player.hitpoints / self.player.max_hitpoints
        )
        arcade.draw_texture_rectangle(
            centx + (hp_bar_indicator_width - HP_BAR_WIDTH) / 2,
            centy,
            hp_bar_indicator_width,
            HP_BAR_HEIGHT,
            arcade.load_texture(abspath(join("textures", "img.png"))),
        )

        arcade.draw_text(
            f"{self.player.hitpoints} / {self.player.max_hitpoints}",
            centx,
            centy - HP_TEXT_SIZE // 2,
            arcade.color.WHITE,
            HP_TEXT_SIZE,
            anchor_x="center",
        )

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player_list.draw()
        self.enemies.draw()
        for enemy in self.enemies:
            enemy.draw_hp_bar()
            enemy.draw_effects()

        self.draw_hp()

    def on_update(self, delta_time):
        self.process_keychange(delta_time)
        self.center_camera_to_player()
        self.physics_engine.update()
        self.setup_animations()
        self.update_enemies(delta_time)
        try:
            if self.player.frames:
                self.player_list.update_animation()
        except IndexError as e:
            print(e, self.player.frames)

    def update_enemies(self, delta_time):
        i = len(self.enemies) - 1
        while i >= 0:  # TODO use "for"?
            if self.enemies[i].dead:
                self.enemies.pop(i)
            i -= 1

        if len(self.enemies) < 10:  # TODO just for testing purposes here, replace later
            for _ in range(10 - len(self.enemies)):
                self.enemies.append(
                    Enemy(center_x=randint(0, 2000), center_y=randint(0, 2000))
                )

        player_pos = sprite_pos(self.player)
        for enemy in self.enemies:
            camera_x, camera_y = self.camera.position
            camera_w, camera_h = self.camera.viewport_width, self.camera.viewport_height
            enemy_pos = sprite_pos(enemy)
            enemy2player_distance = player_pos.distance(enemy_pos)

            if enemy.is_attacking:
                enemy.update_attack(delta_time)
            elif enemy2player_distance <= enemy.attack.attack_start_range:
                enemy.start_attacking(self.player)
            elif is_point_in_rect(
                enemy.center_x,
                enemy.center_y,
                camera_x,
                camera_y,
                camera_w,
                camera_h,
            ):
                if not enemy.is_attacking:
                    enemy_x_delta, enemy_y_delta = (player_pos - enemy_pos).normalize()
                    enemy.center_x += enemy_x_delta * delta_time * enemy.speed
                    enemy.center_y += enemy_y_delta * delta_time * enemy.speed

    def process_keychange(self, delta_time):
        self.player.direction = self.player.direction.normalize()
        self.player.change_x, self.player.change_y = mul_vec_const(
            self.player.direction, self.player.speed
        )

        if self.up_pressed and not self.down_pressed:
            self.player.direction.y = 1
        elif self.down_pressed and not self.up_pressed:
            self.player.direction.y = -1
        else:
            self.player.change_y = 0

        if self.left_pressed and not self.right_pressed:
            self.player.direction.x = -1
        elif self.right_pressed and not self.left_pressed:
            self.player.direction.x = 1
        else:
            self.player.change_x = 0

        if self.space_pressed:
            player_pos = sprite_pos(self.player)
            for enemy in self.enemies:
                enemy_pos = sprite_pos(enemy)
                attack_end_pos = player_pos + mul_vec_const(
                    self.player.direction, self.player.attack_range
                )
                c = attack_end_pos.distance(enemy_pos)
                a = attack_end_pos.distance(player_pos)
                b = enemy_pos.distance(player_pos)
                player_enemy_angle = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
                if player_enemy_angle < math.pi / 2 and b < self.player.attack_range:
                    if self.player.is_attacking:
                        self.player.update_attack(delta_time)
                    else:
                        self.player.start_attacking()
                        enemy.damage(self.player.attack_damage)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.up_pressed = True
        elif symbol == arcade.key.S:
            self.down_pressed = True
        elif symbol == arcade.key.A:
            self.left_pressed = True
        elif symbol == arcade.key.D:
            self.right_pressed = True
        elif symbol == arcade.key.SPACE:
            self.space_pressed = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.up_pressed = False
        elif symbol == arcade.key.S:
            self.down_pressed = False
        elif symbol == arcade.key.A:
            self.left_pressed = False
        elif symbol == arcade.key.D:
            self.right_pressed = False
        elif symbol == arcade.key.SPACE:
            self.space_pressed = False
