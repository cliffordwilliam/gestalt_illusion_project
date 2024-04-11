from constants import *
import autoload as a


class MiniMap:
    '''
    How to use: 
        1: Create it before player and room
        2: Call its draw method
        3: When room change call my add room method

    What will happen:
        1: This thing will draw the added room is rel pos to player pos
    '''

    def __init__(self):
        # TODO: Read save data and populate my rooms
        self.rooms = []
        self.visited_rooms = set()

        # Whole minimap topleft anchor, change this to move the entire thing
        self.x = TILE_S * 0
        self.y = TILE_S * 9

        # Padding from left and bottom, update room top left
        self.padding = TILE_S // 4
        self.x += self.padding
        self.y -= self.padding

        # Set minimap size
        self.w = TILE_S * 2
        self.h = TILE_S * 2

        # Determine where the center of the map is at to draw player icon
        self.offset_x = (self.w // 2) + self.x
        self.offset_y = (self.h // 2) + self.y
        # To draw player since rect is 2 by 2, need to shift the tl by 1
        self.offset_x_1 = self.offset_x - 1
        self.offset_y_1 = self.offset_y - 1

        # Get the map other points, right and bottom
        self.r = self.x + self.w
        self.b = self.y + self.h

        # Gameplay or menu mode
        self.state = "gameplay"

        # Drawn once in inventory entry, avoid looping when player is not moving anyways why for loop
        self.inventory_surface = pg.Surface((NATIVE_W, NATIVE_H))

    def set_state(self, value):
        # Update the is inventory
        self.state = value

        if self.state == "gameplay":
            # Whole minimap topleft anchor, change this to move the entire thing
            self.x = TILE_S * 0
            self.y = TILE_S * 9

            # Padding from left and bottom, update room top left
            self.padding = TILE_S // 4
            self.x += self.padding
            self.y -= self.padding

            # Set minimap size
            self.w = TILE_S * 2
            self.h = TILE_S * 2

            # Determine where the center of the map is at to draw player icon
            self.offset_x = (self.w // 2) + self.x
            self.offset_y = (self.h // 2) + self.y
            # To draw player since rect is 2 by 2, need to shift the tl by 1
            self.offset_x_1 = self.offset_x - 1
            self.offset_y_1 = self.offset_y - 1

            # Get the map other points, right and bottom
            self.r = self.x + self.w
            self.b = self.y + self.h

        elif self.state == "inventory":
            # Clear previous draw
            self.inventory_surface.fill("black")

            # Inventory mode topleft
            self.x = TILE_S * 7
            self.y = TILE_S * 2

            # Inventory mode size
            self.w = TILE_S * 11
            self.h = TILE_S * 6

            # Determine where the center of the map is at to draw player icon
            self.offset_x = (self.w // 2) + self.x
            self.offset_y = (self.h // 2) + self.y
            # To draw player since rect is 2 by 2, need to shift the tl by 1
            self.offset_x_1 = self.offset_x - 1
            self.offset_y_1 = self.offset_y - 1

            # Get the map other points, right and bottom
            self.r = self.x + self.w
            self.b = self.y + self.h

            # Draw on the inventory page
            player_x_tu = 0
            player_y_tu = 0

            # Iterate over each room
            for data in self.rooms:
                # Get room rect
                room_rect = data["rect"]

                # Get room 4 points with the player offset and minimap position offset
                x = room_rect[0] - (player_x_tu //
                                    TILE_S) + self.offset_x
                y = room_rect[1] - (player_y_tu //
                                    TILE_S) + self.offset_y
                r = x + room_rect[2]
                b = y + room_rect[3]

                # Ensure 4 rects points are in the minimap 4 points
                x = max(self.x, min(x, self.r))
                y = max(self.y, min(y, self.b))
                r = max(self.x, min(r, self.r))
                b = max(self.y, min(b, self.b))

                # Compute the w and h for drawing
                w = r - x
                h = b - y

                # Draw the room
                pg.draw.rect(self.inventory_surface, "white", (x, y, w, h), 1)

                # Get the doors
                for door in data["doors_pos"]:
                    # Get room 4 points with the player offset and minimap position offset
                    x = door["xtu"] - (player_x_tu //
                                       TILE_S) + self.offset_x
                    y = door["ytu"] - \
                        (player_y_tu // TILE_S) + self.offset_y
                    r = x + 1
                    b = y + 1

                    # Ensure 4 rects points are in the minimap 4 points
                    x = max(self.x, min(x, self.r))
                    y = max(self.y, min(y, self.b))
                    r = max(self.x, min(r, self.r))
                    b = max(self.y, min(b, self.b))

                    # Compute the w and h for drawing
                    w = r - x
                    h = b - y

                    # Draw the door
                    pg.draw.rect(self.inventory_surface,
                                 "black", (x, y, w, h), 1)

            # Draw the white frame
            pg.draw.rect(self.inventory_surface, "white",
                         (self.x, self.y, self.w, self.h), 1)

            # Inventory mode draw player rel to center offset
            player_x_tu = a.player.rect.center[0] // TILE_S + self.offset_x
            player_y_tu = a.player.rect.center[1] // TILE_S + self.offset_y
            pg.draw.rect(self.inventory_surface, "red",
                         (player_x_tu, player_y_tu, 2, 2))

    def add_room(self, data):
        room_name = data["name"]

        # This given room not added yet?
        if room_name not in self.visited_rooms:
            # Add it to list, to be drawn
            self.rooms.append(data)

            # Add it to set, to check, no dup
            self.visited_rooms.add(room_name)

    def draw(self, surf=NATIVE_SURF):
        # Draw the mini map background
        pg.draw.rect(surf, "black", (self.x, self.y, self.w, self.h))

        # In inventory mode, no player offset
        if self.state == "inventory":
            surf.blit(self.inventory_surface, (0, 0))

        # In inventory mode, no player offset
        elif self.state == "gameplay":
            # Get player pos
            player_x_tu = a.player.rect.center[0]
            player_y_tu = a.player.rect.center[1]

            # Iterate over each room
            for data in self.rooms:
                # Get room rect
                room_rect = data["rect"]

                # Get room 4 points with the player offset and minimap position offset
                x = room_rect[0] - (player_x_tu //
                                    TILE_S) + self.offset_x
                y = room_rect[1] - (player_y_tu //
                                    TILE_S) + self.offset_y
                r = x + room_rect[2]
                b = y + room_rect[3]

                # Ensure 4 rects points are in the minimap 4 points
                x = max(self.x, min(x, self.r))
                y = max(self.y, min(y, self.b))
                r = max(self.x, min(r, self.r))
                b = max(self.y, min(b, self.b))

                # Compute the w and h for drawing
                w = r - x
                h = b - y

                # Draw the room
                pg.draw.rect(surf, "white", (x, y, w, h), 1)

                # Get the doors
                for door in data["doors_pos"]:
                    # Get room 4 points with the player offset and minimap position offset
                    x = door["xtu"] - (player_x_tu //
                                       TILE_S) + self.offset_x
                    y = door["ytu"] - \
                        (player_y_tu // TILE_S) + self.offset_y
                    r = x + 1
                    b = y + 1

                    # Ensure 4 rects points are in the minimap 4 points
                    x = max(self.x, min(x, self.r))
                    y = max(self.y, min(y, self.b))
                    r = max(self.x, min(r, self.r))
                    b = max(self.y, min(b, self.b))

                    # Compute the w and h for drawing
                    w = r - x
                    h = b - y

                    # Draw the door
                    pg.draw.rect(surf, "black", (x, y, w, h), 1)

            # Draw the white frame
            pg.draw.rect(surf, "white",
                         (self.x, self.y, self.w, self.h), 1)

            # Draw center - represent player
            pg.draw.rect(surf, "red",
                         (self.offset_x_1, self.offset_y_1, 2, 2))
