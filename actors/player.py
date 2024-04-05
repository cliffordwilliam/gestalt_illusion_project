from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
import autoload as a


class Player:
    def __init__(self):
        # region Debug stuff
        self.frame_counter = 0
        self.collided_cell_type = ""
        self.collided_cell_name = ""
        # endregion Debug stuff

        # region Font for debug
        self.font = font.Font(
            TTFS_DATA["cg_pixel_3x5_mono.ttf"]["path"],
            TTFS_DATA["cg_pixel_3x5_mono.ttf"]["h"]
        )
        self.font_h = TTFS_DATA["cg_pixel_3x5_mono.ttf"]["h"]
        self.font_w = TTFS_DATA["cg_pixel_3x5_mono.ttf"]["w"]
        # endregion Font for debug

        # Name
        self.name = "Player"

        # region Inputs
        self.is_left_pressed = 0
        self.is_right_pressed = 0
        self.is_down_pressed = False
        # endregion Inputs

        # region Player sprite sheets
        self.sprite_sheet = pg.image.load(
            PNGS_PATHS["player_sprite_sheet.png"])
        self.sprite_sheet_flip = pg.image.load(
            PNGS_PATHS["player_flip_sprite_sheet.png"])
        self.current_sprite_sheet = self.sprite_sheet
        # endregion Player sprite sheets

        # region Surface offset
        self.surface_offset_x = 21
        self.surface_offset_y = 14
        # endregion Surface offset

        # region Read json animation data
        self.aniamtion_data = {}
        with open(JSONS_PATHS["player_animation.json"], "r") as data:
            self.aniamtion_data = load(data)
        # endregion Read json animation data

        # Init starting region
        self.region = self.aniamtion_data["idle"]["frames_list"][0]["region"]

        # State
        self.state = "idle"

        # Facing direction
        self.facing_direction = 1
        self.old_facing_direction = self.facing_direction

        # Direction input
        self.direction = 0

        # Animator node
        self.animator = Animator(self, self.aniamtion_data, "idle")

        # Rect
        self.rect = pg.FRect(0, 0, 6, 31)

        # Movement
        self.max_run = 0.09
        self.run_lerp_weight = 0.2
        self.max_fall = 0.270
        self.normal_gravity = 0.000533
        self.heavy_gravity = 0.001066
        self.gravity = self.normal_gravity
        self.jump_vel = -0.2330
        self.velocity = pg.math.Vector2()

        # Kinematic
        self.kinematic = Kinematic(self)

        # Camera anchor
        self.camera_anchor = [
            self.rect.center[0] + (self.facing_direction * (2 * TILE_S)),
            self.rect.center[1]
        ]

        # Set to false on next frame immediately after falling 1 frame
        self.is_thin_fall = False

    # Called by kinematic
    def on_collide(self, cells):
        # World not ready? Return
        if a.world == None:
            return False

        # Unpack all found collided cells type and name
        for cell in cells:
            self.collided_cell_type = cell["type"]
            self.collided_cell_name = cell["name"]

            # Prioritize solids, found solid first? Stop
            if cell["type"] == "Solid":
                return True

            # Found door next? Pass thru it, handle vel
            elif cell["type"] == "Door":
                a.world.on_player_hit_door(cell)

                door_name = cell["name"]
                if door_name == "LeftDoor":
                    self.velocity.y = 0
                    self.kinematic.remainder_y = 0
                    return False

                elif door_name == "RightDoor":
                    self.velocity.y = 0
                    self.kinematic.remainder_y = 0
                    return False

                elif door_name == "UpDoor":
                    self.velocity.y /= 1.25
                    self.velocity.x = 0
                    self.kinematic.remainder_x = 0
                    return False

                elif door_name == "DownDoor":
                    self.velocity.x = 0
                    self.kinematic.remainder_x = 0
                    return False

            # Found thin?
            elif cell["type"] == "Thin":
                # Not passing thru?
                if self.is_thin_fall == False:
                    # If I am falling
                    if self.velocity.y > 0:
                        # Player real rect feet flushed on it? Stop
                        if (self.rect.bottom - cell["yds"]) == 0:
                            return True

    def event(self, event):
        if event.type == pg.KEYDOWN:
            # Just pressed left
            if event.key == a.game.key_bindings["left"]:
                # Set is pressed left 1
                self.is_left_pressed = 1

            # Just pressed right
            if event.key == a.game.key_bindings["right"]:
                # Set is pressed right 1
                self.is_right_pressed = 1

            # Just pressed down
            if event.key == a.game.key_bindings["down"]:
                # Set is pressed down true
                self.is_down_pressed = True

            # Just pressed jump
            elif event.key == a.game.key_bindings["jump"]:
                # Idle, run crouch can jump
                if self.state in [
                    "idle",
                    "run",
                    "crouch"
                ]:

                    # Cannot crouch to jump if on thin
                    if self.state == "crouch":
                        if self.collided_cell_type == "Thin":
                            # Can pass thru thin
                            self.is_thin_fall = True
                            return

                    # Exit up
                    self.set_state("up")

        elif event.type == pg.KEYUP:
            # Just released left
            if event.key == a.game.key_bindings["left"]:
                # Set is released left 0
                self.is_left_pressed = 0

            # Just released right
            if event.key == a.game.key_bindings["right"]:
                # Set is released right 0
                self.is_right_pressed = 0

            # Just released down
            if event.key == a.game.key_bindings["down"]:
                # Set is released down false
                self.is_down_pressed = False

            # Just released jump
            elif event.key == a.game.key_bindings["jump"]:
                # Idle, run crouch can jump
                if self.state == "up":
                    self.gravity = self.heavy_gravity

    def draw(self):
        # Room not ready? Return
        if a.room == None:
            return

        # Camera not ready? Return
        if a.camera == None:
            return

        # Game not ready? Return
        if a.game == None:
            return

        # region Draw player to native surface
        xds = (self.rect.x - self.surface_offset_x) - a.camera.rect.x
        yds = (self.rect.y - self.surface_offset_y) - a.camera.rect.y
        NATIVE_SURF.blit(
            self.current_sprite_sheet, (xds, yds), self.region
        )
        # endregion Draw player to native surface

        # region Debug draw
        if a.game.is_debug == True:
            # region Draw grid
            for i in range(20):
                offset = TILE_S * i
                xd = (offset - a.camera.rect.x) % NATIVE_W
                yd = (offset - a.camera.rect.y) % NATIVE_H
                pg.draw.line(DEBUG_SURF, "grey4", (xd, 0), (xd, NATIVE_H))
                pg.draw.line(DEBUG_SURF, "grey4", (0, yd), (NATIVE_W, yd))
            xd = -a.camera.rect.x % NATIVE_W
            yd = -a.camera.rect.y % NATIVE_H
            pg.draw.line(DEBUG_SURF, "grey8", (xd, 0), (xd, NATIVE_H))
            pg.draw.line(DEBUG_SURF, "grey8", (0, yd), (NATIVE_W, yd))
            self.font.render_to(
                DEBUG_SURF, (xd + self.font_w, yd + self.font_h), f"{
                    int(a.camera.rect.x - 1) // NATIVE_W + 1}{
                    int(a.camera.rect.y - 1) // NATIVE_H + 1}", "white"
            )
            # endregion Draw grid

            # region Draw fps
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h),
                f'fps: {int(CLOCK.get_fps())}',
                "white",
                "black"
            )
            # endregion Draw fps

            # region Draw frame counter
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 3),
                f'frame: {self.frame_counter}',
                "white",
                "black"
            )
            # endregion Draw frame counter

            # region Draw current animation
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 5),
                f'current animation: {self.animator.current_animation}',
                "white",
                "black"
            )
            # endregion Draw current animation

            # region Draw collision
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 7),
                f'collision type: {self.collided_cell_type}',
                "white",
                "black"
            )
            # endregion Draw collision

            # region Draw collision
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 9),
                f'collision name: {self.collided_cell_name}',
                "white",
                "black"
            )
            # endregion Draw collision

            # region Draw is on floor
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 11),
                f'is on floor: {self.kinematic.is_on_floor}',
                "white",
                "black"
            )
            # endregion Draw is on floor

            # region Draw is on wall
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 13),
                f'is on wall: {self.kinematic.is_on_wall}',
                "white",
                "black"
            )
            # endregion Draw is on wall

            # region Draw is on wall
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 15),
                f'state: {self.state}',
                "white",
                "black"
            )
            # endregion Draw is on wall

            # region Draw look dir
            value = "right" if self.facing_direction == 1 else "left"
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 17),
                f'facing direction: {value}',
                "white",
                "black"
            )
            # endregion Draw look dir

            # region Draw look dir
            value = "false" if self.is_thin_fall == False else "true"
            self.font.render_to(
                DEBUG_SURF,
                (self.font_w, self.font_h * 19),
                f'fall thru: {value}',
                "white",
                "black"
            )
            # endregion Draw look dir

            # region Draw my rect in tu tile
            # pos -> tu
            x_tu = (self.rect.centerx // TILE_S) - a.room.x_tu
            y_tu = (self.rect.centery // TILE_S) - a.room.y_tu
            # tu -> xds
            xds = ((x_tu + a.room.x_tu) * TILE_S) - \
                a.camera.rect.x
            yds = ((y_tu + a.room.y_tu) * TILE_S) - \
                a.camera.rect.y
            pg.draw.lines(
                DEBUG_SURF,
                "aqua",
                True,
                [
                    (xds, yds),
                    (xds + TILE_S, yds),
                    (xds + TILE_S, yds + TILE_S),
                    (xds, yds + TILE_S),
                ]
            )
            # endregion Draw my rect in tu tile
        # endregion Debug draw

    def update(self, dt):
        # Game not ready? Return
        if a.game == None:
            return

        # region Update debug stuff
        self.collided_cell_type = ""
        self.collided_cell_name = ""
        # endregion Update debug stuff

        # Update animation node
        self.animator.update(dt)

        # region Debug update
        if a.game.is_debug == True:
            self.frame_counter += 1
            if self.frame_counter == 61:
                self.frame_counter = 0
        # endregion Debug update

        # region Update velocity with gravity
        self.velocity.y += self.gravity * dt
        self.velocity.y = min(self.velocity.y, self.max_fall)
        # endregion Update velocity with gravity

        # region Update x velocity with direction
        self.velocity.x = pg.math.lerp(
            self.velocity.x,
            self.direction * self.max_run,
            self.run_lerp_weight
        )
        if abs(self.velocity.x) < 0.001:
            self.velocity.x = 0
        # endregion Update x velocity with direction

        # Update pos with vel
        self.kinematic.move(dt)

        # If previously is thin false was true, then I had moved down by 1px
        self.is_thin_fall = False

        # region Update facing direction and old facing direction
        if self.direction != 0:
            self.old_facing_direction = self.facing_direction
        # endregion Update facing direction and old facing direction

        # Get horizontal input direction
        self.direction = self.is_right_pressed - self.is_left_pressed

        # region Update facing direction and old facing direction
        if self.direction != 0:
            self.facing_direction = self.direction
        # endregion Update facing direction and old facing direction

        # Idle
        if self.state == "idle":
            # region Exit to run
            if self.direction != 0 and not self.kinematic.is_on_wall:
                self.set_state("run")
            # endregion Exit to run

            # region Exit to crouch
            elif self.is_down_pressed:
                self.set_state("crouch")
            # endregion Exit to crouch

            # region Exit to down
            elif not self.kinematic.is_on_floor:
                self.set_state("down")
            # endregion Exit to down

            # Exit jump in just pressed event input

        # Run
        elif self.state == "run":
            # region Exit to idle
            if self.direction == 0 or self.kinematic.is_on_wall:
                self.set_state("idle")
            # endregion Exit to idle

            # region Exit to crouch
            elif self.is_down_pressed:
                self.set_state("crouch")
            # endregion Exit to crouch

            # region Exit to down
            elif not self.kinematic.is_on_floor:
                self.set_state("down")
            # endregion Exit to down

            # Exit jump in just pressed event input

            # region Handle turning - frame perfect
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet
            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip
            if self.old_facing_direction != self.facing_direction:
                self.animator.set_current_animation("turn")
            # endregion Handle turning - frame perfect

        # Crouch
        elif self.state == "crouch":
            # region Exit to run
            if not self.is_down_pressed and self.direction != 0:
                self.set_state("run")
            # endregion Exit to run

            # region Exit to idle
            elif not self.is_down_pressed and self.direction == 0:
                self.set_state("idle")
            # endregion Exit to idle

            # region Exit to down
            elif not self.kinematic.is_on_floor:
                self.set_state("down")
            # endregion Exit to down

            # Exit jump in just pressed event input

            # Cannot move direction 0
            self.direction = 0

        # Up
        elif self.state == "up":
            # region Exit to down
            if self.velocity.y > 0:
                self.set_state("down")
            # endregion Exit to down

        # Down
        elif self.state == "down":
            # region Exit to run
            if self.kinematic.is_on_floor and self.direction != 0:
                self.set_state("run")
            # endregion Exit to run

            # region Exit to idle
            if self.kinematic.is_on_floor and self.direction == 0:
                self.set_state("idle")
            # endregion Exit to idle

            # region Exit to crouch
            if self.kinematic.is_on_floor and self.is_down_pressed:
                self.set_state("crouch")
            # endregion Exit to crouch

        # region Update camera anchor
        if self.current_sprite_sheet == self.sprite_sheet:
            self.facing_direction = 1
        elif self.current_sprite_sheet == self.sprite_sheet_flip:
            self.facing_direction = -1
        self.camera_anchor[0] = self.rect.x + \
            (self.facing_direction * (2 * TILE_S))
        self.camera_anchor[1] = self.rect.y
        # endregion Update camera anchor

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From idle
        if old_state == "idle":
            # To run
            if self.state == "run":
                # region Handle turning
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")
                # endregion Handle turning

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

        # From run
        elif old_state == "run":
            # To idle
            if self.state == "idle":
                # Play run_to_idle animation
                self.animator.set_current_animation("run_to_idle")

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

        # From crouch
        elif old_state == "crouch":
            # To idle
            if self.state == "idle":
                # Play idle animation
                self.animator.set_current_animation("crouch_to_idle")

            # To run
            elif self.state == "run":
                # region Handle turning
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")
                # endregion Handle turning

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

        # From up
        elif old_state == "up":
            # To down
            if self.state == "down":
                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

        # From down
        elif old_state == "down":
            # Reset gravity
            self.gravity = self.normal_gravity

            # To idle
            if self.state == "idle":
                # Play land animation
                self.animator.set_current_animation("land")

            # To run
            if self.state == "run":
                # region Handle turning
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")
                # endregion Handle turning

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")
