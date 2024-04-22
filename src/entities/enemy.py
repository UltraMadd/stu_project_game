from entities.entity import Entity

import arcade
import pyglet.math as gmath


class EnemyAttack:
    def __init__(self, attack_range):
        self.attack_range = attack_range
        self.attack_start_range = attack_range // 2
        self.prepare_time = 0.5
        self.attack_time = 0.5 + self.prepare_time
        self.end_time = 0.3 + self.attack_time

    @classmethod
    def simple(cls):
        return cls(128)


class Enemy(Entity):
    def __init__(
        self,
        scale=0.4,
        center_x=0,
        center_y=0,
        speed=128,
        attack: EnemyAttack = EnemyAttack.simple(),
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.speed = speed
        self.attack = attack
        self.attacking = False
        self.attacking_target = None
        self.damaged = False
        self.attacking_timer = 0
        self.texture = arcade.load_texture(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        )
        self.set_hit_box(self.texture.hit_box_points)
        self.center_x = center_x
        self.center_y = center_y

    def start_attacking(self, target):
        self.attacking = True
        self.damaged = False
        self.attacking_timer = 0
        self.attacking_target = target

    def update_attack(self, delta_time):
        self.attacking_timer += delta_time
        target_pos = gmath.Vec2(
            self.attacking_target.center_x, self.attacking_target.center_y
        )
        enemy_pos = gmath.Vec2(self.center_x, self.center_y)
        enemy2target_distance = target_pos.distance(enemy_pos)

        if (
            self.attacking_timer < self.attack.end_time
            and enemy2target_distance > self.attack.attack_range
        ):
            self.attacking_timer = self.attack.end_time
        if self.attacking_timer < self.attack.prepare_time:
            pass
        elif self.attacking_timer < self.attack.attack_time:
            if not self.damaged:
                self.attacking_target.damage(5)
                self.damaged = True
        elif self.attacking_timer < self.attack.end_time:
            pass
        else:
            self.attacking = False
