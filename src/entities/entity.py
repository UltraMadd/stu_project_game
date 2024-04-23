import arcade


class Entity(arcade.Sprite):
    def __init__(self, *args, hitpoints=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_hitpoints = hitpoints
        self.hitpoints = hitpoints
        self.hit_box_algorithm = "Detailed"

    def damage(self, amount: int):
        self.hitpoints -= amount
