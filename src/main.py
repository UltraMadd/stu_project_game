import arcade

from views.game_view import GameView, MainWindow


def main():
    game_window = arcade.Window(1920, 1080, resizable=True)
    menu_view = MainWindow()
    game_window.show_view(menu_view)
    arcade.run()


if __name__ == '__main__':
    main()

