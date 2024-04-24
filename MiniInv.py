import math

from ursina import *

import items
from GameInventory import Inventory


class MiniInv(Entity):
    def __init__(self, inventory, **kwargs):
        super().__init__(**kwargs)
        self.inventory = inventory
        self.parent = camera.ui
        self.selected_index = 0
        self.image_entities = []
        self.inventory_snapshot = []  # To track inventory changes, including reordering
        self.image_children = [0,0,0,0]

        # Initialize image entities for inventory slots
        for i in range(4):  # Adjust number of slots as needed
            e = Entity(parent=self, model='quad', scale=(0.08, 0.08, 0.08))
            self.image_entities.append(e)

        self.arrange_images()
        self.update_highlight()
        self.input = self.check_input
        self.update_inventory()  # Initial inventory update

    def HeldItem(self):
        return str(self.image_entities[self.selected_index].texture)

    def arrange_images(self):
        for i, e in enumerate(self.image_entities):
            e.y = -0.4
            e.x = i * 0.10 - 0.15  # Adjust spacing as needed

    def update_highlight(self):
        for i, entity in enumerate(self.image_entities):
            entity.color = color.azure if i == self.selected_index else color.white

    def check_input(self, key):
        if key == 'left arrow':
            self.selected_index = max(0, self.selected_index - 1)
            self.update_highlight()

        elif key == 'right arrow':
            self.selected_index = min(len(self.image_entities) - 1, self.selected_index + 1)
            self.update_highlight()
        elif held_keys['right mouse']:
            if not hasattr(self.image_children[self.selected_index], 'texture'):
                return
            print(self.image_children[self.selected_index].texture)
            if str(self.image_entities[self.selected_index].texture) == 'bandage.png' and self.inventory.player.health < 100:
                items.bandage_player(self.inventory.player,self.image_children[self.selected_index])
            if str(self.image_entities[self.selected_index].texture) == 'medkit.png' and self.inventory.player.health < 100:
                items.medkit_player(self.inventory.player,self.image_children[self.selected_index])
            if str(self.image_entities[self.selected_index].texture) == 'potion of swiftness.png':
                items.potion_of_swiftness_player(self.inventory.player,self.image_children[self.selected_index])
            if str(self.image_entities[self.selected_index].texture) == 'potion of leaping.png':
                items.potion_of_leaping_player(self.inventory.player,self.image_children[self.selected_index])

    def update(self):
        self.update_inventory()

    def update_inventory(self):
        i = 0
        slotx = [0, 0, 0, 0]
        for j in self.image_entities:
            j.texture = 'KillCount.png'
        for item in self.inventory.children:
            if item.sloty == 0:
                slotx[round(item.slotx)] = 1
                self.image_entities[math.ceil(item.slotx)].texture = item.texture
                self.image_children[i] = item
            i += 1
            if (i == 4):
                for i in range(4):
                    if slotx[i] == 0:
                        self.image_entities[i].texture = 'KillCount.png'


# Example usage
if __name__ == '__main__':
    app = Ursina()

    # Mock-up inventory Entity
    main_inventory = Entity()
    for i in range(4):  # Populate with example items
        Entity(parent=main_inventory, texture=f'image{i + 1}.png')

    mini_inventory = MiniInv(inventory=main_inventory)
    app.run()
