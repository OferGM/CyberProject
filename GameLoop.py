from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))

player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')
gun = Entity(model='ak-47.obj', origin_z=-.5, color=color.red, on_cooldown=False,scale=0.006,parent=player,position=(1, 1.0, 1.0),rotation_y=270)

bullets = []

class Bullet(Entity):
    def __init__(self,position,rotation):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(0.05, 0.05, 0.05),
            parent=player,
            position = position,
            rotation = rotation,
        )
        invoke(self.self_destroy, delay=1.0)

    def self_destroy(self):
        destroy(self)

def shoot():
    print("shoot")
    bullet = Bullet(position=gun.world_position + (gun.forward * 0.5), rotation=gun.rotation)
    bullet.parent = scene  # Set the parent to scene instead of the player
    bullets.append(bullet)
def update():
    pass


def input(key):
    if key == 'escape':
        application.quit()
    if held_keys['left mouse']:
        shoot()

app.run()
