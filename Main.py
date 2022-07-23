import pygame
import math
import csv
import time
from tools import blitRotate


pygame.font.init()
pygame.init()

MAP = pygame.image.load("img/Karte.png")
BORDER = pygame.image.load("img/Mauer.png")
ROBO = pygame.image.load("img/Robot.png")
ENEMYROBO = pygame.image.load("img/Enemy Robot.png")
BULLET = pygame.image.load("img/Bullet.png")
HEART = pygame.image.load("img/Heart.png")

GRASS = pygame.image.load("img/Grass-Tiles.png")
ELECTRIC = pygame.image.load("img/Electric-Tiles.png")
SAND = pygame.image.load("img/Sand-Tiles.png")
WALL = pygame.image.load("img/Wall-Tiles.png")
WATER = pygame.image.load("img/Water-Tiles.png")

WIDTH, HEIGHT = MAP.get_width(), MAP.get_height()
Window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RoboArena")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SCORE_FONT = pygame.font.SysFont("comicsans", 25)

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
MOVETICKS = 60
MOVETICKS2 = 30
run = True


class GameInfo:  # Game infromation like time Health etc

    def __init__(self,  score=0):
        self.score = score
        self.started = False
        self.gameStartTime = 0
        self.hearts = 3
        self.gameOver = False

    def respawn(self):
        self.score = 0
        self.started = False
        self.gameStartTime = 0
        self.hearts = 3

    def startGame(self):
        self.started = True
        self.gameStartTime = time.time()

    def getGameTime(self):
        if not self.started:
            return 0
        return self.gameStartTime - time.time()


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
        self.ok = True

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

    def stop(self):
        if self.speed > 0:
            self.speed = -1
        elif self.speed < 0:
            self.speed = 1
        self.move()


class bullet:
    def __init__(self, robot):
        self.direction = robot.angle
        self.x = robot.x + 25
        self.y = robot.y + 25
        self.speed = robot.maxSpeed + 1
        self.img = BULLET

    def moveB(self):
        radians = math.radians(self.direction)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed

        self.y -= vertical
        self.x -= horizontal

    def drawB(self, win):
        win.blit(self.img, (self.x, self.y))

    def collideB(self, mask, x=0, y=0):
        bullet_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(bullet_mask, offset)
        return poi


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


class EnemyRobo(Robot):

    IMG = ENEMYROBO
    STARTPOS = (750, 250)

    def __init__(self, maxSpeed, rotSpeed, x, y, xMin, xMax, yMin, yMax):
        super().__init__(maxSpeed, rotSpeed)
        self.speed = maxSpeed
        self.x = x
        self.y = y
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.moveTick = 0

    def moveEnemyRobot(self):
        if self.y < self.yMin or self.y > self.yMax:
            if self.moveTick < MOVETICKS:
                self.moveTick += 1
                self.rotate(left=True)
            self.moveForward()
        else:
            self.moveForward()
            self.moveTick = 0

    def moveEnemy2(self):
        if self.y < self.yMin or self.y > self.yMax:
            if self.moveTick < MOVETICKS2:
                self.moveTick += 1
                self.rotate(left=True)
            self.moveForward()
        if self.x < self.xMin or self.x > self.xMax:
            if self.moveTick < MOVETICKS2:
                self.moveTick += 1
                self.rotate(left=True)
            self.moveForward()
        else:
            self.moveForward()
            self.moveTick = 0

    def moveEnemy3(self):
        self.rotate(right=True)


def scoreblit(win, font, text):
    render = font.render(text, 1, (255, 255, 255))
    win.blit(render, (0, TILEPIX - 5))


def draw(win):
    map.drawtiles(win)
    for b in bullets:
        b.drawB(win)
    player_robo.draw(win)
    for e in enemies:
        e.draw(win)
    for i in range(game_info.hearts):
        win.blit(HEART, (i * TILEPIX, 0))
    scoreblit(win, SCORE_FONT, f"score: {game_info.score}")
    pygame.display.update()


def blitTextCenter(win, font, text):
    render = font.render(text, 1, (255, 255, 255))
    win.blit(render, (win.get_width()/2 - render.get_width()/2,
                      win.get_height()/2 - render.get_height()/2))


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


def moveBullet(player_robo):

    key = pygame.key.get_pressed()

    if key[pygame.K_SPACE]:
        if len(bullets) <= 4 and player_robo.ok:
            bullets.append(bullet(player_robo))
        player_robo.ok = False
    if not key[pygame.K_SPACE]:
        player_robo.ok = True


map = TileMap()
clock = pygame.time.Clock()
player_robo = PlayerRobo(3, 3)
enemy1 = EnemyRobo(3, 3, 800, 500, 200, 800, 200, 500)
enemy2 = EnemyRobo(5, 20, 300, 800, 1, 1, 500, 800)
enemy3 = EnemyRobo(3, 5, 100, 100, 0, 0, 0, 0)
WALLMASK = map.create_Mask(Wall, 1)
SANDMASK = map.create_Mask(Sand, 5)
WATERMASK = map.create_Mask(Water, 3)
ELECTRICMASK = map.create_Mask(Electric, 4)
bullets = []
enemies = [enemy1, enemy2, enemy3]
game_info = GameInfo()

# main loop
while run:
    clock.tick(FPS)

    draw(Window)

    # Pre Game start loop
    while not game_info.started:
        blitTextCenter(Window, MAIN_FONT, "Press any key to start the game")
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                game_info.startGame()

    if game_info.hearts == 0:
        game_info.gameOver = True
        game_info.respawn()
        enemies.clear()
        enemies.append(enemy1)
        enemies.append(enemy2)
        enemies.append(enemy3)
        player_robo = PlayerRobo(3, 3)

    while game_info.gameOver:

        blitTextCenter(Window, MAIN_FONT,
                       "GAME OVER!! Press any key to try again")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                game_info.gameOver = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break

    if player_robo.stun < STUNTICKS:
        player_robo.stun += 1

    if player_robo.tenacity < TENACITY:
        player_robo.tenacity += 1

    movePlayer(player_robo)

    enemy1.moveEnemy2()
    enemy2.moveEnemyRobot()
    enemy3.moveEnemy3()

    moveBullet(player_robo)

    for b in bullets:
        for e in enemies:
            enemyMask = pygame.mask.from_surface(e.img)
            if b.collideB(enemyMask, e.x, e.y):
                bullets.remove(b)
                enemies.remove(e)
                game_info.score += 1

        if b.collideB(WALLMASK) is not None:
            bullets.remove(b)

        else:
            b.moveB()

    for e in enemies:
        enemyMask = pygame.mask.from_surface(e.img)
        if player_robo.collide(enemyMask, e.x, e.y):
            enemies.remove(e)
            game_info.score += 1
            game_info.hearts -= 1

    if player_robo.collide(WALLMASK) is not None:
        player_robo.bounce()

    if player_robo.inTile(SANDMASK):
        player_robo.slowed()

    if player_robo.inTile(ELECTRICMASK):
        player_robo.stunned()

    if player_robo.collide(WATERMASK):
        player_robo.stop()


pygame.quit()
