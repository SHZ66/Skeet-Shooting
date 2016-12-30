import pygame, sys
from pygame.locals import *
import numpy as np
import numpy.linalg as la

### Definitions ###

## constants ##
PI = np.pi
eps = np.finfo(float).eps
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (150, 150, 255)

## settings ##
# gameplay #
FPS = 60 # frames per second setting
viewport_sensitivity = np.array([3, 3])
respawn_area = pygame.Rect(600, -250, 500, 400)
TOTAL_AMMO = 10

# physics #
g = 0.05
friction = 0.005
V0 = 12.

## variables ##
firecount = 0
hitcount = 0
ammo = TOTAL_AMMO

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
    return np.degrees(np.arctan2(vec[1], vec[0]))

def getVector(degree, length=1.):
    rad = np.radians(degree)
    return np.array((length*np.cos(rad), length*np.sin(rad)))

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degrees.
    """
    angle = np.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy

def sqlength(vec):
    return vec[0]*vec[0] + vec[1]*vec[1]

def printText(message, pos, forecolor=BLACK, backcolor=None):
    fontObj = pygame.font.Font('freesansbold.ttf', 32)
    textSurfaceObj = fontObj.render(message, True, forecolor, backcolor)
    textRectObj = textSurfaceObj.get_rect()
    #textRectObj.center = pos
    textRectObj.topleft = pos
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)

## classes
class Sprite(object):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1.):
        self.Coordinate = np.array(coord)
        self.Angle = angle
        if image_file is not None:
            self.loadImage(image_file, scale)
        else:
            self.Image = None

    def loadImage(self, image_file, scale=1.):
        self.Image = pygame.image.load(image_file)
        if scale != 1:
            size = np.array(self.Image.get_size(), dtype=float)
            size *= scale
            size = size.astype(int)
            self.Image = pygame.transform.smoothscale(self.Image, size)
        self.Display = self.Image
        return self.Image

    def draw(self):
        if rifle.Angle != 0:
            image = pygame.transform.rotate(self.Image, -self.Angle) # negative for clockwise
        else:
            image = self.Image
        stage_coord = world2stage(self.Coordinate, viewport, screen_center, image_size=image.get_size())
        self.Display = image
        DISPLAYSURF.blit(image, stage_coord)

class Rifle(Sprite):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1., sound_file=None):
        super(Rifle, self).__init__(coord, angle, image_file, scale)

        if sound_file is not None:
            self.loadSound(sound_file)
        else:
            self.Sound = None

    def getMuzzlePosition(self):
        if self.Image is None:
            return self.Coordinate
        else:
            (width, height) = self.Image.get_size()
            muzzle_pos = np.array([width/2., -height/4.])
            muzzle_pos = rotate((0, 0), muzzle_pos, self.Angle)
            muzzle_pos += self.Coordinate
            return muzzle_pos
    
    def loadSound(self, sound_file):
        self.Sound = pygame.mixer.Sound(sound_file)
        return self.Sound
    
    def fire(self):
        global ammo, firecount
        if ammo > 0:
            velocity = getVector(self.Angle, V0)
            muzzle_pos = self.getMuzzlePosition()
            bullet = Bullet.createBullet(bullets, muzzle_pos, velocity)
            ammo -= 1
            firecount += 1
            self.Sound.play()

class Target(Sprite):
    def hit(self):
        global hitcount
        print('hit!')
        hitcount += 1
        self.random()
    
    def random(self):
        pos_x = np.random.randint(respawn_area.left, respawn_area.right)
        pos_y = np.random.randint(respawn_area.top, respawn_area.bottom)
        self.Coordinate = np.array([pos_x, pos_y], dtype=float)

class Bullet(Sprite):
    def __init__(self, coord=(0.,0.), velocity=(0.,0.), active=True):
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
            # tail trace
            self.tail_coord = np.copy(self.Coordinate)
            # gravity
            self.Velocity += np.array([0., g])
            # air friction
            self.Velocity -= self.Velocity * friction
            # update coordinate
            self.Coordinate += self.Velocity
            # hit detection
            #if target.Display.get_rect().collidepoint(self.Coordinate):
            box = pygame.Rect(target.Coordinate, target.Display.get_size())
            box.center = target.Coordinate
            #box_stage_coord = world2stage(box.topleft, viewport, screen_center)
            #box_stage = pygame.Rect(box_stage_coord, target.Display.get_size())
            #pygame.draw.rect(DISPLAYSURF, BLACK, box_stage)
            if box.collidepoint(self.Coordinate):
                target_radius = target.Image.get_size()[1]/2.
                sqdist_bullet2target = sqlength(self.Coordinate - target.Coordinate)
                if sqdist_bullet2target <= target_radius*target_radius:
                    # hit
                    self.active = False
                    target.hit()
            # eliminate bullets out of range
            if np.any(np.abs(self.Coordinate)>2000):
                self.active = False
    
    @staticmethod
    def createBullet(bullets, coord, velocity):
        the_bullet = None
        for bullet in bullets:
            if not bullet.active:
                the_bullet = bullet
                break
        if the_bullet is None:
            the_bullet = Bullet(coord, velocity, True)
            bullets.append(the_bullet)
        else:
            the_bullet.__init__(coord, velocity, True)
        return the_bullet

### Game ###
## initialization ##
fpsClock = pygame.time.Clock()
pygame.init()
DISPLAYSURF = pygame.display.set_mode((1400, 500), 0, 32)
screen_center = [x/2 for x in DISPLAYSURF.get_size()]
pygame.display.set_caption('Shoot Range Remake')
viewport = np.array([500., -50.])
rifle = Rifle((0., 0.), 0., './Resources/m1a.png', .3, './Resources/gunfire.wav')
target = Target((1000., 0.), 0., './Resources/target.png', .3)
bullets = []

## game logics ##
def terminate():
    pygame.quit()
    sys.exit()

def replay():
    global firecount, hitcount, ammo
    target.random()
    firecount = 0
    hitcount = 0
    ammo = TOTAL_AMMO

def handleEvents():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                terminate()
            if event.key == K_SPACE:
                replay()
        if event.type == KEYDOWN:
            pass
        if event.type == MOUSEBUTTONUP:
            # fire
            if event.button == 1:
                rifle.fire()
    
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
    #pygame.display.set_caption(str(rifle.Angle))

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

    # draw HUD
    printText('Accuracy: %d/%d'%(hitcount, firecount), (10, 10))
    printText('Ammo: %d'%ammo, (10, 50))

    # debug
    #respawn_stage_coord = world2stage(respawn_area.topleft, viewport, screen_center)
    #respawn_stage = pygame.Rect(respawn_stage_coord, respawn_area.size)
    #pygame.draw.rect(DISPLAYSURF, LIGHTBLUE, respawn_stage, 1)

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
