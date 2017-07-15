import math
import random

import pygame

from vector import Vector

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 800
SCREEN = Vector(SCREEN_WIDTH, SCREEN_HEIGHT)
GRIDSIZE = 16

COLORS = {
    "BLACK"     : (  0,   0,   0),
    "RED"       : (255,   0,   0),
    "YELLOW"    : (255, 255,   0),
    "GREEN"     : (  0, 255,   0),
    "CYAN"      : (  0, 255, 255),
    "BLUE"      : (  0,   0, 255),
    "MAGENTA"   : (255,   0, 255),
    "LIGHTGREY" : ( 50,  50,  50),
    "DARKGREY"  : ( 25,  25,  25),
    "WHITE"     : (255, 255, 255),
}


class Entity(object):
    database = []
    def __init__(self, color, radius, position, velocity=None):
        Entity.database.append(self)
        self.position = position
        if velocity == None:
            self.velocity = Vector(0, 0)
        else:
            self.velocity = velocity
        self.radius = radius
        self.color = color

    def render(self, screen):
        pygame.draw.circle( screen,
                            self.color,
                            self.position.round().tuple,
                            self.radius,
                            1)

    def update(self, dt):
        self.position += (self.velocity * dt)
        self.position %= SCREEN
    def collides_with(self, other):
        dist = self.position.distance(other.position)
        return dist < (self.radius + other.radius)

    def delete(self):
        Entity.database.remove(self)
        try:
            self.database.remove(self)
        except ValueError:
            # self does not have a database
            pass



class BoundingBox(object):
    def __init__(self, center, radius, sel=False):
        self.center = center
        self.radius = radius
        self.fill = None
        self.sel = sel

        self.minval = self.center - self.radius
        self.maxval = self.center + self.radius

        self.start = self.center.round()

    def update(self, coord):
        val = Vector(coord)
        if val.x > self.start.x:
            self.maxval[0] = val.x
        else:
            self.minval[0] = val.x

        if val.y > self.start.y:
            self.maxval[1] = val.y
        else:
            self.minval[1] = val.y

        self.radius = (self.maxval - self.minval) / 2
        self.center = self.radius + self.minval

    def contains(self, coord):
        return self.minval <= coord < self.maxval

    def intersects(self, box):
        if self.minval.x > box.maxval.x:
            return False
        if self.minval.y > box.maxval.y:
            return False
        if self.maxval.x < box.minval.x:
            return False
        if self.maxval.y < box.minval.y:
            return False
        return True

    def render(self, screen):
        topleft = self.minval.round().tuple
        widthheight = (self.radius * 2).round().tuple
        rect = pygame.Rect(topleft, widthheight)

        if self.fill is not None:
            pygame.draw.rect(
                    screen,
                    self.fill,
                    rect,
                    0)

        if self.sel:
            color = COLORS["WHITE"]
        else:
            color = COLORS["DARKGREY"]

        pygame.draw.rect(
                screen,
                color,
                rect,
                1)

class QuadTree(object):
    database = []
    def __init__(self, bounds, parent=None):
        QuadTree.database.append(self)
        self.bounds = bounds

        self.points = []
        self.parent = parent
        self.children = None

        self.depth = int(min(self.bounds.radius.map(math.log, 2))) - int(math.log(GRIDSIZE, 2))

    def subdivide(self):
        if (self.depth - 1) > 0:
            half = (self.bounds.radius / 2.).round()
            nw = self.bounds.center - half
            ne = Vector(self.bounds.center.x + half.x, self.bounds.center.y - half.y)
            sw = Vector(self.bounds.center.x - half.x, self.bounds.center.y + half.y)
            se = self.bounds.center + half

            self.children = [
                    QuadTree(BoundingBox(nw, half), parent=self),
                    QuadTree(BoundingBox(ne, half), parent=self),
                    QuadTree(BoundingBox(sw, half), parent=self),
                    QuadTree(BoundingBox(se, half), parent=self)
                    ]
            for quad in self.children:
                if quad.add_point(self.points[0]):
                    self.points = []
                    return True
        return True

    def _merge(self):
        if self.children is not None:
            points = []
            for quad in self.children:
                # assume that the other quads are reduced
                if quad.children is not None:
                    return False
                if quad.points != []:
                    points.extend(quad.points)

            if len(points) > 1:
                return False
            elif len(points) == 1:
                self.points = points[0:1]
                self.points[0].quad = self
                for quad in self.children:
                    quad.delete()
                self.children = None
            else:
                self.points = []
            return True
        else:
            return True

    def merge(self):
        parent = self.parent
        good = True
        while parent != None and good:
            # assert parent.children is not None
            good = parent._merge()
            parent = parent.parent

    def add_point(self, point):
        if self.bounds.contains(point.position):
            if self.children is None:
                if self.points == []:
                    self.points = [point]
                    point.quad = self
                    return True
                elif (self.depth - 1) <= 0:
                    self.points.append(point)
                    point.quad = self
                    return True
                if not self.subdivide():
                    return False
            # assert self.children
            for quad in self.children:
                if quad.add_point(point):
                    return True
            return False
        else:
            return False

    def add_coord(self, coord):
        point = Point(coord)
        return self.add_point(point)

    def remove_point(self, point):
        if self.points == []:
            if point in self.point:
                self.release_point(self, point)
        return self.remove_coord(point.position)

    def remove_coord(self, coord):
        if self.bounds.contains(coord):
            if self.points != []:
                for point in self.points:
                    if point.position == coord:
                        point.delete()
                        self.points.remove(point)
                        self.merge()
                        return True
            if self.children is not None:
                for quad in self.children:
                    if quad.remove_coord(coord):
                        return True
            return False
        else:
            return False

    def release_point(self, point):
        if point in self.points:
            point.quad = None
            self.points.remove(point)
            self.merge()
            return True
        else:
            return False

    def query(self, box):
        quads = []
        if self.bounds.intersects(box):
            if self.children is not None:
                for quad in self.children:
                    quads.extend(quad.query(box))
            else:
                if self.points:
                    return [self]
        return quads

    def delete(self):
        QuadTree.database.remove(self)
        self.points = []
        self.children = None
        del self

    def render(self, screen):
        if self.children is not None:
            for quad in self.children:
                quad.render(screen)
        else:
            self.bounds.render(screen)


