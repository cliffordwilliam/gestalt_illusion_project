from constants import *
import autoload as a
from nodes.camera import Camera
from nodes.room import Room
from actors.player import Player
from actors.goblin import Goblin
from nodes.curtain import Curtain


class World:
    def __init__(self):
        a.room = Room("stage0_gym_small_game.json")

        a.camera = Camera()

        a.world = self

        a.player = Player()
        a.player.rect.x = 32
        a.player.rect.bottom = 144

        a.camera.set_target(a.player.camera_anchor)
        a.camera.set_lerp_weight(0.018)

        # Curtain belongs to world, it needs to distinguish the callback
        self.transition_curtain = Curtain(50, "empty")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_empty_end, "empty_end")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_full_end, "full_end")

        # World state, room transition, pause, cutscene and so on
        self.state = "Playing"

        # To remember which door after transition curtain
        self.next_door = None

    def on_player_hit_door(self, door):
        # Only trigger once, player hit door -> transition state
        if self.state == "Playing":
            self.next_door = door
            self.state = "Transition"

    def on_transition_curtain_empty_end(self):
        # Return to playing state
        self.state = "Playing"

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
        # Player event
        a.player.event(event)

    def draw(self):
        # Fill native surface color to have good contrast for player
        NATIVE_SURF.fill("#6bc5a0")

        # Draw bg
        a.room.draw_bg()

        # Draw player
        a.player.draw()

        # Draw fg
        a.room.draw_fg()

        # Draw curtain
        self.transition_curtain.draw()

    def update(self, dt):
        if self.state == "Playing":
            # Update player
            a.player.update(dt)

            # Update camera
            a.camera.update(dt)

            # Update all bg sprites actors
            a.room.update(dt)

        elif self.state == "Transition":
            # On transition state, immediately update transition curtain
            self.transition_curtain.update(dt)
