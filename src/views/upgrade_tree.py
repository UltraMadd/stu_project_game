from dataclasses import dataclass
from typing import List, Optional, Tuple
from os.path import abspath, join

import arcade
import arcade.gui
from pyglet.math import Vec2

from utils import mul_vec_const


UPGRADE_CIRCLE_BORDER_WIDTH = 8
UPGRADE_CIRCLE_COLOR_NOT_UPGRADED = arcade.color.PASTEL_BROWN
UPGRADE_CIRCLE_COLOR_UPGRADED = arcade.color.PASTEL_GREEN

UPGRADE_OPENED_WIDTH = 500
UPGRADE_OPENED_COLOR = arcade.color.BLUE_BELL
UPGRADE_OPENED_OUTLINE_WIDTH = 5
UPGRADE_OPENED_OUTLINE_COLOR = arcade.color.ANTI_FLASH_WHITE
UPGRADE_OPENED_ICON2TOP_DISTANCE = 50
UPGRADE_OPENED_TITLE2TOP_DISTANCE = UPGRADE_OPENED_ICON2TOP_DISTANCE + 32 + 50
UPGRADE_OPENED_UPGRADE_BUTTON2BOT_DISTANCE = 100

LEFTOF = 1
RIGHTOF = LEFTOF << 1
BOTOF = LEFTOF << 2
TOPOF = LEFTOF << 3


@dataclass
class Upgrade:
    idf: int
    _name: str
    icon_fname: str
    position: Tuple[int, int]
    cost: int
    hp_buff: int = 0
    heal_buff: int = 0
    damage_buff: float = 0
    damage_add: int = 0
    attack_speed_buff: float = 0
    iq_buff: int = 0
    depends_on: Tuple[int, ...] = ()
    icon_res: str = "32x32"

    def get_icon_path(self):
        return abspath(join("textures", "icons", self.icon_res, self.icon_fname))

    @property
    def name(self) -> str:
        return self._name.format(
            hp_buff=self.hp_buff,
            heal_buff=self.heal_buff,
            damage_buff=round((self.damage_buff - 1) * 100, 1),
            iq_buff=self.iq_buff,
            damage_add=self.damage_add,
            attack_speed_buff=round((self.attack_speed_buff - 1) * 100, 1),
        )


HEAL_MORE = "Heal {heal_buff} hp/sec more"
ADD_HP = "Add {hp_buff} more HP"
DAMAGE_MORE = "Damage {damage_buff}% more"
ADD_DAMAGE = "Add {damage_add} damage"
ATTACK_SPEED_MORE = "{attack_speed_buff}% more attack speed"

