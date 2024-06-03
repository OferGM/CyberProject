import builtins
import faulthandler
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from GameInventory import Inventory
from skills import SkillDisplay
from random import choice
from MiniInv import MiniInv
from clientfuncs import clientfuncs
import threading
import time
import socket
from queue import Queue
import subprocess
import clientChat

last_skill_activation = {
    'cooldown': 0,
    'speed': 0,
    'strength': 0
}

# Define possible loot items
LOOT_ITEMS = ['gold_coin', 'silver_coin', 'health_potion', 'ammo']

running = 1
DEAD = 0
counter = 0

mobs = {}
witches = {}
players = {}
orbs = {}
chests = {}
destroyed_orbs = []
rendered_players = {}
rendered_zombies = {}
update_queue = Queue()

lb_ip = ()
login_ip = ()


def RemoveChest(chest_id):
    """
    Removes a chest from the game world and the internal tracking dictionary based on its ID.

    Args:
    chest_id (int): The unique identifier of the chest to be removed.
    """
    # Check if the chest with the given ID exists in the dictionary
    if chest_id in chests:
        # Retrieve the chest entity
        chest = chests[chest_id]
        # Safely remove the chest entity from the scene
        destroy(chest)
        # Remove the chest from the dictionary to prevent future access
        del chests[chest_id]
        print(f"Chest with ID {chest_id} has been removed.")
    else:
        print(f"No chest found with ID {chest_id}.")


def CreateNewPlayer(id):
    if id not in players:
        print(f"CREATED NEW PLAYER {id}")
        pn = MultiPlayer(id=id)
        players[id] = pn


def CreateEnemy(coords, id):
    if id in mobs:
        if mobs[id].position == coords:
            return
    enemy = Enemy(position=coords, id=id)
    mobs[id] = enemy


def CreateWitch(coords, id):
    if id in witches:
        if witches[id].position == coords:
            return
    witch_ = Witch(position=coords, id=id)
    witches[id] = witch_


def CreateOrb(coords, id):
    if id in orbs:
        if orbs[id].position == coords:
            return
    if id not in destroyed_orbs:
        orb_ = orb(position=coords, id=id)
        orbs[id] = orb_
        print("orb created!!")


def CreateItem(coords, id, type):
    if id in items:
        if items[id].position == coords:
            return
    item = Item(position=coords, id=id, ttype=type)
    items[id] = item


def CreateChest(coords, id, items):
    if id in chests:
        return
    print(coords)
    print(items)
    chest = Chest(coords, id=id)
    new_inv = Inventory(None, 4, 4)  # Create a new inventory for each chest
    for item in items:
        print(f"{item} is the item")
        new_inv.add_item(item)
    chest._ChestInv = new_inv
    chests[id] = chest  # Store the chest in a dictionary


def separate_chest_string(all_chest_string):
    chest_entries = all_chest_string.split(';')

    for entry in chest_entries:
        if entry and entry != '&':
            parts = entry.split('&')

            try:
                id = int(parts[0])
                coords = tuple(map(float, parts[1:4]))
                if id in chests.keys():
                    pass
                else:
                    items = list(map(str, parts[4:]))
                    CreateChest(coords, id, items)
            except Exception as e:
                # Handle the case where conversion to int fails
                print(f"Could not convert {entry} to mob data: ", e)


def separate_mob_string(all_mobs_string):
    # Split the string by semicolons to get individual mob data strings
    mob_entries = all_mobs_string.split(';')

    for entry in mob_entries:
        if entry and entry != '&':  # Check if entry is not empty
            parts = entry.split('&')
            # Extract the ID and coordinates, converting them to the appropriate types
            try:
                id = int(parts[0])
                coords = tuple(map(float, parts[1:5]))
                if id in mobs.keys():
                    mobs[id].set_position(coords)
                    mobs[id].rotation_y = float(parts[4])
                    mobs[id].health = int(parts[5])
                else:
                    CreateEnemy(coords, id)
                rendered_zombies[id] = 1
            except Exception as e:
                # Handle the case where conversion to int fails
                print(f"Could not convert {entry} to mob data: ", e)


def separate_Witch_string(all_mobs_string):
    # Split the string by semicolons to get individual mob data strings
    mob_entries = all_mobs_string.split(';')

    for entry in mob_entries:
        if entry and entry != '&':  # Check if entry is not empty
            parts = entry.split('&')
            # Extract the ID and coordinates, converting them to the appropriate types
            try:
                id = int(parts[0])
                coords = tuple(map(float, parts[1:5]))
                if id in witches.keys():
                    witches[id].set_position(coords)
                    witches[id].rotation_y = float(parts[4])
                    witches[id].health = int(parts[5])
                else:
                    CreateWitch(coords, id)
            except Exception as e:
                # Handle the case where conversion to int fails
                print(f"Could not convert {entry} to witch data: ", e)


def separate_orb_string(all_orbs_string):
    # Split the string by semicolons to get individual orb data strings
    orb_entries = all_orbs_string.split(';')

    for entry in orb_entries:
        if entry and entry != '&':  # Check if entry is not empty
            parts = entry.split('&')
            # Extract the ID and coordinates, converting them to the appropriate types
            try:
                orb_id = int(parts[0])
                coords = tuple(map(float, parts[1:4]))  # x, y, z coordinates
                if orb_id in orbs.keys():
                    orbs[orb_id].set_position(coords)
                    # If there are additional attributes like speed or target player
                    if len(parts) > 4:
                        orbs[orb_id].target_player_id = int(parts[4])
                        orbs[orb_id].velocity = float(parts[5]) if len(parts) > 5 else orbs[orb_id].velocity
                else:
                    # If the orb does not exist, create a new one (adapt parameters as needed)
                    CreateOrb(coords, orb_id)
            except Exception as e:
                # Handle the case where conversion to int or float fails
                print(f"Could not convert {entry} to orb data: ", e)


def separate_item_string(all_items_string):
    # Split the string by semicolons to get individual mob data strings
    item_entries = all_items_string.split(';')

    for entry in item_entries:
        if entry:  # Check if entry is not empty
            parts = entry.split('&')
            if parts != ['', '']:
                # Extract the ID and coordinates, converting them to the appropriate types
                try:
                    id = int(parts[0])
                    type = parts[1]
                    coords = tuple(map(float, parts[2:5]))
                    if id in items.keys():
                        items[id].set_position(coords)
                    else:
                        pass
                        CreateItem(coords, id, type)
                except Exception as e:
                    # Handle the case where conversion to int fails
                    print(f"Could not convert {parts} to item data: ", e)


