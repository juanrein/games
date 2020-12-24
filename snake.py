"""
Snake game
@author Juha Reinikainen
@date 24.12.2020 
"""

import pygame as pg
import random


class Snake:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.snakeSize = 25
        self.backGroundColor = (255,255,255)
        self.snakeColor = (79, 204, 67)
        self.foodColor = (250, 237, 0)

        self.snake = [
            pg.Rect(self.x, self.y, self.snakeSize, self.snakeSize)
        ]
        self.window = None
        self.running = True
        self.speed = self.snakeSize
        self.dy = 0
        self.dx = self.speed

        self.foodSize = 30
        self.food = [
            pg.Rect(50, 50, self.foodSize, self.foodSize),
            pg.Rect(200, 80, self.foodSize, self.foodSize)
        ]

    def processInput(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                break
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pg.K_RIGHT:
                    self.dx = self.speed
                    self.dy = 0
                elif event.key == pg.K_LEFT:
                    self.dx = -self.speed
                    self.dy = 0
                elif event.key == pg.K_DOWN:
                    self.dy = self.speed
                    self.dx = 0
                elif event.key == pg.K_UP:
                    self.dy = -self.speed
                    self.dx = 0

    def initialize(self):
        pg.init()
        pg.display.set_caption("Snake game")

        self.window = pg.display.set_mode((500, 500))
        self.window.fill(self.backGroundColor)
        pg.display.flip()

    def update(self):
        """
        Moves snake one step towards its direction
        Moves food if eaten
        Grows snake if eats food
        Checks if head touches tail
        Returns:
            List[Rect] parts of the screen that need to be repainted
        """
        self.snake.append(
            pg.Rect(self.x, self.y, self.snakeSize, self.snakeSize))

        tail = self.snake.pop(0)

        updatable = [self.snake[-1], tail]

        #toroidal movement
        self.x = (self.x + self.dx) % self.window.get_width()
        self.y = (self.y + self.dy) % self.window.get_height()

        grow = False

        #eats food
        for rect in self.food:
            if self.snake[-1].colliderect(rect):
                old = rect.copy()
                x = random.randint(0, self.window.get_width() - self.snakeSize)
                y = random.randint(0, self.window.get_height() - self.snakeSize)
                rect.x = x
                rect.y = y
                updatable.append(rect)
                updatable.append(old)
                self.window.fill(self.backGroundColor, old)

                grow = True
        #tail growing
        if grow:
            self.snake.insert(0, tail)
        else:
            self.window.fill(self.backGroundColor, tail)

        # head touches tail
        head = self.snake[-1]
        for piece in self.snake[:-1]:
            if head.collidepoint(piece.centerx, piece.centery):
                self.running = False

        return updatable

    def render(self, updatable):
        #draw snake
        for rec in self.snake:
            pg.draw.rect(self.window, self.snakeColor,rec)

        #draw food
        for rect in self.food:
            rec = pg.draw.circle(self.window, self.foodColor,
                                 rect.center, rect.w // 2)
            updatable.append(rec)

        #redraw updated parts of the screen that have changed
        pg.display.update(updatable)

    def startGame(self):
        self.initialize()
        clock = pg.time.Clock()
        while self.running:
            self.processInput()
            updatable = self.update()
            self.render(updatable)

            clock.tick(10)

        # wait a second so you can see your failure >:)
        pg.time.wait(1000)
        pg.quit()


def main():
    Snake().startGame()


if __name__ == "__main__":
    main()
