import socket
import LoginPage
import LobbyUI

my_socket = socket.socket()
my_socket.connect(("127.0.0.1", 6969))
LoginPage.build_page(my_socket)
data = my_socket.recv(1024).decode()
print(data)
ak, m4, awp, mp5, mk, bnd, sp, lp, cash = data.split("&")
LobbyUI.main(my_socket, int(ak), int(m4), int(awp), int(mp5), int(mk), int(bnd), int(sp), int(lp), int(cash))

my_socket.close()