class orb(Entity):
    def __init__(self, position, id):
        super().__init__(
            model='sphere',
            position=position,
            scale=0.4,
            on_cooldown=False,
            id=id
        )
        self.color = color.pink

    def self_destroy(self):
        destroy(self)


def seperateInv(inv3):
    inv1 = Inventory(player, 4, 4)
    inv2 = Inventory(None, 4, 4)
    for item in inv3.children:
        if item.sloty <= 4:
            inv1.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty)
        else:
            inv2.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty - 4)
    return inv1, inv2


def combineInv(inv1, inv2):
    inv3 = Inventory(None, 4, 8)
    for item in inv1.children:
        inv3.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty + 4)

    for item in inv2.children:
        inv3.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty)

    return inv3


class Chest(Entity):
    def __init__(self, position, id, chest_inventory=None):
        super().__init__(
            model='Suitcase_for_tools.glb',
            position=position,
            collider='box',
            scale=4,
            _ChestInv=0,
            id=id,
        )
        self.isopen = False
        # Ensure a new Inventory instance is created if not provided
        self._ChestInv = Inventory(None) if chest_inventory is None else chest_inventory

    @property
    def ChestInv(self):
        # Lazy initialization of ChestInv, if it's not already set
        if self._ChestInv is None:
            self._ChestInv = Inventory(None, 4, 1)
        return self._ChestInv

    def CloseChest(self):
        global inv, inv3, miniInv
        inv, self._ChestInv = seperateInv(inv3)
        inv3.closeInv(player)
        self.isopen = False
        del inv3  # Delete inv3 after it's no longer needed
        miniInv.inventory = inv
        RemoveChest(self.id)

    def OpenChest(self):
        global inv3
        # Ensure that conditions are right to open the chest (e.g., resources are loaded)
        if not self.isopen:
            self.isopen = True
            inv3 = combineInv(self._ChestInv, inv)  # Combine inventories
            inv3.openInv(player)
            msg = encrypt(f"gREMOVECHEST&{client.id}&{self.id}", secret)
            client.send_data(msg)

        else:
            # Handle situation where chest can't be opened (show message, etc.)
            print("Chest can't be opened right now.")

    def Check(self):
        hovered_entity = mouse.hovered_entity
        if hovered_entity and isinstance(hovered_entity, Chest) and calculate_distance(player.position,
                                                                                       hovered_entity.position) < 5:
            gun.on_cooldown = True
            invoke(gun.reset_cooldown, delay=0.1)  # Set the cooldown duration
            return True
        else:
            pass
        gun.on_cooldown = True
        invoke(gun.reset_cooldown, delay=0.1)  # Set the cooldown duration
        return False

    def can_open_chest(self):
        # Placeholder for any checks you want to perform before opening the chest
        # For example: Check if game resources are loaded, player is not in another interaction, etc.
        return True  # Return True if chest can be opened, False otherwise


class KillCountUI(Entity):
    def __init__(self, icon_path, position=(0, 0), scale=1):
        super().__init__()
        self.kill_count = 0

        # Create and set up the Kill Count label
        self.label = Text(text=f'Kill Count: {self.kill_count}', origin=(0, 0), position=position, scale=scale,
                          color=color.white)

        # Create and set up the Kill Count icon
        self.icon = Sprite(icon_path, parent=camera.ui, scale=scale * 0.035,
                           position=(position[0] - 0.15, position[1] + 0.005))

    def increment_kill_count(self):
        self.kill_count += 1
        self.label.text = f'Kill Count: {self.kill_count}'


class RespawnScreen(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.rgb(1, 0, 0, 0.7),
            position=(0, 0),
            z=-1,
            visible=False,
        )

        self.respawn_button = Button(
            text='Respawn',
            color=color.azure,
            scale=(0.1, 0.02),
            parent=self,
            on_click=self.on_respawn_button_click
        )

        self.visible = False

    def GetVisible(self):
        return self.visible

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False

    def on_respawn_button_click(self):
        global DEAD
        player.respawn(screen=self)
        player.health = 100
        player_health_bar.value = 100
        DEAD = 0
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
            npc=False,
            time_since_last_change=0,
            change_direction_interval=5,
            npc_activate=True
        )

    def respawn(self, screen):
        screen.hide()
        player.position = (0, 0, 0)

    def SpeedSkillEnable(self):
        self.speed = 15
        invoke(player.SpeedSkillDisable)

    def SpeedSkillDisable(self):
        self.speed = 8

    def npc_player(self):
        global random_direction
        self.time_since_last_change += time.dt
        if self.time_since_last_change >= self.change_direction_interval or self.npc_activate:
            random_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.time_since_last_change = 0
            self.npc_activate = False
        self.position += random_direction * 0.045


class Item(Entity):
    def __init__(self, position, id, ttype):  # DONT CHANGE ttype NAME
        super().__init__(
            model=ttype,  # Replace 'cube' with a suitable model for your loot
            position=position,  # Consider specifying an actual texture if available
            collider='box',
            ttype=ttype,
            id=id,
            scale=1
        )
        if ttype == "potion of leaping":
            self.scale = 0.001
        if ttype == "bandage" or ttype == "medkit":
            self.scale = 4

    def self_destroy(self):
        # Schedule the destruction and removal to be handled in the main update loop
        update_queue.put(lambda: self.safe_destroy())

    def safe_destroy(self):
        # This method will be called in the main thread from the update loop
        if self.id in items:
            items.pop(self.id, None)
            destroy(self)

    def pickup(self):
        if distance(self.position, player.position) < 2 and (not inv.isFull()):
            msg = encrypt(f"zPICKED&{client.id}&{self.id}", secret)
            print("sending PICKED msg: ", f"zPICKED&{client.id}&{self.id}")
            client.send_data(msg)
            inv.add_item(self.ttype)
            # Queue the removal to ensure it happens in the main thread
            update_queue.put(lambda: self.safe_destroy())


class Witch(Entity):
    def __init__(self, position, id):
        super().__init__(
            model='witch.glb',
            position=position,
            health=100,
            collider='box',
            scale=0.10,
            on_cooldown=False,
            id=id
        )

    def self_destroy(self):
        kill_count_ui.increment_kill_count()
        destroy(self)

    def enemy_hit(self, gun):
        self.health -= gun.damage
        msg = encrypt(f"zDAMAGEWITCH&{client.id}&{self.id}&{gun.damage}", secret)
        client.send_data(msg)
        if self.health <= 0:
            if self.id in mobs:
                witches.pop(self.id)
            self.self_destroy()
            player_money_bar.value += 100


