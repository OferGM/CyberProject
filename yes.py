import pygame
import math

pygame.init()
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoadBalanceSimulation")

class Grid:
    def __init__(self):
        self.first = (1920/2, 1080/2)
        self.second = (1920 / 2, 1080 / 2)
        self.third = (1920 / 2, 1080 / 2)
    def get_first(self):
        return self.first
    def get_second(self):
        return self.second
    def get_third(self):
        return self.third
    def update_grid(self, ListInstance):
        xArr = ListInstance.get_xList()
        yArr = ListInstance.get_yList()
        firstIndex = math.ceil(len(xArr) * 0.25)
        secondIndex = math.ceil(len(xArr) * 0.5)
        thirdIndex = math.ceil(len(xArr) * 0.75)
        self.first = xArr[firstIndex-1]
        self.second = xArr[secondIndex-1]
        self.third = xArr[thirdIndex-1]
    def draw_grid(self):
        pygame.draw.line(WIN, (120, 120, 120), (self.first, 0), (self.first, 1080))
        pygame.draw.line(WIN, (120, 120, 120), (self.second, 0), (self.second, 1080))
        pygame.draw.line(WIN, (120, 120, 120), (self.third, 0), (self.third, 1080))
    def delete_grid(self):
        pygame.draw.line(WIN, (0, 0, 0), (self.first, 0), (self.first, 1080))
        pygame.draw.line(WIN, (0, 0, 0), (self.second, 0), (self.second, 1080))
        pygame.draw.line(WIN, (0, 0, 0), (self.third, 0), (self.third, 1080))

def color_client(pos, color):
    WIN.fill(color, (pos, (5, 5)))

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

def putSorted(arr, num):
    arr.append(num)
    arr.sort()

def printStatus(posList, first, second, third):
    inFirst = 0
    inSecond = 0
    inThird = 0
    inFourth = 0
    for pos in posList:
        posX = pos[0]
        if posX <= first:
            inFirst += 1
            color_client(pos, (0, 255, 0))
        elif posX <= second:
            inSecond += 1
            color_client(pos, (0, 0, 255))
        elif posX <= third:
            inThird += 1
            color_client(pos, (255, 0, 0))
        else:
            inFourth += 1
            color_client(pos, (255, 0, 255))
    print("in first: " + str(inFirst) + ", in second: " + str(inSecond) + ", in third: " + str(inThird) + ", inFourth: " + str(inFourth))

def main():
    run = True
    ClientPos = [0, 0]
    ListInstance = ClientList()
    GridInstance = Grid()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                ClientPos[0] = pygame.mouse.get_pos()[0]
                ClientPos[1] = pygame.mouse.get_pos()[1]

                ListInstance.update_Clients((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))

                GridInstance.update_grid(ListInstance)
                GridInstance.draw_grid()
                printStatus(ListInstance.get_Clients(), GridInstance.get_first(), GridInstance.get_second(), GridInstance.get_third())
                pygame.display.update()
                GridInstance.delete_grid()

if __name__ == "__main__":
    main()