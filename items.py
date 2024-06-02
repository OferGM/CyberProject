from ursina import *
from ursina.prefabs.health_bar import HealthBar

def bandage_player(player,item):
    player.health = player.health + 10
    destroy(item)

def medkit_player(player,item):
    player.health = 100
    destroy(item)

def potion_of_leaping_player(player,item):
   player.jump_height=5.0
   destroy(item)
   invoke(reset_jump,player,delay=15)

def potion_of_swiftness_player(player,item):
    player.speed=30
    destroy(item)
    invoke(reset_speed, player, delay=15)




def reset_speed (player):
    player.speed=8

def reset_jump (player):
    player.jump_height=1.0
