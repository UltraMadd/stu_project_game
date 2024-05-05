import math
from os.path import abspath, join
from random import randint

import arcade
import arcade.gui
import pyglet.math as gmath
from arcade.experimental.shadertoy import Shadertoy
from pyglet.math import Vec2

from entities.player import Goto, Player
from entities.animated import DOWN, load_default_animated
from entities.fighter import FirstBoss
from entities.enemy import Enemy, MIN_ENEMY_TP, MAX_ENEMY_TP
from utils import get_color_from_gradient, mul_vec_const, is_point_in_rect, sprite_pos
from views.dialog_view import INCOGNITO_START, DialogView, Incognito, Npc
from views.fight_view import FightView
from views.upgrade_tree import UpgradeTreeView


HP_BAR_WIDTH = 500
HP_BAR_HEIGHT = 50
HP_BAR_TEXT_SIZE = 20

XP_BAR_WIDTH = 300
XP_BAR_HEIGHT = 30
XP_BAR_TEXT_SIZE = 15

BARS_SPACING = 10
BARS_BACKGROUND_COLOR = arcade.color.DARK_GREEN

HP_BAR_HEALTH_GRADIENT = [
    arcade.color.PASTEL_RED,
    arcade.color.PASTEL_GREEN,
    arcade.color.PASTEL_GREEN,
]
CHECK_PERF = False
NPC_TRIGGER_DISTANCE = 100
NPC2ICON_DISTANCE = 20
TIP_MARGIN = 5


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = None
        self.enemy_list = None
        self.scene = None
        self.player = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False
        self.f_pressed = False
        self.physics_engine = None
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.scene = None
        self.has_been_setup = False
        self.npc = None
        self.is_fighting = False
        self.freeze_enemies = False

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.npc = arcade.SpriteList()

        self.player = Player()

        self.player.center_x = 2000
        self.player.center_y = 2000
        incognito = Incognito(
            player=self.player, default_direction=DOWN, center_x=1747, center_y=4500
        )
        self.attacks_list = arcade.SpriteList()
        layer_options = {
            "groundcollision1": {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Detailed",
                "hit_box_details": 20,
            },
        }
        self.tiled_map = arcade.load_tilemap(
            abspath(join("map", "map1.json")), 1, layer_options
        )
        self.npc.append(incognito)

        self.map_width = self.tiled_map.width * self.tiled_map.tile_width
        self.map_height = self.tiled_map.height * self.tiled_map.tile_height
        target = self.tiled_map
        for attr in dir(target):
            ...  # print(attr, getattr(target, attr))
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite_list("player", use_spatial_hash=True)
        self.scene.add_sprite("player", self.player)
        self.setup_animations()
        self.setup_physics()

        self.enemy_shadertoys = {}
        self.enemy_shadertoys["glowing_ball"] = Shadertoy.create_from_file(
            self.window.get_size(), "src/shader/glowing_ball.glsl"
        )
        self.enemy_shadertoys["shield"] = Shadertoy.create_from_file(
            self.window.get_size(), "src/shader/shield.glsl"
        )

        if CHECK_PERF:
            arcade.enable_timings()

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
            self.player,
            walls=[self.scene["water"], self.scene["groundcollision1"]],
        )

    def center_camera_to_player(self, restrict=False):
        scr_center_x = self.player.center_x - self.camera.viewport_width / 2
        scr_center_y = self.player.center_y - self.camera.viewport_height / 2

        if restrict:
            scr_center_x = max(
                min(scr_center_x, self.map_width - self.camera.viewport_width), 0
            )
            scr_center_y = max(
                min(scr_center_y, self.map_height - self.camera.viewport_height), 0
            )

        player_centered = Vec2(scr_center_x, scr_center_y)

        self.camera.move_to(player_centered)

    def on_show_view(self):
        self.is_fighting = False
        if not self.has_been_setup:
            self.setup()
            self.has_been_setup = True
        self.player.update_stats()

    def draw_bar(
        self,
        center_x,
        center_y,
        width,
        height,
        value,
        max_value,
        indicator_color,
        background_color,
        outline_color,
        text_size,
    ):
        arcade.draw_rectangle_filled(
            center_x, center_y, width, height, background_color
        )
        arcade.draw_rectangle_outline(center_x, center_y, width, height, outline_color)

        indicator_width = int(width * value / max_value)
        arcade.draw_rectangle_filled(
            center_x + (indicator_width - width) // 2,
            center_y,
            indicator_width,
            height,
            indicator_color,
        )

        arcade.draw_text(
            f"{value} / {max_value}",
            center_x,
            center_y - text_size // 2,
            arcade.color.WHITE,
            text_size,
            anchor_x="center",
            bold=True,
        )

    def draw_bars(self, draw_hp=False, draw_xp=False):
        left_margin = HP_BAR_HEIGHT

        hp_bar_y = self.camera.position.y + HP_BAR_HEIGHT

        if draw_hp:
            self.draw_bar(
                self.camera.position.x + HP_BAR_WIDTH // 2 + left_margin,
                hp_bar_y,
                HP_BAR_WIDTH,
                HP_BAR_HEIGHT,
                self.player.hitpoints,
                self.player.max_hitpoints,
                get_color_from_gradient(
                    HP_BAR_HEALTH_GRADIENT,
                    self.player.hitpoints,
                    self.player.max_hitpoints,
                ),
                BARS_BACKGROUND_COLOR,
                arcade.color.BLACK,
                HP_BAR_TEXT_SIZE,
            )

        if draw_xp:
            xp_bar_y = hp_bar_y + XP_BAR_HEIGHT + HP_BAR_HEIGHT // 2

            self.draw_bar(
                self.camera.position.x + XP_BAR_WIDTH // 2 + left_margin,
                xp_bar_y,
                XP_BAR_WIDTH,
                XP_BAR_HEIGHT,
                self.player.xp,
                self.player.max_xp,
                arcade.color.SAPPHIRE_BLUE,
                BARS_BACKGROUND_COLOR,
                arcade.color.BLACK,
                XP_BAR_TEXT_SIZE,
            )

    def _draw_fps(self):
        arcade.draw_text(
            str(arcade.get_fps()),
            self.player.center_x + 100,
            self.player.center_y + 100,
            arcade.color.WHITE,
            20,
            bold=True,
        )

    def draw_gotos(self):
        dist2arrow = self.player.height * 2
        for goto in self.player.gotos:
            goto_pos = Vec2(goto.x, goto.y)
            if is_point_in_rect(
                goto_pos.x,
                goto_pos.y,
                self.camera.position.x,
                self.camera.position.y,
                self.camera.viewport_width,
                self.camera.viewport_height,
            ):
                continue
            player_pos = Vec2(self.player.center_x, self.player.center_y)
            direction = (goto_pos - player_pos).normalize()
            arrow_pos = player_pos + mul_vec_const(direction, dist2arrow)
            texture = arcade.load_texture(
                abspath(join("textures", "icons", "32x32", "gem_01a.png"))
            )
            arcade.draw_texture_rectangle(
                center_x=arrow_pos.x,
                center_y=arrow_pos.y,
                width=texture.width,
                height=texture.height,
                texture=texture,
            )

    def draw_npc(self):
        self.npc.draw()
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        for npc in self.npc:
            npc_icon = arcade.load_texture(
                abspath(join("textures", "icons", "32x32", "gem_01a.png"))
            )
            arcade.draw_texture_rectangle(
                center_x=npc.center_x,
                center_y=npc.center_y + npc.height // 2 + NPC2ICON_DISTANCE,
                width=npc_icon.width,
                height=npc_icon.height,
                texture=npc_icon,
            )
            if (
                player_pos.distance(Vec2(npc.center_x, npc.center_y))
                <= NPC_TRIGGER_DISTANCE
            ):
                tip_y = npc.center_y - npc.height // 2 - NPC2ICON_DISTANCE
                press2talk_text = arcade.Text(
                    "Press F to talk",
                    npc.center_x,
                    tip_y,
                    anchor_x="center",
                    anchor_y="center",
                    color=arcade.color.BLACK,
                )
                arcade.draw_rectangle_filled(
                    center_x=npc.center_x,
                    center_y=tip_y - TIP_MARGIN // 2,
                    width=press2talk_text.content_width + TIP_MARGIN,
                    height=press2talk_text.content_height + TIP_MARGIN,
                    color=arcade.color.WHITE_SMOKE,
                )
                press2talk_text.draw()

    def on_draw_universal(self):
        self.camera.use()
        self.player_list.draw()
        self.draw_bars(draw_hp=True)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.enemies.draw()
        self.draw_npc()
        self.on_draw_universal()
        for enemy in self.enemies:
            if is_point_in_rect(
                enemy.center_x,
                enemy.center_y,
                self.camera.position.x,
                self.camera.position.y,
                self.camera.viewport_width,
                self.camera.viewport_height,
            ):
                enemy.draw_hp_bar()
                enemy.draw_effects(self)
        self.draw_gotos()
        self.draw_bars(draw_xp=True)

        if CHECK_PERF:
            self._draw_fps()

    def update_npc(self, delta_time):
        player_pos = Vec2(self.player.center_x, self.player.center_y)
        for npc in self.npc:
            npc.on_update(delta_time)

            if (
                self.f_pressed
                and player_pos.distance(Vec2(npc.center_x, npc.center_y))
                <= NPC_TRIGGER_DISTANCE
            ):
                self.release_all()
                self.window.show_view(
                    DialogView(self, INCOGNITO_START, chars={})
                )  # TODO take dialog from npc and chars

    def update_universal(self, delta_time):
        self.process_keychange(delta_time)
        self.center_camera_to_player()
        self.setup_animations()
        self.player.update()
        if self.player.hitpoints <= 0:
            self.scene.remove_sprite_list_by_name("player")
            self.window.show_view(GameOverView())
        try:
            if self.player.frames:
                self.player_list.update_animation()
        except IndexError as e:
            print(e, self.player.frames)

    def on_update(self, delta_time):
        if not self.freeze_enemies:
            self.update_enemies(delta_time)
        self.update_npc(delta_time)
        self.update_universal(delta_time)
        self.center_camera_to_player(restrict=True)
        self.physics_engine.update()

    def update_enemies(self, delta_time):
        i = len(self.enemies) - 1
        while i >= 0:  # TODO use "for"
            if self.enemies[i].dead:
                self.player.gain_xp(self.enemies[i].kill_xp_reward)
                self.enemies.pop(i)
            i -= 1

        enemies_cnt = 100 + len(self.player.acquired_upgrades_idf) * 10
        if (
            len(self.enemies) < enemies_cnt
        ):  # TODO just for testing purposes here, replace later
            for _ in range(enemies_cnt - len(self.enemies)):
                new_enemy = Enemy.from_tp(
                    randint(MIN_ENEMY_TP, MAX_ENEMY_TP),
                    shadertoys=self.enemy_shadertoys,
                )
                new_enemy.center_x = randint(0, self.map_width)
                new_enemy.center_y = randint(0, self.map_height)
                self.enemies.append(new_enemy)

        player_pos = sprite_pos(self.player)
        self.enemy_shield_cnt = 0
        for enemy in self.enemies:
            enemy.update()
            camera_x, camera_y = self.camera.position
            camera_w, camera_h = self.camera.viewport_width, self.camera.viewport_height
            enemy_pos = sprite_pos(enemy)
            enemy2player_distance = player_pos.distance(enemy_pos)

            if enemy.is_attacking:
                enemy.update_attack(delta_time)
            elif (
                not enemy.attack.no_attack
                and enemy2player_distance <= enemy.attack.attack_start_range
            ):
                enemy.start_attacking(self.player)
            elif is_point_in_rect(
                enemy.center_x,
                enemy.center_y,
                camera_x,
                camera_y,
                camera_w,
                camera_h,
            ):
                if (
                    not enemy.is_attacking
                    and enemy2player_distance > enemy.attack.attack_start_range
                ):
                    enemy_x_delta, enemy_y_delta = (player_pos - enemy_pos).normalize()
                    enemy.center_x += enemy_x_delta * delta_time * enemy.speed
                    enemy.center_y += enemy_y_delta * delta_time * enemy.speed
                if enemy.does_activate_shield:
                    self.enemy_shield_cnt += 1

    def process_keychange(self, delta_time):
        self.player.direction = self.player.direction.normalize()
        self.player.change_x, self.player.change_y = mul_vec_const(
            self.player.direction, self.player.speed * delta_time * 40
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
            for enemy in self.enemies:
                enemy_pos = sprite_pos(enemy)
                if self.player.can_attack(enemy_pos):
                    if self.player.is_attacking:
                        self.player.update_attack(delta_time)
                    else:
                        self.player.start_attacking()
                        damage_coeff = 1
                        if self.enemy_shield_cnt > 0:
                            damage_coeff = 2 / (2 + self.enemy_shield_cnt)
                        enemy.damage(self.player.attack_damage * damage_coeff)

    def on_key_press_universal(self, symbol: int, modifiers: int):
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

    def on_key_press(self, symbol: int, modifiers: int):
        self.on_key_press_universal(symbol, modifiers)
        if symbol == arcade.key.F:
            self.f_pressed = True
        elif symbol == arcade.key.P:
            print(self.player.center_x, self.player.center_y)
        elif symbol == arcade.key.T:
            self.player.set_position(self.npc[0].center_x, self.npc[0].center_y)
        elif symbol == arcade.key.G:
            boss = FirstBoss()
            self.window.show_view(FightView(self, boss))
        elif symbol == arcade.key.E:
            self.window.show_view(UpgradeTreeView(self))
        elif symbol == arcade.key.N:
            self.freeze_enemies = not self.freeze_enemies
        elif symbol == arcade.key.M:
            self.player.gain_xp(1000000)

    def on_key_release_universal(self, symbol: int, modifiers: int):
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
        elif symbol == arcade.key.F:
            self.f_pressed = False

    def on_key_release(self, symbol: int, modifiers: int):
        self.on_key_release_universal(symbol, modifiers)

    def release_all(self):
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False
        self.f_pressed = False


class FadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fade_out = None
        self.fade_in = 255

    def update_fade(self, next_view=None):
        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if self.fade_out is not None and self.fade_out > 255 and next_view is not None:
                game_view = next_view()
                self.window.show_view(game_view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self):
        if self.fade_out is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_out))

        if self.fade_in is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_in))


