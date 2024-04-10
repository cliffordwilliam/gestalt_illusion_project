from constants import *
import autoload as a
from nodes.camera import Camera
from nodes.room import Room
from actors.player import Player
from nodes.curtain import Curtain
from nodes.mini_map import MiniMap


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

        # Inventory overlay
        self.overlay_inventory_curtain = Curtain(80, "empty", 200)
        self.overlay_inventory_curtain.add_event_listener(
            self.on_overlay_inventory_curtain_empty_end, "empty_end")
        self.overlay_inventory_curtain.add_event_listener(
            self.on_overlay_inventory_curtain_full_end, "full_end")

        # Menu input
        self.allow_inventory_input = False

    def on_overlay_inventory_curtain_empty_end(self):
        # Overlay curtain is gone? Set playing
        self.state = "playing"

        # Set map to gameplay
        a.mini_map.set_state("gameplay")

        # Reset overlay curtain
        self.overlay_inventory_curtain.reset()

    def on_overlay_inventory_curtain_full_end(self):
        self.allow_inventory_input = True

    def on_player_hit_door(self, door):
        # Only trigger once, player hit door -> transition state
        if self.state == "playing":
            self.next_door = door
            self.state = "transition"

    def on_transition_curtain_empty_end(self):
        # Return to playing state
        self.state = "playing"

        # Reset transition curtain
        self.transition_curtain.reset()

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
            # Prioritize pause event
            if event.type == pg.KEYUP:
                if event.key == a.game.key_bindings["pause"]:
                    self.state = "pause"
                    a.mini_map.set_state("inventory")

            # Player event
            a.player.event(event)

        elif self.state == "transition":
            pass

        elif self.state == "pause":
            # Not allowed, return
            if self.allow_inventory_input == False:
                return

            if event.type == pg.KEYUP:
                # Pressed pause again in overlay?
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
        # Fill native surface color to have good contrast for player
        NATIVE_SURF.fill("#6bc5a0")

        if self.state == "playing":
            # Draw player is done in room with other moving actors in draw bg and non moving actors
            a.room.draw()

            # Draw the mini map
            a.mini_map.draw()

        # Draw transition curtain
        elif self.state == "transition":
            # Draw player is done in room with other moving actors in draw bg and non moving actors
            a.room.draw()

            # Draw the mini map
            a.mini_map.draw()

            # Draw transition curtain
            self.transition_curtain.draw()

        # Draw the overlay curtain
        elif self.state == "pause":
            # Draw player is done in room with other moving actors in draw bg and non moving actors
            a.room.draw()

            # Draw overlay curtain
            self.overlay_inventory_curtain.draw()

            # Draw the mini map
            a.mini_map.draw()

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
            self.overlay_inventory_curtain.update(dt)
