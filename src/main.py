import arcade
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.gui.events import UIOnChangeEvent
import arcade.gui
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
        if self.player.hitpoints <= 0:
            arcade.close_window()
            DeadWindow()
            arcade.run()

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
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
            MainWindow()
            arcade.run()
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


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(1920, 1080, title="Main window")

        arcade.set_background_color(arcade.color.WHITE)

        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        self.set_location(0, 0)

        start_button = arcade.gui.UIFlatButton(text="Start Game",
                                               width=300,
                                               height=75
                                               )
        settings_button = arcade.gui.UIFlatButton(text="Settings",
                                                  width=300,
                                                  height=75
                                                  )
        exit_button = arcade.gui.UIFlatButton(text="Exit",
                                              width=300,
                                              height=75
                                              )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-790,
                anchor_y="center_y",
                child=start_button)
        )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-790,
                align_y=-100,
                child=settings_button)
        )
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-790,
                align_y=-200,
                child=exit_button)
        )

        start_button.on_click = self.on_button_click

        exit_button.on_click = self.exit

        settings_button.on_click = self.settings

    def exit(self, event):
        arcade.exit()

    def settings(self, event):
        self.close()
        Settings()
        arcade.run()

    def on_button_click(self, event):
        arcade.close_window()
        main()

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()


class Settings(arcade.Window):
    def __init__(self):
        self.music = True
        self.volume = 100
        super().__init__(1920, 1080, title='Settings', resizable=True)

        self.manager = UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.WHITE)

        self.set_location(0, 0)

        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        screen_resolution = arcade.gui.UIFlatButton(text="Screen_resolution",
                                                    width=300,
                                                    height=75
                                                    )
        volume = arcade.gui.UIFlatButton(text="Volume",
                                         width=300,
                                         height=75
                                         )
        music = arcade.gui.UIFlatButton(text="Music",
                                        width=300,
                                        height=75
                                        )
        back = arcade.gui.UIFlatButton(text='Back',
                                       width=300,
                                       height=75
                                       )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-250,
                align_y=+200,
                child=back)
        )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=+150,
                align_y=+200,
                child=volume)
        )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=-780,
                align_y=+200,
                child=screen_resolution)
        )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                align_x=+600,
                align_y=+200,
                child=music)
        )
        back.on_click = self.back

        ui_slider = UISlider(value=100, width=300, height=50)
        label = UILabel(text=f"{ui_slider.value:}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label.text = f"{ui_slider.value // 1:}"
            label.fit_content()

        self.manager.add(UIAnchorWidget(child=ui_slider, align_x=+150, align_y=+50))
        self.manager.add(UIAnchorWidget(child=label, align_y=+100, align_x=+150))

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()
        self.manager.draw()

    def back(self, event):
        self.close()
        r = MainWindow()
        r.width = self.width
        r.height = self.height
        arcade.run()


class DeadWindow(arcade.Window):
    def __init__(self):
        super().__init__(1920, 1080, title="Main window")

        arcade.set_background_color(arcade.color.WHITE)

        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        self.set_location(0, 0)

        start_button = arcade.gui.UIFlatButton(text="Start Game",
                                               width=300,
                                               height=75
                                               )
        main_menu = arcade.gui.UIFlatButton(text='To main menu',
                                            width=300,
                                            height=75
                                            )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                child=start_button)
        )

        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                child=main_menu, align_y=-100
            )
        )

        start_button.on_click = self.on_button_click
        main_menu.on_click = self.to_main

    def to_main(self, event):
        arcade.close_window()
        MainWindow()
        arcade.run()

    def on_button_click(self, event):
        arcade.close_window()
        main()

    def on_draw(self):
        arcade.start_render()
        self.uimanager.draw()


class Game:
    def __init__(self, game_window):
        self.game_window = game_window

    def run(self):
        self.game_window.show_view(GameView())
        arcade.run()


def main():
    game_window = GameWindow(1920, 1080, "the game")
    game = Game(game_window)
    game.run()


if __name__ == '__main__':
    MainWindow()
    arcade.run()
