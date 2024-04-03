from constants import *


class Curtain:
    def __init__(self, duration, start="empty"):
        # Empty or full
        self.start = start

        # Curtain init
        self.curtain = pg.Surface((NATIVE_W, NATIVE_H))
        self.curtain.fill("black")

        # Start empty
        self.curtain.set_alpha(0)
        self.alpha = 0
        self.fade_duration = duration
        self.fade_timer = 0
        self.direction = 1

        # Start full
        if self.start == "full":
            self.curtain.set_alpha(255)
            self.alpha = 255
            self.fade_duration = duration
            self.fade_timer = self.fade_duration
            self.direction = -1

        # Remainder and fade early flag
        self.remainder = 0

        # Callbacks
        self.listener_empty_ends = []
        self.listener_full_ends = []

    def add_event_listener(self, value, event):
        if event == "empty_end":
            self.listener_empty_ends.append(value)
        if event == "full_end":
            self.listener_full_ends.append(value)

    def draw(self):
        # Draw transition curtain
        NATIVE_SURF.blit(self.curtain, (0, 0))

    def update(self, dt):
        # Update timer with direction and dt, go left or right
        self.fade_timer += dt * self.direction
        # Clamp timer
        self.fade_timer = max(
            0, min(self.fade_duration, self.fade_timer))
        # Use timer as position
        fraction = self.fade_timer / self.fade_duration
        # Use position to update alpha value
        lerp_alpha = pg.math.lerp(0, 255, fraction)
        # Add prev round float loss
        lerp_alpha += self.remainder
        # Round to int
        self.alpha = max(0, min(255, round(lerp_alpha)))
        # Collect round loss
        self.remainder = lerp_alpha - self.alpha
        # Set alpha
        self.curtain.set_alpha(self.alpha)

        # End reached? Blink prompt
        if self.fade_timer == 0:
            for callback in self.listener_empty_ends:
                callback()
            # self.owner.on_curtain_empty_end()
            # Transition state is over
            # self.is_transitioning = False
            # self.curtain.set_alpha(0)
            # self.alpha = 0
            # self.fade_duration = self.fade_duration
            # self.fade_timer = 0
            # self.direction = 1
            # # Remainder and fade early flag
            # self.remainder = 0

        # Other end reached?
        if self.fade_timer == self.fade_duration:
            for callback in self.listener_full_ends:
                callback()
            # self.owner.on_curtain_full_end()
            # # Change room
            # self.change_room()
            # # Reverse my direction
            # self.direction *= -1
            pass
        return
