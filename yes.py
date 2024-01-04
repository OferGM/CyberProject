import pygame
import math

pygame.init()
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoadBalanceSimulation")

class Grid:
    def __init__(self):
        self.center = (1920/2, 1080/2)
    def get_center(self):
        return self.center
    def update_center(self, ListInstance):
        xArr = ListInstance.get_xList()
        yArr = ListInstance.get_yList()
        self.center = (xArr[math.floor(len(xArr)/2)], yArr[math.floor(len(yArr)/2)])
    def draw_grid(self):
        pygame.draw.line(WIN, (120, 120, 120), (0, self.center[1]), (1920, self.center[1]))
        pygame.draw.line(WIN, (120, 120, 120), (self.center[0], 0), (self.center[0], 1080))
    def delete_grid(self):
        pygame.draw.line(WIN, (0, 0, 0), (0, self.center[1]), (1920, self.center[1]))
        pygame.draw.line(WIN, (0, 0, 0), (self.center[0], 0), (self.center[0], 1080))

def color_client(pos, color):
    WIN.fill(color, (pos, (5, 5)))

class Client:
    def __init__(self):
        self.x = 0
        self.y = 0
    def get_position(self):
        return self.x, self.y
    def draw_client(self):
        WIN.fill((255, 255, 255), ((self.x, self.y), (5, 5)))

class ClientList:
    def __init__(self):
        self.Clients = []
        self.xList = []
        self.yList = []
    def get_Clients(self):
        return self.Clients
    def get_xList(self):
        return self.xList
    def get_yList(self):
        return self.yList
    def update_Clients(self, clientPos):
        self.Clients.append(clientPos)
        putSorted(self.xList, clientPos[0])
        putSorted(self.yList, clientPos[1])

def putSorted(arr, num):        #inserts num in sorted arr
    arr.append(num)
    arr.sort()

def printStatus(posList, center):
    TopLeft = 0
    TopRight = 0
    BotLeft = 0
    BotRight = 0
    for pos in posList:
        if pos[0] <= center[0] and pos[1] <= center[1]:
            TopLeft += 1
            color_client(pos, (0, 255, 0))
        if pos[0] > center[0] and pos[1] > center[1]:
            BotRight += 1
            color_client(pos, (0, 0, 255))
        if pos[0] <= center[0] and pos[1] > center[1]:
            BotLeft += 1
            color_client(pos, (255, 0, 0))
        if pos[0] > center[0] and pos[1] <= center[1]:
            TopRight += 1
            color_client(pos, (255, 0, 255))
    print("TopLeft: " + str(TopLeft) + ", TopRight: " + str(TopRight) + ", BotLeft: " + str(BotLeft) + ", BotRight: " + str(BotRight))

def main():
    run = True
    ClientInstance = Client()
    ListInstance = ClientList()
    GridInstance = Grid()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                ClientInstance.x = pygame.mouse.get_pos()[0]
                ClientInstance.y = pygame.mouse.get_pos()[1]

                ClientInstance.draw_client()
                ListInstance.update_Clients(ClientInstance.get_position())

                GridInstance.delete_grid()
                GridInstance.update_center(ListInstance)
                GridInstance.draw_grid()
                printStatus(ListInstance.get_Clients(), GridInstance.get_center())
                pygame.display.update()


if __name__ == "__main__":
    main()