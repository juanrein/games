"""
Multiple robots moving in parallel
@author Juha Reinikainen
@date 10.2.2021
"""

import os
import pygame as pg
from threading import Semaphore, Thread
import concurrent.futures
from time import sleep

class House:
    """
    # wall
    " " free space
    R robot
    """
    def __init__(self):
        fn = os.path.join(os.path.split(os.path.abspath(__file__))[0], "house.txt")
        self.grid = []
        with open(fn) as f:
            for line in f:
                self.grid.append(list(line[0:len(line)-1]))

    def hw(self):
        h = len(self.grid)
        w = len(self.grid[0])
        return h,w

    def addRobot(self, i,j):
        self.grid[i][j] = "R"

    def move(self, i,j, i2, j2):
        if i == i2 and j == j2:
            raise ValueError("not moving")
        if self.grid[i2][j2] == "R":
            raise ValueError("robot already in destination location")
        self.grid[i2][j2] = "R"
        self.grid[i][j] = " "

    def __str__(self):
        return "\n".join(map(repr, self.grid))


class Service:
    def __init__(self, units):
        self.sem = Semaphore(units)
        self.running = True

    def stop(self):
        self.running = False

class Drawing(Thread):
    def __init__(self, service: Service, grid, blockSize, window, robots):
        Thread.__init__(self) 
        self.grid = grid
        self.blockSize = blockSize
        self.window = window
        self.service = service

        self.robots = robots
        
    def run(self):
        while True:
            self.service.sem.acquire()
            if not self.service.running:
                self.service.sem.release()
                break
            self.draw()
            self.service.sem.release()
            sleep(0.05)
        print("stopped drawing")

    def draw(self):
        self.window.fill((255,255,255))

        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                rect = (j*self.blockSize[0], i*self.blockSize[1], self.blockSize[0], self.blockSize[1])

                c = self.grid[i][j]
                if c == " ":
                    visited = False
                    for robot in self.robots:
                        if robot.visited[i][j] > 0:
                            times = robot.visited[i][j] + 1
                            color = color = (255 / times, 255 / times, 255 / times)
                            visited = True
                            break
                        if not visited:
                            color = (255,255,255)

                elif c == "#":
                    color = (0,0,0)
                elif c == "R":
                    color = (0,0,255)
                else:
                    raise ValueError("what")

                pg.draw.rect(self.window, color, rect)   

        pg.display.flip()


class Robot(Thread):
    def __init__(self, x,y, h, w, service: Service, house: House):
        Thread.__init__(self) 
        self.x = x
        self.y = y

        self.house = house
        self.visited = [[0 for _ in range(w)] for _ in range(h)]
        self.service = service

    def run(self):
        while True:
            self.service.sem.acquire()
            if not self.service.running:
                self.service.sem.release()
                break
            self.move()
            self.service.sem.release()
            sleep(0.05)
        print("stopped robot")

    def move(self):
        self.visited[self.y][self.x] += 1
        moves = []
        for x,y in [(self.x-1, self.y), (self.x+1, self.y), (self.x, self.y-1), (self.x, self.y+1)]:
            if x < 0 or y < 0 or x >= len(self.house.grid[0]) or y >= len(self.house.grid):
                continue
            if self.house.grid[y][x] == "#":
                continue
            if self.house.grid[y][x] == "R":
                continue
            moves.append((x,y,self.visited[y][x]))

        moves = sorted(moves, key = lambda x: x[2])
        if len(moves) > 0:
            x,y,_ = moves[0]
            self.house.move(self.y, self.x, y, x)
            self.x = x
            self.y = y


        
class Sim:
    def __init__(self):
        self.running = True
        self.WINDOW_SIZE = (1200, 500)
        self.BACKGROUND_COLOR = (255,255,255)
        self.window = None

        self.house = None
        self.blockSize = None

        self.service = Service(1)
        self.robots = []

    def initialize(self):
        pg.init()
        self.house = House()
        h,w = self.house.hw()
        self.blockSize = (self.WINDOW_SIZE[0] / w, self.WINDOW_SIZE[1] / h)

        self.window = pg.display.set_mode(self.WINDOW_SIZE)

        self.robots = [
            Robot(1,1, h, w, self.service, self.house),
            Robot(40, 9, h, w, self.service, self.house),
            Robot(24, 6, h, w, self.service, self.house)
        ]
        self.drawing = Drawing(self.service, self.house.grid, self.blockSize, self.window, self.robots)

        self.house.addRobot(1,1)
        self.house.addRobot(9, 40)
        self.house.addRobot(6, 24)

    def start(self):
        self.initialize()

        for robot in self.robots:
            robot.start()

        self.drawing.start()

        def process():
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    self.service.stop()
                    self.drawing.join()
                    for robot in self.robots:
                        robot.join()
                    return False
            return True

        while True:
            if not process():
                break
            
        pg.quit()

def main():
    Sim().start()


if __name__ == "__main__":
    main()
