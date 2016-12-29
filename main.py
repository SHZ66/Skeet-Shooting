import pygame, sys
from pygame.locals import *
import numpy as np

### Definitions ###

## constants ##
FPS = 60 # frames per second setting
WHITE = (255, 255, 255)
fpsClock = pygame.time.Clock()
viewport_sensitivity = np.array([3, 3])

## functions ##
def world2stage(world_pos, viewport, screen_center, image_size=(0,0), scale=1.0):
    image_center = np.array([x/2. for x in image_size])
    stage_x = (world_pos[0] - viewport[0])*scale + screen_center[0] - image_center[0]
    stage_y = (world_pos[1] - viewport[1])*scale + screen_center[1] - image_center[1]
    return np.array([stage_x, stage_y])

### Game main ###
## Initialization ##
pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 600), 0, 32)
screen_center = [x/2 for x in DISPLAYSURF.get_size()]
pygame.display.set_caption('Test')
viewport = np.array([10, 10])
catImg = pygame.image.load('cat.png')
catCoord = np.array([10, 10])

## Game logics ##
def terminate():
    pygame.quit()
    sys.exit()

def handleEvents():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                terminate()
        if event.type == KEYDOWN:
            pass

    pressed = pygame.key.get_pressed()
    if pressed[K_LEFT]:
        viewport[0] -= viewport_sensitivity[0]
    if pressed[K_RIGHT]:
        viewport[0] += viewport_sensitivity[0]
    if pressed[K_UP]:
        viewport[1] -= viewport_sensitivity[1]
    if pressed[K_DOWN]:
        viewport[1] += viewport_sensitivity[1]

def draw():
    rotatedcatImg = pygame.transform.rotate(catImg, 45)
    catStageCoord = world2stage(catCoord, viewport, screen_center, image_size=rotatedcatImg.get_size())
    
    DISPLAYSURF.blit(rotatedcatImg, catStageCoord)
    pygame.display.update()

## Main loop ##
while True: # the main game loop
    DISPLAYSURF.fill(WHITE)

    handleEvents()
    draw()

    fpsClock.tick(FPS)
