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
import LoginPage
import LobbyUI
import subprocess


# Define possible loot items
LOOT_ITEMS = ['gold_coin', 'silver_coin', 'health_potion', 'ammo']

running = 1

mobs = {}
players = {}
rendered_players = {}
update_queue = Queue()

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

def CreateItem(coords, id,type):
    if id in items:
        if items[id].position == coords:
            return
    item = Item(position=coords, id=id, ttype=type)
    items[id] = item


def separate_mob_string(all_mobs_string):
    # Split the string by semicolons to get individual mob data strings
    mob_entries = all_mobs_string.split(';')

    for entry in mob_entries:
        if entry and entry != '&':  # Check if entry is not empty
            parts = entry.split('&')
            # Extract the ID and coordinates, converting them to the appropriate types
            try:
                id = int(parts[0])
                coords = tuple(map(float, parts[1:4]))
                if id in mobs.keys():
                    mobs[id].set_position(coords)
                    mobs[id].rotation_y = float(parts[4])
                else:
                    CreateEnemy(coords, id)
            except Exception as e:
                # Handle the case where conversion to int fails
                print(f"Could not convert {entry} to mob data: ", e)

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


def seperateInv(inv3):
    inv1 = Inventory(player, 4, 4)
    inv2 = Inventory(None, 4, 1)
    for item in inv3.children:
        if item.sloty <= 4:
            inv1.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty)
        else:
            inv2.append(str(item.texture).replace('.png', ''), item.slotx, 0)
    return inv1, inv2


def combineInv(inv1, inv2):
    inv3 = Inventory(None, 4, 5)
    for item in inv1.children:
        inv3.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty + 4)

    for item in inv2.children:
        inv3.append(str(item.texture).replace('.png', ''), item.slotx, item.sloty)

    return inv3


class Chest(Entity):
    def __init__(self, position, chest_inventory=None):
        super().__init__(
            model='Suitcase_for_tools.glb',
            position=position,
            collider='box',
            scale=4,
        )
        # Initialize ChestInv with the provided inventory or a new one if not provided
        self.isopen = False
        self._ChestInv = chest_inventory if chest_inventory is not None else Inventory(None)

    @property
    def ChestInv(self):
        # Lazy initialization of ChestInv, if it's not already set
        if self._ChestInv is None:
            self._ChestInv = Inventory(None, 4, 1)
        return self._ChestInv

    def CloseChest(self):
        global inv, inv3
        inv, self._ChestInv = seperateInv(inv3)
        inv3.closeInv(player)
        self.isopen = False
        del inv3  # Delete inv3 after it's no longer needed

    def OpenChest(self):
        global inv3
        # Ensure that conditions are right to open the chest (e.g., resources are loaded)
        if not self.isopen:
            self.isopen = True
            inv3 = combineInv(self.ChestInv, inv)  # Combine inventories
            inv3.openInv(player)
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

    def respawn(self, screen):
        screen.hide()
        player.position = (0, 0, 0)

    def SpeedSkillEnable(self):
        self.speed = 15
        invoke(player.SpeedSkillDisable)

    def SpeedSkillDisable(self):
        self.speed = 8


