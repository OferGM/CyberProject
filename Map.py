from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader


def build_map():
    #ground = Entity(model='plane', collider='mesh', scale=(2500, 0, 2500), texture='grass')
    #colosseum = Entity(model='my_colosseum3_test', collider='mesh', texture='marble', scale=2, position=(0, 6, 0))
    jeep = Entity(model='jeep', collider='mesh', texture='jeep', scale=5, position=(-600, 11, -800))
    helicopter = Entity(model='helicopter', collider='mesh', texture='Huey', scale=5, position=(800, 0, 650),
                        rotation_x=-90)
    wall1 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(0, 0, -1250))
    wall2 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(0, 0, 1250),
                   rotation_y=180)
    wall3 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(-1250, 0, 0),
                   rotation_y=90)
    wall4 = Entity(model='wall', collider='box', scale=(5, 1, 1), texture='wall_texture', position=(1250, 0, 0),
                   rotation_y=-90)
    Entity(model='forest_trunk', collider='mesh', texture='brown', scale=2, position=(0, 0, 0))
    Entity(model='forest_head', texture='dark_green', scale=2, position=(0, 0, 0))

    tree_scale = 3
    x_array = [159, 1056, 715, -1076, -936, -99, -123, 269, 384, 325, 1002, -203, -823, 1065, 743, -368, -821, 526,
               -368, 653]
    z_array = [-684, -892, -590, -1062, 348, -748, -335, -738, -469, -1034, -70, -704, 112, -889, 890, -960, 1075, -288,
               -535, -114]
    angle_array = [162, 53, 105, 223, 156, 175, 236, 212, 288, 308, 262, 290, 294, 334, 343, 180, 276, 253, 104, 266]
    for i in range(0, 20):
        Entity(model='tree_trunk2', collider='mesh', texture='brown', scale=tree_scale,
               position=(x_array[i], 0, z_array[i]), rotation_y=angle_array[i])
        Entity(model='tree_head2', texture='med_gren', scale=tree_scale, position=(x_array[i], 0, z_array[i]),
               rotation_y=angle_array[i])

    x_array = [296, 208, -524, -847, 720, -323, 436, 454, -552, -485, -540, -161, -346, -442, 712, 237, 273, 542, 940,
               905]
    z_array = [217, 980, -725, 950, -183, 768, -805, 660, -489, -197, 292, 150, -221, -825, 364, 373, 456, -508, -206,
               221]
    angle_array = [40, 135, 200, 278, 318, 231, 269, 84, 310, 165, 201, 74, 28, 256, 352, 206, 249, 56, 30, 360]
    for i in range(0, 20):
        Entity(model='tree_trunk4', collider='mesh', texture='brown', scale=tree_scale,
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


