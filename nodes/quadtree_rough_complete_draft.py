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
# But this data is modified to reflect my game better
# Original had 1 million rects in a 1 miilion px square room
# After testing, with biggest room of size 640, 352 and actor sizes from 0 to 32
# There is no increase in performance at all, from 10 to 50000 actors

# The lone coder guy separates 2 trees, one for bushes and the other for bugs
# He did search on both for deleting and drawing

# Unless you have

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
room_rect = pg.FRect(0, 0, NATIVE_W * 2, NATIVE_H * 2)

# Book to store all quad with their actors
actor_to_quad = {}


class QuadTree:
    def __init__(self, rect, nDepth=0):
        self.depth = nDepth
        self.rect = rect
        self.kids = [None] * 4
        self.actors = []

        # Update my children
        vChildSize = (self.rect.size[0] / 2.0, self.rect.size[1] / 2.0)
        self.kids_rects = [
            pg.FRect(self.rect.topleft, vChildSize),
            pg.FRect((self.rect.topleft[0] + vChildSize[0],
                     self.rect.topleft[1]), vChildSize),
            pg.FRect((self.rect.topleft[0], self.rect.topleft[1] +
                     vChildSize[1]), vChildSize),
            pg.FRect((self.rect.topleft[0] + vChildSize[0],
                     self.rect.topleft[1] + vChildSize[1]), vChildSize)
        ]

    def set_rect(self, rect):
        # Clear first
        self.clear()

        # Update my rect
        self.rect = rect

        # Update my children
        vChildSize = (self.rect.size[0] / 2.0, self.rect.size[1] / 2.0)
        self.kids_rects = [
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
            if self.kids[i]:
                self.kids[i].clear()
                self.kids[i] = None

    def size(self):
        # Return total amount of actors
        total_actors = len(self.actors)
        for i in range(4):
            if self.kids[i]:
                total_actors += self.kids[i].size()
        return total_actors

    def insert(self, actor):
        for i in range(4):
            if self.kids_rects[i].contains(actor.rect):
                # Inside limit
                if self.depth + 1 < MAX_DEPTH:

                    # No child
                    if not self.kids[i]:

                        # Create child
                        self.kids[i] = QuadTree(
                            self.kids_rects[i], self.depth + 1)
                        self.kids[i].set_rect(self.kids_rects[i])

                    # Got child, add actor to it
                    self.kids[i].insert(actor)
                    return

        # Actor did not fit in any child, then its mine
        self.actors.append(actor)

        # Fill global book
        actor_to_quad[actor.id] = self  # Store the mapping

    def search(self, given_rect):
        found_actors = []
        self.search_helper(given_rect, found_actors)
        return found_actors

    def search_helper(self, given_rect, found_actors):
        # Check my actors, collect actors in me that overlap with given rect
        for actor in self.actors:
            if given_rect.colliderect(actor.rect):
                found_actors.append(actor)

        # Check children see if they can add actor
        for i in range(4):
            if self.kids[i]:
                # This child is entirely in given rect, dump all of its actors to collection
                if given_rect.contains(self.kids_rects[i]):
                    self.kids[i].add_actors(found_actors)

                # This child only overlap? Tell them to search again
                elif self.kids_rects[i].colliderect(given_rect):
                    self.kids[i].search_helper(given_rect, found_actors)

    def add_actors(self, found_actors):
        # Dump all of my actors into collection
        for actor in self.actors:
            found_actors.append(actor)

        # Dump all my children actors into collection
        for i in range(4):
            if self.kids[i]:
                self.kids[i].add_actors(found_actors)

    def remove_actor(self, given_actor):
        if given_actor.id in actor_to_quad:
            quad_tree = actor_to_quad[given_actor.id]
            if given_actor in quad_tree.actors:
                quad_tree.actors.remove(given_actor)
            del actor_to_quad[given_actor.id]
            return True
        return False

        # # Do I have actor? Remove it
        # if given_actor in self.actors:
        #     self.actors.remove(given_actor)
        #     return True

        # # I do not have it, check kids, kids have actor?
        # for i in range(4):
        #     if self.kids[i]:
        #         if self.kids[i].remove_actor(given_actor):
        #             return True

        # # I do not have it, kids do not have it, 404 actor not found
        # return False

    def relocate(self, given_actor):
        # This func is used for moving things
        # How can I remove it from quad
        # And insert it with new location
        if self.remove_actor(given_actor):
            self.insert(given_actor)

    def draw(self):
        # Draw the current quad
        x = self.rect.x - cam.x
        y = self.rect.y - cam.y
        pg.draw.rect(NATIVE_SURF, "cyan",
                     ((x, y), (self.rect.width, self.rect.height)), 1)

        # Recursively draw children
        for i in range(4):
            if self.kids[i]:
                self.kids[i].draw()

    def get_all_actors(self):
        all_actors = []

        # Iterate over all quads in actor_to_quad
        for quad_tree in actor_to_quad.values():
            # Add actors from each quad to the list
            all_actors.extend(quad_tree.actors)

        return all_actors


class Actor:
    def __init__(self, rect, id):
        self.id = id
        self.rect = rect
        self.velocity = [
            random.uniform(-0.1, 1.0), random.uniform(-0.1, 1.0)]


# Quadtree init, as big as biggest room
quad_tree = QuadTree(
    pg.FRect((0.0, 0.0), (100000.0, 100000.0)))
quad_tree.set_rect(pg.FRect((0.0, 0.0), (100000.0, 100000.0)))


# Flag to toggle between quadtree and naive checks
use_quadtree = True
# use_quadtree = False

# # Adjusted size to fit the largest room, 640, 352, 2 by 2 room tu
# quad_tree = QuadTree(
#     pg.FRect((0.0, 0.0), (640.0, 352.0)))
# quad_tree.set_rect(pg.FRect((0.0, 0.0), (640.0, 352.0)))

# 1000 things in 1000 by 1000 room size (bullets, enemies, butterfly, whatever)
# Actor size ranging from 0 - 32, actors should not be bigger than this in my game

speed = 1000
# speed = 10
total_actors = []
total_actors_len = 1000000
# total_actors_len = 1000
for i in range(total_actors_len):
    # # Init actor pos and size within level boundaries
    # pos = (random.uniform(0.0, 640.0), random.uniform(
    #     0.0, 352.0))  # Adjusted to fit level size
    # size = (random.uniform(0.1, 32.0), random.uniform(0.1, 32.0))

    # Init actor pos and size within level boundaries
    pos = (random.uniform(0.0, 100000.0),
           random.uniform(0.0, 100000.0))
    size = (random.uniform(0.1, 100.0), random.uniform(0.1, 100.0))

    # Instance random rect
    actor_rect = pg.FRect((pos), (size))
    actor = Actor(actor_rect, i)

    # Collect for naive check iteration
    total_actors.append(actor)

    # Collect actor to the quadtree
    quad_tree.insert(actor)

# The more things are on the camera, the less improvement you get
# If what is on the screen in significantly smaller than the whole total hidden ones, then it works good

tot_dt = 0
tot_duration = 0
tot_iter = 0

# Mouse cursor area to delete things
mouse_rect = pg.FRect(0.0, 0.0, 50.0, 50.0)

# Get all actors in quad
all_quad_actors = quad_tree.get_all_actors()

while 1:
    # region Get dt
    dt = CLOCK.tick(FPS)

    # For timing test
    # tot_dt += dt
    # if tot_dt > 10000:
    #     print(f'average: {tot_duration / tot_iter}')
    #     pg.quit()
    #     exit()

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
              [pg.K_d] - pg.key.get_pressed()[pg.K_a]) * speed
    cam.y += (pg.key.get_pressed()
              [pg.K_s] - pg.key.get_pressed()[pg.K_w]) * speed
    # cam.clamp_ip(room_rect)

    # region Move cursor
    pos = pg.mouse.get_pos()
    x = pos[0] // RESOLUTION
    y = pos[1] // RESOLUTION
    xd = x + cam.x
    yd = y + cam.y
    mouse_rect.center = (xd, yd)
    # endregion

    # Clear screen
    NATIVE_SURF.fill("white")

    # Draw
    if use_quadtree:
        # Start timer
        start = timer()

        found_actors = 0

        # # Move ALL quad actors regardless of position or whatever
        # for actor in all_quad_actors:
        #     # Update pos with velocity that is in view
        #     actor.rect.x += actor.velocity[0] * dt
        #     actor.rect.y += actor.velocity[1] * dt

        #     # Bounce off inner room walls
        #     if actor.rect.left < room_rect.left or actor.rect.right > room_rect.right:
        #         actor.rect.x -= actor.velocity[0] * dt
        #         actor.velocity[0] *= -1

        #     if actor.rect.top < room_rect.top or actor.rect.bottom > room_rect.bottom:
        #         actor.rect.y -= actor.velocity[1] * dt
        #         actor.velocity[1] *= -1

        #     # Relocate actor in quadtree
        #     quad_tree.relocate(actor)

        # Use quadtree to find nearby actors to my camera
        for actor in quad_tree.search(cam):
            # pos, size = actor
            x = actor.rect.x - cam.x
            y = actor.rect.y - cam.y
            pg.draw.rect(NATIVE_SURF, "red",
                         ((x, y), (actor.rect.width, actor.rect.height)), 1)

            # # Update pos with velocity that is in view
            # actor.rect.x += actor.velocity[0] * dt
            # actor.rect.y += actor.velocity[1] * dt

            # # Bounce off inner room walls
            # if actor.rect.left < room_rect.left or actor.rect.right > room_rect.right:
            #     actor.rect.x -= actor.velocity[0] * dt
            #     actor.velocity[0] *= -1

            # if actor.rect.top < room_rect.top or actor.rect.bottom > room_rect.bottom:
            #     actor.rect.y -= actor.velocity[1] * dt
            #     actor.velocity[1] *= -1

            # # Relocate actor in quadtree
            # quad_tree.relocate(actor)

            found_actors += 1

        # Use quadtree to find nearby actors to my cursor
        for actor in quad_tree.search(mouse_rect):
            # pos, size = actor
            x = actor.rect.x - cam.x
            y = actor.rect.y - cam.y
            pg.draw.rect(NATIVE_SURF, "yellow",
                         ((x, y), (actor.rect.width, actor.rect.height)), 1)

            # Delete if I press the K_a
            if pg.key.get_pressed()[pg.K_LSHIFT]:
                quad_tree.remove_actor(actor)

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

        # # Move ALL actors regardless of position or whatever
        # for actor in total_actors:
        #     # Update pos with velocity that is in view
        #     actor.rect.x += actor.velocity[0] * dt
        #     actor.rect.y += actor.velocity[1] * dt

        #     # Bounce off inner room walls
        #     if actor.rect.left < room_rect.left or actor.rect.right > room_rect.right:
        #         actor.rect.x -= actor.velocity[0] * dt
        #         actor.velocity[0] *= -1

        #     if actor.rect.top < room_rect.top or actor.rect.bottom > room_rect.bottom:
        #         actor.rect.y -= actor.velocity[1] * dt
        #         actor.velocity[1] *= -1

        # Naive check each one to cam collide, if collide then draw
        for actor in total_actors:
            if actor.rect.colliderect(cam):
                x = actor.rect.x - cam.x
                y = actor.rect.y - cam.y
                w = actor.rect.width
                h = actor.rect.height
                pg.draw.rect(NATIVE_SURF, "green", (x, y, w, h), 1)

                # # Update pos with velocity that is in view
                # actor.rect.x += actor.velocity[0] * dt
                # actor.rect.y += actor.velocity[1] * dt

                # # Bounce off inner room walls
                # if actor.rect.left < room_rect.left or actor.rect.right > room_rect.right:
                #     actor.rect.x -= actor.velocity[0] * dt
                #     actor.velocity[0] *= -1

                # if actor.rect.top < room_rect.top or actor.rect.bottom > room_rect.bottom:
                #     actor.rect.y -= actor.velocity[1] * dt
                #     actor.velocity[1] *= -1

                found_actors += 1

        # Use quadtree to find nearby actors to my cursor
        for actor in total_actors:
            if actor.rect.colliderect(mouse_rect):
                # pos, size = actor.rect
                x = actor.rect.x - cam.x
                y = actor.rect.y - cam.y
                pg.draw.rect(NATIVE_SURF, "yellow",
                             ((x, y), (actor.rect.width, actor.rect.height)), 1)

            # Delete if I press the K_a
            if pg.key.get_pressed()[pg.K_LSHIFT]:
                total_actors = [
                    actor for actor in total_actors if not actor.rect.colliderect(mouse_rect)]

        # End timer
        end = timer()
        duration = end - start
        tot_duration += duration
        tot_iter += 1

        print(f'linear: {found_actors} / {total_actors_len} in {duration}')

    # Draw room
    xs = room_rect.x - cam.x
    ys = room_rect.y - cam.y
    pg.draw.rect(NATIVE_SURF, "cyan",
                 (xs, ys, room_rect.width, room_rect.height), 1)

    if use_quadtree:
        quad_tree.draw()

    # region Draw cursor
    xs = xd - cam.x - (mouse_rect.width / 2)
    ys = yd - cam.y - mouse_rect.height / 2
    pg.draw.rect(NATIVE_SURF, "orange",
                 (xs, ys, mouse_rect.width, mouse_rect.height), 1)
    # endregion

    # region Native to window and update window
    scaled_native_surf = pg.transform.scale_by(NATIVE_SURF, RESOLUTION)
    window_surf.blit(scaled_native_surf, (0, y_offset))
    pg.display.update()
    # endregion Native to window and update window
