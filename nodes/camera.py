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
    '''

    def __init__(self):
        self.rect = pg.FRect(0, 0, NATIVE_W, NATIVE_H)
        self.target = None
        self.lerp_weight = 0.01

    def set_target(self, value):
        self.target = value

    def update(self, dt):
        # Room not ready? Return
        if a.room == None:
            return

        # Unpack target
        target_center_x = self.target.camera_anchor[0]
        target_center_y = self.target.camera_anchor[1]

        # Prevent target to be in a pos where cam is outside of room x
        left = a.room.rect[0]
        right = left + a.room.rect[2]
        left += NATIVE_W // 2
        right -= NATIVE_W // 2
        target_center_x = max(min(target_center_x, right), left)

        # Prevent target to be in a pos where cam is outside of room y
        top = a.room.rect[1]
        bottom = top + a.room.rect[3]
        top += NATIVE_H // 2
        bottom -= NATIVE_H // 2
        target_center_y = max(min(target_center_y, bottom), top)

        # Lerp targets, get the topleft - lerp works with topleft
        target_x = target_center_x - (NATIVE_W // 2)
        target_y = target_center_y - (NATIVE_H // 2)

        # Update horizontal position when I am not on target
        if self.rect.x != target_x:
            self.rect.x = pg.math.lerp(
                self.rect.x,
                target_x,
                self.lerp_weight * dt
            )
            if abs(self.rect.x) < 0.001:
                self.rect.x = 0

            # Snap to target if close enough x
            diff = abs(self.rect.x - target_x)
            if diff < 1:
                self.rect.x = target_x

        # Update vertical position when I am not on target
        if self.rect.y != target_y:
            self.rect.y = pg.math.lerp(
                self.rect.y,
                target_y,
                self.lerp_weight * dt
            )
            if abs(self.rect.y) < 0.001:
                self.rect.y = 0

            # Snap to target if close enough y
            diff = abs(self.rect.y - target_y)
            if diff < 1:
                self.rect.y = target_y

        # Debug draw
        if a.game.is_debug:
            # Draw my center
            x = (NATIVE_W // 2) - 1
            y = (NATIVE_H // 2) - 1
            pg.draw.line(DEBUG_SURF, "red4", (x, 0), (x, NATIVE_H), 2)
            pg.draw.line(DEBUG_SURF, "red4", (0, y), (NATIVE_W, y), 2)
            FONT.render_to(DEBUG_SURF, (x, 0),
                           "cam center x", "white", "black")
            FONT.render_to(DEBUG_SURF, (0, y),
                           "cam center y", "white", "black")

            # Draw target
            target_center_x = target_x + (NATIVE_W // 2)
            target_center_y = target_y + (NATIVE_H // 2)
            x = target_center_x - self.rect.x
            y = target_center_y - self.rect.y
            pg.draw.circle(DEBUG_SURF, "yellow", (x, y), 2)
            FONT.render_to(DEBUG_SURF, (x, y),
                           "cam target", "white", "black")