class Enemy(Entity):
    def __init__(self, position, id):
        super().__init__(
            model='zombie.glb',
            position=position,
            health=100,
            collider='box',
            scale=0.12,
            on_cooldown=False,
            id=id
        )

    def self_destroy(self):
        kill_count_ui.increment_kill_count()
        destroy(self)

    def distance_to_ground(self):
        # Cast a ray straight down from the entity
        try:
            ray = raycast(self.world_position, Vec3(0, -1, 0), ignore=(self,))

            if ray.hit:
                # If the ray hits the ground, calculate the distance
                return self.world_position.y - ray.world_point.y
            else:
                # If the ray doesn't hit anything, return some large number or a default value
                return float('inf')  # or some large number
        except:
            pass

    def drop_loot(self):
        """ Drops a random loot item at the enemy's position on the ground. """
        # loot_item = choice(LOOT_ITEMS)
        ground_height = 0  # Assuming your ground is at y=0
        # Create a new entity for the loot item at the enemy's position on the ground
        # loot = Item((self.position.x, self.position.y - self.distance_to_ground(), self.position.z))
        # items.append(loot)

    def enemy_hit(self, gun):
        self.health -= gun.damage
        msg = encrypt(f"zDAMAGEMOB&{client.id}&{self.id}&{gun.damage}", secret)
        print("SENT DAMAGEMOB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        client.send_data(msg)
        if self.health <= 0:
            self.drop_loot()  # Drop loot when the enemy is killed
            if self.id in mobs:
                mobs.pop(self.id)
            self.self_destroy()
            player_money_bar.value += 100

    def gravity(self):
        # Apply gravity
        if not self.intersects(ground):
            self.position = (self.position.x, self.position.y - 0.05, self.position.z)

    def reset_attack_cooldown(self):
        self.on_cooldown = False

    def chase(self):
        if not distance(self.position, player.position) < 20:
            return
        self.position = (self.position.x + 0.0012 * (player.position.x - self.position.x), self.position.y,
                         self.position.z + 0.0012 * (player.position.z - self.position.z))
        self.look_at(player)
        self.rotation_x = 0  # Lock rotation around X-axis
        self.rotation_z = 0
        self.rotation_y += 180
        if distance(self.position, player.position) < 2 and self.on_cooldown == False:
            self.attack()
            self.on_cooldown = True
            invoke(self.reset_attack_cooldown, delay=0.8)

    def attack(self):
        player.health -= 10
        if player.health <= 0:
            death()


class MultiPlayer(Entity):
    def __init__(self, id, position=(0, 0, 0), health=100, model='minecraft_steve.glb', scale=0.08, **kwargs):
        super().__init__(
            position=position,
            model=model,
            scale=scale,
            collider='box',
            heldItem='',
            item_entity=0,
            last_held=0,
            **kwargs
        )
        self.id = id
        self.health = health

    def damage(self, amount):
        self.health -= amount
        msg = encrypt(f"gDAMAGE&{self.id}&{self.health}", secret)
        client.send_data(msg)

    def UpdateItem(self, Item):
        print("UPDATED ITEM", Item)
        if Item == 'ak-47' and self.last_held != 'ak-47':
            destroy(self.item_entity)
            print("UPDATED ITEM AK")
            self.last_held = 'ak-47'
            self.item_entity = Entity(parent=self, model='Ak-47.obj', texture=f'{Item}_tex.png')
            self.item_entity.position = Vec3(1, 0, 0)  # Adjust position relative to the player
            self.item_entity.scale = 0.06
            self.item_entity.rotation_y += 180
            self.item_entity.x += 4
            self.item_entity.z += 4
        if Item == 'awp' and self.last_held != 'awp':
            print("UPDATED ITEM AWP")
            destroy(self.item_entity)
            self.last_held = 'awp'
            self.item_entity = Entity(parent=self, model='awp.obj', texture=f'{Item}_tex.png')
            self.item_entity.position = Vec3(1, 0, 0)  # Adjust position relative to the player
            self.item_entity.scale = 0.5  # Adjust scale to fit the scene
            self.item_entity.rotation_y += 180
            self.item_entity.x += 4
            self.item_entity.z += 4
        if Item == 'mp5' and self.last_held != 'mp5':
            print("UPDATED ITEM MP5")
            destroy(self.item_entity)
            self.last_held = 'mp5'
            self.item_entity = Entity(parent=self, model='mp5.obj', texture=f'{Item}_tex.png')
            self.item_entity.position = Vec3(1, 0, 0)  # Adjust position relative to the player
            self.item_entity.scale = 0.6  # Adjust scale to fit the scene
            self.item_entity.rotation_y += 180
            self.item_entity.x += 4
            self.item_entity.z += 4
        if Item == 'm4' and self.last_held != 'm4':
            print("UPDATED ITEM M4")
            destroy(self.item_entity)
            self.last_held = 'm4'
            self.item_entity = Entity(parent=self, model='m4.obj', texture=f'{Item}_tex.png')
            self.item_entity.position = Vec3(1, 0, 0)  # Adjust position relative to the player
            self.item_entity.scale = 2.5  # Adjust scale to fit the scene
            self.item_entity.rotation_y += 180
            self.item_entity.x += 4
            self.item_entity.z += 4

        if Item == "None" and self.item_entity and self.last_held != 'None':
            self.last_held = 'None'
            destroy(self.item_entity)


class Gun(Entity):
    def __init__(self, parent_entity, gun_type='ak-47', position=(0.5, 1.5, 1), damage=25):
        super().__init__(
            model='',
            origin_z=0,
            origin_y=0,
            on_cooldown=False,
            scale=0.006,
            gun_type=gun_type,
            parent=parent_entity,
            position=position,
            rotation_y=180,
            damage=damage,
            texture='',
            aiming=False,
            on_cooldown_scope=False,
            last_toggle_time=0,
            canShoot=False,
            cooldown=0,

        )
        self.on_cooldown = False
        self.gun_type = gun_type

        # Additional gun type configuration
        if gun_type == 'ak-47':
            self.canShoot = True
            self.model = 'Ak-47.obj'
            self.texture = 'Ak-47_tex'
            self.position = (0.5, 1.5, 1)
            self.rotation_y = 0
            self.damage = 35
            self.scale = 0.01
            self.cooldown = 0.5
            player.cursor.visible = True

        if gun_type == 'm4':
            self.canShoot = True
            self.model = 'M4a1.obj'
            self.texture = 'm4_tex'
            self.position = (0.5, 1.5, 1)
            self.scale = 0.25
            self.cooldown = 0.25
            player.cursor.visible = True

        if gun_type == 'awp':
            self.canShoot = True
            self.model = 'awp.obj'
            self.texture = 'awp_tex.png'
            self.position = (0.5, 1.4, 0.2)
            self.rotation_y = 0
            self.damage = 100
            self.scale = 0.05
            self.cooldown = 2
            player.cursor.visible = False

        if type == 'mp5':
            self.gun_type = "mp5"
            self.canShoot = True
            self.model = 'mp5.obj'
            self.texture = 'mp5_tex.png'
            self.position = (0.5, 1.5, 1)
            self.rotation_y = 0
            self.damage = 25
            self.scale = 0.06
            player.cursor.visible = False
            self.cooldown = 0
            player.cursor.visible = True

    def switchType(self, type):
        if type == 'ak-47':
            self.gun_type = "ak-47"
            self.canShoot = True
            self.model = 'Ak-47.obj'
            self.texture = 'Ak-47_tex'
            self.position = (0.5, 1.5, 1)
            self.rotation_y = 0
            self.damage = 35
            self.scale = 0.01
            self.cooldown = 0.5
            player.cursor.visible = True

        if type == 'm4':
            self.gun_type = "m4"
            self.canShoot = True
            self.model = 'M4a1.obj'
            self.texture = 'm4_tex'
            self.position = (0.5, 1.5, 1)
            self.scale = 0.25
            player.cursor.visible = True
            self.cooldown = 0.25

        if type == 'awp':
            self.gun_type = "awp"
            self.canShoot = True
            self.model = 'awp.obj'
            self.texture = 'awp_tex.png'
            self.position = (0.5, 1.4, 0.2)
            self.rotation_y = 0
            self.damage = 100
            self.scale = 0.05
            player.cursor.visible = False
            # m=load_model('awp.obj',reload=True)
            self.cooldown = 0.2

        if type == 'mp5':
            self.gun_type = "mp5"
            self.canShoot = True
            self.model = 'mp5.obj'
            self.texture = 'mp5_tex.png'
            self.position = (0.5, 1.5, 1)
            self.rotation_y = 0
            self.damage = 25
            self.scale = 0.06
            player.cursor.visible = False
            self.cooldown = 0


        if type == "None":
            self.gun_type = "None"
            self.canShoot = False
            self.enabled = False

    def reset_cooldown(self):
        self.on_cooldown = False

    def reset_cooldown_scope(self):
        self.on_cooldown_scope = False

    def shoot(self):
        print(self.on_cooldown, self.canShoot)
        if self.on_cooldown == True or self.canShoot == False:
            return
        sound.play()
        self.on_cooldown = True
        print("Shooting")
        hovered_entity = mouse.hovered_entity
        print(type(hovered_entity))

        if hovered_entity and isinstance(hovered_entity, Enemy) and (calculate_distance(player.position,
                                                                                        hovered_entity.position) < 20 or gun.gun_type == 'awp'):
            hovered_entity.enemy_hit(self)

        if hovered_entity and isinstance(hovered_entity, Witch) and (calculate_distance(player.position,
                                                                                        hovered_entity.position) < 20 or gun.gun_type == 'awp'):
            hovered_entity.enemy_hit(self)

        if hovered_entity and isinstance(hovered_entity, MultiPlayer) and (calculate_distance(player.position,
                                                                                              hovered_entity.position) < 20 or gun.gun_type == 'awp'):
            print("HIT PLAYER")
            hovered_entity.damage(self.damage)
        print(self.cooldown)
        invoke(self.reset_cooldown, delay=self.cooldown)  # Set the cooldown duration (0.5 seconds in this example)

    def aim(self):
        current_time = time.time()
        if current_time - self.last_toggle_time >= self.cooldown:
            if self.gun_type == "awp":
                if not self.aiming:
                    camera.fov = 30
                    background.visible = True
                    self.aiming = True
                else:
                    camera.fov = 90
                    background.visible = False
                    self.aiming = False
                self.last_toggle_time = current_time


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


def Hold_gun():
    held_item = miniInv.HeldItem()
    msg = encrypt(f"gHELD&{client.id}&{held_item}", secret)
    client.send_data(msg)
    if held_item == 'awp.png' and gun.gun_type != "awp":
        melee.destroy_arms()
        awp.enabled = True
        ak.enabled = False
        mp5.enabled = False
        m4.enabled = False
        selectedGun = awp
        gun.gun_type = 'awp'
        gun.canShoot = True
        gun.damage = 100
        gun.cooldown = 2
        return
    if held_item == 'm4.png':
        melee.destroy_arms()
        gun.switchType("m4")
        selectedGun = m4
        awp.enabled = False
        ak.enabled = False
        mp5.enabled = False
        m4.enabled = True
        gun.gun_type = 'm4'
        gun.canShoot = True
        gun.damage = 30
        gun.cooldown = 0.25
        return
    if held_item == 'ak-47.png' and gun.gun_type != "ak-47":
        melee.destroy_arms()
        selectedGun = ak
        awp.enabled = False
        ak.enabled = True
        m4.enabled = False
        mp5.enabled = False
        gun.gun_type = 'ak-47'
        gun.canShoot = True
        gun.damage = 20
        gun.cooldown = 0.5
        return
    if held_item == 'mp5.png' and gun.gun_type != 'mp5':
        melee.destroy_arms()
        selectedGun = mp5
        awp.enabled = False
        ak.enabled = False
        m4.enabled = False
        mp5.enabled = True
        gun.gun_type = 'mp5'
        gun.canShoot = True
        gun.damage = 25
        gun.cooldown = 0
        return
    if held_item != "awp.png" and held_item != "m4.png" and held_item != "ak-47.png" and held_item != "mp5.png":
        awp.enabled = False
        ak.enabled = False
        m4.enabled = False
        mp5.enabled = False
        gun.switchType("None")
        gun.canShoot = False


def update():
    while not update_queue.empty():
        task = update_queue.get()
        task()  # Execute the task

    player_health_bar.value = player.health

    if player.npc:
        player.npc_player()

    for item_id in list(items.keys()):
        item = items[item_id]
        item.pickup()

    for zombie_id in list(mobs.keys()):
        mob = mobs[zombie_id]
        if calculate_distance(player.position, mob.position) < 2:
            player.health -= 10

    Hold_gun()


def openInv():
    inv.enabled = True
    inv.button_enabled = True
    player.enabled = False
    mouse.visible = False
    Cursor.enabled = False


def closeInv():
    inv.enabled = False
    inv.button_enabled = False
    player.enabled = True
    mouse.visible = False
    Cursor.enabled = True


def setup_inventory():
    # Define the image paths for your inventory items
    image_paths = ['bandage.png', 'bandage.png', 'bandage.png', 'bandage.png']
    # Create an instance of MiniInv and set it to be a child of camera.ui for UI purposes
    inventory = MiniInv.MiniInv(inv, image_paths=image_paths, parent=camera.ui)


def stop_rendering_continuosly(player, stop_event):
    while not stop_event.is_set():
        for ID in rendered_players.keys():
            if rendered_players[ID] == 1:
                players[ID].enabled = True
                rendered_players[ID] = 0
            else:
                players[ID].enabled = False

        for ID in rendered_zombies.keys():
            if rendered_zombies[ID] == 1:
                mobs[ID].enabled = True
                rendered_zombies[ID] = 0
            else:
                mobs[ID].enabled = False
        time.sleep(0.3)


def send_game_data_continuously(player, stop_event, secret):
    while not stop_event.is_set():
        try:
            msg = encrypt(f"gSTATE&{client.id}&{player.x}&{player.y}&{player.z}&{player.rotation_y}&{player.health}",
                          secret)
            client.send_data(msg)
            time.sleep(0.01)
        except AssertionError as e:
            print(e)


def updatePlayer(id, x, y, z, rotation, health, item):
    if int(id) in players:
        p = players[int(id)]
        p.x = float(x)
        p.y = float(y) + 1.2
        p.z = float(z)
        p.rotation_y = float(rotation) + 180
        p.health = int(health)
        p.UpdateItem(item)


def decrypt(data, shared_key):
    # Convert key to bytes (using 4 bytes and little endian byteorder)
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the encrypted message and the key
    decrypted_bytes = bytes([encrypted_byte ^ key_byte for encrypted_byte, key_byte in zip(data, key_bytes)])
    # Convert the decrypted bytes back to a string
    decrypted_message = decrypted_bytes.decode('ascii', 'ignore')

    return decrypted_message


def encrypt(data, shared_key):
    # Convert message and key to byte arrays
    message_bytes = data.encode('ascii', 'ignore')
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the message and the key
    encrypted_bytes = bytes([message_byte ^ key_byte for message_byte, key_byte in zip(message_bytes, key_bytes)])
    poo = f"{client_id}&".encode('ascii', 'ignore')
    encrypted_bytes = poo + encrypted_bytes
    return encrypted_bytes


def recv_game_data_continuosly(player, stop_event, shared_key):
        global DEAD
    #try:
        while not stop_event.is_set():
            a = client.receive_data()
            print("Received: ", a)
            a = decrypt(a, shared_key)
            aList = a.split('&')
            if aList[0] == 'STATE':
                print("Received STATE msg: ", a)
                if int(aList[1]) != int(client.get_id()):
                    if int(aList[1]) in players and len(aList) >= 7:
                        rendered_players[int(aList[1])] = 1
                        id = aList[1]
                        x = aList[2]
                        y = aList[3]
                        z = aList[4]
                        rotation = aList[5]
                        health = aList[6]
                        item = aList[7].replace('.png', '')
                        update_task = lambda: updatePlayer(id, x, y, z, rotation, health, item)
                        update_queue.put(update_task)
                        pass
                    else:
                        players[int(aList[1])] = MultiPlayer(id=int(aList[1]))
            if aList[0] == 'aM':
                print("got aM: ", a)
                separate_mob_string(a.replace('aM', ''))
            if aList[0] == 'aW':
                separate_Witch_string(a.replace('aW', ''))
            if aList[0] == 'aI':
                if a.replace('aI&', '') != '':
                    separate_item_string(a.replace('aI', ''))
            if aList[0] == 'aC':
                if a.replace('aC&', '') != '':
                    separate_chest_string(a.replace('aC', ''))
            if aList[0] == 'aREMOVECHEST':
                if int(aList[1]) != int(client.id):
                    print("Chest Removed")
                    RemoveChest(int(aList[2]))
            if aList[0] == 'NEW':
                print("NEW PLAYER")
                CreateNewPlayer(int(aList[1]))
            if aList[0] == 'aR':
                print(f"Zombie removed: {aList[1]}")
                if int(aList[1]) in mobs:
                    destroy(mobs[int(aList[1])])
                    mobs.pop(int(aList[1]))
            if aList[0] == 'aH':
                if int(aList[1]) in players:
                    p = players[int(aList[1])]
                    p.health = int(aList[2])
                if int(aList[1]) == client.get_id():
                    player.health = int(aList[2])
                    if player.health <= 0 and DEAD == 0:
                        DEAD = 1
                        death()
            if aList[0] == 'aPICKED':
                items[int(aList[1])].enabled = False
            if aList[0] == 'aO':
                separate_orb_string(a.replace('aO', ''))
            if aList[0] == 'aRemoveOrb':
                orb_id = int(aList[1])  # Parse the orb ID safely
                if orb_id in orbs:  # Check if the orb actually exists
                    orbToDestroy = orbs.pop(orb_id)  # Remove the orb from the dictionary and get the reference
                    destroy(orbToDestroy)  # Safely destroy the orb entity
                    destroyed_orbs.append(orb_id)
                    print("Removed Orb")
                    print(len(orbs))
                else:
                    players[int(aList[1])] = MultiPlayer(id=int(aList[1]))
        if aList[0] == 'aM':
            separate_mob_string(a.replace('aM', ''))
        if aList[0] == 'aW':
            separate_Witch_string(a.replace('aW', ''))
        if aList[0] == 'aI':
            if a.replace('aI&', '') != '':
                separate_item_string(a.replace('aI', ''))
        if aList[0] == 'aC':
            if a.replace('aC&', '') != '':
                separate_chest_string(a.replace('aC', ''))
        if aList[0] == 'aREMOVECHEST':
            if int(aList[1]) != int(client.id):
                print("Chest Removed")
                RemoveChest(int(aList[2]))
        if aList[0] == 'NEW':
            print("NEW PLAYER")
            CreateNewPlayer(int(aList[1]))
        if aList[0] == 'aR':
            print(f"Zombie removed: {aList[1]}")
            if int(aList[1]) in mobs:
                destroy(mobs[int(aList[1])])
                mobs.pop(int(aList[1]))
        if aList[0] == 'aH':
            if int(aList[1]) in players:
                p = players[int(aList[1])]
                p.health = int(aList[2])
            if int(aList[1]) == client.get_id():
                player.health = int(aList[2])
                if player.health <= 0 and DEAD == 0:
                    DEAD = 1
                    death()
        if aList[0] == 'aPICKED':
            items[int(aList[1])].enabled = False
        if aList[0] == 'aO':
            separate_orb_string(a.replace('aO', ''))
        if aList[0] == 'aRemoveOrb':
            orb_id = int(aList[1])  # Parse the orb ID safely
            if orb_id in orbs:  # Check if the orb actually exists
                orbToDestroy = orbs.pop(orb_id)  # Remove the orb from the dictionary and get the reference
                destroy(orbToDestroy)  # Safely destroy the orb entity
                destroyed_orbs.append(orb_id)
                print("Removed Orb")
                print(len(orbs))
            else:
                print(f"Orb with ID {orb_id} not found")


# except Exception as e:
#    print("error: ", e)


stop_event = threading.Event()


def death():
    items = inv.get_inventory_items()
    print(items)
    kaki = f"gPLAYERDEATH&{client.id}&{player.x}&{player.y}&{player.z}&{'&'.join(items)}"
    kaki = encrypt(kaki, secret)
    client.send_data(kaki)
    player.position = (random.randint(-150,150),player.y,random.randint(-150,150))
    for ID in rendered_players.keys():
            players[ID].enabled = False
    gun = 0
    inv.CleanInv()
    player.health = 100


activeChest = 0


def safe_exit():
    stop_event.set()
    recvThread.join()
    sendThread.join()
    renderThread.join()
    time.sleep(1)
    kaki = f"zSafeDisconnect&{client_id}"
    kaki = encrypt(kaki, secret)
    client.send_data(kaki)
    application.quit()
    exit()


def input(key):
    global cursor, inv, activeChest
    if key == 'escape':
        stop_event.set()
        recvThread.join()
        sendThread.join()
        renderThread.join()
        time.sleep(1)
        kaki = f"zDisconnect&{client_id}"
        kaki = encrypt(kaki, secret)
        client.send_data(kaki)
        application.quit()
        exit()
    if held_keys['left mouse']:
        if melee.check():
            melee.punch()
        else:
            selectedGun.shoot()
    if held_keys['right mouse']:
        hoveredEntity = mouse.hovered_entity
        if isinstance(hoveredEntity, Chest):
            if hoveredEntity.Check():
                hoveredEntity.OpenChest()
                activeChest = hoveredEntity
        elif selectedGun.gun_type == 'awp' and inv.enabled == False:
            gun.aim()
    if key == 'j':
        ActivateStrengthSkill()
    if key == 'k':
        ActivateCoolDownSkill()
    if key == 'l':
        ActivateSpeedSkill()
    if key == 'c':
        chat = threading.Thread(target=clientChat.ClientChat)
        chat.start()
    if key == 'b' and not player.npc:
        player.npc = True
    elif key == 'b' and player.npc:
        player.npc = False
        player.npc_activate = True
    if key == 'q':
        print(calculate_distance(player.position, (-600, 11, -800)))
        print(calculate_distance(player.position, (800, 0, 650)))
    if key == 'q' and (calculate_distance(player.position, (-600, 0, -800)) < 20 or calculate_distance(player.position,
                                                                                                       (800, 0,
                                                                                                        650)) < 20):
        print(calculate_distance(player.position, (-600, 11, -800)))
        print(calculate_distance(player.position, (800, 0, 650)))
        safe_exit()

    # Check if 'i' is pressed and the chest is open
    if key == 'i' and activeChest != 0:
        if activeChest.isopen:
            activeChest.CloseChest()
            activeChest = 0
    else:
        # Check if 'i' is pressed and the inventory button is enabled
        if key == 'i':
            if inv.enabled:
                inv.closeInv(player)
            else:
                inv.openInv(player)


def addItems(data):
    packet_values = data.split('&')
    print(packet_values)
    ak47_count = int(packet_values[3])
    m4_count = int(packet_values[4])
    awp_count = int(packet_values[5])
    mp5_count = int(packet_values[6])
    medkit_count = int(packet_values[7])
    bandage_count = int(packet_values[8])
    potion_swiftness_count = int(packet_values[9])
    potion_leaping_count = int(packet_values[10])
    if ak47_count > 0:
        for _ in range(ak47_count):
            inv.add_item("ak-47")
    if m4_count > 0:
        for _ in range(m4_count):
            inv.add_item("m4")
    if awp_count > 0:
        for _ in range(awp_count):
            inv.add_item("awp")
    if mp5_count > 0:
        for _ in range(mp5_count):
            inv.add_item("mp5")
    if medkit_count > 0:
        for _ in range(medkit_count):
            inv.add_item("medkit")
    if bandage_count > 0:
        for _ in range(bandage_count):
            inv.add_item("bandage")
    if potion_swiftness_count > 0:
        for _ in range(potion_swiftness_count):
            inv.add_item("potion of swiftness")
    if potion_leaping_count > 0:
        for _ in range(potion_leaping_count):
            inv.add_item("potion of leaping")


def build_map():
    # ground = Entity(model='plane', collider='mesh', scale=(2500, 0, 2500), texture='grass')
    # colosseum = Entity(model='my_colosseum3_test', collider='sphere', texture='marble', scale=2, position=(0, 6, 0))
    jeep = Entity(model='jeep', collider='sphere', texture='sphere', scale=5, position=(-600, 11, -800))
    helicopter = Entity(model='helicopter', collider='sphere', texture='Huey', scale=5, position=(800, 0, 650),
                        rotation_x=-90)
    wall1 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(0, 0, -1250))
    wall2 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(0, 0, 1250),
                   rotation_y=180)
    wall3 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(-1250, 0, 0),
                   rotation_y=90)
    wall4 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(1250, 0, 0),
                   rotation_y=-90)
    Entity(model='forest_trunk', collider='sphere', texture='brown', scale=2, position=(0, 0, 0))
    Entity(model='forest_head', texture='dark_green', scale=2, position=(0, 0, 0))

    tree_scale = 3
    x_array = [159, 1056, 715, -1076, -936, -99, -123, 269, 384, 325, 1002, -203, -823, 1065, 743, -368, -821, 526,
               -368, 653]
    z_array = [-684, -892, -590, -1062, 348, -748, -335, -738, -469, -1034, -70, -704, 112, -889, 890, -960, 1075, -288,
               -535, -114]
    angle_array = [162, 53, 105, 223, 156, 175, 236, 212, 288, 308, 262, 290, 294, 334, 343, 180, 276, 253, 104, 266]
    for i in range(0, 20):
        Entity(model='tree_trunk2', collider='sphere', texture='brown', scale=tree_scale,
               position=(x_array[i], 0, z_array[i]), rotation_y=angle_array[i])
        Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(x_array[i], 0, z_array[i]),
               rotation_y=angle_array[i])

    x_array = [296, 208, -524, -847, 720, -323, 436, 454, -552, -485, -540, -161, -346, -442, 712, 237, 273, 542, 940,
               905]
    z_array = [217, 980, -725, 950, -183, 768, -805, 660, -489, -197, 292, 150, -221, -825, 364, 373, 456, -508, -206,
               221]
    angle_array = [40, 135, 200, 278, 318, 231, 269, 84, 310, 165, 201, 74, 28, 256, 352, 206, 249, 56, 30, 360]
    for i in range(0, 20):
        Entity(model='tree_trunk4', collider='sphere', texture='brown', scale=tree_scale,
               position=(x_array[i], 0, z_array[i]), rotation_y=angle_array[i])
        Entity(model='tree_head4', texture='dark_green', scale=tree_scale, position=(x_array[i], 0, z_array[i]),
               rotation_y=angle_array[i])

    grass_scale = 4
    x_array = [690, 910, -581, 621, 572, 583, -290, 155, 683, 556, 620, -569, 176, 814, -652, -140, 475, 237, -160,
               -624]
    z_array = [-358, -371, 749, 706, -25, 445, 439, 424, 690, 119, 297, 919, 145, -612, 55, -364, -535, 672, 560, -859]
    for i in range(0, 20):
        Entity(model='grass', texture='light_green', scale=grass_scale, position=(x_array[i], 0, z_array[i]))

    x_array = [-261, -469, -761, 261, 994, 257, 461, 321, 561, -758, 717, -372, 93, 147, -686, 731, 168, 843, 651, 479]
    z_array = [-377, 354, 630, -866, 470, -338, -75, 139, -135, -408, 97, -647, -399, -923, -454, -540, 625, -475, 101,
               -158]
    for i in range(0, 20):
        Entity(model='rocks1', collider='box', texture='grey', scale=4, position=(x_array[i], 0, z_array[i]))

    x_array = [40, 183, -838, 245, -786, 303, -640, -154, -867, -733, 694, 225, 525, -690, -698, -830, 695, -665, 871,
               264]
    z_array = [-736, -497, 758, 762, -676, -128, 930, -201, -7, 407, -870, -606, 753, -539, -361, -54, -587, -889, 166,
               219]
    for i in range(0, 20):
        Entity(model='rocks2', collider='box', texture='grey', scale=3, position=(x_array[i], 0, z_array[i]))

    return


