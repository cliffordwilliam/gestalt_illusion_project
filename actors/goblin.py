from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
from nodes.timer import Timer
import autoload as a


class Goblin:
    def __init__(self):
        # Name
        self.name = "Goblin"

        # region sprite sheets
        self.sprite_sheet = pg.image.load(
            PNGS_PATHS["goblin_sprite_sheet.png"])
        self.sprite_sheet_flip = pg.image.load(
            PNGS_PATHS["goblin_flip_sprite_sheet.png"])
        self.current_sprite_sheet = self.sprite_sheet
        # endregion sprite sheets

        # region Surface offset
        self.surface_offset_x = 37
        self.surface_offset_y = 30
        # endregion Surface offset

        # region Read json animation data
        self.aniamtion_data = {}
        with open(JSONS_PATHS["goblin_animation.json"], "r") as data:
            self.aniamtion_data = load(data)
        # endregion Read json animation data

        # Init starting region
        self.region = self.aniamtion_data["idle"]["frames_list"][0]["region"]

        # State
        self.state = "idle"

        # Direction input, updated by timer and wall / when not on floor
        self.direction = 0

        # Animator node
        self.animator = Animator(self, self.aniamtion_data, "idle")

        # Rect
        self.rect = pg.FRect(0, 0, 6, 31)

        # Movement
        self.max_run = 0.017
        self.max_fall = 0.270
        self.gravity = 0.000533
        self.velocity = pg.math.Vector2()

        # Kinematic
        self.kinematic = Kinematic(self)

        # Timer to toggle between idle and run
        self.idle_timer = Timer(2000)
        self.run_timer = Timer(4000)
        self.idle_timer.add_event_listener(self.on_idle_timer_end, "timer_end")
        self.run_timer.add_event_listener(self.on_run_timer_end, "timer_end")

    # Timer callback
    def on_idle_timer_end(self):
        self.set_state("run")

    # Timer callback
    def on_run_timer_end(self):
        self.set_state("idle")

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

            # Found door next? Stop
            elif cell["type"] == "Door":
                return True

            # Found thin? Stop
            elif cell["type"] == "Thin":
                return True

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

        # region Draw to native surface
        xds = (self.rect.x - self.surface_offset_x) - a.camera.rect.x
        yds = (self.rect.y - self.surface_offset_y) - a.camera.rect.y
        NATIVE_SURF.blit(
            self.current_sprite_sheet, (xds, yds), self.region
        )
        # endregion Draw to native surface

    def update(self, dt):
        # Game not ready? Return
        if a.game == None:
            return

        # Update animation node
        self.animator.update(dt)

        # region Update velocity with gravity
        self.velocity.y += self.gravity * dt
        self.velocity.y = min(self.velocity.y, self.max_fall)
        # endregion Update velocity with gravity

        # region Update x velocity with direction
        self.velocity.x = self.direction * self.max_run
        # endregion Update x velocity with direction

        # Get old position
        old_position_x = self.rect.x
        old_position_y = self.rect.y

        # Update pos with vel
        self.kinematic.move(dt)

        # Idle
        if self.state == "idle":
            self.idle_timer.update(dt)

            # Exits are taken care of timers

            # In state logic

        # Run
        elif self.state == "run":
            self.run_timer.update(dt)

            # Exits are taken care of timers

            # In state logic
            # region Pressing against wall?
            if self.kinematic.is_on_wall:
                # Flip direction
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
            # endregion Pressing against wall?

            # region Walked off cliff?
            if not self.kinematic.is_on_floor:
                # Flip
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Go back in time, set current pos to prev frame pos
                self.rect.x = old_position_x
                self.rect.y = old_position_y
            # endregion Walked off cliff?

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From idle
        if old_state == "idle":
            # To run
            if self.state == "run":
                # region Set direction input based on sprite sheet right now
                # Use current sprite sheet to determine direction
                if self.current_sprite_sheet == self.sprite_sheet:
                    self.direction = 1
                elif self.current_sprite_sheet == self.sprite_sheet_flip:
                    self.direction = -1
                # endregion Set direction input based on sprite sheet right now

                # Play run animation
                self.animator.set_current_animation("run")

        # From run
        elif old_state == "run":
            # To idle
            if self.state == "idle":
                # Set direction input to 0
                self.direction = 0

                # Play idle animation
                self.animator.set_current_animation("idle")
