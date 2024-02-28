from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import socket

app = Ursina()

ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))

player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')
player2 = Entity(model='cube', z=-5, color=color.pink, origin_y=-.5, speed=8, collider='box')


DESTIP = "127.0.0.1"
DESTPORT = 5555
CLIENT_ID = "1"
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp type socket


def updatescreen(data):
    data = data.split()
    ID = data[0]
    z = data[1]
    x = data[2]
    if ID != CLIENT_ID:
        player2.x = float(x) + 5
        player2.z = float(z)


def input(key) :
    if key == 'escape' :
        application.quit()

    if held_keys['w'] or held_keys['d'] or held_keys['s'] or held_keys['a'] :
        data = CLIENT_ID + " " + str(player.getZ()) + " " + str(player.getX())
        my_socket.sendto(data.encode(), (DESTIP, DESTPORT))  # sends player pos to server

    (reply, remote_address) = my_socket.recvfrom(1024)
    updatescreen(reply.decode())

app.run()