def deactivate_cooldown_skill():
    skill_display.changeToWhite('cooldown')
    if gun.gun_type == 'awp':
        gun.cooldown = 2
    if gun.gun_type == 'm4':
        gun.cooldown = 0.25
    if gun.gun_type == 'ak-47':
        gun.cooldown = 0.5
    if gun.gun_type == 'mp5':
        gun.cooldown = 0
    print("Cooldown skill deactivated!")


def deactivate_speed_skill():
    skill_display.changeToWhite('speed')
    player.speed = 20  # Reset speed to default or previous value
    print("Speed skill deactivated!")


def deactivate_strength_skill():
    skill_display.changeToWhite('strength')
    if gun.gun_type == 'awp':
        gun.damage = 100
    if gun.gun_type == 'm4':
        gun.damage = 33
    if gun.gun_type == 'ak-47':
        gun.damage = 36
    if gun.gun_type == 'mp5':
        gun.damage = 25
    print("Strength skill deactivated!")


def can_activate_skill(skill_name):
    cooldown_seconds = 60  # 30 seconds cooldown
    current_time = time.time()
    last_activation_time = last_skill_activation.get(skill_name, 0)
    return (current_time - last_activation_time) >= cooldown_seconds


def ActivateCoolDownSkill():
    skill_display.changeToRed('cooldown')
    if can_activate_skill('cooldown'):
        gun.cooldown = 0
        last_skill_activation['cooldown'] = time.time()
        print("Cooldown skill activated!")
        invoke(deactivate_cooldown_skill, delay=15)  # Deactivate after 15 seconds
    else:
        print("Cooldown skill is still on cooldown!")


