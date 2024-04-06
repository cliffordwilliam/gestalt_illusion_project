from constants import *
import autoload as a


class Camera:
    '''
    How to use: 
        1: Give me target with setter -> [x, y]

    What will happen:
        1: Store target data in list
        2: On every frame, clamp target to be a value where the cam will not overshoot limit
        3: Update camera position to lerp to target position
        4: Has a debug draw to show target position with draw offset in update method

    Notes:
        - 0.09 (player speed) * dt (distance) * 0.2 (lerp) -> 0.288 (distance / frame)
        - camera have to cover 32px, so 32 (distance) * 0.009 (lerp) = 0.288 (distance / frame)
    '''

    def __init__(self):
        self.rect = pg.FRect(0, 0, NATIVE_W, NATIVE_H)
        self.lerp_weight = 0.009
        self.target = [0, 0]
        self.target_x = 0
        self.target_y = 0

    def set_target(self, value):
        self.target = value

    def set_lerp_weight(self, value):
        self.lerp_weight = value

    def update(self, dt):
        # Room not ready? Return
        if a.room == None:
            return

        # Prevent target to be in a pos where cam is outside of room x
        self.target_x = self.target[0]
        left = a.room.rect[0]
        right = left + a.room.rect[2]
        left += NATIVE_W // 2
        right -= NATIVE_W // 2
        self.target_x = max(min(self.target_x, right), left)

        # Prevent target to be in a pos where cam is outside of room y
        self.target_y = self.target[1]
        top = a.room.rect[1]
        bottom = top + a.room.rect[3]
        top += NATIVE_H // 2
        bottom -= NATIVE_H // 2
        self.target_y = max(min(self.target_y, bottom), top)

        # Lerp targets
        target_x = self.target_x - (NATIVE_W // 2)
        target_y = self.target_y - (NATIVE_H // 2)

        # Update horizontal position
        self.rect.x = pg.math.lerp(
            self.rect.x,
            target_x,
            self.lerp_weight * dt
        )
        if abs(self.rect.x) < 0.001:
            self.rect.x = 0

        # Update vertical position
        self.rect.y = pg.math.lerp(
            self.rect.y,
            target_y,
            self.lerp_weight * dt
        )
        if abs(self.rect.y) < 0.001:
            self.rect.y = 0

        # Snap to room left if too close
        diff = abs(self.rect.x - target_x)
        if diff < 0.1:
            self.rect.x = target_x

        # Snap to room top if too close
        diff = abs(self.rect.y - target_y)
        if diff < 0.1:
            self.rect.y = target_y

        # Debug draw
        if a.game.is_debug:
            # Draw my center
            x = (NATIVE_W // 2) - 1
            y = (NATIVE_H // 2) - 1
            pg.draw.line(DEBUG_SURF, "red4", (x, 0), (x, NATIVE_H), 2)
            pg.draw.line(DEBUG_SURF, "red4", (0, y), (NATIVE_W, y), 2)

            # Draw target
            x = self.target_x - self.rect.x
            y = self.target_y - self.rect.y
            pg.draw.circle(DEBUG_SURF, "yellow", (x, y), 2)
