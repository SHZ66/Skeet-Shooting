import pygame, sys, eztext, platform
from pygame.locals import *
from pygame.math import Vector2
import math
from leaderboard import *
from physics import *
import time as systime

### Definitions ###

## constants ##
PI = math.pi
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (150, 150, 255)
RED = (255, 0, 0)
LIGHTRED = (255, 150, 150)
DARKRED = (100, 0, 0)
O = Vector2(0,0)

## settings ##
# gameplay #
leaderboard_file = 'data'
screen_size = (1400, 700)
FPS = 60 # frames per second setting
viewport_sensitivity = Vector2(3, 3)
move_sensitivity = 2
respawn_box = pygame.Rect(600, -250, 500, 400)
respawn_disk_box = pygame.Rect(1000, 200, 100, 50)
world_box = pygame.Rect(-300, -1000, 1800, 1300)
total_ammo = 100
round_length = 60000 # ms
monospace_font = 'Courier New'

# physics #
g = 0.05
friction = 0.005
bullet_V0 = 20.
disk_V0 = 12.

## variables ##
game = 1
mode = 2
firecount = 0
hitcount = 0
ammo = total_ammo
countdown = 0
time = 0
gameover_reason = ''
recent_record = None

## functions ##
def world2stage(world_pos, viewport, screen, image_size=(0,0), scale=1.0):
    image_center = Vector2([x/2. for x in image_size])
    screen_center = screen.get_rect().center
    stage_x = (world_pos[0] - viewport[0])*scale + screen_center[0] - image_center[0]
    stage_y = (world_pos[1] - viewport[1])*scale + screen_center[1] - image_center[1]
    return Vector2([stage_x, stage_y])

def stage2world(stage_pos, viewport, screen, scale=1.0):
    screen_center = screen.get_rect().center
    world_x = (stage_pos[0] - screen_center[0])/scale + viewport[0]
    world_y = (stage_pos[1] - screen_center[1])/scale + viewport[1] 
    return Vector2([world_x, world_y])

def intVector2(vec):
    return [int(vec[0]), int(vec[1])]

def getDegree(vec):
    return -vec.angle_to(O)

