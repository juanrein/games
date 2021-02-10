"""
Cannon shooting cannonballs
"""

import pygame as pg
import random
import os

class House:
    def __init__(self):
        fn = os.path.join(os.path.split(os.path.abspath(__file__))[0], "house.txt")
        self.grid = []
        with open(fn) as f:
            for line in f:
                self.grid.append(line[0:len(line)])

    def hw(self):
        h = len(self.grid)
        w = len(self.grid[0])
        return h,w

    def __str__(self):
        return "\n".join(map(str, self.grid))

class Robot:
    def __init__(self, x,y, h, w):
        self.x = x
        self.y = y

        self.visited = [[0 for _ in range(w)] for _ in range(h)]

    def move(self, grid):
        self.visited[self.y][self.x] += 1
        moves = []
        for x,y in [(self.x-1, self.y), (self.x+1, self.y), (self.x, self.y-1), (self.x, self.y+1)]:
            if x == self.x and y == self.y:
                continue
            if x < 0 or y < 0 or x >= len(grid[0]) or y >= len(grid):
                continue
            if grid[y][x] == "#":
                continue
            moves.append((x,y,self.visited[y][x]))

        moves = sorted(moves, key = lambda x: x[2])
        x,y,score = moves[0]
        self.x = x
        self.y = y


class Sim:
    def __init__(self):
        self.running = True
        self.WINDOW_SIZE = (1200, 500)
        self.BACKGROUND_COLOR = (255,255,255)
        self.window = None

        self.robot = None
        self.house = None

    def initialize(self):
        pg.init()
        self.house = House()
        h,w = self.house.hw()
        self.blockSize = (self.WINDOW_SIZE[0] / w, self.WINDOW_SIZE[1] / h)

        self.window = pg.display.set_mode(self.WINDOW_SIZE)
        self.robot = Robot(1,1, h, w)

    def processInput(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                break

    def start(self):
        self.initialize()
        clock = pg.time.Clock()

        while self.running:
            clock.tick(45)
            self.processInput()

            self.window.fill((255,255,255))

            for i in range(len(self.house.grid)):
                for j in range(len(self.house.grid[0])):

                    rect = (j*self.blockSize[0], i*self.blockSize[1], self.blockSize[0], self.blockSize[1])

                    if self.robot.x == j and self.robot.y == i:
                        pg.draw.rect(self.window, (0,0,255), rect)
                    else:
                        if self.house.grid[i][j] == " ":
                            if self.robot.visited[i][j] > 0:
                                times = self.robot.visited[i][j] + 1
                                if times > 255:
                                    color = (255,255,255)
                                else:
                                    color = (255 / times, 255 / times, 255 / times)
                            else:
                                color = (255,255,255)
                        else:
                            color = (0,0,0)
                        pg.draw.rect(self.window, color, rect)

            self.robot.move(self.house.grid)
            pg.display.flip()

        pg.quit()

def main():
    Sim().start()


if __name__ == "__main__":
    main()
