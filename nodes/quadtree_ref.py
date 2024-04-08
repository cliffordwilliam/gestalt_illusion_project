import pygame as pg
import random
from enum import Enum
from timeit import default_timer as timer
from sys import exit
import pygame as pg

pg.init()

# Run this as a separate stand alone file
# I made this for studying how quadtrees work
# Info and data is from:
# https://youtu.be/ASAowY6yJII?si=SJUmD0M7-XpeVp00

# Constants
TILE_S = 16
FPS = 60
NATIVE_W = 320
NATIVE_H = 176
WINDOW_W = 320
WINDOW_H = 180

# Pg constants
NATIVE_SURF = pg.Surface((NATIVE_W, NATIVE_H))
NATIVE_RECT = NATIVE_SURF.get_rect()

CLOCK = pg.time.Clock()
EVENTS = [pg.KEYDOWN, pg.KEYUP, pg.QUIT]

RESOLUTION = 4
window_w = WINDOW_W * RESOLUTION
window_h = WINDOW_H * RESOLUTION
window_surf = pg.display.set_mode((window_w, window_h))
y_offset = 2 * RESOLUTION

# Define constants
MAX_DEPTH = 8

# Camera
cam = pg.FRect(0, 0, NATIVE_W, NATIVE_H)

# Biggest possible room in my game
# room_rect = pg.FRect(0, 0, NATIVE_W * 2, NATIVE_H * 2)

# Flag to toggle between quadtree and naive checks
use_quadtree = True
# use_quadtree = False


class QuadTree:
    def __init__(self, rect, nDepth=0):
        self.depth = nDepth
        self.rect = rect
        self.kid = [None] * 4
        self.actors = []

    def set_rect(self, rect):
        # Clear first
        self.clear()

        # Update my rect
        self.rect = rect

        # Update my children
        vChildSize = (self.rect.size[0] / 2.0, self.rect.size[1] / 2.0)
        self.kid = [
            pg.FRect(self.rect.topleft, vChildSize),
            pg.FRect((self.rect.topleft[0] + vChildSize[0],
                     self.rect.topleft[1]), vChildSize),
            pg.FRect((self.rect.topleft[0], self.rect.topleft[1] +
                     vChildSize[1]), vChildSize),
            pg.FRect((self.rect.topleft[0] + vChildSize[0],
                     self.rect.topleft[1] + vChildSize[1]), vChildSize)
        ]

    def clear(self):
        # Clear actor
        self.actors.clear()

        # Tell children to clear and empty themselves
        for i in range(4):
            if self.kid[i]:
                self.kid[i].clear()
                self.kid[i] = None

    def size(self):
        # Return total amount of actors
        total_actors = len(self.actors)
        for i in range(4):
            if self.kid[i]:
                total_actors += self.kid[i].size()
        return total_actors

    def insert(self, actor):
        for i in range(4):
            if self.kid[i] and self.kid[i].contains(actor):
                # Inside limit
                if self.depth + 1 < MAX_DEPTH:

                    # No child
                    if not self.kid[i]:

                        # Create child
                        self.kid[i] = QuadTree(
                            self.kid[i], self.depth + 1)

                    # Got child, add actor to it
                    self.kid[i].insert(actor)
                    return

        # Actor did not fit in any child, then its mine
        self.actors.append(actor)

    def search(self, given_rect):
        found_actors = []
        self.search_helper(given_rect, found_actors)
        return found_actors

    def search_helper(self, given_rect, found_actors):
        # Check my actors, collect actors in me that overlap with given rect
        for actor in self.actors:
            if given_rect.colliderect(actor):
                found_actors.append(actor)

        # Check children see if they can add actor
        for i in range(4):
            if self.kid[i]:
                # This child is entirely in given rect, dump all of its actors to collection
                if given_rect.contains(self.kid[i].rect):
                    self.kid[i].add_actors(found_actors)

                # This child only overlap? Tell them to search again
                elif self.kid[i].rect.colliderect(given_rect):
                    self.kid[i].search_helper(given_rect, found_actors)

    def add_actors(self, found_actors):
        # Dump all of my actors into collection
        for actor in self.actors:
            found_actors.append(actor)

        # Dump all my children actors into collection
        for i in range(4):
            if self.kid[i]:
                self.kid[i].add_actors(found_actors)


