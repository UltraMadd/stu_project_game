import arcade

from views.game_view import GameView, MainWindow


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, fullscreen=True)


class Game:
    def __init__(self, game_window):
        self.game_window = game_window

    def run(self):
        self.game_window.show_view(GameView())
        arcade.run()


def main():
    game_window = arcade.Window(1920, 1080, fullscreen=True)
    menu_view = MainWindow()
    game_window.show_view(menu_view)
    arcade.run()


if __name__ == '__main__':
    main()