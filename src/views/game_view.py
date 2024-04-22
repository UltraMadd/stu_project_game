import arcade
from os.path import abspath, join
from entities.player import Player


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.player_list = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.speed = 4
        self.physics_engine = None
        self.tiled_map = None
        self.physics_engine = None
        self.camera = None
        self.scene = None

    def setup(self):
        self.player_sprite = Player()
        self.player_list = arcade.SpriteList()
        self.player_sprite.center_x = self.window.width / 2
        self.player_sprite.center_y = self.window.height / 2
        self.tiled_map = arcade.load_tilemap(abspath(join("map", "map1.tmx")), 1)
        self.scene = arcade.Scene.from_tilemap(self.tiled_map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.scene.add_sprite("player", self.player_sprite)

        self.setup_animations()
        self.setup_physics()
    
    def load_player_animation_frames(self, all_frames: str):
        res = []
        for i in (1, 0, 1, 2):
            texturee = arcade.load_texture(abspath(join("textures", "player", all_frames)), x=i*32, y=0, width=32, height=32)
            anim = arcade.AnimationKeyframe(i, 120, texturee)
            res.append(anim)
        return res

    def setup_animations(self):
        if self.player_sprite.change_x == 0 and self.player_sprite.change_y == 0:
            self.player_sprite.frames = [arcade.AnimationKeyframe(0, 120, self.player_sprite.texture)]*4  # FIXME Костыль*3?
        if self.player_sprite.change_x < 0:
            self.player_sprite.frames = self.load_player_animation_frames("walkleft.png")
        elif self.player_sprite.change_x > 0:
            self.player_sprite.frames = self.load_player_animation_frames("walkright.png")
        if self.player_sprite.change_y < 0:
            self.player_sprite.frames = self.load_player_animation_frames("walkdown.png")
        elif self.player_sprite.change_y > 0:
            self.player_sprite.frames = self.load_player_animation_frames("walkup.png")

    def setup_physics(self):
        self.player_list.append(self.player_sprite)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=[self.scene["water"], self.scene["groundcollision1"]])

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
        self.setup()
        arcade.set_background_color(arcade.color.TEA_GREEN)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.camera.use()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.process_keychange()
        self.center_camera_to_player()
        self.physics_engine.update()
        self.setup_animations()
        try:
            if self.player_sprite.frames:
                self.player_list.update_animation()
        except IndexError as e:
            print(e, self.player_sprite.frames)


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
            self.player_sprite.change_x *= self.speed / total_velocity
            self.player_sprite.change_y *= self.speed / total_velocity

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

