import arcade

from entities.player import Player


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.speed = 128 // 64
        self.physics_engine = None

    def setup(self):
        self.player_sprite = Player()
        self.player_sprite.center_x = self.window.width/2
        self.player_sprite.center_y = self.window.height/2

        self.setup_physics()

    def setup_physics(self):
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, arcade.SpriteList()  # TODO replace with walls
        )

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def on_draw(self):
        self.clear()
        self.player_sprite.draw()

    def on_update(self, delta_time):
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
            self.player_sprite.change_x *= self.speed / total_velocity
            self.player_sprite.change_y *= self.speed / total_velocity
        
        self.physics_engine.update()

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

