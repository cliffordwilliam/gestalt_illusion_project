from constants import *


class Timer:
    '''
    How to use: 
        1: Set my duration
        2: Call my update to start counting
        3: When time is up, I will call your callback

    What will happen:
        1: Timer is incremented on every frame
        2: When reaches end, it will reset the timer to 0
    '''

    def __init__(self, duration):
        self.timer = 0
        self.duration = duration

        # Callbacks
        self.listener_end = []

    def add_event_listener(self, value, event):
        if event == "timer_end":
            self.listener_end.append(value)

    def reset(self):
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer > self.duration:
            self.timer = 0
            for callback in self.listener_end:
                callback()
