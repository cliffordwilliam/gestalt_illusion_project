from constants import *
import autoload as a
from nodes.curtain import Curtain


class Inventory:
    def __init__(self):
        # Prevent input during curtain fade
        self.allow_inventory_input = False

        # Inventory overlay
        self.overlay_inventory_curtain = Curtain(80, "empty")
        self.overlay_inventory_curtain.add_event_listener(
            self.on_overlay_inventory_curtain_empty_end, "empty_end")
        self.overlay_inventory_curtain.add_event_listener(
            self.on_overlay_inventory_curtain_full_end, "full_end")

        # Menu input
        self.allow_inventory_input = False

    def on_overlay_inventory_curtain_empty_end(self):
        # Reset overlay curtain
        self.overlay_inventory_curtain.reset()

        # Overlay curtain is gone? Set playing for world
        a.world.set_state("playing")

    def on_overlay_inventory_curtain_full_end(self):
        # Allow input when fade to full is done
        self.allow_inventory_input = True

    def event(self, event):
        if event.type == pg.KEYUP:
            # Pressed pause again in inventory overlay?
            if event.key == a.game.key_bindings["pause"]:
                # Remove player all inputs
                a.player.is_left_pressed = 0
                a.player.is_right_pressed = 0
                a.player.is_down_pressed = False
                a.player.is_jump_just_pressed = False
                a.player.is_jump_just_released = False

                # Flip overlay curtain dir
                self.overlay_inventory_curtain.flip_direction()

                # Prevent input here
                self.allow_inventory_input = False

    def draw(self):
        # Draw my overlay
        self.overlay_inventory_curtain.draw()

        # Draw map on overlay in its inventory mode
        a.mini_map.draw(self.overlay_inventory_curtain.curtain)

    def update(self, dt):
        # If input is allowed that means fade is done
        if self.allow_inventory_input == False:
            self.overlay_inventory_curtain.update(dt)
