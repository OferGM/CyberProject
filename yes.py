import pygame
from pyskiplist import SkipList

pygame.init()
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoadBalanceSimulation")


class ClientList:
    def __init__(self):
        self.client_dict = {}
        self.sl = SkipList()

    def get_dict(self):
        return self.client_dict

    def get_sl(self):
        return self.sl

    def insert_client(self, client_x, client_id):
        self.client_dict[client_id] = client_x
        self.sl.insert(client_x, client_id)

    def remove_client(self, client_id):
        client_x = self.client_dict.pop(client_id)
        self.sl.remove(client_x)

    def update_client(self, new_x, client_id):
        self.remove_client(client_id)
        self.insert_client(new_x, client_id)


def print_status(sl, _dict):
    in_first = 0
    in_second = 0
    in_third = 0
    in_fourth = 0
    length = len(_dict)

    for client_x in _dict.values():
        ind = sl.index(client_x)
        if ind <= length / 4:
            in_first += 1
        elif ind <= length / 4 * 2:
            in_second += 1
        elif ind <= length / 4 * 3:
            in_third += 1
        else:
            in_fourth += 1

    print("in first: {}, in second: {}, in third: {}, in fourth: {}".format(in_first, in_second, in_third, in_fourth))


def main():
    run = True
    client = [0, 0]
    list_instance = ClientList()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                client[0] = pygame.mouse.get_pos()[0]
                list_instance.insert_client(client_x=client[0], client_id=client[1])
                client[1] += 1  # increment client ID

                print_status(list_instance.get_sl(), list_instance.get_dict())
                pygame.display.update()


if __name__ == "__main__":
    main()
