from dataclasses import dataclass

import arcade
import numpy as np


class GameView(arcade.View):  # TODO player logic in arcade.Character
    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.speed = 128

    def setup(self):
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", 1)
        self.player_sprite.center_x = self.window.width/2
        self.player_sprite.center_y = self.window.height/2

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def on_draw(self):
        self.clear()
        self.player_sprite.draw()

    def on_update(self, delta_time):
        self.player_sprite.center_x += self.player_sprite.change_x * delta_time * self.speed
        self.player_sprite.center_y += self.player_sprite.change_y * delta_time * self.speed

    def process_keychange(self):
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
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)


class Game:
    def __init__(self, game_window):
        self.game_window = game_window

    def run(self):
        self.game_window.show_view(GameView())
        arcade.run()

def main():
    game_window = GameWindow(640, 400, "the game")
    game = Game(game_window)
    game.run()


if __name__ == '__main__':
    main()

