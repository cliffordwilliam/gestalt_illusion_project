from constants import *
import autoload as a


class Kinematic:
    '''
    How to use: 
        1: I am always a child of a moving actor
        2: Call my move function after you have updated velocity in actor
        3: Require a callback for me to call and pass what you collided with
        4: I Have debug draw in my update

    What will happen:
        1: For every frame, the following is done on x first then y axis
        2: Get magnitude direction based of vel
        3: Update is on wall, if input direction is 0, actor is not on wall
        4: Proceed if there is magnitude direction vel
        5: Compute displacement from dt and vel, store decimal in remainder, keep the int in displacement
        6: Do while loop as long as displacement int is not 0, decrease by 1 each iteration
        7: On each iteration convert pwner pos to index
        8: Use index to lookup table for collision neighbour checks
        9: If found something in neighbour, collect in list
        10: Iterate over every found enighbour cell and do aabb with my next frame pos
        11: If I did hit something, owner callback on hit. Let owner do what they want based on what it hits, also update is on wall and is on floor
        12: Did not hit anything? Move owner rect 1 px and go to next iteration
        13: After updating both x and y, check if I am on floor and is on wall, if yes then take away the owner x velocity
    '''

    def __init__(self, owner):
        # For movement while loop
        self.remainder_x = 0
        self.remainder_y = 0

        # Owner
        self.owner = owner

        self.is_on_floor = False
        self.is_on_wall = False

    def move(self, dt):
        # Game not ready? Return
        if a.game == None:
            return

        # Room not ready? Return
        if a.room == None:
            return

        # Camera not ready? Return
        if a.camera == None:
            return

        old_owner_tl = self.owner.rect.topleft

        # Debug draw owner real rect
        if a.game.is_debug:
            xd = self.owner.rect.x - a.camera.rect.x
            yd = self.owner.rect.y - a.camera.rect.y
            pg.draw.rect(DEBUG_SURF, "orange",
                         (xd, yd, self.owner.rect.width, self.owner.rect.height), 1)

        # region Update direction sign for movement
        direction_x = 0
        if self.owner.velocity.x > 0:
            direction_x = 1
        if self.owner.velocity.x < 0:
            direction_x = -1

        direction_y = 0
        if self.owner.velocity.y > 0:
            direction_y = 1
        if self.owner.velocity.y < 0:
            direction_y = -1
        # endregion Update direction sign for movement

        # region Update horizontal position
        # Distance to cover horizontally
        if direction_x != 0:
            amount = self.owner.velocity.x * dt
            self.remainder_x += amount
            displacement_x = round(self.remainder_x)
            self.remainder_x -= displacement_x
            displacement_x = abs(displacement_x)

            # Check 1px at a time
            while displacement_x > 0:
                # Actor currrent pos to tu
                possible_x_tu = (self.owner.rect.centerx //
                                 TILE_S) - a.room.x_tu
                possible_y_tu = (self.owner.rect.centery //
                                 TILE_S) - a.room.y_tu

                # Possible positions
                actor_tl_tu = (possible_x_tu - 1, possible_y_tu - 1)
                actor_tt_tu = (possible_x_tu, possible_y_tu - 1)
                actor_tr_tu = (possible_x_tu + 1, possible_y_tu - 1)
                actor_ml_tu = (possible_x_tu - 1, possible_y_tu - 0)
                actor_mr_tu = (possible_x_tu + 1, possible_y_tu - 0)
                actor_bl_tu = (possible_x_tu - 1, possible_y_tu + 1)
                actor_bm_tu = (possible_x_tu, possible_y_tu + 1)
                actor_br_tu = (possible_x_tu + 1, possible_y_tu + 1)

                # Select the ones needed with direction
                possible_pos_tus = []
                if direction_x == 0 and direction_y == 0:
                    possible_pos_tus = []
                elif direction_x == 0 and direction_y == -1:
                    possible_pos_tus = [actor_tl_tu,
                                        actor_tt_tu, actor_tr_tu]
                elif direction_x == 1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu, actor_tt_tu, actor_tr_tu, actor_mr_tu, actor_br_tu]
                elif direction_x == 1 and direction_y == 0:
                    possible_pos_tus = [actor_tr_tu,
                                        actor_mr_tu, actor_br_tu]
                elif direction_x == 1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_bm_tu, actor_br_tu, actor_mr_tu, actor_tr_tu]
                elif direction_x == 0 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_bm_tu, actor_br_tu]
                elif direction_x == -1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_tl_tu, actor_ml_tu, actor_bl_tu, actor_bm_tu, actor_br_tu]
                elif direction_x == -1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tl_tu, actor_ml_tu, actor_bl_tu]
                elif direction_x == -1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_ml_tu, actor_tl_tu, actor_tt_tu, actor_tr_tu]

                # Check filtered_possible_locations_tu
                possible_cells = []
                for possible_pos_tu in possible_pos_tus:
                    possible_x_tu = possible_pos_tu[0]
                    possible_y_tu = possible_pos_tu[1]

                    # Clamp withing room
                    possible_x_tu = max(
                        min(possible_x_tu, a.room.w_tu - 1), a.room.x_tu)
                    possible_y_tu = max(
                        min(possible_y_tu, a.room.h_tu - 1), a.room.y_tu)
                    possible_x_tu = int(possible_x_tu)
                    possible_y_tu = int(possible_y_tu)

                    # Tu -> cell
                    cell = a.room.collision_layer[possible_y_tu *
                                                  a.room.w_tu + possible_x_tu]

                    # Debug draw possible cell
                    if a.game.is_debug:
                        possible_xd = ((possible_x_tu + a.room.x_tu) * TILE_S) - \
                            a.camera.rect.x
                        possible_yd = ((possible_y_tu + a.room.y_tu) * TILE_S) - \
                            a.camera.rect.y
                        pg.draw.lines(
                            DEBUG_SURF,
                            "green",
                            True,
                            [
                                (possible_xd, possible_yd),
                                (possible_xd + TILE_S, possible_yd),
                                (possible_xd + TILE_S, possible_yd + TILE_S),
                                (possible_xd, possible_yd + TILE_S),
                            ]
                        )

                    # Air? look somewhere else
                    if cell == 0:
                        continue

                    # Found rect?
                    possible_cells.append(cell)

                    # Debug draw possible found cells
                    if a.game.is_debug:
                        pg.draw.rect(
                            DEBUG_SURF,
                            "yellow",
                            [
                                possible_xd,
                                possible_yd,
                                TILE_S,
                                TILE_S
                            ]
                        )

                # My future position
                xds = self.owner.rect.x
                yds = self.owner.rect.y
                xds += direction_x
                w = xds + self.owner.rect.width
                h = yds + self.owner.rect.height

                # Debug draw my future rect
                if a.game.is_debug:
                    pg.draw.rect(
                        DEBUG_SURF,
                        "blue",
                        [xds - a.camera.rect.x, yds - a.camera.rect.y,
                            self.owner.rect.width, self.owner.rect.height],
                        1
                    )

                # AABB with all possible neighbours
                collided_cells = []
                for cell in possible_cells:
                    # Cell rect
                    c_xds = cell["xds"]
                    c_yds = cell["yds"]
                    c_w = c_xds + TILE_S
                    c_h = c_yds + TILE_S
                    # Future hit something? Break set flag to true
                    if (c_xds < w and xds < c_w and c_yds < h and yds < c_h):
                        # Collect overlaps
                        collided_cells.append(cell)

                        # Update collision flag
                        self.is_on_wall = True

                # Collision callback
                is_stop = self.owner.on_collide(collided_cells)

                # Stop?
                if is_stop == True:
                    break

                # Future no hit? Move to next pixel
                self.is_on_wall = False
                displacement_x -= 1
                self.owner.rect.x += direction_x
                # self.owner.rect.clamp_ip(a.camera.rect)
        # endregion Update horizontal position

        # region Update vertical position
        # Distance to cover vertically
        if direction_y != 0:
            amount = self.owner.velocity.y * dt
            self.remainder_y += amount
            displacement_y = round(self.remainder_y)
            self.remainder_y -= displacement_y
            displacement_y = abs(displacement_y)

            # Check 1px at a time
            while displacement_y > 0:
                # owner currrent pos to tu
                possible_x_tu = (self.owner.rect.centerx //
                                 TILE_S) - a.room.x_tu
                possible_y_tu = (self.owner.rect.centery //
                                 TILE_S) - a.room.y_tu

                # Possible positions
                actor_tl_tu = (possible_x_tu - 1, possible_y_tu - 1)
                actor_tt_tu = (possible_x_tu, possible_y_tu - 1)
                actor_tr_tu = (possible_x_tu + 1, possible_y_tu - 1)
                actor_ml_tu = (possible_x_tu - 1, possible_y_tu - 0)
                actor_mr_tu = (possible_x_tu + 1, possible_y_tu - 0)
                actor_bl_tu = (possible_x_tu - 1, possible_y_tu + 1)
                actor_bm_tu = (possible_x_tu, possible_y_tu + 1)
                actor_br_tu = (possible_x_tu + 1, possible_y_tu + 1)

                # Select the ones needed with direction
                possible_pos_tus = []
                if direction_x == 0 and direction_y == 0:
                    possible_pos_tus = []
                elif direction_x == 0 and direction_y == -1:
                    possible_pos_tus = [actor_tl_tu,
                                        actor_tt_tu, actor_tr_tu]
                elif direction_x == 1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu, actor_tt_tu, actor_tr_tu, actor_mr_tu, actor_br_tu]
                elif direction_x == 1 and direction_y == 0:
                    possible_pos_tus = [actor_tr_tu,
                                        actor_mr_tu, actor_br_tu]
                elif direction_x == 1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_bm_tu, actor_br_tu, actor_mr_tu, actor_tr_tu]
                elif direction_x == 0 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_bm_tu, actor_br_tu]
                elif direction_x == -1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_tl_tu, actor_ml_tu, actor_bl_tu, actor_bm_tu, actor_br_tu]
                elif direction_x == -1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tl_tu, actor_ml_tu, actor_bl_tu]
                elif direction_x == -1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_bl_tu, actor_ml_tu, actor_tl_tu, actor_tt_tu, actor_tr_tu]

                # Check filtered_possible_locations_tu
                possible_cells = []
                for possible_pos_tu in possible_pos_tus:
                    possible_x_tu = possible_pos_tu[0]
                    possible_y_tu = possible_pos_tu[1]

                    # Clamp withing room
                    possible_x_tu = max(
                        min(possible_x_tu, a.room.w_tu - 1), a.room.x_tu)
                    possible_y_tu = max(
                        min(possible_y_tu, a.room.h_tu - 1), a.room.y_tu)
                    possible_x_tu = int(possible_x_tu)
                    possible_y_tu = int(possible_y_tu)

                    # Tu -> cell
                    cell = a.room.collision_layer[possible_y_tu *
                                                  a.room.w_tu + possible_x_tu]

                    # Debug draw possible cell
                    if a.game.is_debug:
                        possible_xd = ((possible_x_tu + a.room.x_tu) * TILE_S) - \
                            a.camera.rect.x
                        possible_yd = ((possible_y_tu + a.room.y_tu) * TILE_S) - \
                            a.camera.rect.y
                        pg.draw.lines(
                            DEBUG_SURF,
                            "green",
                            True,
                            [
                                (possible_xd, possible_yd),
                                (possible_xd + TILE_S, possible_yd),
                                (possible_xd + TILE_S, possible_yd + TILE_S),
                                (possible_xd, possible_yd + TILE_S),
                            ]
                        )

                    # Air? look somewhere else
                    if cell == 0:
                        continue

                    # Found rect?
                    possible_cells.append(cell)

                    # Debug draw possible found cells
                    if a.game.is_debug:
                        pg.draw.rect(
                            DEBUG_SURF,
                            "yellow",
                            [
                                possible_xd,
                                possible_yd,
                                TILE_S,
                                TILE_S
                            ]
                        )

                # My future position
                xds = self.owner.rect.x
                yds = self.owner.rect.y
                yds += direction_y
                w = xds + self.owner.rect.width
                h = yds + self.owner.rect.height

                # Debug draw my future rect
                if a.game.is_debug:
                    pg.draw.rect(
                        DEBUG_SURF,
                        "blue",
                        [xds - a.camera.rect.x, yds - a.camera.rect.y,
                            self.owner.rect.width, self.owner.rect.height],
                        1
                    )

                # AABB with all possible neighbours
                collided_cells = []
                for cell in possible_cells:
                    # Cell rect
                    c_xds = cell["xds"]
                    c_yds = cell["yds"]
                    c_w = c_xds + TILE_S
                    c_h = c_yds + TILE_S
                    # Future hit something? Break set flag to true
                    if (c_xds < w and xds < c_w and c_yds < h and yds < c_h):
                        # Collect overlaps
                        collided_cells.append(cell)

                        # If I am moving down
                        if direction_y == 1:
                            self.is_on_floor = True

                # Collision callback
                is_stop = self.owner.on_collide(collided_cells)

                # Stop?
                if is_stop == True:
                    break

                # Future no hit? Move to next pixel
                self.is_on_floor = False
                displacement_y -= 1
                self.owner.rect.y += direction_y
                # self.owner.rect.clamp_ip(a.camera.rect)
        # endregion Update vertical position

        # region Did owner move? relocate them in quadtree ONLY if they are moving things that is not the player
        if self.owner.rect.topleft != old_owner_tl:
            a.quad_tree.relocate(self.owner)
        # endregion Did owner move? relocate them in quadtree