class Item(Entity):
    def __init__(self, position, id,ttype): #DONT CHANGE ttype NAME
        super().__init__(
            model=ttype,  # Replace 'cube' with a suitable model for your loot
            position=position,  # Consider specifying an actual texture if available
            collider='box',
            ttype = ttype,
            id=id,
            scale = 1
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
            client.send_data(f"gPICKED&{client.id}&{self.id}")
            inv.add_item(self.ttype)
            # Queue the removal to ensure it happens in the main thread
            update_queue.put(lambda: self.safe_destroy())


class Enemy(Entity):
    def __init__(self, position, id):
        super().__init__(
            model='zombie.glb',
            position=position,
            health=100,
            collider='box',
            scale=0.08,
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
        if self.health <= 0:
            self.drop_loot()  # Drop loot when the enemy is killed
            if self.id in mobs:
                mobs.pop(self.id)
                client.send_data(f"gDEAD&{client.id}&{self.id}")
            else:
                pass
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
        player.health = player.health - 10
        if player.health <= 0:
            respawn_screen.show()


class MultiPlayer(Entity):
    def __init__(self, id, position=(0,0,0), health=100, model='minecraft_steve.glb', scale=0.08, **kwargs):
        super().__init__(
            position=position,
            model=model,
            scale=scale,
            collider='box',
            **kwargs
        )
        self.id = id
        self.health = health

    def damage(self,amount):
        self.health -= amount
        client.send_data(f"gDAMAGE&{self.id}&{self.health}")
        print(f"DAMAGED {self.id}")



class Gun(Entity):
    def __init__(self, parent_entity, gun_type='ak-47', position=(0.5, 1.5, 1), damage=25):
        super().__init__(
            model='',
            origin_z=0,
            origin_y=0,
            on_cooldown=False,
            scale=0.006,
            parent=parent_entity,
            position=position,
            rotation_y=180,
            damage=damage,
            texture='',
            aiming=False,
            on_cooldown_scope=False,
            last_toggle_time=0,
            cooldown_duration=0.5  # Cooldown duration in seconds

        )
        self.gun_type = gun_type

        # Additional gun type configuration
        if gun_type == 'ak-47':
            self.model = 'Ak-47.obj'
            self.texture = 'Ak-47_tex'
            self.position = (0.5, 1.5, 1)
            self.rotation_y = 0
            self.damage = 35
            self.scale = 0.01
            player.cursor.visible = True

        if gun_type == 'm4':
            self.model = 'M4a1.obj'
            self.texture = 'm4_tex'
            self.position = (0.5, 1.5, 1)
            self.scale = 0.25
            player.cursor.visible = True

        if gun_type == 'awp':
            self.model = 'awp.obj'
            self.texture = 'awp_tex.png'
            self.position = (0.5, 1.4, 0.2)
            self.rotation_y = 0
            self.damage = 100
            self.scale = 0.05
            player.cursor.visible = False

    def reset_cooldown(self):
        self.on_cooldown = False

    def reset_cooldown_scope(self):
        self.on_cooldown_scope = False

    def shoot(self):
        if gun.on_cooldown:
            return

        hovered_entity = mouse.hovered_entity
        print(type(hovered_entity))

        if hovered_entity and isinstance(hovered_entity, Enemy) and (calculate_distance(player.position,
                                                                                        hovered_entity.position) < 20 or gun.gun_type == 'awp'):
            hovered_entity.enemy_hit(gun)
        if hovered_entity and isinstance(hovered_entity, MultiPlayer) and (calculate_distance(player.position,
                                                                                        hovered_entity.position) < 20 or gun.gun_type == 'awp'):
            print("HIT PLAYER")
            hovered_entity.damage(20)
        gun.on_cooldown = True
        invoke(gun.reset_cooldown, delay=0.1)  # Set the cooldown duration (0.5 seconds in this example)

    def aim(self):
        current_time = time.time()
        if current_time - self.last_toggle_time >= self.cooldown_duration:
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


def update():
    while not update_queue.empty():
        task = update_queue.get()
        task()  # Execute the task

    for item_id in list(items.keys()):
        item = items[item_id]
        item.pickup()

    for zombie_id in list(mobs.keys()):
        mob = mobs[zombie_id]
        if calculate_distance(player.position,mob.position) < 2:
            player.health -= 10

    player_health_bar.value = player.health


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

def stop_rendering_continuosly():
    while True:
        for ID in rendered_players.keys():
            print("sdklsdkl")
            if rendered_players[ID] == 1:
                players[ID].enabled = True
                rendered_players[ID] = 0
            else:
                players[ID].enabled = False
        time.sleep(0.2)

def send_game_data_continuously(player, stop_event):
    while not stop_event.is_set():
        client.send_data(f"gSTATE&{client.id}&{player.x}&{player.y}&{player.z}&{player.rotation_y}&{player.health}")
        time.sleep(0.01)

def recv_game_data_continuosly(player, stop_event):
    try:
        while not stop_event.is_set():
            a = client.receive_data()
            print("received: ", a)
            aList = a.split('&')
            if aList[0] == 'STATE':
                if int(aList[1]) != int(client.get_id()):
                    if int(aList[1]) in players:
                        rendered_players[int(aList[1])] = 1
                        p2 = players[int(aList[1])]
                        p2.x = float(aList[2])
                        p2.y = float(aList[3]) + 1.2
                        p2.z = float(aList[4])
                        p2.rotation_y = float(aList[5]) + 180
                        p2.health = int(aList[6])
                    else:
                        players[int(aList[1])] = MultiPlayer(id=int(aList[1]))
            if aList[0] == 'aM':
                separate_mob_string(a.replace('aM', ''))
            if aList[0] == 'aI':
                if (a.replace('aI&', '') != ''):
                    separate_item_string(a.replace('aI', ''))
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
                    if player.health <= 0:
                        respawn_screen.show()
            if aList[0] == 'aPICKED':
                items[int(aList[1])].enabled = False
    except Exception as e:
        print("error: ", e)

stop_event = threading.Event()


def input(key):
    global cursor
    if key == 'escape':
        # Wait for the background thread to finish
        stop_event.set()
        thread.join()
        application.quit()
        exit()
    if held_keys['left mouse']:
        gun.shoot()
    if held_keys['right mouse']:
        if chest.Check():
            chest.OpenChest()
        elif gun.gun_type == 'awp' and inv.enabled == False:
            gun.aim()

    # Check if 'i' is pressed and the chest is open
    if key == 'i' and chest.isopen:
        chest.CloseChest()
    else:
        # Check if 'i' is pressed and the inventory button is enabled
        if key == 'i':
            if inv.enabled:
                skill_display.close_skills()
                inv.closeInv(player)
            else:
                skill_display.show_skills()
                inv.openInv(player)


if __name__ == "__main__":
    try:

    my_socket = socket.socket()
    my_socket.connect(("127.0.0.1", 6969))
    subprocess.run(['python', 'LoginPage.py'])
    # data = my_socket.recv(9192).decode()
    # print(data)
    # ak, m4, awp, mp5, mk, bnd, sp, lp, cash = data.split("&")
    subprocess.run(['python', 'LobbyUI.py'])
    # data = my_socket.recv(9192).decode()
    # client_id = data.split("&")[1]
    # print(client_id)
    client = clientfuncs(int(123123))

        client = clientfuncs(int(client_id))

        addr = client.get_ip()
        addr = f'({addr[0]}, {addr[1]})'
        msg = f'HI&{client.get_id()}'
        client.send_data(msg)
        print("sending: ", msg)

        print("0")

        app = Ursina(borderless=False)

        print("1")

        ground = Entity(model='plane', collider='box', scale=128, texture='grass', texture_scale=(8, 8))
        skill_display = SkillDisplay()
        skill_display.close_skills()
        player = player()

        print("2")

        time.sleep(1)

        thread = threading.Thread(target=send_game_data_continuously, args=(player, stop_event))
        thread.start()

        print("3")

        thread = threading.Thread(target=stop_rendering_continuosly, args=())
        thread.start()

        thread = threading.Thread(target=recv_game_data_continuosly, args=(player, stop_event))
        thread.start()

        print("4")

        print("5")

        gun = Gun(player, 'awp')

        print("6")

        kill_count_ui = KillCountUI('KillCount.png', position=(0, 0.45), scale=2)

        print("7")

        inv = Inventory(player, 4, 4)
        inv.enabled = False
        inv.add_item("medkit")
        inv.add_item("medkit")

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

        chest = Chest((2, 0, 2))
        chest.ChestInv = Inventory(None)

        player_money_bar = HealthBar(position=(-0.9, -0.445), bar_color=color.gold, max_value=1000)
        player_money_bar.value = 100

        print("10")

        time.sleep(1)

        app.run()

        print("11")
    except Exception as e:
        print("error: ", e)