UPGRADES = [
    # Left - HP
    Upgrade(1, ADD_HP, "helmet_01a.png", (LEFTOF, 0), cost=1, hp_buff=100),
    Upgrade(
        2,
        ADD_HP,
        "helmet_01b.png",
        (LEFTOF, 1),
        cost=1,
        hp_buff=300,
        depends_on=(1,),
    ),
    Upgrade(
        3,
        ADD_HP,
        "helmet_01c.png",
        (LEFTOF, 2),
        cost=1,
        hp_buff=500,
        depends_on=(2,),
    ),
    Upgrade(
        4,
        ADD_HP,
        "helmet_01d.png",
        (LEFTOF, 3),
        cost=1,
        hp_buff=1000,
        depends_on=(3,),
    ),
    Upgrade(
        5,
        ADD_HP,
        "helmet_01e.png",
        (LEFTOF, 4),
        cost=1,
        hp_buff=2000,
        depends_on=(4,),
    ),
    # Top - Heal
    Upgrade(101, HEAL_MORE, "hat_01a.png", (TOPOF, 0), cost=1, heal_buff=1),
    Upgrade(
        102,
        HEAL_MORE,
        "hat_01b.png",
        (TOPOF, 101),
        cost=1,
        heal_buff=2,
        depends_on=(101,),
    ),
    Upgrade(
        103,
        HEAL_MORE,
        "hat_01c.png",
        (TOPOF, 102),
        cost=1,
        heal_buff=4,
        depends_on=(102,),
    ),
    Upgrade(
        104,
        HEAL_MORE,
        "hat_01d.png",
        (TOPOF, 103),
        cost=1,
        heal_buff=8,
        depends_on=(103,),
    ),
    Upgrade(
        105,
        HEAL_MORE,
        "hat_01e.png",
        (TOPOF, 104),
        cost=1,
        heal_buff=14,
        depends_on=(104,),
    ),
    # Right - damage
    Upgrade(201, DAMAGE_MORE, "sword_03a.png", (RIGHTOF, 0), cost=1, damage_buff=1.20),
    # Right
    Upgrade(
        202,
        DAMAGE_MORE,
        "sword_03b.png",
        (RIGHTOF, 201),
        cost=2,
        damage_buff=1.25,
        depends_on=(201,),
    ),
    Upgrade(
        203,
        DAMAGE_MORE,
        "sword_03c.png",
        (RIGHTOF, 202),
        cost=2,
        damage_buff=1.30,
        depends_on=(202,),
    ),
    Upgrade(
        204,
        DAMAGE_MORE,
        "sword_03d.png",
        (RIGHTOF, 203),
        cost=3,
        damage_buff=1.35,
        depends_on=(203,),
    ),
    Upgrade(
        205,
        DAMAGE_MORE,
        "sword_03e.png",
        (RIGHTOF, 204),
        cost=4,
        damage_buff=1.5,
        depends_on=(204,),
    ),
    # Top - Right
    Upgrade(
        210,
        ADD_DAMAGE,
        "sword_02a.png",
        (RIGHTOF | TOPOF, 201),
        cost=2,
        damage_add=10,
        depends_on=(201,),
    ),
    Upgrade(
        211,
        ADD_DAMAGE,
        "sword_02b.png",
        (RIGHTOF | TOPOF, 202),
        cost=2,
        damage_add=10,
        depends_on=(210, 202),
    ),
    Upgrade(
        212,
        ADD_DAMAGE,
        "sword_02c.png",
        (RIGHTOF | TOPOF, 203),
        cost=2,
        damage_add=20,
        depends_on=(211, 203),
    ),
    Upgrade(
        213,
        ADD_DAMAGE,
        "sword_02d.png",
        (RIGHTOF | TOPOF, 204),
        cost=3,
        damage_add=30,
        depends_on=(212, 204),
    ),
    Upgrade(
        214,
        ADD_DAMAGE,
        "sword_02e.png",
        (RIGHTOF | TOPOF, 205),
        cost=4,
        damage_add=40,
        depends_on=(213, 205),
    ),
    # Bottom - Right
    Upgrade(
        220,
        ATTACK_SPEED_MORE,
        "sword_01a.png",
        (RIGHTOF | BOTOF, 201),
        cost=2,
        attack_speed_buff=1.1,
        depends_on=(201,),
    ),
    Upgrade(
        221,
        ATTACK_SPEED_MORE,
        "sword_01b.png",
        (RIGHTOF | BOTOF, 202),
        cost=2,
        attack_speed_buff=1.1,
        depends_on=(220, 202),
    ),
    Upgrade(
        222,
        ATTACK_SPEED_MORE,
        "sword_01c.png",
        (RIGHTOF | BOTOF, 203),
        cost=2,
        attack_speed_buff=1.2,
        depends_on=(221, 203),
    ),
    Upgrade(
        223,
        ATTACK_SPEED_MORE,
        "sword_01d.png",
        (RIGHTOF | BOTOF, 204),
        cost=3,
        attack_speed_buff=1.25,
        depends_on=(222, 204),
    ),
    Upgrade(
        224,
        ATTACK_SPEED_MORE,
        "sword_01e.png",
        (RIGHTOF | BOTOF, 205),
        cost=4,
        attack_speed_buff=1.3,
        depends_on=(223, 205),
    ),
    # Bottom - iq
]
# Upgrades with lower id cannot reference ones with bigger
UPGRADES.sort(key=lambda upgrade: upgrade.idf)
IDF2UPGRADE = {upgrade.idf: upgrade for upgrade in UPGRADES}


