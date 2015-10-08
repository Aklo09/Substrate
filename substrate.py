import math
import pygame
import pygame.gfxdraw
import numpy as np
import random

class SandPainter():
    def __init__(self, s):
        self.ss = s
        self.c = s.somecolor()
        self.g = random.uniform(0.01, 0.1)

    def render(self, x, y, ox, oy):
        self.g = self.g + random.uniform(-0.050, 0.050)
        if self.g < 0.0 : self.g=0.0
        if self.g > 1.0 : self.g=1.0

        grains = int(math.sqrt((ox-x)*(ox-x)+(oy-y)*(oy-y)))
        grains = 64
        
        # lay down grains of sand
        w = self.g / (grains - 1)
        
        for i in range(grains):
            a = 0.1 - i / (grains*10.0)
            
            self.c.a = int(a*256)
            
            pygame.gfxdraw.pixel(self.ss.surface,
                                int(ox + (x - ox) * math.sin(math.sin(i * w))),
                                int(oy + (y - oy) * math.sin(math.sin(i * w))),
                                self.c)


class Crack():
    
    def __init__(self, s):
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self.sp = SandPainter(s)
        self.ss = s
        self.color = pygame.Color(0,0,0)
        self.findStart()

    def findStart(self):

        ####
        #aa = [[x1,y1] for x1 in range(self.ss.dimx) for y1 in range(self.ss.dimy) if self.ss.cgrid[x1,y1] < 10000 ]

        #print(len(aa))
        #px, py = aa[random.randrange(len(aa))]

        px, py = random.choice(self.ss.used)

        a = self.ss.cgrid[px, py]
    
        if random.randrange(100) < 50 :
            a = a - 90 + random.randrange(-9, 10) # -2, 3
        else:
            a = a + 90 + random.randrange(-9, 10)
        
        self.x=px + 0.61*math.cos(a*math.pi/180.0)
        self.y=py + 0.61*math.sin(a*math.pi/180.0)
        self.t=a
        #print("Crack start: ", self.x, self.y, self.t)

    def move(self):
        self.x=self.x + 0.42*math.cos(self.t*math.pi/180.0)
        self.y=self.y + 0.42*math.sin(self.t*math.pi/180.0)

        z=0.33
        cx = int(self.x + random.uniform(-z,z))
        cy = int(self.y + random.uniform(-z,z))

        self.regionColor()

        pygame.gfxdraw.pixel(self.ss.surface,
                             int(self.x + random.uniform(-z,z)),
                             int(self.y + random.uniform(-z,z)),
                             self.color)

        if cx >= 0 and cx < self.ss.dimx and cy >= 0 and cy < self.ss.dimy :
            if self.ss.cgrid[cx, cy] > 10000 or abs(self.ss.cgrid[cx, cy] - self.t) < 5 :
                self.ss.cgrid[cx, cy] = int(self.t)
                self.ss.used.append([cx,cy])
            else:
                if abs(self.ss.cgrid[cx, cy] - self.t) > 2 :
                    self.findStart()
                    #self.ss.makeCrack()
                else:
                    print("???")
        else:
            self.findStart()
            #self.ss.makeCrack()

    def regionColor(self):
        rx=self.x
        ry=self.y
        openspace=True

        # find extents of open space
        while openspace:
            # move perpendicular to crack
            rx = rx + 0.81 * math.sin(self.t * math.pi/180)
            ry = ry - 0.81 * math.cos(self.t * math.pi/180)
            cx = int(rx)
            cy = int(ry)
            if cx >= 0 and cx < self.ss.dimx and cy >= 0 and cy < self.ss.dimy :
                if self.ss.cgrid[cx, cy] > 10000 :
                    openspace = True
                else:
                    openspace = False
            else:
                 openspace = False

        self.sp.render(rx,ry,self.x,self.y)
        
class Substrate():

    def __init__(self, x, y, s, fn, numcracks):
        
        super().__init__()
        
        self.dimx = x
        self.dimy = y

        self.surface = s
        
        self.maxcracks = 200       ###

        # grid of cracks
        self.cgrid = np.zeros((self.dimx, self.dimy))
        self.cracks = list()
        self.used = list()

        # color parameters
        self.maxpal = 512
        self.goodcolor = list()
        self.takecolor(fn)

        # sand painters
        self.sands = list()

        self.cgrid[:,:] = 10001

        #initial seeds
        for k in range(16):
            px = random.randrange(self.dimx)
            py = random.randrange(self.dimx)
            self.cgrid[px,py] = random.randrange(360)
            self.used.append([px,py])
            #print("Seed:",[px,py],self.cgrid[px,py])

        for k in range(numcracks):
            self.makeCrack()


    def takecolor(self, fn):
        
        b = pygame.image.load(fn)
        bx, by = b.get_size()
        numpal = 0
        
        for x in range(bx):
            for y in range(by):
                
                c = b.get_at((x, y))

                if c not in self.goodcolor:
                    if numpal < self.maxpal:
                        self.goodcolor.append(c)
                        numpal = numpal +1


    def somecolor(self):
        return random.choice(self.goodcolor)
      

    def makeCrack(self):
        if len(self.cracks) < self.maxcracks :
            self.cracks.append(Crack(self))
            return True
        else:
            return False
            

##-----------------------
                    
def setup(dimx=300, dimy=300, numcracks=3):

    pygame.init()

    surface = pygame.display.set_mode((int(dimx), int(dimy)))

    surface.fill((255,255,255))

    substrate = Substrate(dimx, dimy, surface, "background.png" , numcracks)

    return substrate

def Move(s, n):
    for i in range(n):
        for c in s.cracks:
            c.move()
        pygame.display.flip()



    


