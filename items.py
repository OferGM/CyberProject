from ursina import *
from ursina.prefabs.health_bar import HealthBar

def bandage_player(player,item):
    player.health = player.health + 10
    print("Player healed by 10 HP")
    print (player.health)
    destroy(item)

def medkit_player(self):
    player.health=100