def getVector(degree, length=1.):
    rad = math.radians(degree)
    return Vector2((length*math.cos(rad), length*math.sin(rad)))

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degrees.
    """
    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def sqlength(vec):
    return vec[0]*vec[0] + vec[1]*vec[1]

def printSimpleText(screen, message, pos, forecolor=BLACK, backcolor=None, fontsize=32, bold=False, location='topleft', fontname='freesansbold.ttf'):
    if '.ttf' in fontname:
        fontObj = pygame.font.Font(fontname, fontsize, bold=bold)
    else:
        fontObj = pygame.font.SysFont(fontname, fontsize, bold=bold)
    textSurfaceObj = fontObj.render(message, True, forecolor, backcolor)
    textRectObj = textSurfaceObj.get_rect()
    if location == 'center':
        textRectObj.center = pos
    elif location == 'topleft':
        textRectObj.topleft = pos
    elif location == 'topright':
        textRectObj.topright = pos
    screen.blit(textSurfaceObj, textRectObj)

def createText(message, forecolor=BLACK, backcolor=None, fontsize=32, bold=False, location='topleft', fontname='freesansbold.ttf'):
    if '.ttf' in fontname:
        fontObj = pygame.font.Font(fontname, fontsize, bold=bold)
    else:
        fontObj = pygame.font.SysFont(fontname, fontsize, bold=bold)
    textSurfaceObj = fontObj.render(message, True, forecolor, backcolor)
    return textSurfaceObj

def printText(screen, textSurfaceObj, pos, forecolor=BLACK, backcolor=None, fontsize=32, bold=False, location='topleft', fontname='freesansbold.ttf'):
    textRectObj = textSurfaceObj.get_rect()
    if location == 'center':
        textRectObj.center = pos
    elif location == 'topleft':
        textRectObj.topleft = pos
    elif location == 'topright':
        textRectObj.topright = pos
    screen.blit(textSurfaceObj, textRectObj)

def timeleft():
    if countdown > 0:
        t = (round_length)//1000
    else:
        t = (round_length - time)//1000
    if t < 0: t = 0
    return t

def makeBullet(bullets, coord, velocity, type):
    the_bullet = None
    for bullet in bullets:
        if not bullet.active:
            the_bullet = bullet
            break
    if the_bullet is None:
        the_bullet = type(coord, velocity, True)
        bullets.append(the_bullet)
    else:
        the_bullet.__init__(coord, velocity, True)
    return the_bullet

def isInBox(box, point):
    x,y = point
    if x >= box.left and x <= box.right:
        if y >= box.top and y <= box.bottom:
            return True
    return False

def loadImage(image_file, scale=1.):
    image = pygame.image.load(image_file)
    if scale != 1:
        size = Vector2(image.get_size())
        size *= scale
        image = pygame.transform.smoothscale(image, intVector2(size))
    return image

## classes
class Sprite(object):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1., velocity=(0.,0.)):
        self.Coordinate = Vector2(coord)
        self.Angle = angle
        self.Velocity = Vector2(velocity)
        if image_file is not None:
            self.loadImage(image_file, scale)
        else:
            self.Image = None
    
    def loadSound(self, sound_file):
        return pygame.mixer.Sound(sound_file)

    def loadImage(self, image_file, scale=1.):
        self.Image = pygame.image.load(image_file)
        if scale != 1:
            size = Vector2(self.Image.get_size())
            size *= scale
            self.Image = pygame.transform.smoothscale(self.Image, intVector2(size))
        self.Display = self.Image
        return self.Image

    def draw(self, screen):
        if self.Angle != 0:
            image = pygame.transform.rotate(self.Image, -self.Angle) # negative for clockwise
        else:
            image = self.Image
        stage_coord = world2stage(self.Coordinate, viewport, screen, image_size=image.get_size())
        self.Display = image
        screen.blit(image, stage_coord)

    def update(self):
        return

class Rifle(Sprite):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1., fire_sound_file=None, dry_sound_file=None):
        super(Rifle, self).__init__(coord, angle, image_file, scale)

        if fire_sound_file is not None:
            self.FireSound = self.loadSound(fire_sound_file)
        else:
            self.FireSound = None

        if dry_sound_file is not None:
            self.DrySound = self.loadSound(dry_sound_file)
        else:
            self.DrySound = None

    def getMuzzlePosition(self):
        if self.Image is None:
            return self.Coordinate
        else:
            (width, height) = self.Image.get_size()
            muzzle_pos = Vector2([width/2., -height/4.])
            muzzle_pos = muzzle_pos.rotate(self.Angle)
            muzzle_pos += self.Coordinate
            return muzzle_pos
    
    def fire(self):
        global ammo, firecount
        if ammo > 0:
            velocity = getVector(self.Angle, bullet_V0)
            muzzle_pos = self.getMuzzlePosition()
            bullet = makeBullet(bullets, muzzle_pos, velocity, type=Bullet)
            ammo -= 1
            firecount += 1
            self.FireSound.play()
        else:
            self.DrySound.play()
            pass
        return ammo

class Target(Sprite):
    def __init__(self, coord=(0,0), angle=0., image_file=None, scale=1., velocity=(0.,0.), skeet_sound_file=None):
        super(Target, self).__init__(coord, angle, image_file, scale)
        if skeet_sound_file is not None:
            self.Skeet = self.loadSound(skeet_sound_file)
        else:
            self.Skeet = None

    def hit(self, bullet):
        global hitcount, mode
        #print('hit!')
        if mode == 0:
            hitcount += 1
        # splash effect
        V = initSplash(1., 2., bullet.Velocity, O, 8)
        for v in V:
            p = makeBullet(particles, self.Coordinate, v, type=Particle)
            r = random.randint(0,len(fragimages)-1)
            p.Image = fragimages[r]
        self.replace()
    
    def replace(self):
        global game
        if game == 0:
            pos_x = random.randint(respawn_box.left, respawn_box.right)
            pos_y = random.randint(respawn_box.top, respawn_box.bottom)
            self.Coordinate = Vector2([pos_x, pos_y])
            self.Angle = getDegree(self.Coordinate - rifle.Coordinate) - 90
        elif game == 1:
            pos_x = random.randint(respawn_disk_box.left, respawn_disk_box.right)
            pos_y = random.randint(respawn_disk_box.top, respawn_disk_box.bottom)
            self.Coordinate = Vector2([pos_x, pos_y])
            angle = random.randint(100, 120)
            speed = random.randint(disk_V0-2, disk_V0+2)
            self.Velocity = getVector(-angle, speed)
            self.Skeet.play()

    def update(self):
        global game
        if game == 1:
            # tail trace
            tail_coord = Vector2(self.Coordinate)
            # gravity
            self.Velocity += Vector2(0., g)
            # air friction
            self.Velocity -= self.Velocity * friction
            # update coordinate
            self.Coordinate += self.Velocity
            # ajust angle based on direction
            self.Angle = getDegree(self.Coordinate-tail_coord) + 180
            # eliminate bullets out of range
            #if not world_box.collidepoint(self.Coordinate):
            if not isInBox(world_box, self.Coordinate):
                self.replace()
            
class Bullet(Sprite):
    def __init__(self, coord=(0.,0.), velocity=(0.,0.), active=True):
        self.active = active
        super(Bullet, self).__init__(coord, velocity=velocity)
        self.tail_coord = Vector2(self.Coordinate)

    def draw(self, screen):
        if self.active:
            stage_coord = world2stage(self.Coordinate, viewport, screen)
            tail_stage_coord = world2stage(self.tail_coord, viewport, screen)
            pygame.draw.line(screen, BLACK, stage_coord, tail_stage_coord, 4)

    def update(self):
        if self.active:
            # tail trace
            self.tail_coord = Vector2(self.Coordinate)
            # gravity
            self.Velocity += Vector2(0., g)
            # air friction
            self.Velocity -= self.Velocity * friction
            # update coordinate
            self.Coordinate += self.Velocity
            # hit detection
            self.collision()
            # eliminate bullets out of range
            #if not world_box.collidepoint(self.Coordinate):
            if not isInBox(world_box, self.Coordinate):
                self.active = False
        
    def collision(self):
        #if target.Display.get_rect().collidepoint(self.Coordinate):
        box = pygame.Rect(target.Coordinate, target.Display.get_size())
        box.center = target.Coordinate
        #box_stage_coord = world2stage(box.topleft, viewport, DISPLAYSURF)
        #box_stage = pygame.Rect(box_stage_coord, target.Display.get_size())
        #pygame.draw.rect(DISPLAYSURF, LIGHTBLUE, box_stage, 1)
        #if box.collidepoint(self.Coordinate):
        if isInBox(box, self.Coordinate):
            target_radius = target.Image.get_size()[0]/2.
            sqdist_bullet2target = sqlength(self.Coordinate - target.Coordinate)
            if sqdist_bullet2target <= target_radius*target_radius:
                # hit
                self.active = False
                target.hit(self)

class Particle(Bullet):
    def __init__(self, coord=(0.,0.), velocity=(0.,0.), active=True, image=None):
        self.active = active
        super(Particle, self).__init__(coord, velocity=velocity)
        self.tail_coord = Vector2(self.Coordinate)
        self.Image = image
        self.Display = self.Image

    def collision(self):
        pass

    def draw(self, screen):
        if self.active:
            stage_coord = world2stage(self.Coordinate, viewport, screen)
            tail_stage_coord = world2stage(self.tail_coord, viewport, screen)
            if self.Image is None:
                pygame.draw.line(screen, DARKRED, stage_coord, tail_stage_coord, 4)
            else:
                self.Angle = getDegree(stage_coord-tail_stage_coord)
                super(Bullet, self).draw(screen)



### Game ###
## game logics (functions) ##
def terminate():
    pygame.quit()
    sys.exit()

def replay():
    global firecount, hitcount, ammo, mode, countdown, time
    firecount = 0
    hitcount = 0
    ammo = total_ammo
    countdown = 270
    time = 0
    if mode == 1:
        mode = 0

def record():
    global hitcount, leaderboard_file, records, recent_record
    if len(records) > 0:
        min_score = records[-1]['score']
    else:
        min_score = -1
    if hitcount <= min_score and len(records) >= 10:
        return False
    name = namebox.value.strip()
    if name == '': name = 'Anonymous'
    namebox.value = ''
    r = {'name':name, 'score': hitcount, 'time':systime.strftime("%Y-%m-%d %H:%M:%S", systime.localtime())}
    #r = Record(name, hitcount)
    records.append(r)
    recent_record = r
    records = sortRecords(records)[:10]
    writeRecords(leaderboard_file, records)
    return True

def gameover(reason=''):
    global mode, ammo, gameover_reason
    gameover_reason = reason
    mode = 1

def handleEvents(events, screen):
    global mode, countdown
    for event in events:
        if event.type == QUIT:
            if mode == 1:
                record()
            terminate()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                terminate()
            if event.key == K_RETURN or event.key == K_KP_ENTER:
                countdown = 0
                if mode == 1:
                    record()
                if mode == 2:
                    replay()
                mode += 1
                if mode > 2: mode = 0

        if event.type == KEYDOWN:
            # fire
            if event.key == K_SPACE:
                if countdown == 0:
                    ammo = rifle.fire()
        if event.type == MOUSEBUTTONDOWN:
            # fire
            if event.button == 1:
                if countdown == 0:
                    ammo = rifle.fire()
        if event.type == MOUSEMOTION:
            mouse_pos = event.pos
            mouse_world_pos = stage2world(mouse_pos, viewport, screen)
            diff_mouse2rifle = mouse_world_pos - rifle.Coordinate
            rifle.Angle = getDegree(diff_mouse2rifle)
            #pygame.display.set_caption(str(rifle.Angle))
    
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
    if keys[K_w]:
        rifle.Angle -= move_sensitivity
    if keys[K_s]:
        rifle.Angle += move_sensitivity    
   
    # mouse #
    mousebuttons = pygame.mouse.get_pressed()
    # left button down
    if mousebuttons[0]:
        pass

    # mode 1
    if mode == 1:
        namebox.update(events)

def draw(screen):
    global mode
    # draw rifle #
    rifle.draw(screen)

    # draw target #
    target.draw(screen)

    # draw bullets #
    for bullet in bullets:
        bullet.draw(screen)

    # draw particles #
    for particle in particles:
        particle.draw(screen)

    # draw HUD
    printSimpleText(screen, 'Score: %d'%(hitcount), (10, 10), fontname=monospace_font)
    printSimpleText(screen, ' Time: %d'%timeleft(), (10, 50), fontname=monospace_font)
    printSimpleText(screen, ' Ammo: %d'%ammo, (10, 90), fontname=monospace_font)

    # draw FPS
    printSimpleText(screen, 'FPS: %i'%fpsClock.get_fps(), (screen.get_size()[0]-10, 10), fontsize=16, location='topright')

    # draw countdown
    if mode == 0:
        if countdown > 0:
            printSimpleText(screen, str(countdown//90+1), screen.get_rect().center, fontsize=144, location='center')

    # mode 1
    if mode == 1:
        printSimpleText(screen, 'Game Over!', (screen.get_size()[0]/2, screen.get_size()[1]/2-150), fontsize=48, location='center')
        printSimpleText(screen, gameover_reason, (screen.get_size()[0]/2, screen.get_size()[1]/2-100), fontsize=24, location='center')
        printSimpleText(screen, str(hitcount), (screen.get_size()[0]/2, screen.get_size()[1]/2), fontsize=144, forecolor=RED, location='center')
        namebox.draw(screen)
        printSimpleText(screen, 'Press [ENTER] to replay', (screen.get_size()[0]/2, screen.get_size()[1]-30), fontsize=16, location='center')
        #printSimpleText(screen, 'Press [SPACE] to replay', (screen.get_size()[0]/2, screen.get_size()[1]-30), fontsize=16, location='center')
    if mode == 2:
        printSimpleText(screen, 'Leaderboard', (screen.get_size()[0]/2, screen.get_size()[1]/2-220), fontsize=48, location='center')
        printSimpleText(screen, 'Press [ENTER] to start', (screen.get_size()[0]/2, screen.get_size()[1]-30), fontsize=16, location='center', fontname=monospace_font)
        template = '%15s %8s %12s'
        printSimpleText(screen, template%('Name','Score','Time'), (screen.get_size()[0]/2-320, screen.get_size()[1]/2-160), 
                        fontsize=24, location='topleft', fontname=monospace_font, bold=True)
        for i,r in enumerate(records):
            name = r['name']
            score = str(r['score'])
            datetime = r['time'][:10]
            if r is recent_record:
                color = DARKRED
                bold = True
            else:
                color = BLACK
                bold = False
            printSimpleText(screen, template%(name,score,datetime), (screen.get_size()[0]/2-320, screen.get_size()[1]/2-120 + i*40), 
                            fontsize=24, forecolor=color, location='topleft', fontname=monospace_font, bold=bold)


    # debug #
    # respawn box
    respawn_stage_coord = world2stage(respawn_disk_box.topleft, viewport, screen)
    respawn_stage = pygame.Rect(respawn_stage_coord, respawn_disk_box.size)
    pygame.draw.rect(DISPLAYSURF, LIGHTRED, respawn_stage, 1)
    # world box
    box_stage_coord = world2stage(world_box.topleft, viewport, screen)
    box_stage = pygame.Rect(box_stage_coord, world_box.size)
    pygame.draw.rect(DISPLAYSURF, LIGHTBLUE, box_stage, 1)
    #pygame.display.set_caption(str(mode))

    pygame.display.update()

## initialization ##
records = readRecords(leaderboard_file)
records = sortRecords(records)[:10]
fpsClock = pygame.time.Clock()
pygame.init()
if 'Darwin' in platform.platform():
    flags = pygame.FULLSCREEN|pygame.DOUBLEBUF
else:
    flags = pygame.DOUBLEBUF
DISPLAYSURF = pygame.display.set_mode(screen_size, flags, 32)
#screen_center = [x/2 for x in DISPLAYSURF.get_size()]
screen_center = DISPLAYSURF.get_rect().center
pygame.display.set_caption('Skeet Shooting')
namebox = eztext.Input(maxlength=45, color=BLACK, x=screen_center[0]-150, y=screen_center[1]+80, prompt='Your name: ')
#namebox.value = 'Shooter'
viewport = Vector2(500., -200.)
rifle = Rifle((0., 0.), 0., './Resources/m1a.png', .3, './Resources/gunfire.wav', './Resources/gundry.wav')
target = Target((-1000., -1000.), -90., './Resources/disk.png', .3, skeet_sound_file='./Resources/skeet.wav')
ding = pygame.mixer.Sound('./Resources/ding.wav')
ding2 = pygame.mixer.Sound('./Resources/ding2.wav')
fragimages = [loadImage('./Resources/frag0.png', .3),
              loadImage('./Resources/frag1.png', .3),
              loadImage('./Resources/frag2.png', .3)]
bullets = []
particles = []
replay()

## main loop ##
while True: # the main game loop
    DISPLAYSURF.fill(WHITE)
    
    handleEvents(pygame.event.get(), DISPLAYSURF)

    # update world #
    #if countdown == 0:
    any_active = False
    for bullet in bullets:
        bullet.update()
        if bullet.active:
            any_active = True

    for particle in particles:
        particle.update()

    target.update()

    # count down
    if mode == 0:
        if countdown > 0:
            if countdown == 270 or countdown == 180 or countdown == 90:
                ding.play()
                pass
            if countdown == 1:
                ding2.play()
                time = 0
            countdown -= 1
        else:
            if timeleft() <= 0:
                gameover('Out of time')

        if not any_active and ammo == 0:
            gameover('Out of ammo')

    draw(DISPLAYSURF)

    time += fpsClock.tick(FPS)

