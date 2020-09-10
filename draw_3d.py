#!/usr/bin/env python3

from math import sin, cos, pi
from pygame import Surface, display, event, gfxdraw, init, key
from pygame.locals import K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_PAGEUP, K_PAGEDOWN, K_m, KEYDOWN, QUIT, SRCALPHA
from time import time


class Mesh(object):
    def __init__(self, vertices, faces):
        for vertex in vertices:
            if type(vertex) != tuple or len(vertex) != 3:
                raise ValueError(f'All vertices must be a 3-tuple of coordinates, but this one is not: {vertex}')

        for face in faces:
            if type(face) != tuple or len(face) != 3:
                raise ValueError(f'All faces must be a 3-tuple of vertex numbers, but this one is not: {face}')

            for vertex_index in face:
                if vertex_index < 0 or vertex_index > len(vertices) - 1:
                    raise IndexError('Vertices in face {face} out of range of vertices in mesh')

        self.vertices = vertices
        self.faces = faces


class Dot(Surface):
    def __init__(self):
        global screen

        scale = 80
        color = (255, 255, 255)

        super().__init__((screen.get_width() / scale,
                          screen.get_height() / scale * (screen.get_width() / screen.get_height())),
                         flags=SRCALPHA)

        gfxdraw.filled_circle(self,
                              self.get_width() // 2,
                              self.get_height() // 2,
                              self.get_width() // 2 - 1,
                              color)


class Camera(object):
    def __init__(self):
        global screen

        self.origin = ((0, 0, 0),
                       (0, 0, 0))

        self.width = 1.0
        self.height = self.width * screen.get_height() / screen.get_width()
        self.focal_length = 0.6

    def project_coord(self, x, y, z):
        global screen

        scale_x = (x / self.width) * (self.focal_length / y) + 0.5
        scale_y = (z / self.height) * (self.focal_length / y) + 0.5

        screen_x = int(scale_x * screen.get_width())
        screen_y = int(scale_y * screen.get_height())
        return screen_x, screen_y


def draw_dot(x, y):
    global screen

    # Centre dot by on x and y by calculating offsets relative to surface size
    x_offset, y_offset = tuple(s // 2 for s in dot.get_size())

    # Convert co-ordinates to origin in bottom-left, then blit
    screen.blit(dot,
                (x - x_offset,
                 screen.get_height() - (y + y_offset)))


def draw_line(x1, y1, x2, y2):
    global screen

    color = (255, 255, 255)
    screen_height = screen.get_height()

    if any([abs(c) > 32666 for c in [x1, x2, y1, y2]]):
        return
    else:
        gfxdraw.line(screen,
                     x1,
                     screen_height - y1,
                     x2,
                     screen_height - y2,
                     color)


def draw_mesh(mesh, x, y, z):
    global screen
    global camera

    for vertex in mesh.vertices:
        screen_coords = camera.project_coord(vertex[0] + x,
                                             vertex[1] + y,
                                             vertex[2] + z)

        draw_dot(*screen_coords)
        for vertex2 in mesh.vertices:
            if vertex2 == vertex:
                continue

            screen_coords_v2 = camera.project_coord(vertex2[0] + x,
                                                    vertex2[1] + y,
                                                    vertex2[2] + z)
            draw_line(*screen_coords, *screen_coords_v2)


def main():
    global screen
    global camera
    global dot

    init()

    # Init globals
    screen = display.set_mode((1920, 1080))
    camera = Camera()
    dot = Dot()

    # Init locals
    test_cube = Mesh([(0, 0, 0),
                      (0, 2.0, 0),
                      (2.0, 2.0, 0),
                      (2.0, 0, 0),
                      (0, 0, 2.0),
                      (0, 2.0, 2.0),
                      (2.0, 2.0, 2.0),
                      (2.0, 0, 2.0)],
                     [])
    mode = 0

    # Fill background
    background = Surface(screen.get_size())

    tick_length = 1 / 25
    tick = 0
    period = 10
    running = True
    x, y, z = 0, 0, 0
    while running:
        # Get new tick
        last_tick = time()
        tick += 1

        # Handle events
        for new_event in event.get():
            if new_event.type == QUIT:
                running = False

            elif new_event.type == KEYDOWN:
                if new_event.key == K_ESCAPE:
                    running = False
                elif new_event.key == K_m:
                    mode = (mode + 1) % 2

        # Draw some stuff
        screen.blit(background, (0, 0))

        if mode == 0:
            x = sin((tick % (period / tick_length) / (period / tick_length)) * 2 * pi) * 3 - 0.5
            y = 6 + cos((tick % (period / tick_length) / (period / tick_length)) * 4 * pi) * 4 - 0.5
            z = cos((tick % (period / tick_length) / (period / tick_length)) * 2 * pi) * 3 - 0.5
        elif mode == 1:
            keys = key.get_pressed()
            if keys[K_UP]:
                z += 0.2
            if keys[K_DOWN]:
                z -= 0.2
            if keys[K_LEFT]:
                x -= 0.2
            if keys[K_RIGHT]:
                x += 0.2
            if keys[K_PAGEUP]:
                y += 0.2
            if keys[K_PAGEDOWN]:
                y -= 0.2
        else:
            raise ValueError(f'Invalid mode: {mode}')
        draw_mesh(test_cube, x, y, z)

        display.flip()

        # Wait for next tick
        while time() < last_tick + tick_length:
            pass


if __name__ == '__main__':
    main()
