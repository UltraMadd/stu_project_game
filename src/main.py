from dataclasses import dataclass

import arcade
import numpy as np


class GameView(arcade.View):  # TODO player logic in arcade.Character
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player_sprite = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.speed = 128
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None

    def setup(self):
        """ Настройки игры """

        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", 0.5)
        self.player_sprite.center_x = self.window.width / 2
        self.player_sprite.center_y = self.window.height / 2
        self.tiled_map = arcade.load_tilemap("map/map.tmx", 1.5)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player_sprite)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, walls=[self.scene["2"], self.scene["3"], self.scene["4"]])

    def center_camera_to_player(self):
        scr_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        scr_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        if scr_center_x < 0:
            scr_center_x = 0
        if scr_center_y < 0:
            scr_center_y = 0

        player_centered = [scr_center_x, scr_center_y]

        self.camera.move_to(player_centered)
    def on_show_view(self):
        """ Инициализация """

        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def on_draw(self):
        """ Отрисовка """

        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player_sprite.draw()

    def on_update(self, delta_time):
        """ Логика """

        self.player_sprite.center_x += self.player_sprite.change_x * delta_time * self.speed
        self.player_sprite.center_y += self.player_sprite.change_y * delta_time * self.speed
        self.center_camera_to_player()

    def process_keychange(self):
        """ Обработка нажатия клавиш """

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = 1
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -1
        else:
            self.player_sprite.change_y = 0

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -1
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = 1
        else:
            self.player_sprite.change_x = 0
        total_velocity = abs(self.player_sprite.change_x) + abs(self.player_sprite.change_y)
        if total_velocity != 0:
            self.player_sprite.change_x /= total_velocity
            self.player_sprite.change_y /= total_velocity

    def on_key_press(self, symbol: int, modifiers: int):
        """ Нажатие клавиш """

        if symbol == arcade.key.W:
            self.up_pressed = True
        elif symbol == arcade.key.S:
            self.down_pressed = True
        elif symbol == arcade.key.A:
            self.left_pressed = True
        elif symbol == arcade.key.D:
            self.right_pressed = True
        
        self.process_keychange()

    def on_key_release(self, symbol: int, modifiers: int):
        """ Отпускание клавиш """

        if symbol == arcade.key.W:
            self.up_pressed = False
        elif symbol == arcade.key.S:
            self.down_pressed = False
        elif symbol == arcade.key.A:
            self.left_pressed = False
        elif symbol == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()


class GameWindow(arcade.Window):
    """ Класс окна """

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)


class Game:
    """ Класс игры """

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

