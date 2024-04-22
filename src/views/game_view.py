import arcade
import pyglet.math as gmath

from entities.player import Player
from entities.enemy import Enemy


def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_w, rect_h):
    return (rect_x < point_x < rect_x + rect_w) and \
           (rect_y < point_y < rect_y + rect_h)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.enemies = None

    def setup(self):
        self.player = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.player.center_x = self.window.width / 2
        self.player.center_y = self.window.height / 2
        self.tiled_map = arcade.load_tilemap("map/map1.tmx", 1)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, walls=[self.scene["water"], self.scene["groundcollision1"]])
        self.enemies = arcade.SpriteList()
        self.enemies.append(Enemy(center_x=1000, center_y=1000))

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

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player.draw()
        self.enemies.draw()
        arcade.draw_text(str(self.player.hitpoints), self.player.center_x, self.player.center_y, arcade.color.RED, 40, width=100, align="center")

    def on_update(self, delta_time):
        self.process_keychange()
        self.physics_engine.update()
        self.center_camera_to_player()
        self.update_enemies(delta_time)

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
            elif is_point_in_rect(enemy.center_x, enemy.center_y, camera_x, camera_y, camera_w, camera_h):
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
