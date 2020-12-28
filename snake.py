"""
Snake game with autopilot option
@author Juha Reinikainen
@date 24.12.2020
"""

import random
import math
from typing import Tuple
import pygame as pg


class Constants:
    SNAKE_SIZE = 25
    SPEED = 25
    FOOD_SIZE = 25

    BACKGROUND_COLOR = (255, 255, 255)
    SNAKE_COLOR = (79, 204, 67)
    FOOD_COLOR = (250, 237, 0)
    CONTROL_BOX_COLOR = (0, 0, 0)
    AUTOPILOT_BUTTON_COLOR = (71, 71, 71)
    CONTROLBOX_TEXT_COLOR = (255, 255, 255)
    CONTROLBOX_HEIGHT = 50
    SCREEN_W = 500
    SCREEN_H = 500

    STEPS_TO_TAKE = 4


class State:
    def __init__(self, x, y, dx, dy, running, autopilot, snake, food):
        self.x = x
        self.y = y
        self.dy = dx
        self.dx = dy
        self.running = running
        self.autopilot = autopilot
        self.snake = snake
        self.food = food

    def copy(self):
        return State(
            self.x, self.y,
            self.dx, self.dy,
            self.running, self.autopilot,
            [rect.copy() for rect in self.snake],
            self.food.copy()
        )

    def update(self, window: pg.Surface, virtual: bool):
        """
        Moves snake one step towards its direction
        Moves food if eaten
        Grows snake if eats food
        Checks if head touches tail
        Params:
            window: Surface
            virtual: whether to update window
        Returns:
            (List[Rect], grow) parts of the screen that need to be repainted
            and boolean flag indicating if snake has grown
        """
        self.x = (self.x + self.dx) % Constants.SCREEN_W
        self.y = (self.y + self.dy) % Constants.SCREEN_H

        self.snake.append(
            pg.Rect(self.x, self.y, Constants.SNAKE_SIZE, Constants.SNAKE_SIZE))

        tail = self.snake.pop(0)

        updatable = [self.snake[-1], tail]

        grow = False

        # eats food
        if self.snake[-1].colliderect(self.food):
            old = self.food.copy()
            #x = random.randint(0, Constants.SCREEN_W - Constants.FOOD_SIZE)
            #y = random.randint(0, Constants.SCREEN_H - Constants.FOOD_SIZE)
            pos = self.generatePosition()
            if not pos:
                self.running = False
            self.food.x = pos[0]
            self.food.y = pos[1]
            updatable.append(self.food)
            updatable.append(old)
            if not virtual:
                window.fill(Constants.BACKGROUND_COLOR, old)

            grow = True
        # tail growing
        if grow:
            self.snake.insert(0, tail)
        else:
            if not virtual:
                window.fill(Constants.BACKGROUND_COLOR, tail)

        # head touches tail
        head = self.snake[-1]
        for piece in self.snake[:-1]:
            if head.collidepoint(piece.centerx, piece.centery):
                self.running = False

        return updatable, grow

    def handleEvent(self, event):
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            self.running = False
            return
        elif not self.autopilot and event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                self.dx = Constants.SPEED
                self.dy = 0
            elif event.key == pg.K_LEFT:
                self.dx = -Constants.SPEED
                self.dy = 0
            elif event.key == pg.K_DOWN:
                self.dy = Constants.SPEED
                self.dx = 0
            elif event.key == pg.K_UP:
                self.dy = -Constants.SPEED
                self.dx = 0

    def generatePosition(self):
        """
        Generate new position for the food that doesn't have snake in it
        Returns:
            (x,y) | None if no free cells left
        """
        w, h = Constants.SCREEN_W, Constants.SCREEN_H
        columns, rows = w // Constants.FOOD_SIZE, h // Constants.FOOD_SIZE
        freeCells = []
        for row in range(rows):
            for col in range(columns):
                x, y = row * Constants.FOOD_SIZE, col * Constants.FOOD_SIZE
                cell = pg.Rect(x, y, Constants.FOOD_SIZE, Constants.FOOD_SIZE)
                if cell.collidelist(self.snake) == -1:
                    freeCells.append(cell)

        if len(freeCells) == 0:
            return None

        return random.choice(freeCells)


