from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController



class Enemy(Entity):
    def __init__(self,position):
        super().__init__(
            model='cube',
            color=color.red,
            position = position,
            health = 100,
            collider='box'
        )

    def self_destroy(self):
        destroy(self)
    def enemy_hit(self):
        self.health -= 10
        if self.health <= 0:
            invoke(self.self_destroy)



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

class Gun(Entity):
    def __init__(self, parent_entity, gun_type='ak-47', position=(1, 1.0, 1.0)):
        super().__init__(
            model=f'{gun_type}.obj',
            origin_z=-.5,
            color=color.red,
            on_cooldown=False,
            scale=0.006,
            parent=parent_entity,
            position=position,
            rotation_y=270
        )
        self.gun_type = gun_type

        # Additional gun type configuration
        if gun_type == 'ak-47':
            # Configure properties specific to the AK-47
            pass
        elif gun_type == 'shotgun':
            # Configure properties specific to the shotgun
            self.color = color.green  # Example: change color for shotgun
        elif gun_type == 'pistol':
            # Configure properties specific to the pistol
            self.scale = 0.25  # Example: adjust scale for pistol
            rotation_y=0

    def reset_cooldown(self):
        self.on_cooldown = False

    def shoot(self):
        if gun.on_cooldown:
            print("cooldown")
            return

        hovered_entity = mouse.hovered_entity

        if hovered_entity and isinstance(hovered_entity, Enemy) and calculate_distance(player.position,
                                                                                       hovered_entity.position) < 20:
            print("DEAD")
            hovered_entity.enemy_hit()
            print(hovered_entity.health)
        else:
            print("ALIVE")

        print(gun.on_cooldown)
        gun.on_cooldown = True
        invoke(gun.reset_cooldown, delay=0.5)  # Set the cooldown duration (0.5 seconds in this example)

def calculate_distance(vector1, vector2):
    # Ensure both vectors have three components (x, y, z)
    if len(vector1) != 3 or len(vector2) != 3:
        raise ValueError("Both vectors must have three components (x, y, z)")

    # Calculate the squared differences for each component
    squared_diff_x = (vector1[0] - vector2[0]) ** 2
    squared_diff_y = (vector1[1] - vector2[1]) ** 2
    squared_diff_z = (vector1[2] - vector2[2]) ** 2

    # Sum the squared differences and take the square root
    distance = math.sqrt(squared_diff_x + squared_diff_y + squared_diff_z)

    return distance


def update():
    pass


def input(key):
    if key == 'escape':
        application.quit()
    if held_keys['left mouse']:
        gun.shoot()

if __name__ == "__main__":
    app = Ursina()

    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))

    player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')

    gun = Gun(player, 'pistol')

    enemy = Enemy((2, 2, 2))
    enemy = Enemy((3, 3, 3))

    app.run()