def ActivateSpeedSkill():
    skill_display.changeToRed('speed')
    if can_activate_skill('speed'):
        player.speed = 15
        last_skill_activation['speed'] = time.time()
        print("Speed skill activated!")
        invoke(deactivate_speed_skill, delay=15)  # Deactivate after 15 seconds
    else:
        print("Speed skill is still on cooldown!")


def ActivateStrengthSkill():
    skill_display.changeToRed('strength')
    if can_activate_skill('strength'):
        gun.damage = 100
        last_skill_activation['strength'] = time.time()
        print("Strength skill activated!")
        invoke(deactivate_strength_skill, delay=15)  # Deactivate after 15 seconds
    else:
        print("Strength skill is still on cooldown!")


def close_game():
    stop_event.set()
    application.quit()
    exit()
    pass


def client_program(port_yes, host, port):
    host = host
    port = port

    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Receive prime and base from the server
    prime = int(client_socket.recv(1024).decode())
    print(prime)
    base = int(client_socket.recv(1024).decode())
    print(base)
    # Generate client's private key
    private_key_client = random.randint(1, prime - 1)  # Assume this is generated securely

    # Receive server's public key
    data = client_socket.recv(1024).decode()
    print(1)
    print(data)

    # Calculate public key to send to the server
    public_key_client = pow(base, private_key_client, prime)
    print(f"{public_key_client}&{port_yes}")
    client_socket.send(f"{public_key_client}&{port_yes}".encode())

    # Calculate shared secret
    print("5")
    shared_secret = pow(int(data), private_key_client, prime)

    client_socket.close()
    return shared_secret, public_key_client, private_key_client