class Snake:
    def __init__(self):
        self.state = State(
            100, 100, 0, Constants.SPEED, True, False,
            [pg.Rect(100, 100, Constants.SNAKE_SIZE, Constants.SNAKE_SIZE)],
            pg.Rect(50, 50, Constants.FOOD_SIZE, Constants.FOOD_SIZE)
        )
        self.window = None
        self.autopilotButton = None

    def processInput(self):
        for event in pg.event.get():
            self.state.handleEvent(event)

            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                if self.autopilotButton.collidepoint(x, y):
                    if self.state.autopilot:
                        self.state.autopilot = False
                    else:
                        self.state.autopilot = True

    def initialize(self):
        pg.init()
        pg.display.set_caption("Snake game")

        self.window = pg.display.set_mode(
            (Constants.SCREEN_W, Constants.SCREEN_H + Constants.CONTROLBOX_HEIGHT))
        pg.draw.rect(self.window, Constants.BACKGROUND_COLOR,
                     (0, 0, Constants.SCREEN_W, Constants.SCREEN_H))

        font = pg.font.SysFont(None, 24)
        img = font.render("Autopilot", True, Constants.CONTROLBOX_TEXT_COLOR)

        controlBoxRec = (0, Constants.SCREEN_H,
                         Constants.SCREEN_W, Constants.CONTROLBOX_HEIGHT)
        pg.draw.rect(self.window, Constants.CONTROL_BOX_COLOR, controlBoxRec)
        self.autopilotButton = pg.draw.rect(
            self.window, Constants.AUTOPILOT_BUTTON_COLOR,
                (0, Constants.SCREEN_H, img.get_width(), Constants.CONTROLBOX_HEIGHT))

        self.window.blit(
            img, (0, Constants.SCREEN_H + Constants.CONTROLBOX_HEIGHT // 2 - 12))

        pg.display.flip()

    def eatsOwnTail(self, nextState):
        head = nextState.snake[-1]
        for piece in nextState.snake[:-1]:
            if piece.colliderect(head):
                return True
        return False

    def getScore(self, nextState):
        score = (nextState.food.x - nextState.x)**2 + \
            (nextState.food.y - nextState.y)**2
        return score

    def getBest(self, scores):
        best = scores[0]
        for score, move, steps in scores:
            if score < best[0]:
                best = (score, move, steps)
            elif score == best[0]:
                if steps < best[2]:
                    best = (score, move, steps)

        return best

    def nextMove(self, state: State, stepsTaken: int, maxSteps: int) -> \
        Tuple[int, Tuple[int, int], int]:
        """
        Deside next move based on calculating outcome after certain number of steps
        - if food is been eaten stops as it's not possible to predict the next location of
        randomly relocated food
        - stops stepping if hits own tail
        Returns:
            (score, (dx,dy), stepsTaken)
        """
        possible_moves = ((-Constants.SPEED, 0), (Constants.SPEED, 0),
                          (0, Constants.SPEED), (0, -Constants.SPEED))

        scores = []
        for dx, dy in possible_moves:
            move = (dx, dy)
            nextState = state.copy()
            nextState.dx = dx
            nextState.dy = dy
            _, grow = nextState.update(self.window, True)

            if self.eatsOwnTail(nextState):
                scores.append((math.inf, move, stepsTaken))
            elif grow:
                scores.append((0, move, stepsTaken))
            elif stepsTaken >= maxSteps:
                scores.append((self.getScore(nextState), move, stepsTaken))
            else:
                score, _, steps = self.nextMove(
                    nextState, stepsTaken+1, maxSteps)
                scores.append((score, move, steps))

        return self.getBest(scores)

    def render(self, updatable):
        # draw snake
        for rec in self.state.snake:
            pg.draw.rect(self.window, Constants.SNAKE_COLOR, rec)

        # draw food
        rec = pg.draw.circle(self.window, Constants.FOOD_COLOR,
                             self.state.food.center, self.state.food.w // 2)
        updatable.append(rec)

        # redraw updated parts of the screen that have changed
        pg.display.update(updatable)

    def startGame(self):
        self.initialize()
        clock = pg.time.Clock()
        while self.state.running:
            if self.state.autopilot:
                (_, (dx, dy), _) = self.nextMove(
                    self.state, 0, Constants.STEPS_TO_TAKE)
                self.state.dx = dx
                self.state.dy = dy

            self.processInput()
            updatable, _ = self.state.update(self.window, False)
            self.render(updatable)
            clock.tick(10)

        pg.time.wait(1000)
        pg.quit()


def main():
    Snake().startGame()


if __name__ == "__main__":
    main()
