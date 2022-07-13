from turtle import left
import pygame
import time
import math
from tools import blitRotate

MAP = pygame.image.load("img/Karte.png")
BORDER = pygame.image.load("img/Mauer.png")
ROBO = pygame.image.load("img/Robot.png")

WIDTH, HEIGHT = MAP.get_width(), MAP.get_height()
Window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RoboArena")

FPS = 60


class Robot:  # Abstract class for player and ai robots

    # initiator
    def __init__(self, maxSpeed, rotSpeed):
        self.img = self.IMG
        self.maxSpeed = maxSpeed
        self.speed = 0
        self.rotSpeed = rotSpeed
        self.angle = 0
        self.x, self.y = self.STARTPOS
        self.acceleration = 0.1

    # if either left or right is true will adjust the angle
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotSpeed
        elif right:
            self.angle -= self.rotSpeed

    # draws the robot on the field
    def draw(self, win):
        blitRotate(win, self.img, (self.x, self.y), self.angle)

    # robot takes the smaller or speed and maxSpeed and will move forward
    def moveForward(self):
        self.speed = min(self.speed + self.acceleration, self.maxSpeed)
        self.move()

    # movement vector
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed

        self.y -= vertical
        self.x -= horizontal

    # reduces the speed only active if w is not pressed
    def slowDown(self):
        self.speed = max(self.speed - self. acceleration / 2, 0)
        self.move()


class PlayerRobo(Robot):

    IMG = ROBO
    STARTPOS = (500, 500)


def draw(win, images):
    for img, pos in images:
        Window.blit(img, pos)
        player_robo.draw(win)
        pygame.display.update()

run = True
clock = pygame.time.Clock()
images = [(MAP, (0, 0)), (BORDER, (0, 0))]
player_robo = PlayerRobo(4, 4)

    # main loop
while run:
    clock.tick(FPS)

    draw(Window, images)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()
    moved = False

    # key events
    if keys[pygame.K_a]:
        player_robo.rotate(left=True)
    if keys[pygame.K_d]:
        player_robo.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_robo.moveForward()
    if not moved:
        player_robo.slowDown()

pygame.quit()
