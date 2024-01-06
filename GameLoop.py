from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar

class RespawnScreen(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.rgb(1,0,0,0.7),
            position=(0, 0),
            z=-1,
            visible = False,
        )

        self.respawn_button = Button(
            text='Respawn',
            color=color.azure,
            scale=(0.1, 0.02),
            parent=self,
            on_click=self.on_respawn_button_click
        )

        self.visible = False

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False

    def on_respawn_button_click(self):
        player.respawn(screen=self)
        player.health = 100
        player_health_bar.value = 100
        self.hide()

class player(FirstPersonController):
    def __init__(self):
        super().__init__(
            model='cube',
            z=-10,
            color=color.orange,
            origin_y=-.5,
            speed=8,
            collider='box',
            health=100,
        )
    def respawn(self,screen):
        screen.hide()
        player.position=(0,0,0)

class Enemy(Entity):
    def __init__(self,position):
        super().__init__(
            model='zombie.glb',
            position = position,
            health = 100,
            collider='box',
            scale=0.08,
            on_cooldown=False
        )
    def self_destroy(self):
        destroy(self)
        enemies.remove(self)
    def enemy_hit(self):
        self.health -= 10
        if self.health <= 0:
            invoke(self.self_destroy)
    def gravity(self):
        # Apply gravity
        if not self.intersects(ground):
            self.position=(self.position.x,self.position.y-0.05,self.position.z)

    def reset_attack_cooldown(self):
        self.on_cooldown = False

    def chase (self):
        if not distance(self.position, player.position) < 20:
            return
        self.position=(self.position.x+0.0012*(player.position.x-self.position.x),self.position.y,self.position.z+0.0012*(player.position.z-self.position.z))
        self.look_at(player)
        self.rotation_x = 0  # Lock rotation around X-axis
        self.rotation_z = 0
        self.rotation_y+=180
        if distance(self.position, player.position) < 2 and self.on_cooldown==False:
            self.attack()
            self.on_cooldown=True
            invoke(self.reset_attack_cooldown,delay=0.8)

    def attack (self):
        player.health=player.health-10
        player_health_bar.value=player.health
        if player.health <= 0:
            respawn_screen.show()

class Gun(Entity):
    def __init__(self, parent_entity, gun_type='ak-47', position=(1, 1.0, 1.0)):
        super().__init__(
            model=f'{gun_type}.glb',
            origin_z=-.3,
            origin_y=-1,
            on_cooldown=False,
            scale=0.006,
            parent=parent_entity,
            position=position,
            rotation_y=90
        )
        self.gun_type = gun_type

        # Additional gun type configuration
        if gun_type == 'ak-47':
            # Configure properties specific to the AK-47
            pass
        if gun_type == 'galil':
            self.model='galil.glb'
            self.scale=0.5

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
            return

        hovered_entity = mouse.hovered_entity

        if hovered_entity and isinstance(hovered_entity, Enemy) and calculate_distance(player.position,
                                                                                       hovered_entity.position) < 20:
            hovered_entity.enemy_hit()
        else:
            pass

        gun.on_cooldown = True
        invoke(gun.reset_cooldown, delay=0.1)  # Set the cooldown duration (0.5 seconds in this example)

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
    for enemy in enemies:
        enemy.gravity()
        enemy.chase()

def input(key):
    if key == 'escape':
        application.quit()
    if held_keys['left mouse']:
        gun.shoot()

if __name__ == "__main__":
    app = Ursina()

    ground = Entity(model='plane', collider='box', scale=128, texture='grass', texture_scale=(8, 8))

    player = player()

    gun = Gun(player, 'galil')

    # enemy1 = Enemy((10, 2, 2))
    # enemy2= Enemy((3, 3, 9))
    enemies=[]
    for _ in range(10):
        random_coordinates = (random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
        enemy = Enemy(random_coordinates)
        enemies.append(enemy)

    player_health_bar = HealthBar(value=100, position=(-0.9,-0.48))

    respawn_screen = RespawnScreen()
    respawn_screen.hide()

    player_money_bar = HealthBar(position=(-0.9, -0.445),bar_color=color.gold,max_value=1000)
    player_money_bar.value = 100

    app.run()
