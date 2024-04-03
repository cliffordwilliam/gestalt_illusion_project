from constants import *
import autoload as a
from nodes.camera import Camera
from nodes.room import Room
from actors.player import Player
from nodes.curtain import Curtain


class World:
    def __init__(self):
        a.room = Room("stage0_gym_small_game.json")

        a.camera = Camera()

        a.world = self

        a.player = Player()
        a.player.rect.x = 32

        a.camera.set_target(a.player.camera_anchor)

        # Curtain belongs to world, it needs to distinguish the callback
        self.transition_curtain = Curtain(50, "empty")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_empty_end, "empty_end")
        self.transition_curtain.add_event_listener(
            self.on_transition_curtain_full_end, "full_end")

        self.state = "Normal"

        self.next_door = None

    def on_player_hit_door(self, door):
        if self.state == "Normal":
            self.next_door = door
            self.state = "Transition"

    def on_transition_curtain_empty_end(self):
        self.state = "Normal"
        self.transition_curtain.curtain.set_alpha(0)
        self.transition_curtain.alpha = 0
        self.transition_curtain.fade_duration = self.transition_curtain.fade_duration
        self.transition_curtain.fade_timer = 0
        self.transition_curtain.direction = 1
        self.transition_curtain.remainder = 0

    def on_transition_curtain_full_end(self):
        # Change room
        self.change_room()
        # Reverse transition curtain direction
        self.transition_curtain.direction *= -1

    def change_room(self):
        # region Replace this room with new room
        door_target = self.next_door["target"]
        STAGE_NO = door_target["STAGE_NO"]
        target = door_target["target"]
        a.room.set_name(f"stage{STAGE_NO}_{target}_game.json")

        # region Move player and camera to new room
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
        # endregion Move player and camera to new room

    def event(self, event):
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
        if self.state == "Normal":
            # Update player
            a.player.update(dt)

            # Update camera
            a.camera.update(dt)

            # Update all bg sprites actors
            a.room.update(dt)

        if self.state == "Transition":
            # On transition state, immediately play curtain
            self.transition_curtain.update(dt)
