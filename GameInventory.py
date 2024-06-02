from ursina import *
import items

class Inventory(Entity):
    def __init__(self,player, width=7, height=8, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=.015),
            texture='white_cube',
            texture_scale=(width, height),
            scale=(width * .1, height * .1),
            origin=(-.5, .5),
            position=(-.3, .4),
            color=color.color(0, 0, .1, .9),
            button_enabled=False,
            enabled=False,
            player = player,
            width = width,
            height = height,
        )

        self.width = width
        self.height = height

        for key, value in kwargs.items():
            setattr(self, key, value)
        add_item_button = Button(
            scale=(.1, .1),
            x=-.5,
            color=color.lime.tint(-.25),
            text='+',
            on_click=self.add_item,
            enabled=self.button_enabled
        )

        mouse.visible = False

    def find_free_spot(self):
        for y in range(self.height):
            for x in range(self.width):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]

                if not (x, -y) in grid_positions:
                    return x, y

    def input(self, key):
        for item in self.children:
            if held_keys['right mouse'] and item.hovered:
                destroy(item)
    def isFull(self):
        if len(self.children) >= self.width * self.height:
            return True
        return False

    def append(self, item, x=0, y=0):

        if len(self.children) >= self.width * self.height:
            error_message = Text('<red>Inventory is full!', origin=(0, -1.5), x=-.5, scale=2)
            destroy(error_message, delay=1)
            return

        if x + y == 0:
            x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            slotx=x,
            sloty=y,
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )
        name = item.replace('_', ' ').title()


        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * self.width) / self.width
            icon.y = int((icon.y - (icon.scale_y / 2)) * self.height) / self.height
            icon.z += .01

            icon.slotx = icon.x * self.width
            icon.sloty = icon.y * -self.height

            # if outside, return to original position
            if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
                icon.position = (icon.org_pos)
                return

            # if the spot is taken, swap positions
            for c in self.children:
                if c == icon:
                    continue

                if c.x == icon.x and c.y == icon.y:
                    c.position = icon.org_pos
                    temp_x, temp_y = c.slotx, c.sloty

                    # Swap values
                    c.slotx, c.sloty = icon.slotx, icon.sloty
                    icon.slotx, icon.sloty = temp_x, temp_y

        icon.drag = drag
        icon.drop = drop

    def add_item(self,type):
        self.append(type)

    def input(self, key):
        for item in self.children:
            if held_keys['right mouse'] and item.hovered:
                self.use_item(item)

    def use_item(self, item):
        if str(item.texture) == 'bandage.png':
            if self.player.health == 100:
                return
            items.bandage_player(self.player, item)

        if str(item.texture) == 'medkit.png':
                if self.player.health == 100:
                    return
                items.medkit_player(self.player, item)
        if str(item.texture) == 'potion of leaping.png':
                items.potion_of_leaping_player(self.player,item)
        if str(item.texture) == 'potion of swiftness.png':
            items.potion_of_swiftness_player(self.player, item)

    def openInv(self, player):
        global cursor
        self.enabled = True
        self.button_enabled = True
        player.enabled = False
        mouse.visible = False
        Cursor.enabled = False
        cursor = Cursor(texture='cursor', scale=.1)

    def closeInv(self, player):
        self.enabled = False
        self.button_enabled = False
        player.enabled = True
        mouse.visible = False
        Cursor.enabled = True
        destroy(cursor)

    def get_inventory_items(self):
        return [str(item.texture).replace('.png','') for item in self.children]
    def CleanInv(self):
        for item in self.children:
            destroy(item)


if __name__ == '__main__':
    app = Ursina()

    inventory = Inventory()


    def add_item(item):
        inventory.append(item)


    add_item_button = Button(
        scale=(.1, .1),
        x=-.5,
        color=color.lime.tint(-.25),
        text='+',
        on_click=add_item
    )

    app.run()
