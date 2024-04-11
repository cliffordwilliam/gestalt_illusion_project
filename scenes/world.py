from constants import *
import autoload as a
from nodes.camera import Camera
from nodes.room import Room
from actors.player import Player
from nodes.curtain import Curtain
from nodes.mini_map import MiniMap
from actors.inventory import Inventory


class World:
    def __init__(self):
        a.world = self

        a.mini_map = MiniMap()

        a.player = Player()
        a.player.rect.x = 32
        a.player.rect.bottom = 144

        a.room = Room("stage0_gym_small_game.json")

        a.camera = Camera()

        a.camera.set_target(a.player)

        # This belongs to me only, no one talks to this
        self.inventory = Inventory()

        # Curtain belongs to world, it needs to distinguish the callback
        self.transition_curtain = Curtain(50, "empty")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_empty_end, "empty_end")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_full_end, "full_end")

        # World state, room transition, pause, cutscene and so on
        self.state = "playing"

        # To remember which door after transition curtain
        self.next_door = None

    def on_player_hit_door(self, door):
        # Only trigger once, do not call if alr in transition
        if self.state != "transition":
            self.next_door = door
            self.set_state("transition")

    def on_transition_curtain_empty_end(self):
        # Return to playing state
        self.set_state("playing")

    def on_transition_curtain_full_end(self):
        # Change room
        self.change_room()

        # Reverse transition curtain direction
        self.transition_curtain.flip_direction()

    def change_room(self):
        # region Replace this room with new room
        door_data = self.next_door["data"]

        # Unpack door data
        stage_no = door_data["STAGE_NO"]
        target = door_data["target"]

        # Change to new room
        a.room.set_name(f"stage{stage_no}_{target}_game.json")

        # region Adjust player and camera to new room position
        door_name = self.next_door["name"]
        if door_name == "LeftDoor":
            a.player.rect.right = (
                a.room.rect[0] + a.room.rect[2]) - TILE_S
            a.camera.rect.x -= NATIVE_W

        elif door_name == "RightDoor":
            a.player.rect.left = a.room.rect[0] + TILE_S
            a.camera.rect.x += NATIVE_W

        elif door_name == "UpDoor":
            a.player.rect.bottom = (
                a.room.rect[1] + a.room.rect[3]) - (2 * TILE_S)
            a.camera.rect.y -= NATIVE_H

        elif door_name == "DownDoor":
            a.player.rect.top = a.room.rect[1] + TILE_S
            a.camera.rect.y += NATIVE_H
        # endregion Adjust player and camera to new room position

    def event(self, event):
        if self.state == "playing":
            # Prioritize pause event, exit to inventory state
            if event.type == pg.KEYUP:
                if event.key == a.game.key_bindings["pause"]:
                    self.set_state("pause")

            # Player event
            a.player.event(event)

        elif self.state == "transition":
            # Player event
            a.player.event(event)

        elif self.state == "pause":
            # Inventory event
            self.inventory.event(event)

    def draw(self):
        # Fill native surface color to have good contrast for player
        NATIVE_SURF.fill("#6bc5a0")

        if self.state == "playing":
            # Draw room
            a.room.draw()

            # Draw the mini map
            a.mini_map.draw()

        # Draw transition curtain
        elif self.state == "transition":
            # Draw room
            a.room.draw()

            # Draw the mini map
            a.mini_map.draw()

            # Draw transition curtain
            self.transition_curtain.draw()

        # Draw the overlay curtain
        elif self.state == "pause":
            # Draw player is done in room with other moving actors in draw bg and non moving actors
            a.room.draw()

            # Draw inventory
            self.inventory.draw()

        # # region Draw grid
        # if a.game.is_debug == True:
        #     for i in range(20):
        #         offset = TILE_S * i
        #         xd = (offset - a.camera.rect.x) % NATIVE_W
        #         yd = (offset - a.camera.rect.y) % NATIVE_H
        #         pg.draw.line(NATIVE_SURF, "grey4", (xd, 0), (xd, NATIVE_H))
        #         pg.draw.line(NATIVE_SURF, "grey4", (0, yd), (NATIVE_W, yd))
        #     xd = -a.camera.rect.x % NATIVE_W
        #     yd = -a.camera.rect.y % NATIVE_H
        #     pg.draw.line(NATIVE_SURF, "grey8", (xd, 0), (xd, NATIVE_H))
        #     pg.draw.line(NATIVE_SURF, "grey8", (0, yd), (NATIVE_W, yd))
        #     FONT.render_to(
        #         NATIVE_SURF, (xd + FONT_W, yd + FONT_H), f"{
        #             (a.camera.rect.x - 1) // NATIVE_W + 1}{
        #             (a.camera.rect.y - 1) // NATIVE_H + 1}", "grey100"
        #     )
        # # endregion

    def update(self, dt):
        if self.state == "playing":
            # Update all bg sprites actors, and moving actors
            a.room.update(dt)

            # Update camera (must be here, after its target actor moved)
            a.camera.update(dt)

        elif self.state == "transition":
            # On transition state, immediately update transition curtain
            self.transition_curtain.update(dt)

        elif self.state == "pause":
            # On pause state, immediately update overlay curtain
            self.inventory.update(dt)

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From playing
        if old_state == "playing":
            # To pause
            if self.state == "pause":
                # Set map to inventory
                a.mini_map.set_state("inventory")

            # To pause
            elif self.state == "transition":
                pass

        # From transition
        if old_state == "transition":
            # To playing
            if self.state == "playing":
                # Reset transition curtain
                self.transition_curtain.reset()

            # Cannot go to pause

        # From pause
        if old_state == "pause":
            # To playing
            if self.state == "playing":
                # Set map to gameplay
                a.mini_map.set_state("gameplay")

            # Impossible to go to transition
