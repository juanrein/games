"""
Snake game with autopilot option
@author Juha Reinikainen
@date 24.12.2020 
"""

import pygame as pg
import random
import math


class Snake:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.snakeSize = 25
        self.backGroundColor = (255, 255, 255)
        self.snakeColor = (79, 204, 67)
        self.foodColor = (250, 237, 0)
        self.controlBoxColor = (0,0,0)
        self.autopilotButtonColor = (71, 71, 71)
        self.controlBoxTextColor = (255,255,255)
        self.controlBoxHeight = 50
        self.screenW = 500
        self.screenH = 500

        self.autopilot = False

        self.snake = [
            pg.Rect(self.x, self.y, self.snakeSize, self.snakeSize)
        ]
        self.window = None
        self.running = True
        self.speed = self.snakeSize
        self.dy = 0
        self.dx = self.speed

        self.foodSize = 30
        self.food = pg.Rect(50, 50, self.foodSize, self.foodSize)

    def processInput(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                break
            elif not self.autopilot and event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
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
            elif event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                if self.autopilotButton.collidepoint(x, y):
                    if self.autopilot:
                        self.autopilot = False
                    else:
                        self.autopilot = True

    def initialize(self):
        pg.init()
        pg.display.set_caption("Snake game")

        self.window = pg.display.set_mode((self.screenW, self.screenH + self.controlBoxHeight))
        pg.draw.rect(self.window, self.backGroundColor, (0, 0, self.screenW, self.screenH))

        font = pg.font.SysFont(None, 24)
        img = font.render("Autopilot", True, self.controlBoxTextColor)

        controlBoxRec = (0, self.screenH, self.screenW, self.controlBoxHeight)
        pg.draw.rect(self.window, self.controlBoxColor, controlBoxRec)
        self.autopilotButton = pg.draw.rect(
            self.window, self.autopilotButtonColor, (0, self.screenH, img.get_width(), self.controlBoxHeight))
        
        self.window.blit(img, (0, self.screenH + self.controlBoxHeight // 2 - 12))
        
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

        # toroidal movement
        self.x = (self.x + self.dx) % self.screenW
        self.y = (self.y + self.dy) % self.screenH

        grow = False

        # eats food
        if self.snake[-1].colliderect(self.food):
            old = self.food.copy()
            x = random.randint(0, self.screenW - self.snakeSize)
            y = random.randint( 0, self.screenH - self.snakeSize)
            self.food.x = x
            self.food.y = y
            updatable.append(self.food)
            updatable.append(old)
            self.window.fill(self.backGroundColor, old)

            grow = True
        # tail growing
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

    def move(self):
        """
        More towards food if possible
        """
        dest_x = self.food.x
        dest_y = self.food.y

        def eatsOwnTail(x, y):
            futureHead = pg.Rect(x, y, self.snakeSize, self.snakeSize)
            for rect in self.snake:
                if futureHead.collidepoint(rect.centerx, rect.centery):
                    return True

            return False

        def getScore(x, y):
            if eatsOwnTail(x, y):
                return math.inf
            score = (dest_x - x)**2 + (dest_y - y)**2
            return score

        possible_moves = [(-self.speed, 0), (self.speed, 0),
                          (0, self.speed), (0, -self.speed)]
        scores = [getScore(self.x + dx, self.y + dy)
                  for dx, dy in possible_moves]

        lowestScore = scores[0]
        bestMove = possible_moves[0]

        for i in range(1, len(scores)):
            if scores[i] < lowestScore:
                lowestScore = scores[i]
                bestMove = possible_moves[i]

        self.dx = bestMove[0]
        self.dy = bestMove[1]

    def render(self, updatable):
        # draw snake
        for rec in self.snake:
            pg.draw.rect(self.window, self.snakeColor, rec)

        # draw food
        rec = pg.draw.circle(self.window, self.foodColor,
                                self.food.center, self.food.w // 2)
        updatable.append(rec)

        # redraw updated parts of the screen that have changed
        pg.display.update(updatable)

    def startGame(self):
        self.initialize()
        clock = pg.time.Clock()
        while self.running:
            if self.autopilot:
                self.move()

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