class Dead_window(FadingView):
    def __init__(self):
        super().__init__()

        self.w = MainWindow

        self.manager = UIManager()
        self.manager.enable()

        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

    def on_update(self, dt):
        self.update_fade(next_view=self.w)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.TEA_GREEN)
        resp = arcade.gui.UIFlatButton(width=300,
                                height=75,
                                text='Respawn')
        t_m_m = arcade.gui.UIFlatButton(width=300,
                                height=75,
                                text='To main menu')
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_y=100,
                child=resp
            )
        )
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_y=-100,
                child=t_m_m
            )
        )

        resp.on_click = self.Respawn

        t_m_m.on_click = self.t_m_main

    def Respawn(self, event):
        self.w = GameView
        self.fade_out = 0

    def t_m_main(self, event):
        self.fade_out = 0

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()
        self.manager.draw()

FADE_RATE = 100
START_BUTTON_WIDTH = 300
SETTINGS_BUTTON_WIDTH = 300
EXIT_BUTTON_WIDTH = 300

class MainWindow(FadingView):
    def __init__(self):
        super().__init__()
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()
        self.w = GameView

    def exit(self, event):
        arcade.exit()

    def setup(self):
        pass

    def on_update(self, dt):
        self.update_fade(next_view=self.w)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.TEA_GREEN)
        start_button = arcade.gui.UIFlatButton(text="Start Game",
                                               width=START_BUTTON_WIDTH,
                                               height=75
                                               )
        settings_button = arcade.gui.UIFlatButton(text="Settings",
                                                  width=SETTINGS_BUTTON_WIDTH,
                                                  height=75
                                                  )
        exit_button = arcade.gui.UIFlatButton(text="Exit",
                                              width=EXIT_BUTTON_WIDTH,
                                              height=75
                                              )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-self.window.width / 2 + START_BUTTON_WIDTH // 2 + 20,
                anchor_y="center_y",
                child=start_button)
        )
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-self.window.width / 2 + EXIT_BUTTON_WIDTH // 2 + 20,
                align_y=-100,
                child=exit_button)
        )

        start_button.on_click = self.on_button_click

        exit_button.on_click = self.exit

    def on_button_click(self, event):
        self.fade_out = 0

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        restart_button = RestartButton(text="Restart", width=200)
        self.vertical_box = arcade.gui.UIBoxLayout()
        self.vertical_box.add(restart_button.with_space_around(bottom=60))
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.vertical_box
            )
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Game Over",
            self.window.width / 2,
            self.window.height / 2 + 150,
            arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
        )
        self.manager.draw()


class RestartButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        game_view = GameView()
        self.window = arcade.get_window()
        self.window.show_view(game_view)
