from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
import autoload as a


class Player:
    def __init__(self):
        # Name
        self.name = "Player"

        # region Inputs
        self.is_left_pressed = 0
        self.is_right_pressed = 0
        self.is_down_pressed = False
        self.is_jump_just_pressed = False
        self.is_jump_just_released = False
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

        # Facing direction (when direction is 0, I still need to know where I am, this determine when I turn)
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

        # Set to false on next frame immediately after falling for 1 frame distance
        self.is_thin_fall = False

    # Called by kinematic - this is for static things
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

            # Found thin?
            elif cell["type"] == "Thin":
                # Not passing thru?
                if self.is_thin_fall == False:
                    # If I am falling
                    if self.velocity.y > 0:
                        # Player real rect feet flushed on it? Stop
                        if (self.rect.bottom - cell["yds"]) == 0:
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

    def event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == a.game.key_bindings["left"]:
                self.is_left_pressed = 1

            if event.key == a.game.key_bindings["right"]:
                self.is_right_pressed = 1

            if event.key == a.game.key_bindings["down"]:
                self.is_down_pressed = True

            elif event.key == a.game.key_bindings["jump"]:
                self.is_jump_just_pressed = True

        elif event.type == pg.KEYUP:
            if event.key == a.game.key_bindings["left"]:
                self.is_left_pressed = 0

            if event.key == a.game.key_bindings["right"]:
                self.is_right_pressed = 0

            if event.key == a.game.key_bindings["down"]:
                self.is_down_pressed = False

            elif event.key == a.game.key_bindings["jump"]:
                self.is_jump_just_released = True

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

    def update(self, dt):
        # Game not ready? Return
        if a.game == None:
            return

        # Update animation node
        self.animator.update(dt)

        # region Update y velocity with gravity
        self.velocity.y += self.gravity * dt
        self.velocity.y = min(self.velocity.y, self.max_fall)
        # endregion Update y velocity with gravity

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
            # Always prioritize exits first, prioritize falling exit then up exit
            # region Exit to down
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return
            # endregion Exit to down

            # region Exit to up
            elif self.kinematic.is_on_floor and self.is_jump_just_pressed:
                self.set_state("up")
                return
            # endregion Exit to up

            # region Exit to run
            elif self.kinematic.is_on_floor and self.direction != 0 and not self.kinematic.is_on_wall:
                self.set_state("run")
                return
            # endregion Exit to run

            # region Exit to crouch
            elif self.kinematic.is_on_floor and self.is_down_pressed:
                self.set_state("crouch")
                return
            # endregion Exit to crouch

            # Then handle in state logic

        # Run
        elif self.state == "run":
            # Always prioritize exits first, prioritize falling exit
            # region Exit to down
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return
            # endregion Exit to down

            # region Exit to up
            elif self.kinematic.is_on_floor and self.is_jump_just_pressed:
                self.set_state("up")
                return
            # endregion Exit to up

            # region Exit to idle
            elif self.kinematic.is_on_floor and self.direction == 0 or self.kinematic.is_on_wall:
                self.set_state("idle")
                return
            # endregion Exit to idle

            # region Exit to crouch
            elif self.kinematic.is_on_floor and self.is_down_pressed:
                self.set_state("crouch")
                return
            # endregion Exit to crouch

            # Then handle in state logic
            # region Handle turning - frame perfect
            # Update sprite flip
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet
            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip

            # Turn?
            if self.old_facing_direction != self.facing_direction:
                self.animator.set_current_animation("turn")
            # endregion Handle turning - frame perfect

        # Crouch
        elif self.state == "crouch":
            # Always prioritize exits first, prioritize falling exit
            # region Exit to down
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return
            # endregion Exit to down

            # region Exit to up OR DOWN PASS THRU THIN
            elif self.kinematic.is_on_floor and self.is_down_pressed and self.is_jump_just_pressed:
                # Crouching and just pressed jump?
                if self.collided_cell_type == "Thin":
                    # Did that on a thin? Pass thru next frame and this state will kick to down
                    self.is_thin_fall = True
                    return
                else:
                    # Did that on solid? Jump
                    self.set_state("up")
                    return
            # endregion Exit to up

            # region Exit to run
            elif self.kinematic.is_on_floor and not self.is_down_pressed and self.direction != 0:
                self.set_state("run")
                return
            # endregion Exit to run

            # region Exit to idle
            elif self.kinematic.is_on_floor and not self.is_down_pressed and self.direction == 0:
                self.set_state("idle")
                return
            # endregion Exit to idle

            # Then handle in state logic
            # Cannot move direction 0
            self.direction = 0

        # Up
        elif self.state == "up":
            # Always prioritize exits first, prioritize falling exit
            # region Exit to down
            if self.velocity.y > 0:
                self.set_state("down")
                return
            # endregion Exit to down

            # Then handle in state logic
            # Jump was released while going up? Heavy gravity
            if self.is_jump_just_released == True:
                self.gravity = self.heavy_gravity

        # Down
        elif self.state == "down":
            # Always prioritize exits first, prioritize falling exit
            # region Exit to run
            if self.kinematic.is_on_floor and self.direction != 0:
                self.set_state("run")
                return
            # endregion Exit to run

            # region Exit to idle
            if self.kinematic.is_on_floor and self.direction == 0:
                self.set_state("idle")
                return
            # endregion Exit to idle

            # region Exit to crouch
            if self.kinematic.is_on_floor and self.is_down_pressed:
                self.set_state("crouch")
                return
            # endregion Exit to crouch

            # region Exit to up
            if self.kinematic.is_on_floor and self.is_jump_just_pressed:
                self.set_state("up")
                return
            # endregion Exit to up

        # region Update my camera anchor to follow me
        self.camera_anchor[0] = self.rect.center[0] + \
            (self.facing_direction * (2 * TILE_S))
        self.camera_anchor[1] = self.rect.center[1]
        # endregion Update my camera anchor to follow me

        # Reset if before this update call the event toggle this to true, event is called first
        self.is_jump_just_pressed = False
        self.is_jump_just_released = False

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From idle
        if old_state == "idle":
            # To run
            if self.state == "run":
                # region Handle turning
                # Update the flip sprite
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Turn animation or not?
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
                # Remove grav build up if fall off cliff
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
                # Update the flip sprite
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Turn animation or not?
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
                # Update the flip sprite
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Turn animation or not?
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
