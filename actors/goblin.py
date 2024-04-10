from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
from nodes.timer import Timer
import autoload as a


class Goblin:
    def __init__(self, id):
        # UUID for quadtree bookeeping, for quick relocation in quad
        self.id = id

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
        self.animator.add_event_listener(
            self.on_attack_animation_end, "animation_end")

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

        # For indicating the sprite flip or not, easier to read
        self.facing_direction = 1

        # On player enter go to attack
        self.aggro_rect = pg.FRect(0, 0, 80, 31)

        # On player enter call player hit
        self.hit_rect = pg.FRect(0, 0, 40, 31)

    # Animation callback
    def on_attack_animation_end(self):
        # Player is still in the aggor rect, play the attack animation again
        if a.player in a.quad_tree.search(self.aggro_rect):
            # region Set current sprite sheet input based on where player is right now
            # Player on left or right? Positive rel_player_pos = right
            rel_player_pos = a.player.rect.center[0] - self.rect.center[0]

            # Only update sprite sheet if player is not exactly where I am in x axis
            if rel_player_pos != 0:

                # I am facing right?
                if self.current_sprite_sheet == self.sprite_sheet:
                    # Player on my left?
                    if rel_player_pos < 0:
                        # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                        self.current_sprite_sheet = self.sprite_sheet_flip

                # I am facing left?
                elif self.current_sprite_sheet == self.sprite_sheet_flip:
                    # Player on my right?
                    if rel_player_pos > 0:
                        # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                        self.current_sprite_sheet = self.sprite_sheet
            # endregion Set current sprite sheet input based on where player is right now

            # Replay the attack anim, stay in attack state
            self.animator.set_current_animation("attack")
            return

        # Player is not in agrro, exit to idle state
        self.set_state("idle")

    # Timer callback
    def on_idle_timer_end(self):
        self.set_state("run")

    # Timer callback
    def on_run_timer_end(self):
        self.set_state("idle")

    # Called by kinematic
    def on_collide(self, cells):
        # Unpack all found collided cells type and name
        for cell in cells:
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

        if a.game.is_debug:
            # Debug draw state
            x = self.rect.x - a.camera.rect.x
            y = self.rect.y - a.camera.rect.y - FONT_H
            FONT.render_to(DEBUG_SURF, (x, y),
                           f'state: {self.state}', "white", "black")

            # Debug draw facing
            x = self.rect.x - a.camera.rect.x
            y = self.rect.y - a.camera.rect.y - (2 * FONT_H) - 1
            FONT.render_to(DEBUG_SURF, (x, y),
                           f'face: {self.facing_direction}', "white", "black")

            x = self.rect.x - a.camera.rect.x
            y = self.rect.y - a.camera.rect.y - (3 * FONT_H) - 2
            if a.game.is_debug:
                FONT.render_to(DEBUG_SURF, (x, y),
                               f'wall: {self.kinematic.is_on_wall}', "white", "black")

            x = self.rect.x - a.camera.rect.x
            y = self.rect.y - a.camera.rect.y - (4 * FONT_H) - 3
            if a.game.is_debug:
                FONT.render_to(DEBUG_SURF, (x, y),
                               f'floor: {self.kinematic.is_on_floor}', "white", "black")

            # Draw aggro rect
            x = self.aggro_rect.x - a.camera.rect.x
            y = self.aggro_rect.y - a.camera.rect.y
            w = self.aggro_rect.width
            h = self.aggro_rect.height
            pg.draw.rect(DEBUG_SURF, "red4", (x, y, w, h), 1)

            # Draw hit rect
            x = self.hit_rect.x - a.camera.rect.x
            y = self.hit_rect.y - a.camera.rect.y
            w = self.hit_rect.width
            h = self.hit_rect.height
            pg.draw.rect(DEBUG_SURF, "yellow", (x, y, w, h), 1)

    def update(self, dt):
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

        # Update aggro rect to follow rect
        self.aggro_rect.midbottom = self.rect.midbottom

        # Update hit rect to follow rect, depends on my sprite sheet
        if self.current_sprite_sheet == self.sprite_sheet:
            self.hit_rect.midleft = self.rect.center
        elif self.current_sprite_sheet == self.sprite_sheet_flip:
            self.hit_rect.midright = self.rect.center

        # Idle
        if self.state == "idle":
            self.idle_timer.update(dt)

            # Exit to run are taken care of timers

            # region Exit to attack
            if a.player in a.quad_tree.search(self.aggro_rect):
                self.set_state("attack")
                return
            # endregion Exit to attack

            # In state logic

        # Run
        elif self.state == "run":
            self.run_timer.update(dt)

            # Exit to idle are taken care of timers

            # region Exit to attack
            if a.player in a.quad_tree.search(self.aggro_rect):
                self.set_state("attack")
                return
            # endregion Exit to attack

            # In state logic
            # region Walked off cliff?
            if not self.kinematic.is_on_floor:
                # Flip
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                    self.facing_direction = 1
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                    self.facing_direction = -1

                # Go back in time (before off floor is true), set current pos to prev frame pos
                self.rect.x = old_position_x
                self.rect.y = old_position_y
            # endregion Walked off cliff?

            # region Pressing against wall?
            elif self.kinematic.is_on_wall:
                # Flip direction
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                    self.facing_direction = 1
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                    self.facing_direction = -1

                # Go back in time (before on wall is true), set current pos to prev frame pos
                self.rect.x = old_position_x + self.direction
                self.rect.y = old_position_y
            # endregion Pressing against wall?

        # Idle
        elif self.state == "attack":
            # Exit to idle are taken care of animation end callback

            # In state logic

            # During active hit box frame
            if self.animator.frame_index == 2 or self.animator.frame_index == 3:
                # Player inside it?
                if self.hit_rect.colliderect(a.player):
                    # Call player hurt callback
                    # TODO: Pass my damage data
                    a.player.ouch()

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

            # To attack
            elif self.state == "attack":
                # region Set current sprite sheet input based on where player is right now
                # Player on left or right? Positive rel_player_pos = right
                rel_player_pos = a.player.rect.center[0] - self.rect.center[0]

                # Only update sprite sheet if player is not exactly where I am in x axis
                if rel_player_pos != 0:

                    # I am facing right?
                    if self.current_sprite_sheet == self.sprite_sheet:
                        # Player on my left?
                        if rel_player_pos < 0:
                            # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet_flip

                    # I am facing left?
                    elif self.current_sprite_sheet == self.sprite_sheet_flip:
                        # Player on my right?
                        if rel_player_pos > 0:
                            # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet
                # endregion Set current sprite sheet input based on where player is right now

                # Set direction input to 0
                self.direction = 0

                # Play attack animation
                self.animator.set_current_animation("attack")

        # From run
        elif old_state == "run":
            # To idle
            if self.state == "idle":
                # Set direction input to 0
                self.direction = 0

                # Play idle animation
                self.animator.set_current_animation("idle")

            # To attack
            elif self.state == "attack":
                # region Set current sprite sheet input based on where player is right now
                # Player on left or right? Positive rel_player_pos = right
                rel_player_pos = a.player.rect.center[0] - self.rect.center[0]

                # Only update sprite sheet if player is not exactly where I am in x axis
                if rel_player_pos != 0:

                    # I am facing right?
                    if self.current_sprite_sheet == self.sprite_sheet:
                        # Player on my left?
                        if rel_player_pos < 0:
                            # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet_flip

                    # I am facing left?
                    elif self.current_sprite_sheet == self.sprite_sheet_flip:
                        # Player on my right?
                        if rel_player_pos > 0:
                            # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet
                # endregion Set current sprite sheet input based on where player is right now

                # Set direction input to 0
                self.direction = 0

                # Play attack animation
                self.animator.set_current_animation("attack")

        # From run
        elif old_state == "attack":
            # To idle
            if self.state == "idle":
                # Set direction input to 0
                self.direction = 0

                # Play idle animation
                self.animator.set_current_animation("idle")