class Melee:
    def _init_(self, arm1, arm2):
        self.arm1 = arm1
        self.arm2 = arm2
        self.original_arm1_position = arm1.position
        self.original_arm2_position = arm2.position
        self.right_arm = True
        self.punch_cooldown = 0.7
        self.last_toggle_time = 0
        self.activation_cooldown = 1
        self.prev_activation_time = 0
        self.damage = 100

    def punch(self):
        # Move arms forward slightly as a punch
        if time.time() - self.last_toggle_time >= self.punch_cooldown:
            if self.right_arm:
                self.arm1.animate_position(self.arm1.position + Vec3(0, 0, 1), duration=0.2)
                self.right_arm = False
            else:
                self.arm2.animate_position(self.arm2.position + Vec3(0, 0, 1), duration=0.2)
                self.right_arm = True
            self.hit()
            # Reset arm positions after punch
            self.last_toggle_time = time.time()
            invoke(self.reset_arm_positions, delay=0.3)

    def reset_arm_positions(self):
        # Reset arm positions back to their original positions
        self.arm1.animate_position(self.original_arm1_position, duration=0.2)
        self.arm2.animate_position(self.original_arm2_position, duration=0.2)

    def hit(self):
        hovered_entity = mouse.hovered_entity
        #dist = calculate_distance(player.position, hovered_entity.position)
        if hovered_entity and calculate_distance(player.position, hovered_entity.position) < 3.5 and (isinstance(hovered_entity, Enemy) or isinstance(hovered_entity, Witch)):
            hovered_entity.enemy_hit(self)

        if hovered_entity and calculate_distance(player.position, hovered_entity.position) < 3.5 and isinstance(hovered_entity, MultiPlayer):
            print("HIT PLAYER")
            hovered_entity.damage(self.damage)

    def deactivate(self):
        # Animate the arms to a deactivated position (putting them down)
        if time.time() - self.prev_activation_time >= self.activation_cooldown:
            if self.arm1.enabled and self.arm2.enabled:
                self.arm1.animate_position(self.original_arm1_position + Vec3(0, -0.8, 0), duration=0.4)
                self.arm2.animate_position(self.original_arm2_position + Vec3(0, -0.8, 0), duration=0.4)
                invoke(self.create_destroy_arms, delay=0.6)
                self.prev_activation_time = time.time()
                self.last_toggle_time = time.time()  # So that you won't be able to punch mid animation

    def activate(self):
        # Animate the arms to an activated position (putting them up)
        if time.time() - self.prev_activation_time >= self.activation_cooldown:
            if not (self.arm1.enabled and self.arm2.enabled):
                self.create_destroy_arms()
                self.arm2.animate_position(self.original_arm2_position, duration=0.4)
                self.arm1.animate_position(self.original_arm1_position, duration=0.4)
                self.prev_activation_time = time.time()
                self.last_toggle_time = time.time()

    def create_destroy_arms(self):
        # Enable or disable arms accordingly
        if self.arm1.enabled and self.arm2.enabled:
            self.arm1.enabled = False
            self.arm2.enabled = False
        else:
            self.arm1.enabled = True
            self.arm2.enabled = True

    def destroy_arms(self):
        self.arm1.enabled = False
        self.arm2.enabled = False

    def create_arms(self):
        self.arm1.enabled = True
        self.arm2.enabled = True

    def check_active_cooldown(self):
        if time.time() - self.prev_activation_time >= self.activation_cooldown:
            return True
        else:
            return False

    def check(self):
        return self.arm1.enabled and self.arm2.enabled

