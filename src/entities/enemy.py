import arcade


class Enemy(arcade.Sprite):
    def __init__(self, center_x=0, center_y=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 0.3
        self.speed = 128
        self.texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.set_hit_box(self.texture.hit_box_points)
        self.center_x = center_x
        self.center_y = center_y