# Quadtree init, as big as biggest room
# quad_tree = QuadTree(
#     pg.FRect((0.0, 0.0), (100000.0, 100000.0)))

quad_tree = QuadTree(
    # Adjusted size to fit the largest level
    pg.FRect((0.0, 0.0), (400.0, 200.0)))


# 1000000 things in 1000000 by 1000000 room size (bullets, enemies, butterfly, whatever)
# Actor size ranging from 0 - 100
total_actors_rect = []
total_actors_len = 1000
for _ in range(total_actors_len):
    # Init actor pos and size within level boundaries
    # pos = (random.uniform(0.0, 100000.0),
    #        random.uniform(0.0, 100000.0))
    # size = (random.uniform(0.1, 100.0), random.uniform(0.1, 100.0))

    # Init actor pos and size within level boundaries
    pos = (random.uniform(0.0, 320.0), random.uniform(
        0.0, 176.0))  # Adjusted to fit level size
    size = (random.uniform(0.1, 100.0), random.uniform(0.1, 100.0))

    # Instance random rect
    actor_rect = pg.FRect((pos), (size))

    # Collect for naive check iteration
    total_actors_rect.append(actor_rect)

    # Collect actor to the quadtree
    quad_tree.insert(actor_rect)

# The more things are on the camera, the less improvement you get
# If what is on the screen in significantly smaller than the whole total hidden ones, then it works good

tot_dt = 0
tot_duration = 0
tot_iter = 0

while 1:
    # region Get dt
    dt = CLOCK.tick(FPS)

    # For timing test
    tot_dt += dt
    if tot_dt > 10000:
        print(f'average: {tot_duration / tot_iter}')
        pg.quit()
        exit()

    # Get event
    for event in pg.event.get(EVENTS):
        # region Window quit
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        # endregion Window quit

        # region Quad toggle
        if event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                # Toggle between quadtree and naive checks
                use_quadtree = not use_quadtree
        # endregion Quad toggle

    # Move cam
    cam.x += (pg.key.get_pressed()
              [pg.K_RIGHT] - pg.key.get_pressed()[pg.K_LEFT]) * 10
    cam.y += (pg.key.get_pressed()
              [pg.K_DOWN] - pg.key.get_pressed()[pg.K_UP]) * 10
    # cam.clamp_ip(room_rect)

    # Clear screen
    NATIVE_SURF.fill("white")

    # Draw
    if use_quadtree:
        # Start timer
        start = timer()

        found_actors = 0

        # Use quadtree to find nearby actors to my camera
        for actor in quad_tree.search(cam):
            # pos, size = actor
            x = actor.x - cam.x
            y = actor.y - cam.y
            pg.draw.rect(NATIVE_SURF, "red",
                         ((x, y), (actor.width, actor.height)), 1)
            found_actors += 1

        # End timer
        end = timer()
        duration = end - start
        tot_duration += duration
        tot_iter += 1

        print(f'quadtr: {found_actors} / {total_actors_len} in {duration}')
    else:
        # Start timer
        start = timer()

        found_actors = 0

        # Naive check each one to cam collide, if collide then draw
        for actor_rect in total_actors_rect:
            if actor_rect.colliderect(cam):
                x = actor_rect.x - cam.x
                y = actor_rect.y - cam.y
                w = actor_rect.width
                h = actor_rect.height
                pg.draw.rect(NATIVE_SURF, "green", (x, y, w, h), 1)
                found_actors += 1

        # End timer
        end = timer()
        duration = end - start
        tot_duration += duration
        tot_iter += 1

        print(f'linear: {found_actors} / {total_actors_len} in {duration}')

    # region Native to window and update window
    scaled_native_surf = pg.transform.scale_by(NATIVE_SURF, RESOLUTION)
    window_surf.blit(scaled_native_surf, (0, y_offset))
    pg.display.update()
    # endregion Native to window and update window
