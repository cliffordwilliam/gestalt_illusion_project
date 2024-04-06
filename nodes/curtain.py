from constants import *


class Curtain:
    '''
    How to use: 
        1: Give me duration of 0 -> 255, same value is used for 255 -> 0
        2: Tell me either to start from 0 or 255
        3: Optional can give me subs on my 2 events, reach 0 (empty) and reach 255 (full)

    What will happen:
        1: For every frame I draw my curtain
        2: My curtain alpha is determined by the timer, timer acts as a position
        3: Timer is 50% of duration? then 122 is the value. Timer == duration? 255. Timer = 0? 0
        4: Timer can go from 0 to 255 or 255 to 0 based on direction, update direction to go wherever you want
    '''

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

    def flip_direction(self):
        self.direction *= -1

    def reset(self):
        # Start empty
        self.curtain.set_alpha(0)
        self.alpha = 0
        self.fade_timer = 0
        self.direction = 1
        self.remainder = 0

        # Start full
        if self.start == "full":
            self.curtain.set_alpha(255)
            self.alpha = 255
            self.fade_timer = self.fade_duration
            self.direction = -1
            self.remainder = 0

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

        # Empty end reched - 0 - invisible?
        if self.fade_timer == 0:
            for callback in self.listener_empty_ends:
                callback()

        # Filled end reached - 255 - pitch black?
        if self.fade_timer == self.fade_duration:
            for callback in self.listener_full_ends:
                callback()
            pass
        return
