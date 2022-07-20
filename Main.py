import pygame
import math
import csv
from tools import blitRotate

MAP = pygame.image.load("img/Karte.png")
BORDER = pygame.image.load("img/Mauer.png")
ROBO = pygame.image.load("img/Robot.png")

GRASS = pygame.image.load("img/Grass-Tiles.png")
ELECTRIC = pygame.image.load("img/Electric-Tiles.png")
SAND = pygame.image.load("img/Sand-Tiles.png")
WALL = pygame.image.load("img/Wall-Tiles.png")
WATER = pygame.image.load("img/Water-Tiles.png")

WIDTH, HEIGHT = MAP.get_width(), MAP.get_height()
Window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RoboArena")

# Surfaces for masks
Wall = pygame.Surface((WIDTH, HEIGHT))
Wall.set_colorkey((0, 0, 0))
Sand = pygame.Surface((WIDTH, HEIGHT))
Sand.set_colorkey((0, 0, 0))
Water = pygame.Surface((WIDTH, HEIGHT))
Water.set_colorkey((0, 0, 0))
Electric = pygame.Surface((WIDTH, HEIGHT))
Electric.set_colorkey((0, 0, 0))

FPS = 60
TILECOUNT = 40
TILEPIX = 25
STUNTICKS = 90
TENACITY = 240
run = True


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
        self.stun = STUNTICKS
        self.tenacity = TENACITY

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
        if self.stun == STUNTICKS:
            self.speed = min(self.speed + self.acceleration, self.maxSpeed)
            self.move()

    # robot takes the smaller or speed and maxSpeed and will move backward
    def moveBackward(self):
        if self.stun == STUNTICKS:
            self.speed = max(self.speed - self.acceleration, -self.maxSpeed/2)
            self.move()

    # movement vector
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        robo_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(robo_mask, offset)
        return poi

    def inTile(self, mask, x=0, y=0):
        robo_mask = pygame.mask.from_surface(self.img)
        bits_robo_mask = robo_mask.count()
        offset = (int(self.x - x), int(self.y - y))
        if bits_robo_mask == mask.overlap_area(robo_mask, offset):
            return True

    def slowDown(self):
        self.speed = max(self.speed - self.acceleration, 0)
        self.move()

    def bounce(self):
        self.speed = -self.speed
        self.move()

    def slowed(self):
        self.speed = self.speed/1.6
        self.move()

    def stunned(self):
        if self.tenacity == TENACITY:
            self.tenacity = 0
            self.stun = 0
            print("stun")
            self.move()


class TileMap():
    def __init__(self):
        self.background = []
        self.loadbackground()

    def drawtiles(self, win):
        for i in range(TILECOUNT):
            for j in range(TILECOUNT):
                if self.background[i][j] == 1:
                    win.blit(WALL, (j * TILEPIX, i * TILEPIX))
                elif self.background[i][j] == 2:
                    win.blit(GRASS, (j * TILEPIX, i * TILEPIX))
                elif self.background[i][j] == 3:
                    win.blit(WATER, (j * TILEPIX, i * TILEPIX))
                elif self.background[i][j] == 4:
                    win.blit(ELECTRIC, (j * TILEPIX, i * TILEPIX))
                elif self.background[i][j] == 5:
                    win.blit(SAND, (j * TILEPIX, i * TILEPIX))

    # save csv map in a list of lists
    def loadbackground(self):
        file = open('csvmap.csv')
        csvreader = csv.reader(file)
        rows = []
        test = list()
        for row in csvreader:
            rows.append(row)

        for i in range(len(rows)):
            for j in range(len(rows[i])):
                test.append(int(rows[i][j]))
            self.background.append(test.copy())
            test.clear()
        file.close()

    # uses list of list background to create a mask of walls
    def create_Wall_Mask(self, win):
        for i in range(TILECOUNT):
            for j in range(TILECOUNT):
                if self.background[i][j] == 1:
                    win.blit(WALL, (j * TILEPIX, i * TILEPIX))
        return pygame.mask.from_surface(win)

    # uses list of list background to create a mask of walls
    def create_Mask(self, win, tile):
        if tile == 1:
            for i in range(TILECOUNT):
                for j in range(TILECOUNT):
                    if self.background[i][j] == 1:
                        win.blit(WALL, (j * TILEPIX, i * TILEPIX))
        elif tile == 2:
            for i in range(TILECOUNT):
                for j in range(TILECOUNT):
                    if self.background[i][j] == 2:
                        win.blit(GRASS, (j * TILEPIX, i * TILEPIX))
        elif tile == 3:
            for i in range(TILECOUNT):
                for j in range(TILECOUNT):
                    if self.background[i][j] == 3:
                        win.blit(WATER, (j * TILEPIX, i * TILEPIX))
        elif tile == 4:
            for i in range(TILECOUNT):
                for j in range(TILECOUNT):
                    if self.background[i][j] == 4:
                        win.blit(ELECTRIC, (j * TILEPIX, i * TILEPIX))
        elif tile == 5:
            for i in range(TILECOUNT):
                for j in range(TILECOUNT):
                    if self.background[i][j] == 5:
                        win.blit(SAND, (j * TILEPIX, i * TILEPIX))
        return pygame.mask.from_surface(win)


class PlayerRobo(Robot):

    IMG = ROBO
    STARTPOS = (500, 500)


def draw(win):
    map.drawtiles(win)
    player_robo.draw(win)
    pygame.display.update()


def movePlayer(player_robo):

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
    if keys[pygame.K_s]:
        moved = True
        player_robo.moveBackward()
    if not moved:
        player_robo.slowDown()


map = TileMap()
clock = pygame.time.Clock()
player_robo = PlayerRobo(3, 3)
WALLMASK = map.create_Mask(Wall, 1)
SANDMASK = map.create_Mask(Sand, 5)
WATERMASK = map.create_Mask(Water, 3)
ELECTRICMASK = map.create_Mask(Electric, 4)

# main loop
while run:
    clock.tick(FPS)

    draw(Window)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    if player_robo.stun < STUNTICKS:
        player_robo.stun += 1

    if player_robo.tenacity < TENACITY:
        player_robo.tenacity += 1

    movePlayer(player_robo)

    if player_robo.collide(WALLMASK) is not None:
        player_robo.bounce()

    if player_robo.inTile(SANDMASK):
        player_robo.slowed()

    if player_robo.inTile(ELECTRICMASK):
        player_robo.stunned()

pygame.quit()
