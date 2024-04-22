import arcade


class Entity(arcade.Sprite):
    def __init__(self, *args, hitpoints=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.hitpoints = hitpoints
    
    def damage(self, amount: int):
        self.hitpoints -= amount

