from constants import *
import autoload as a


class QuadTree:
    def __init__(self, rect, nDepth=0):
        # Keeps track of my depth level
        self.depth = nDepth

        # My rect, to check if actor is inside or not
        self.rect = rect

        # To hold my potential kids
        self.kids = [None] * 4

        # Actors that I own
        self.actors = []

        # Prepare rects for my kids, used to check if actor is in my kids, if so make kids
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

    # Called when room changed, set my rect to be as big as room
    def set_rect(self, rect):
        # Clear first, removes all existing kids
        self.clear()

        # Update my rect
        self.rect = rect

        # Prepare rects for my kids, used to check if actor is in my kids, if so make kids
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

    # Removes all actors and kids, until only root is left
    def clear(self):
        # Clear actor
        self.actors.clear()

        # Tell children to clear and empty themselves
        for i in range(4):
            if self.kids[i]:
                self.kids[i].clear()
                self.kids[i] = None

    # In case I need to know how many actors are in this quad
    def size(self):
        # Return total amount of actors in this quad
        total_actors = len(self.actors)
        for i in range(4):
            if self.kids[i]:
                total_actors += self.kids[i].size()
        return total_actors

    # Called when root first created or when actors position changed / relocated
    def insert(self, given_actor):
        for i in range(4):
            # Given actor is completely inside one of my kid?
            if self.kids_rects[i].contains(given_actor.rect):
                # Still inside limit? Go to next depth / level deeper
                if self.depth + 1 < MAX_QUADTREE_DEPTH:

                    # No child
                    if not self.kids[i]:

                        # Create child
                        self.kids[i] = QuadTree(
                            self.kids_rects[i], self.depth + 1)

                    # Got child? Or from creation above? Add given_actor to it
                    self.kids[i].insert(given_actor)
                    return

        # Actors is not completely inside any kids? Then its mine
        self.actors.append(given_actor)

        # Fill global book, store the mapping of actor to me
        a.actor_to_quad[given_actor.id] = self

    # Return actors list that overlap with given rect
    def search(self, given_rect):
        # Prepare output
        found_actors = []

        # Recurssion search, this is expensive
        self.search_helper(given_rect, found_actors)

        # Return output
        return found_actors

    # Search helper above
    def search_helper(self, given_rect, found_actors):
        # Check my actors, collect actors in me that overlap with given rect
        for actor in self.actors:
            if given_rect.colliderect(actor.rect):
                found_actors.append(actor)

        # Check my kids see if they can add actor
        for i in range(4):
            # I have kids?
            if self.kids[i]:
                # This kid is completely inside the given rect, dump all of its actors to collection
                if given_rect.contains(self.kids_rects[i]):
                    self.kids[i].add_actors(found_actors)

                # This kid only overlap given rect? Tell them to search again, recurssion
                elif self.kids_rects[i].colliderect(given_rect):
                    self.kids[i].search_helper(given_rect, found_actors)

    # Used by kids to dump all of their actors and their subsequent kids actors to search output
    def add_actors(self, found_actors):
        # Dump all of my actors into collection
        for actor in self.actors:
            found_actors.append(actor)

        # Dump all my children actors into collection
        for i in range(4):
            if self.kids[i]:
                self.kids[i].add_actors(found_actors)

    # Remove a certain actor from a certain quad (section / kid)
    def remove_actor(self, given_actor):
        # Make sure that id is valid, it is in the book
        if given_actor.id in a.actor_to_quad:
            # Use the actor id to immediately get the quad it is in
            quad_tree = a.actor_to_quad[given_actor.id]

            # Make sure that the given actor is in the quad from book
            if given_actor in quad_tree.actors:
                # Remove actor from that quad
                quad_tree.actors.remove(given_actor)

            # Delete that book row
            del a.actor_to_quad[given_actor.id]

            # 200 deleted ok
            return True

        # 400 not found
        return False

    # Call this and pass the actor right after they have moved / updated their position
    def relocate(self, given_actor):
        if self.remove_actor(given_actor):
            self.insert(given_actor)

    # Debugging purposes to show all of the quads (sections / kids)
    def draw(self):
        # Draw the current quad
        x = self.rect.x - a.camera.rect.x
        y = self.rect.y - a.camera.rect.y
        pg.draw.rect(DEBUG_SURF, "cyan",
                     ((x, y), (self.rect.width, self.rect.height)), 1)

        # Draw how many actors I have
        FONT.render_to(DEBUG_SURF, (x, y),
                       f'actors: {len(self.actors)}', "white", "black")

        # Recursively draw kids
        for i in range(4):
            if self.kids[i]:
                self.kids[i].draw()

    # In case I need to get all of the actors instance from this quad
    def get_all_actors(self):
        # Prepare output
        all_actors = []

        # Iterate over all quads in actor_to_quad
        for quad_tree in a.actor_to_quad.values():
            # Add actors from each quad to the list
            all_actors.extend(quad_tree.actors)

        # Return output
        return all_actors
