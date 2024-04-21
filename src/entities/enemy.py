import arcade


class EnemyAttack:
    def __init__(self, attack_range):
        self.attack_range = attack_range
        self.prepare_time = 0.5
        self.attacK_time = 0.5
        self.end_time = 0.3
    
    @classmethod
    def simple(cls):
        return cls(128)

class Enemy(arcade.Sprite):
    def __init__(self, scale=0.4, center_x=0, center_y=0, speed=128, attack: EnemyAttack=EnemyAttack.simple(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.speed = speed
        self.attack = attack
        self.attacking = False
        self.attacking_target = None
        self.attacking_timer = 0
        self.texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.set_hit_box(self.texture.hit_box_points)
        self.center_x = center_x
        self.center_y = center_y

    def start_attacking(self, target):
        self.attacking = True
        self.attacking_timer = 0
        self.attacking_target = target

    def update_attack(self, delta_time):
        self.attacking_timer += delta_time
        if self.attacking_timer < self.attack.prepare_time:
            pass
        elif self.attacking_timer < self.attack.attack_time:
            pass
        elif self.attacking_timer < self.attack.end_time:
            pass
        else:
            self.attacking = False


