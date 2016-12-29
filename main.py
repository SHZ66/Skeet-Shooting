import pygame, sys
from pygame.locals import *
import numpy as np

### Definitions ###

## constants ##
PI = np.pi
eps = np.finfo(float).eps
g = 0.01
V0 = 10.
FPS = 60 # frames per second setting
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
fpsClock = pygame.time.Clock()
viewport_sensitivity = np.array([3, 3])

## functions ##
def world2stage(world_pos, viewport, screen_center, image_size=(0,0), scale=1.0):
    image_center = np.array([x/2. for x in image_size])
    stage_x = (world_pos[0] - viewport[0])*scale + screen_center[0] - image_center[0]
    stage_y = (world_pos[1] - viewport[1])*scale + screen_center[1] - image_center[1]
    return np.array([stage_x, stage_y])

def stage2world(stage_pos, viewport, screen_center, scale=1.0):
    world_x = (stage_pos[0] - screen_center[0])/scale + viewport[0]
    world_y = (stage_pos[1] - screen_center[1])/scale + viewport[1] 
    return np.array([world_x, world_y])

def getDegree(vec):
    return -np.degrees(np.arctan2(vec[1], vec[0]))

## classes
class Sprite(object):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1.):
        self.Coordinate = np.array(coord)
        self.Angle = angle
        if image_file is not None:
            self.loadImage(image_file, scale)

    def loadImage(self, image_file, scale=1.):
        self.Image = pygame.image.load(image_file)
        if scale != 1:
            size = np.array(self.Image.get_size(), dtype=float)
            size *= scale
            size = size.astype(int)
            self.Image = pygame.transform.smoothscale(self.Image, size)

        return self.Image
    
    def draw(self):
        if rifle.Angle != 0:
            image = pygame.transform.rotate(self.Image, self.Angle)
        else:
            image = self.Image
        stage_coord = world2stage(self.Coordinate, viewport, screen_center, image_size=image.get_size())
        DISPLAYSURF.blit(image, stage_coord)

class Rifle(Sprite):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1.):
        super(Rifle, self).__init__(coord, angle, image_file, scale)

class Bullet(Sprite):
    def __init__(self, coord=(0.,0.), velocity=(0.,0.), active=False):
        self.active = active
        self.Velocity = np.array(velocity)
        super(Bullet, self).__init__(coord)
        self.tail_coord = np.array(self.Coordinate, copy=True)

    def draw(self):
        if self.active:
            stage_coord = world2stage(self.Coordinate, viewport, screen_center)
            tail_stage_coord = world2stage(self.tail_coord, viewport, screen_center)
            pygame.draw.line(DISPLAYSURF, BLACK, stage_coord, tail_stage_coord, 4)

    def update(self):
        if self.active:
            self.tail_coord = np.copy(self.Coordinate)
            self.Coordinate += self.Velocity
            if np.any(np.abs(self.Coordinate)>2000):
                self.active = False

### Game ###
## initialization ##
pygame.init()
DISPLAYSURF = pygame.display.set_mode((1400, 500), 0, 32)
screen_center = [x/2 for x in DISPLAYSURF.get_size()]
pygame.display.set_caption('Shoot Range')
viewport = np.array([500., 0.])
rifle = Rifle((0., 0.), 0., './Resources/m1a.png', .3)
target = Sprite((1000., 0.), 0., './Resources/target.jpg', .3)
bullets = []

## game logics ##
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
        if event.type == MOUSEBUTTONUP:
            # shoot
            if event.button == 1:
                rad_angle = np.radians(rifle.Angle)
                velocity = (V0*np.cos(rad_angle), -V0*np.sin(rad_angle))
                bullet = Bullet(rifle.Coordinate, velocity, True)
                bullets.append(bullet)
    
    # keyboard #
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        viewport[0] -= viewport_sensitivity[0]
    if keys[K_RIGHT]:
        viewport[0] += viewport_sensitivity[0]
    if keys[K_UP]:
        viewport[1] -= viewport_sensitivity[1]
    if keys[K_DOWN]:
        viewport[1] += viewport_sensitivity[1]

    # mouse #
    mouse_pos = pygame.mouse.get_pos()
    mouse_world_pos = stage2world(mouse_pos, viewport, screen_center)
    diff_mouse2rifle = mouse_world_pos - rifle.Coordinate
    rifle.Angle = getDegree(diff_mouse2rifle)

    mousebuttons = pygame.mouse.get_pressed()
    # left button down
    if mousebuttons[0]:
        pass


def draw():
    # draw rifle #
    rifle.draw()

    # draw target #
    target.draw()

    # draw bullets #
    for bullet in bullets:
        bullet.draw()

    pygame.display.update()


## main loop ##
while True: # the main game loop
    DISPLAYSURF.fill(WHITE)

    handleEvents()

    # update world #
    for bullet in bullets:
        bullet.update()

    draw()

    fpsClock.tick(FPS)