def get_private_ip():
    # Create a socket connection to a remote server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This IP and port are arbitrary and don't need to be reachable
        # We just need to open a socket and get the local address used
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
    except Exception as e:
        private_ip = "Unable to determine IP address: " + str(e)
    finally:
        s.close()
    return private_ip


if __name__ == "__main__":
    try:

        ip = builtins.input("Fill the ip of the login-server")
        login_ip = ip
        ip = builtins.input("Fill the ip of the load-balancer")
        lb_ip = ip

        port_yes = random.randint(50000, 65534)
        print("Port generated is: ", port_yes)

        secret, client_public_key, client_private_key = client_program(port_yes, lb_ip, 1010)
        print("secret: " + str(secret))
        print("public: " + str(client_public_key))
        print("private: " + str(client_private_key))

        secret_login, client_public_key_login, client_private_key_login = client_program(port_yes, login_ip, 7878)
        print("secret login: " + str(secret_login))
        print("public login: " + str(client_public_key_login))
        print("private login: " + str(client_private_key_login))

        subprocess.run(
            ['python', 'LoginPage.py', str(port_yes).encode(), str(secret_login).encode(), login_ip.encode(), get_private_ip().encode()])

        subprocess.run(['python', 'LobbyUI.py', str(port_yes).encode(), str(secret_login).encode(), login_ip.encode(), get_private_ip().encode()])

        client_id = port_yes

        client = clientfuncs(int(client_id), lb_ip)

        addr = client.get_ip()
        addr = f'({addr[0]}, {addr[1]})'
        msg = f'HI&{client.get_id()}'
        brr = encrypt(msg, secret)
        client.send_data(brr)
        print("Sending: ", msg)

        invdata = 0
        counter = 0

        while True:
            invdata = client.receive_data()
            invdata = decrypt(invdata, secret)
            if invdata.startswith("sINV"):
                print("Current inv is: ", invdata)
                break

        app = Ursina(borderless=False)
        skybox_image = load_texture("scattered-clouds-blue-sky.jpg")
        Sky(texture=skybox_image)

        ground = Entity(model='plane', collider='mesh', scale=(2500, 0, 2500), texture='grass')
        build_map()
        skill_display = SkillDisplay()
        # skill_display.close_skills()
        player = player()

        sendThread = threading.Thread(target=send_game_data_continuously, args=(player, stop_event, secret))
        sendThread.start()

        renderThread = threading.Thread(target=stop_rendering_continuosly, args=(player, stop_event))
        renderThread.start()

        recvThread = threading.Thread(target=recv_game_data_continuosly, args=(player, stop_event, secret))
        recvThread.start()

        print("here")

        awp = Gun(player, 'awp')
        ak = Gun(player, 'ak-47')
        m4 = Gun(player, 'm4')
        mp5 = Gun(player, 'mp5')
        gun = Gun(player, 'None')
        mp5.enabled = False
        awp.enabled = False
        ak.enabled = False
        m4.enabled = False
        selectedGun = gun

        print("6")

        kill_count_ui = KillCountUI('KillCount.png', position=(0, 0.45), scale=2)

        print("7")

        inv = Inventory(player, 4, 4)
        inv.enabled = False
        addItems(invdata)

        print("8")

        miniInv = MiniInv(inv)

        print("9")

        enemies = {}
        items = {}

        player_health_bar = HealthBar(value=100, position=(-0.9, -0.48))

        # Load the PNG image for the scope
        scope_texture = load_texture('scope.png')  # Replace 'scope.png' with the path to your scope image

        # Create a window panel to display the scope image
        scope_panel = WindowPanel(texture=scope_texture, scale=(0.5, 0.5), enabled=False)

        background = Entity(parent=camera.ui, model='quad', texture='scope.png', scale_x=camera.aspect_ratio, z=1)
        background.visible = False

        respawn_screen = RespawnScreen()
        respawn_screen.hide()

        arm1 = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
                      color=color.white)
        arm2 = Entity(model='cube', parent=camera, position=(-.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
                      color=color.white)
        melee = Melee(arm1, arm2)
        melee.create_destroy_arms()

        sound = Audio("pistol_shoot.mp3", loop=False, autoplay=False)

        random_direction = Vec3()

        # chest = Chest((2, 0, 2))
        # chest._ChestInv = Inventory(None,4,4)
        # chest._ChestInv.add_item("ak-47")

        player_money_bar = HealthBar(position=(-0.9, -0.445), bar_color=color.gold, max_value=1000)
        player_money_bar.value = 100

        print("10")

        time.sleep(1)

        app.run()

        print("11")
    except Exception as e:
        print(f"{Exception}:", e)
