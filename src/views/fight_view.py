import arcade
from arcade.experimental.shadertoy import Shadertoy
from pyglet.math import Vec2

from entities.fighter import Fighter
from utils import sprite_pos


BOSSBAR2TOP_MARGIN = 40
BOSSBAR_WIDTH = 500
BOSSBAR_HEIGHT = 50


class FightView(arcade.View):
    def __init__(self, prev_view, fighter: Fighter):
        super().__init__()
        self.prev_view = prev_view
        self.prev_view.is_fighting = True
        self.player = self.prev_view.player
        self.camera = self.prev_view.camera
        self.fighter = fighter
        self.fighter.parent_view = self
        self.fighter.setup()
        self.prev_x = self.player.center_x
        self.prev_y = self.player.center_y
        self.arena_center = Vec2(200000, 200000)
        self.fighter.center_x = self.arena_center.x
        self.fighter.center_y = self.arena_center.y
        self.player.center_x = self.arena_center.x - 500
        self.player.center_y = self.arena_center.y
        self.arena_width = 700
        self.arena_height = 700

    def on_hide_view(self):
        self.player.center_x = self.prev_x
        self.player.center_y = self.prev_y

    def draw_walls(self):
        WALL_LENGTH = 100
        WALL_COLOR = arcade.color.BRICK_RED
        for left_or_right, up_or_down in (1, 0), (-1, 0), (0, -1), (0, 1):
            arcade.draw_rectangle_filled(
                self.arena_center.x
                + left_or_right * (self.arena_width // 2 + WALL_LENGTH // 2),
                self.arena_center.y
                + up_or_down * (self.arena_height // 2 + WALL_LENGTH // 2),
                (
                    WALL_LENGTH // 2
                    if left_or_right
                    else self.arena_width + WALL_LENGTH * 3 // 2
                ),
                (
                    WALL_LENGTH // 2
                    if up_or_down
                    else self.arena_height + WALL_LENGTH * 3 // 2
                ),
                WALL_COLOR,
            )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.RED_DEVIL)
        self.fighter.on_draw()
        self.draw_walls()
        self.prev_view.on_draw_universal()
        self.prev_view.draw_bar(
            self.camera.position.x + self.camera.viewport_width // 2,
            self.camera.position.y + self.camera.viewport_height - BOSSBAR2TOP_MARGIN,
            BOSSBAR_WIDTH,
            BOSSBAR_HEIGHT,
            int(self.fighter.hitpoints),
            self.fighter.max_hitpoints,
            arcade.color.PURPLE,
            arcade.color.RICH_BLACK,
            arcade.color.BLACK,
            20,
        )
        self.fighter.draw_ui()

    def restrict_player(self):
        self.player.center_x = max(
            min(self.player.center_x, self.arena_center.x + self.arena_width // 2),
            self.arena_center.x - self.arena_width // 2,
        )
        self.player.center_y = max(
            min(self.player.center_y, self.arena_center.y + self.arena_height // 2),
            self.arena_center.y - self.arena_height // 2,
        )

    def update_fighter(self, delta_time: float):
        if self.fighter.is_dead and self.fighter.is_ready_to_hide:
            self.window.show_view(self.prev_view)
            return
        self.fighter.on_update(delta_time)
        if (
            self.prev_view.space_pressed
            and not self.fighter.is_dead
            and self.player.can_attack(sprite_pos(self.fighter))
        ):  # TODO FIXME This logic should be in player
            if self.player.is_attacking:
                self.player.update_attack(delta_time)
            else:
                self.player.start_attacking()
                self.fighter.damage(self.player.attack_damage)

        self.fighter.attack(self.player, delta_time)

    def move_player(self, delta_time: float):
        self.player.center_x += self.player.change_x
        self.player.center_y += self.player.change_y

    def on_update(self, delta_time: float):
        self.prev_view.update_universal(delta_time)
        self.restrict_player()
        self.update_fighter(delta_time)
        self.move_player(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.prev_view.on_key_press_universal(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.prev_view.on_key_release_universal(symbol, modifiers)
