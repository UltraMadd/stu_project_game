from os.path import abspath, join
import arcade


def load_boss_textures(filepath, row, width=96, height=96):
    frames = []
    for col in range(3):
        frames.append(
            arcade.AnimationKeyframe(
                col,
                120,
                arcade.load_texture(
                    filepath, x=col * width, y=row * height, width=width, height=height
                ),
            )
        )
    return frames


class Fighter:
    def __init__(self) -> None:
        super().__init__()
        self.hitpoints = None
        self.max_hitpoints = None
        self.is_dead = False

    def damage(self, amount: int):
        self.hitpoints -= amount
        if self.hitpoints < 0:
            self.is_dead = True


class FirstBoss(Fighter, arcade.AnimatedTimeBasedSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = load_boss_textures(
            abspath(join("textures", "boss", "Boss 01.png")), 0
        )
        self.max_hitpoints = 10000
        self.hitpoints = self.max_hitpoints

    def on_draw(self):
        self.draw()

    def on_update(self, delta_time: float = 1 / 60):
        self.update_animation(delta_time)
