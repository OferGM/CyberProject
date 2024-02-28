from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader


def build_map():
    ground = Entity(model='plane', collider='mesh', scale=(2500, 0, 2500), texture='grass')
    colosseum = Entity(model='Test_Colosseum', collider='mesh', texture='marble', scale=4, position=(0, 13, 0))
    jeep = Entity(model='jeep', collider='mesh', texture='jeep', scale=10, position=(-600, 15, -800))
    helicopter = Entity(model='helicopter', collider='mesh', texture='Huey', scale=10, position=(800, 0, 650),
                        rotation_x=-90)
    Entity(model='forest_trunk', collider='mesh', texture='brown', scale=4, position = (0, 0 , 0))
    Entity(model='forest_head', texture='dark_green', scale=4, position = (0, 0 , 0))


    tree_scale = 6
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-1100, 0, -1000), rotation_y = 65)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-1100, 0, -1000), rotation_y = 65)
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-950, 0, -800), rotation_y=40)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-950, 0, -800), rotation_y=40)
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-700 0,-700), rotation_y=25)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-700, 0, -700), rotation_y=25)
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-400, 0, -750), rotation_y=30)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-400, 0, -750), rotation_y=30)
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-200, 0, -370), rotation_y=80)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-200, 0, -370), rotation_y=80)
    Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale, position=(-1100, 0, -1000), rotation_y=65)
    Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(-1100, 0, -1000), rotation_y=65)

    for i in range(10):
        angle = random.randrange(0, 180)
        x = random.randrange(200, 1200)
        z = random.randrange(200, 1200)
        Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=6, position=(x, 0, z), rotation_y = angle)
        Entity(model='tree_head2', texture='med_gren', scale=6, position=(x, 0, z), rotation_y = angle)
        range1 = -1300
        range2 = 1300
    for i in range(15):
        angle = random.randrange(0, 180)
        x = random.randrange(range1, range2)
        z = random.randrange(range1, range2)
        Entity(model='tree_trunk4', collider='mesh', texture='brown', scale=6, position=(x, 0, z), rotation_y = angle)
        Entity(model='tree_head4', texture='dark_green', scale=6, position=(x, 0, z), rotation_y = angle)
    for i in range(20):
        x = random.randrange(range1, range2)
        z = random.randrange(range1, range2)
        Entity(model='grass', texture='light_green', scale=8, position=(x, 0, z))
    for i in range(20):
        angle = random.randrange(0, 180)
        rocks1 = Entity(model='rocks1', collider='box', texture='grey', scale=4, rotation_y = angle ,
                        position=(random.randrange(-1000, 1000), 0, random.randrange(-1000, 1000)))
        rocks2 = Entity(model='rocks2', collider='box', texture='grey', scale=3, rotation_y = angle,
                        position=(random.randrange(-1000, 1000), 0, random.randrange(-1000, 1000)))
    wall1 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position = (0 , 0 , -1250))
    wall2 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(0, 0, 1250), rotation_y = 180)
    wall3 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(-1250, 0, 0),
                   rotation_y=90)
    wall4 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(1250, 0, 0),
                   rotation_y=-90)
build_map()
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent


for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
        x=random.uniform(-8,8),
        z=random.uniform(-8,8) + 8,
        collider='box',
        scale_y = random.uniform(2,3),
        color=color.hsv(0, 0, random.uniform(.9, 1))
        )

def update():
    if held_keys['left mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)



def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

app.run()