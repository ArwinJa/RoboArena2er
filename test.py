import pygame
import sys

pygame.init()
screen = pygame.display.set_mode([600, 600])
clock = pygame.time.Clock()

x = 300
y = 300
speed = 3
width = 40
height = 80

go = True
while go:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             sys.exit()
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]:
        y -= speed
    if pressed[pygame.K_RIGHT]:
        x += speed
    if pressed[pygame.K_DOWN]:
        y += speed
    if pressed[pygame.K_LEFT]:
        x -= speed

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height))
    pygame.display.update()
    clock.tick(60)
