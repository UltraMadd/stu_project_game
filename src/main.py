import arcade
import pyglet.math as gmath

from entities.player import Player
from entities.enemy import Enemy




def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_w, rect_h):
    return (rect_x < point_x < rect_x + rect_w) and \
           (rect_y < point_y < rect_y + rect_h)


class GameView(arcade.View):  # TODO player logic in arcade.Character
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player_sprite = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.enemies = None

    def setup(self):
        self.player_sprite = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png", 0.5)
        self.player_sprite.center_x = self.window.width / 2
        self.player_sprite.center_y = self.window.height / 2
        self.tiled_map = arcade.load_tilemap("map/map1.tmx", 1)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player_sprite)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, walls=[self.scene["water"], self.scene["groundcollision1"]])
        self.enemies = arcade.SpriteList()
        self.enemies.append(Enemy(1000, 1000))

    def center_camera_to_player(self):
        scr_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        scr_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # if scr_center_x < 0:
        #     scr_center_x = 0
        # if scr_center_y < 0:
        #     scr_center_y = 0

        player_centered = [scr_center_x, scr_center_y]

        self.camera.move_to(player_centered)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player_sprite.draw()
        self.enemies.draw()

    def on_update(self, delta_time):
        self.process_keychange()
        self.physics_engine.update()
        self.center_camera_to_player()
        self.update_enemies(delta_time)

    def update_enemies(self, delta_time):
        for enemy in self.enemies:
            camera_x, camera_y = self.camera.position
            camera_w, camera_h = self.camera.viewport_width, self.camera.viewport_height
            if is_point_in_rect(enemy.center_x, enemy.center_y, camera_x, camera_y, camera_w, camera_h):
                enemy_x_delta, enemy_y_delta = (
                    gmath.Vec2(self.player_sprite.center_x, self.player_sprite.center_y)
                    - gmath.Vec2(enemy.center_x, enemy.center_y)
                ).normalize()
                enemy.center_x += enemy_x_delta * delta_time * enemy.speed
                enemy.center_y += enemy_y_delta * delta_time * enemy.speed
        if len(self.enemies) > 10:
            return

    def process_keychange(self):
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = self.player_sprite.speed
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -self.player_sprite.speed
        else:
            self.player_sprite.change_y = 0

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -self.player_sprite.speed
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = self.player_sprite.speed
        else:
            self.player_sprite.change_x = 0

        if self.player_sprite.change_x and self.player_sprite.change_y:
            self.player_sprite.change_x /= 1.5
            self.player_sprite.change_y /= 1.5

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


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)


class Game:
    def __init__(self, game_window):
        self.game_window = game_window

    def run(self):
        self.game_window.show_view(GameView())
        arcade.run()


def main():
    game_window = GameWindow(1600, 900, "the game")
    game = Game(game_window)
    game.run()


if __name__ == '__main__':
    main()

