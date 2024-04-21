import arcade

from entities.entity import Entity


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 0.55
        self.speed = 2
        self.texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.set_hit_box(self.texture.hit_box_points)
