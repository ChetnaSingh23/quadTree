#   Python+Pillow/Pygame program to illustrate computing the Mandelbrot Set.
#   Note that it's far from efficient; it can easily be sped up!

 
import pygame                                       # see pygame.org
from PIL import Image
width, height = 1000,1000                           # display window size
screen = pygame.display.set_mode((width, height))   # initialise pygame window
img=Image.new("RGB",(width,height))
xaxis = width / 1.5 + 140                           # scaling for x & y axes
yaxis = height / 2
scale = 400
maxit = 99                                          # maximum iterations
for iy in range(int(height/2)+1):                   # scan y-axis
    for ix in range(width):                         # scan x-axis
        z = 0 + 0j                                  # initialise z=0
                                                    # map pixel position to complex plane
        c = complex(float(ix - xaxis) / scale, float(iy - yaxis) / scale)
 
        for it in range(maxit):                     # up to maximum iterations:
            z = z*z + c                             # iterate z^2 + c
            if abs(z) > 2:                          # z is flying off to infinity!
                col=(it % 4 * 64, it % 8 * 32, it % 16 * 16)    # pick a colour
                break                               # break out of closest loop
        else:                                       # loop finished so
            col = (0, 0, 0)                         # point is in set = colour black
 
        screen.set_at((ix, iy), col)                # set colour on top half
        screen.set_at((ix, height-iy), col)         # set colour on bottom half
        img.putpixel((ix,iy),col)
        img.putpixel((ix,height-iy-1),col)
    pygame.display.update()                         # update window on screen
raw_input("Done")                                   # picture disappears when Enter
