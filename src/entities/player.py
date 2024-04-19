import arcade


class Player(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1
        self.texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.set_hit_box(self.texture.hit_box_points)
