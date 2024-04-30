import arcade

from entities.fighter import Fighter
from utils import sprite_pos


class FightView(arcade.View):
    def __init__(self, prev_view, fighter: Fighter):
        super().__init__()
        self.prev_view = prev_view
        self.prev_view.is_fighting = True
        self.player = self.prev_view.player
        self.fighter = fighter
        self.prev_x = self.player.center_x
        self.prev_y = self.player.center_y
        self.player.center_x = 500
        self.player.center_y = 500

    def on_hide_view(self):
        self.player.center_x = self.prev_x
        self.player.center_y = self.prev_y

    def on_draw(self):
        arcade.set_background_color(arcade.color.RED_DEVIL)
        self.prev_view.on_draw_universal()
        self.fighter.on_draw()

    def update_fighter(self, delta_time: float):
        if self.fighter.is_dead:
            ...  # TODO logic when defating a boss
        self.fighter.on_update(delta_time)
        if self.player.can_attack(sprite_pos(self.fighter)):
            if self.player.is_attacking:
                self.player.update_attack(delta_time)
            else:
                self.player.start_attacking()
                self.fighter.damage(self.player.attack_damage)

    def on_update(self, delta_time: float):
        self.prev_view.update_universal(delta_time)
        self.update_fighter(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.prev_view.on_key_press_universal(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.prev_view.on_key_release_universal(symbol, modifiers)
