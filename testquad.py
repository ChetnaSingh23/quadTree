import pygame, random
from collections import deque
from math import sqrt
 
side = height = 2**10        # must be a power of 2
width = int(1.5*side)
maxit = 1440                    # maximum iterations per point
csc = 360.0/maxit
randCol = False                 # random not continuous colours
sqrtCol = True                  # square root colour scale
colOff = 9                      # colour offset in range 0-360 (in HSV)
line = 0                        # thickness of square's border lines
 
#   Complex plane
xmin = -2.0
xmax = 1.0
xd = xmax - xmin
ymax = xd/3.0
ymin = -ymax
yd = ymax - ymin
xscale = xd / float(width)
yscale = yd / float(height)
 
def inCardioidOrBulb(x, y):
    '''
    http://en.wikipedia.org/wiki/Mandelbrot_set#Cardioid_.2F_bulb_checking
    '''
    y2 = y*y
    q = (x-0.25)**2+y2
    return (q*(q+(x-0.25))<y2/4.0 or (x+1.0)**2 + y2 <0.0625)
 
def mandel(ix, iy):
    ''' Is this pixel in the Mandelbrot Set; return escape time '''
 
    x =  xscale * ix + xmin     # Scale pixel coordinate to complex plane
    y = -yscale * iy + ymax
 
    if inCardioidOrBulb(x,y):   return maxit + 1
    c = complex(x, y)
    z = complex(0, 0)
    for it in range(maxit):
        z *= z
        z += c
        if abs(z) > 2:  break
    else:    it = maxit
    return   it               # in set
 
sfm = sqrt(float(maxit))
fg = pygame.Color(0, 0, 0, 0)
 
def col(it):
    ''' Make a colour palette '''
    if it >=  maxit: return pygame.Color(0, 0, 0, 0)
    if (randCol):
        it = random.randint(0, maxit - 1)
    elif (sqrtCol):
        it = int(sqrt(float(it)) * sfm)
    fg.hsva = ((it * csc + colOff) % 360, 100, 100, 0)
    return fg
 
def Mandelbrot():
#   Add 3 squares to queue, in a line on top of the real axis
    squares = deque([(0, 0, side / 2), (side / 2, 0, side / 2), (side,0,side/2)])
    c = (0,0,0)
#   Pop squares off the queue
    while squares:
        ix, iy, l = squares.popleft()
        l2 = l / 2
#       Determine colour
        if l ==  1:      # down to 1 pixel
            itav = mandel(ix, iy)
        elif l ==  2:
#        else:
#           Get iteration counts at 4 corners.
            it = [mandel(ix, iy),
                  mandel(ix + l - 1, iy),
                  mandel(ix + l - 1, iy + l - 1),
                  mandel(ix, iy + l - 1)]
            di = max(it) - min(it)
            itav = sum(it) / 4
        else:
#           Get iteration counts at 4 corners & midpoints
            it = [mandel(ix, iy),                   # top left
                  mandel(ix + l2 - 1, iy),          # top mid
                  mandel(ix + l - 1, iy),           # top right
                  mandel(ix + l - 1, iy+l2-1),      # mid right
                  mandel(ix + l2 - 1, iy+l2-1),     # mid
                  mandel(ix + l - 1, iy + l-1),     # bot right
                  mandel(ix + l2 - 1, iy + l-1),    # bot mid
                  mandel(ix, iy + l - 1),           # bot left
                  mandel(ix, iy + l2 - 1)           # mid left
            ]
            di = max(it) - min(it)
            itav = sum(it) / 9
 
        c = col(itav)
#       Draw square
        yn = side - iy - l
 
        if (line > 0):
#           Clunky way to add borders -
#               just shrink the square exposing colour behind!
            b = l - line
            d.fill(c, pygame.Rect(ix + 1, iy + 1, b, b))
            d.fill(c, pygame.Rect(ix + 1, yn + 1, b, b))
        else:
            d.fill(c, pygame.Rect(ix, iy, l, l))
            d.fill(c, pygame.Rect(ix, yn, l, l))
 
        pygame.display.update([(ix, iy, l, l), (ix, yn, l, l)])
 
#       Subdivide square; midpoints
        ixn = ix + l2
        iyn = iy + l2
 
#       If squares are more than 1 pixel,
#           and there's a variation of iteration counts
        if l > 1 and di > 0:
#           Add sub-squares to queue
            squares.append((ix, iy, l2))
            squares.append((ixn, iy, l2))
            squares.append((ixn, iyn, l2))
            squares.append((ix, iyn, l2))
 
d = pygame.display.set_mode((width, height))
pygame.display.set_caption("Application of Quadtree by Manikanta..")
 
Mandelbrot()