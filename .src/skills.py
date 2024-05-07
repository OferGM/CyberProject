from ursina import *
from ursina.prefabs.health_bar import HealthBar

class SkillDisplay(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements = []  # List to keep track of created elements
        self.create_skills()

    def create_skills(self):
        # text1 = Text(text='Hello', origin=(0, 0), position=(-.325, -0.397), scale=.5, color=color.white)
        # text2 = Text(text='Hello', origin=(0, 0), position=(-.325, -0.367), scale=.5, color=color.white)
        # text3 = Text(text='Hello', origin=(0, 0), position=(-.325, -0.337), scale=.5, color=color.white)
        #
        # self.elements.extend([text1, text2, text3])
        #
        # health_bar_1 = HealthBar(bar_color=color.red, roundness=.5, value=50, position=(-0.85, -0.38), max_value=10000, show_text=False)
        # health_bar_2 = HealthBar(bar_color=color.green, roundness=.5, value=50, position=(-0.85, -0.35))
        # health_bar_3 = HealthBar(bar_color=color.cyan, roundness=.5, value=50, position=(-0.85, -0.32))
        #
        # self.elements.extend([health_bar_1, health_bar_2, health_bar_3])
        #
        # icon_path = 'KillCount.png'  # Path to your 'killshot.png' image

        icon_1 = Entity(parent=camera.ui, model='quad', texture='speed.png', position=(-0.82, 0.1), scale=0.10)
        icon_2 = Entity(parent=camera.ui, model='quad', texture='strength.png', position=(-0.82, 0), scale=0.10)
        icon_3 = Entity(parent=camera.ui, model='quad', texture='machine-gun.png', position=(-0.82, -0.1), scale=0.10)
        self.elements.extend([icon_1, icon_2, icon_3])

    def close_skills(self):
        for element in self.elements:
            element.enabled = False  # Disable elements instead of destroying

    def show_skills(self):
        for element in self.elements:
            element.enabled = True  # Re-enable elements to show them

    def changeToRed(self,skill):
        print("CHANGED TO RED")
        if skill == 'speed':
            self.elements[0].scale = 0
        if skill == 'strength':
            self.elements[1].scale = 0
        if skill == 'cooldown':
            self.elements[2].scale = 0


    def changeToWhite(self,skill):
        if skill == 'speed':
            self.elements[0].scale = 0.10
        if skill == 'strength':
            self.elements[1].scale = 0.10
        if skill == 'cooldown':
            self.elements[2].scale = 0.10