class UpgradeTreeView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.game_view.release_all()
        self.camera: arcade.Camera = game_view.camera
        self.upgrade_circle_radius = game_view.player.height
        self.upgrade_circles_spacing = self.upgrade_circle_radius // 2
        self.lmb_pressed = False
        self.rmb_pressed = False
        self.buy_pressed = False
        self.back_pressed = False
        self.rmb_x = 0
        self.rmb_y = 0
        self.upgrade_positions = {}  # id : Vec2(x, y)
        self.opened_idf = None

    def on_show_view(self):
        self.setup()

    def setup(self):
        pass

    def on_draw(self):
        self.clear()

        arcade.set_background_color(arcade.color.PASTEL_BLUE)
        self.camera.use()
        arcade.draw_circle_outline(
            self.game_view.player.center_x,
            self.game_view.player.center_y,
            self.upgrade_circle_radius,
            UPGRADE_CIRCLE_COLOR_UPGRADED,
            border_width=UPGRADE_CIRCLE_BORDER_WIDTH,
        )
        for upgrade in UPGRADES:
            sideof, ref_id = upgrade.position
            if ref_id == 0:  # references root node
                ref_x = self.game_view.player.center_x
                ref_y = self.game_view.player.center_y
            else:
                assert (
                    ref_id in self.upgrade_positions
                )  # Ok to assert if "UPGRADES" is correct
                ref_x = self.upgrade_positions[ref_id].x
                ref_y = self.upgrade_positions[ref_id].y
            icon = arcade.load_texture(upgrade.get_icon_path())
            direction = Vec2(0, 0)
            if sideof & LEFTOF != 0:
                direction.x = -1
            elif sideof & RIGHTOF != 0:
                direction.x = 1
            if sideof & BOTOF != 0:
                direction.y = -1
            elif sideof & TOPOF != 0:
                direction.y = 1
            direction = direction.normalize()
            if upgrade.idf in self.upgrade_positions:
                position = self.upgrade_positions[upgrade.idf]
                upgrade_x, upgrade_y = position.x, position.y
            else:
                offset = mul_vec_const(
                    direction,
                    2 * self.upgrade_circle_radius + self.upgrade_circles_spacing,
                )
                upgrade_x = offset.x + ref_x
                upgrade_y = offset.y + ref_y
                self.upgrade_positions[upgrade.idf] = Vec2(upgrade_x, upgrade_y)

            arcade.draw_texture_rectangle(
                upgrade_x,
                upgrade_y,
                icon.width,
                icon.height,
                icon,
            )

            arcade.draw_line(
                ref_x + self.upgrade_circle_radius * direction.x,
                ref_y + self.upgrade_circle_radius * direction.y,
                upgrade_x - self.upgrade_circle_radius * direction.x,
                upgrade_y - self.upgrade_circle_radius * direction.y,
                (
                    UPGRADE_CIRCLE_COLOR_UPGRADED
                    if ref_id in self.game_view.player.acquired_upgrades_idf
                    or ref_id == 0
                    else UPGRADE_CIRCLE_COLOR_NOT_UPGRADED
                ),
                line_width=10,
            )

            for dep_id in upgrade.depends_on:
                dep_xy = self.upgrade_positions[dep_id]
                dep_x, dep_y = dep_xy.x, dep_xy.y
                dep_dir = Vec2(upgrade_x - dep_x, upgrade_y - dep_y).normalize()
                arcade.draw_line(
                    dep_x + self.upgrade_circle_radius * dep_dir.x,
                    dep_y + self.upgrade_circle_radius * dep_dir.y,
                    upgrade_x - self.upgrade_circle_radius * dep_dir.x,
                    upgrade_y - self.upgrade_circle_radius * dep_dir.y,
                    (
                        UPGRADE_CIRCLE_COLOR_UPGRADED
                        if dep_id in self.game_view.player.acquired_upgrades_idf
                        or dep_id == 0
                        else UPGRADE_CIRCLE_COLOR_NOT_UPGRADED
                    ),
                    line_width=10,
                )

            arcade.draw_circle_outline(
                upgrade_x,
                upgrade_y,
                self.upgrade_circle_radius,
                (
                    UPGRADE_CIRCLE_COLOR_UPGRADED
                    if upgrade.idf in self.game_view.player.acquired_upgrades_idf
                    else UPGRADE_CIRCLE_COLOR_NOT_UPGRADED
                ),
                border_width=UPGRADE_CIRCLE_BORDER_WIDTH,
            )

        self.game_view.player.draw()
        self.draw_opened_upgrade()

    def draw_opened_upgrade(self):
        upgrade_opened_position = Vec2(
            self.camera.position.x
            + self.camera.viewport_width
            - UPGRADE_OPENED_WIDTH // 2,
            self.camera.position.y + self.camera.viewport_height // 2,
        )
        arcade.draw_rectangle_filled(
            upgrade_opened_position.x,
            upgrade_opened_position.y,
            UPGRADE_OPENED_WIDTH,
            self.camera.viewport_height,
            UPGRADE_OPENED_COLOR,
        )
        arcade.draw_rectangle_outline(
            upgrade_opened_position.x,
            upgrade_opened_position.y,
            UPGRADE_OPENED_WIDTH,
            self.camera.viewport_height,
            UPGRADE_OPENED_OUTLINE_COLOR,
            border_width=UPGRADE_OPENED_OUTLINE_WIDTH,
        )
        if self.opened_idf is None:
            arcade.draw_text(
                "Open an upgrade - Right Mouse Button",
                upgrade_opened_position.x,
                upgrade_opened_position.y,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )
            return

        upgrade = IDF2UPGRADE[self.opened_idf]
        icon = arcade.load_texture(upgrade.get_icon_path())
        arcade.draw_texture_rectangle(
            upgrade_opened_position.x,
            upgrade_opened_position.y
            + self.camera.viewport_height // 2
            - UPGRADE_OPENED_ICON2TOP_DISTANCE,
            32,
            32,
            icon,
        )

        arcade.draw_text(
            upgrade.name,
            upgrade_opened_position.x,
            upgrade_opened_position.y
            + self.camera.viewport_height // 2
            - UPGRADE_OPENED_TITLE2TOP_DISTANCE,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        can_buy = self.can_buy(self.opened_idf)
        reason = ""
        if self.game_view.player.points < upgrade.cost:
            reason = "Not enough Points."
        elif self.opened_idf in self.game_view.player.acquired_upgrades_idf:
            reason = "Already acquired."
        else:
            reason = "Dependencies not met."

        arcade.draw_text(
            f"{upgrade.cost} Points",
            upgrade_opened_position.x,
            self.camera.position.y + UPGRADE_OPENED_UPGRADE_BUTTON2BOT_DISTANCE,
            font_size=30,
            anchor_x="center",
            anchor_y="center",
            color=arcade.color.WHITE if can_buy else arcade.color.RED,
            bold=True,
        )

        arcade.draw_text(
            "U to buy" if can_buy else f"Can't buy, {reason}",
            upgrade_opened_position.x,
            self.camera.position.y + UPGRADE_OPENED_UPGRADE_BUTTON2BOT_DISTANCE // 2,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

    def can_buy(self, idf):
        if idf in self.game_view.player.acquired_upgrades_idf:
            return False
        upgrade = IDF2UPGRADE[idf]
        if self.game_view.player.points < upgrade.cost:
            return False
        if upgrade.depends_on is not None:
            for dep_upgrade_idf in upgrade.depends_on:
                if dep_upgrade_idf not in self.game_view.player.acquired_upgrades_idf:
                    return False
        return True

    def buy(self, idf):
        if not self.can_buy(idf):
            return
        upgrade = IDF2UPGRADE[idf]
        self.game_view.player.points -= upgrade.cost
        self.game_view.player.acquired_upgrades_idf.add(idf)
        self.game_view.player.update_stats()

    def on_mouse_press(self, x, y, button, key_modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.lmb_pressed = True
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.rmb_pressed = True
            self.rmb_x = x
            self.rmb_y = y

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.lmb_pressed:
            self.camera.move(
                Vec2(self.camera.position.x - dx, self.camera.position.y - dy)
            )

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.lmb_pressed = False
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.rmb_pressed = False

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.U:
            self.buy_pressed = True
        if symbol == arcade.key.E:
            self.back_pressed = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.U:
            self.buy_pressed = False
        if symbol == arcade.key.E and self.back_pressed:
            self.window.show_view(self.game_view)

    def on_update(self, delta_time: float):
        if self.buy_pressed and self.opened_idf is not None:
            self.buy(self.opened_idf)
        if self.rmb_pressed:
            click_pos_abs = Vec2(self.rmb_x, self.rmb_y) + self.camera.position
            if (
                self.opened_idf
                and self.camera.viewport_width - self.rmb_x - UPGRADE_OPENED_WIDTH < 0
            ):
                return
            for idf, position in self.upgrade_positions.items():
                if click_pos_abs.distance(position) < self.upgrade_circle_radius:
                    if self.opened_idf != idf:
                        self.opened_idf = idf
