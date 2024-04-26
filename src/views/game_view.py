import arcade
from os.path import abspath, join
import pyglet.math as gmath

from entities.player import Player
from entities.enemy import Enemy


HP_BAR_WIDTH = 500
HP_BAR_HEIGHT = 50
HP_TEXT_SIZE = 20


def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_w, rect_h):
    return (rect_x < point_x < rect_x + rect_w) and (rect_y < point_y < rect_y + rect_h)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.scene = None
        self.player = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.physics_engine = None
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.scene = None
        self.rectangle = None
        self.enemies = arcade.SpriteList()

    def setup(self):
        self.player = Player()
        self.player.center_x = 2000
        self.player.center_y = 2000
        self.tiled_map = arcade.load_tilemap(abspath(join("map", "map1.tmx")), 1)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player)
        self.setup_animations()
        self.setup_physics()

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

    def draw_bar(self, center_x, center_y, width, height, value, max_value, indicator_color, background_color, outline_color):
        arcade.draw_rectangle_filled(
            center_x, center_y, width, height, background_color
        )
        arcade.draw_rectangle_outline(
            center_x, center_y, width, height, outline_color
        )

        indicator_width = int(HP_BAR_WIDTH * value / max_value)
        arcade.draw_rectangle_filled(
            center_x + (indicator_width - width) / 2,
            center_y,
            indicator_width,
            HP_BAR_HEIGHT,
            indicator_color,
        )

        arcade.draw_text(
            f"{value} / {max_value}",
            center_x,
            center_y - HP_TEXT_SIZE // 2,
            arcade.color.WHITE,
            HP_TEXT_SIZE,
            anchor_x="center",
        )

    def draw_bars(self):
        self.draw_bar(
            self.camera.position.x + self.camera.viewport_width // 2,
            self.camera.position.y + HP_BAR_HEIGHT,
            HP_BAR_WIDTH,
            HP_BAR_HEIGHT,
            self.player.hitpoints,
            self.player.max_hitpoints,
            arcade.color.PASTEL_GREEN,
            arcade.color.DARK_GREEN,
            arcade.color.BLACK,
        )

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player_list.draw()
        self.enemies.draw()

        # self.draw_hp()
        self.draw_bars()

    def on_update(self, delta_time):
        self.process_keychange()
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
        player_pos = gmath.Vec2(self.player.center_x, self.player.center_y)
        for enemy in self.enemies:
            camera_x, camera_y = self.camera.position
            camera_w, camera_h = self.camera.viewport_width, self.camera.viewport_height
            enemy_pos = gmath.Vec2(enemy.center_x, enemy.center_y)
            enemy2player_distance = player_pos.distance(enemy_pos)

            if enemy.attacking:
                enemy.update_attack(delta_time)
            elif enemy2player_distance <= enemy.attack.attack_start_range:
                enemy.start_attacking(self.player)
            elif is_point_in_rect(
                enemy.center_x, enemy.center_y, camera_x, camera_y, camera_w, camera_h
            ):
                if not enemy.attacking:
                    enemy_x_delta, enemy_y_delta = (player_pos - enemy_pos).normalize()
                    enemy.center_x += enemy_x_delta * delta_time * enemy.speed
                    enemy.center_y += enemy_y_delta * delta_time * enemy.speed

    def process_keychange(self):
        if self.up_pressed and not self.down_pressed:
            self.player.change_y = self.player.speed
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -self.player.speed
        else:
            self.player.change_y = 0

        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -self.player.speed
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = self.player.speed
        else:
            self.player.change_x = 0

        if self.player.change_x and self.player.change_y:
            self.player.change_x /= 1.5
            self.player.change_y /= 1.5

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.up_pressed = True
        elif symbol == arcade.key.S:
            self.down_pressed = True
        elif symbol == arcade.key.A:
            self.left_pressed = True
        elif symbol == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.up_pressed = False
        elif symbol == arcade.key.S:
            self.down_pressed = False
        elif symbol == arcade.key.A:
            self.left_pressed = False
        elif symbol == arcade.key.D:
            self.right_pressed = False