class Point(Entity):
    database = []
    def __init__(self, coords):
        position = Vector(coords)
        color = COLORS["RED"]
        angle = random.uniform(0, 2 * 3.14159265)
        velocity = Vector(math.cos(angle), math.sin(angle)) * 50
        super(Point, self).__init__(color, 2, position, velocity)
        Point.database.append(self)
        self.quad = None

    def update_quad(self, tree):
        quad = self.quad
        if not self.quad.bounds.contains(self.position):
            self.quad.release_point(self)
            tree.add_point(self)
            return True
        else:
            return False

if __name__ == '__main__':
    import time

    def main(screen):
        clock = pygame.time.Clock()

        tree = QuadTree(BoundingBox(SCREEN/2, SCREEN/2))

        onsel = False
        ongrid = False
        ondelete = False
        sel = BoundingBox(Vector(0,0), Vector(0, 0), sel=True)
        start = None
        last = time.time()
        rate = 1/60.
        # for i in xrange(500):
        #     tree.add_coord(SCREEN * Vector(random.random(), random.random()))
        while True:
            screen.fill(COLORS["BLACK"])

            pressedkeys = pygame.key.get_pressed()
            altpressed = pressedkeys[pygame.K_LALT] or pressedkeys[pygame.K_RALT]
            filtered = []
            quit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit = True
                    elif event.key == pygame.K_F4 and altpressed:
                        quit = True
                    elif event.key == pygame.K_SPACE:
                        ondelete = True
                    elif event.key == pygame.K_a:
                        ongrid = not ongrid

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not onsel:
                        onsel = True
                        sel = BoundingBox(Vector(event.pos), Vector(0, 0), sel=True)
                        start = Vector(event.pos)
                        sel.minval = start
                elif event.type == pygame.MOUSEMOTION and onsel:
                    sel.update(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    onsel = False
                    if start.distance2(Vector(event.pos)) < 9:
                        tree.add_coord(event.pos)
                if not quit:
                    filtered.append(event)
            if quit:
                break

            for point in Point.database:
                point.update(rate)
                point.update_quad(tree)
                point.color = COLORS["RED"]


            if onsel:
                selection = tree.query(sel)
                dele = []
                for quad in selection:
                    quad.bounds.fill = COLORS["LIGHTGREY"]
                    for point in quad.points:
                        if sel.contains(point.position):
                            if ondelete:
                                dele.append(point)
                            else:
                                point.color = COLORS["GREEN"]
                for point in dele:
                    point.quad.remove_point(point)
                ondelete = False

            if ongrid:
                tree.render(screen)
            for point in Point.database:
                point.render(screen)

            if onsel:
                for quad in selection:
                    quad.bounds.fill = None
                sel.render(screen)

            pygame.display.flip()
            clock.tick(60)
            if  time.time() - last > 5:
                print clock.get_fps(), len(Point.database)
                last =  time.time()


    pygame.init()
    screen = pygame.display.set_mode(SCREEN.tuple)
    main(screen)
    pygame.quit()