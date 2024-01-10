import pygame
import math
from bisect import bisect_left

pygame.init()
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoadBalanceSimulation")


class SegmentTree:
    def __init__(self, max_size):
        self.size = 1
        while self.size < max_size:
            self.size *= 2
        self.tree = [0] * (2 * self.size)

    def add(self, index, value):
        index += self.size
        self.tree[index] += value
        while index > 1:
            index //= 2
            self.tree[index] = self.tree[2 * index] + self.tree[2 * index + 1]

    def sum(self, left, right):
        left += self.size
        right += self.size
        total_sum = 0
        while left < right:
            if left % 2 == 1:
                total_sum += self.tree[left]
                left += 1
            if right % 2 == 1:
                right -= 1
                total_sum += self.tree[right]
            left //= 2
            right //= 2
        return total_sum

class Grid:
    def __init__(self):
        self.first = WIDTH / 2
        self.second = WIDTH / 2
        self.third = WIDTH / 2

    def update_grid(self, manager):
        x_coords = sorted(manager.client_dict.values())
        first_index = math.ceil(len(x_coords) * 0.25)
        second_index = math.ceil(len(x_coords) * 0.5)
        third_index = math.ceil(len(x_coords) * 0.75)
        self.first = x_coords[first_index - 1][0]
        self.second = x_coords[second_index - 1][0]
        self.third = x_coords[third_index - 1][0]

    def draw_grid(self):
        pygame.draw.line(WIN, (120, 120, 120), (self.first, 0), (self.first, HEIGHT))
        pygame.draw.line(WIN, (120, 120, 120), (self.second, 0), (self.second, HEIGHT))
        pygame.draw.line(WIN, (120, 120, 120), (self.third, 0), (self.third, HEIGHT))

    def delete_grid(self):
        pygame.draw.line(WIN, (0, 0, 0), (self.first, 0), (self.first, HEIGHT))
        pygame.draw.line(WIN, (0, 0, 0), (self.second, 0), (self.second, HEIGHT))
        pygame.draw.line(WIN, (0, 0, 0), (self.third, 0), (self.third, HEIGHT))


def color_client(pos, color):
    WIN.fill(color, (pos, (5, 5)))


class ClientManager:
    def __init__(self):
        self.client_dict = {}
        self.segment_tree = SegmentTree(100000)  # Adjust the size based on maximum possible clients

    def add_client(self, client_id, x, y):
        self.client_dict[client_id] = (x, y)
        self.segment_tree.add(x, 1)

    def remove_client(self, client_id):
        x_coord, _ = self.client_dict.pop(client_id)
        self.segment_tree.add(x_coord, -1)

    def update_client_position(self, client_id, new_x, new_y):
        old_x, old_y = self.client_dict[client_id]
        self.segment_tree.add(old_x, -1)
        self.client_dict[client_id] = (new_x, new_y)
        self.segment_tree.add(new_x, 1)

    def get_client_rectangle(self, client_id):
        x_coord, _ = self.client_dict[client_id]
        total_clients = self.segment_tree.sum(0, 1000)  # Adjust the range based on maximum possible x-coordinates
        index = bisect_left(self.segment_tree.tree, x_coord)
        segment = index * 4 // total_clients
        return segment  # Returns the segment (0-3) the client belongs to

def print_status(manager, grid):
    pos_list = manager.client_dict.values()

    in_first, in_second, in_third, in_fourth = [], [], [], []

    for pos in pos_list:
        if pos[0] <= grid.first:
            in_first.append(pos)
            color_client(pos, (0, 255, 0))
        elif pos[0] <= grid.second:
            in_second.append(pos)
            color_client(pos, (0, 0, 255))
        elif pos[0] <= grid.third:
            in_third.append(pos)
            color_client(pos, (255, 0, 0))
        else:
            in_fourth.append(pos)
            color_client(pos, (255, 0, 255))

    print(
        "in first: " + str(len(in_first))
        + ", in second: " + str(len(in_second))
        + ", in third: " + str(len(in_third))
        + ", in fourth: " + str(len(in_fourth))
    )

    pygame.display.update()

def main():
    run = True
    manager = ClientManager()
    grid = Grid()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                manager.add_client(len(manager.client_dict), *pygame.mouse.get_pos())

                WIN.fill((0, 0, 0))
                grid.update_grid(manager)
                grid.draw_grid()
                print_status(manager, grid)

                pygame.display.update()
                grid.delete_grid()

if __name__ == "__main__":
    main()
