from dataclasses import dataclass

import arcade
import numpy as np

from views.game_view import GameView



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

