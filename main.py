from constants import *
from scenes.world import World
import autoload as a


class Game:
    def __init__(self):
        # Global debug flag, press 0 to toggle
        self.is_debug = False

        # Resolution and window
        self.resolution = 4
        self.window_w = WINDOW_W * self.resolution
        self.window_h = WINDOW_H * self.resolution
        self.window_surf = pg.display.set_mode((self.window_w, self.window_h))
        self.y_offset = 2 * self.resolution

        # Keybinds
        self.key_bindings = {
            "up": pg.K_UP,
            "down": pg.K_DOWN,
            "left": pg.K_LEFT,
            "right": pg.K_RIGHT,
            "enter": pg.K_RETURN,
            "pause": pg.K_ESCAPE,
            "jump": pg.K_c,
        }

        # All scenes
        self.scenes = {
            "World": World
        }
        self.current_scene = self.scenes["World"]()

        # All actors
        self.actors = {
        }

    def set_resolution(self, value):
        # Takes values from 1 to 7
        # Other resolution values
        if value != 7:
            self.resolution = value
            self.window_w = WINDOW_W * self.resolution
            self.window_h = WINDOW_H * self.resolution
            self.window_surf = pg.display.set_mode(
                (self.window_w, self.window_h))
            self.y_offset = 2 * self.resolution

        # Fullscreen
        elif value == 7:
            self.window_surf = pg.display.set_mode(
                (self.window_w, self.window_h), pg.FULLSCREEN)
            self.resolution = self.window_surf.get_width() // NATIVE_W
            self.window_w = WINDOW_W * self.resolution
            self.window_h = WINDOW_H * self.resolution
            self.y_offset = 2 * self.resolution

    def set_scene(self, value):
        self.current_scene = self.scenes[value]()


# Instance a.game
a.game = Game()

# Main loop
while 1:
    # region Get dt
    dt = CLOCK.tick(FPS)

    # Get event
    for event in pg.event.get(EVENTS):
        # region Window quit
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        # endregion Window quit

        # region Debug toggle
        if event.type == pg.KEYUP:
            if event.key == pg.K_0:
                a.game.is_debug = not a.game.is_debug
        # endregion Debug toggle

        # Current scene event
        a.game.current_scene.event(event)

    # Clear native surface
    NATIVE_SURF.fill("red")

    # region Clear debug surface
    if a.game.is_debug == True:
        DEBUG_SURF.fill("red")
    # endregion Clear debug surface

    # Current scene draw on native
    a.game.current_scene.draw()

    # Current scene update
    a.game.current_scene.update(dt)

    # region Draw debug surface on native
    if a.game.is_debug == True:
        NATIVE_SURF.blit(DEBUG_SURF, (0, 0))
    # endregion Draw debug surface on native

    # region Native to window and update window
    scaled_native_surf = pg.transform.scale_by(NATIVE_SURF, a.game.resolution)
    a.game.window_surf.blit(scaled_native_surf, (0, a.game.y_offset))
    pg.display.update()
    # endregion Native to window and update window
