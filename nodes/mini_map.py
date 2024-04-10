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

        # Whole minimap topleft anchor, change this to move the entire thing, Move it to bottom left
        self.mini_map_x = TILE_S * 0
        self.mini_map_y = TILE_S * 9

        # Padding from left and bottom, update room top left
        self.padding = TILE_S // 4
        self.mini_map_x += self.padding
        self.mini_map_y -= self.padding

        # Determine where the center of the map is at to draw player icon
        self.offset_x = TILE_S + self.mini_map_x
        self.offset_y = TILE_S + self.mini_map_y
        # To draw player since rect is 2 by 2, need to shift the tl by 1
        self.offset_x_min_1 = self.offset_x - 1
        self.offset_y_min_1 = self.offset_y - 1

        # Set minimap size
        self.mini_map_width = TILE_S * 2
        self.mini_map_height = TILE_S * 2

        # Get the map other points, right and bottom
        self.mini_map_right = self.mini_map_x + self.mini_map_width
        self.mini_map_bottom = self.mini_map_y + self.mini_map_height

    def add_room(self, data):
        room_name = data["name"]

        # This given room not added yet?
        if room_name not in self.visited_rooms:
            # Add it to list, to be drawn
            self.rooms.append(data)

            # Add it to set, to check, no dup
            self.visited_rooms.add(room_name)

    def draw(self):
        # Draw the mini map background and outline
        pg.draw.rect(NATIVE_SURF, "black",
                     (self.mini_map_x, self.mini_map_y, self.mini_map_width, self.mini_map_height))
        pg.draw.rect(NATIVE_SURF, "white",
                     (self.mini_map_x, self.mini_map_y, self.mini_map_width, self.mini_map_height), 1)

        # Iterate over each room
        for data in self.rooms:
            # Get room rect
            room_rect = data["rect"]

            # Get room 4 points with the player offset and minimap position offset
            x = room_rect[0] - (a.player.rect.center[0] //
                                TILE_S) + self.offset_x
            y = room_rect[1] - (a.player.rect.center[1] //
                                TILE_S) + self.offset_y
            r = x + room_rect[2]
            b = y + room_rect[3]

            # Ensure 4 rects points are in the minimap 4 points
            x = max(self.mini_map_x, min(x, self.mini_map_right))
            y = max(self.mini_map_y, min(y, self.mini_map_bottom))
            r = max(self.mini_map_x, min(r, self.mini_map_right))
            b = max(self.mini_map_y, min(b, self.mini_map_bottom))

            # Compute the w and h for drawing
            w = r - x
            h = b - y

            # Draw the room
            pg.draw.rect(NATIVE_SURF, "white", (x, y, w, h), 1)

        # Draw center - represent player
        pg.draw.rect(NATIVE_SURF, "red",
                     (self.offset_x_min_1, self.offset_y_min_1, 2, 2))
