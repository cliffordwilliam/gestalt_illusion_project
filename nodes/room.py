from constants import *
import autoload as a


class Room:
    '''
    How to use: 
        1: Give me room name
        2: Room name is used to load json game room, not editor
        3: Room data is extracted
        4: There are bg layers and 1 collision layer, collision layer is the lookup table
        5: I have room rect for camera limit and player reposition after transition
        6: Manually typed bg is also extracted to draw the hard coded background, make sure that you type in the correct available bg for distict stages
        7: Use my name setter to change room, if new room is in same stage, I will not re import the image for this stage
        8: Any sprite names that are in game actors list, will be instanced and placed in layer, replacing the dict

    What will happen:
        1: You need to call my bg layer draw, This func, for every frame draws the bg
        2: Same goes with fg, fg includes the collision layer first, then the fg
        3: I have update func to update all actors in my bg layers

    TODO: Add an actor layer, where enemies, or wahtever that is moving around like the player has to be placed into -> then use quad tree for collision check. place quadtree as big as room size
    TODO: Start with a bouncing ball in a room, that goes in linear speed, if it collide with solid static tiles, bounce, use lookup map for that. Then if it hits moving placer, bounce too, use quad tree for that
    TODO: What if it is inside the collision layer? Then have it update its position in the lookup table, like a moving floor - NVM, if 2 actors of small hitbox are in same tile, they wont detect each other
    '''

    def __init__(self, name):
        # Get room name
        self.name = name

        # Room name -> read json
        self.room_data = {}
        with open(JSONS_PATHS[self.name], 'r') as data:
            self.room_data = load(data)

        # Room layers
        self.bg_layers = self.room_data["BG_LAYERS"]
        self.collision_layer = self.room_data["COLLISION_LAYER"]
        self.collision_draw_layer = [x for x in self.collision_layer if x != 0]
        self.fg_layers = self.room_data["FG_LAYERS"]

        # Room rect, room camera limit
        self.rect = self.room_data["ROOM_RECT"]
        self.x_tu = self.rect[0] // TILE_S
        self.y_tu = self.rect[1] // TILE_S
        self.w_tu = self.rect[2] // TILE_S
        self.h_tu = self.rect[3] // TILE_S

        # Room background names that it needs to draw
        self.bg1 = self.room_data["BG1"]
        self.bg2 = self.room_data["BG2"]
        self.bg3 = self.room_data["BG3"]
        self.bg4 = self.room_data["BG4"]

        # Load this room sprite sheet
        self.sprite_sheet_png_name = self.room_data["SPRITE_SHEET_PNG_NAME"]
        self.sprite_sheet_path = PNGS_PATHS[self.sprite_sheet_png_name]
        self.sprite_sheet_surf = pg.image.load(
            self.sprite_sheet_path).convert_alpha()

        # Check if there are any actors in bg layers
        for i in range(len(self.bg_layers)):
            room = self.bg_layers[i]
            for j in range(len(room)):
                sprite = room[j]
                if sprite != 0:
                    name = sprite["name"]
                    x = sprite["xds"]
                    y = sprite["yds"]
                    if name in a.game.actors:
                        actor = a.game.actors[name](
                            self.sprite_sheet_surf, x, y)
                        self.bg_layers[i][j] = {"name": "actor", "obj": actor}

    def set_name(self, name):
        # Get new room name
        self.name = name

        # Use room name to read json
        self.room_data = {}
        with open(JSONS_PATHS[self.name], 'r') as data:
            self.room_data = load(data)

        # Room layers
        self.bg_layers = self.room_data["BG_LAYERS"]
        self.collision_layer = self.room_data["COLLISION_LAYER"]
        self.collision_draw_layer = [x for x in self.collision_layer if x != 0]
        self.fg_layers = self.room_data["FG_LAYERS"]

        # Room rect, room camera limit
        self.rect = self.room_data["ROOM_RECT"]
        self.x_tu = self.rect[0] // TILE_S
        self.y_tu = self.rect[1] // TILE_S
        self.w_tu = self.rect[2] // TILE_S
        self.h_tu = self.rect[3] // TILE_S

        # Room background names that it needs to draw
        self.bg1 = self.room_data["BG1"]
        self.bg2 = self.room_data["BG2"]
        self.bg3 = self.room_data["BG3"]
        self.bg4 = self.room_data["BG4"]

        # Only load new sprite sheet if it is different from what I have now
        if self.room_data["SPRITE_SHEET_PNG_NAME"] != self.sprite_sheet_png_name:
            self.sprite_sheet_png_name = self.room_data["SPRITE_SHEET_PNG_NAME"]
            self.sprite_sheet_path = PNGS_PATHS[self.sprite_sheet_png_name]
            self.sprite_sheet_surf = pg.image.load(
                self.sprite_sheet_path).convert_alpha()

        # Check if there are any actors in bg layers
        for i in range(len(self.bg_layers)):
            room = self.bg_layers[i]
            for j in range(len(room)):
                sprite = room[j]
                if sprite != 0:
                    sprite_name = sprite["name"]
                    x = sprite["xds"]
                    y = sprite["yds"]
                    # Instance actor and place it in bg layer
                    if sprite_name in a.game.actors:
                        actor = a.game.actors[sprite_name](
                            self.sprite_sheet_surf, x, y)
                        self.bg_layers[i][j] = {"name": "actor", "obj": actor}

    def draw_bg(self):
        # Camera not ready? return
        if a.camera == None:
            return

        # Each names are unique ids
        if self.bg1 == "sky":
            x = (-a.camera.rect.x * 0.05) % NATIVE_W
            NATIVE_SURF.blit(self.sprite_sheet_surf, (x, 0), (0, 0, 320, 179))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x - NATIVE_W, 0), (0, 0, 320, 179))

        if self.bg2 == "clouds":
            x = (-a.camera.rect.x * 0.1) % NATIVE_W
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x, 0), (0, 176, 320, 160))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x - NATIVE_W, 0), (0, 176, 320, 160))

        if self.bg3 == "trees":
            x = (-a.camera.rect.x * 0.5) % NATIVE_W
            # 1
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x, 32), (320, 448, 80, 160))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x - NATIVE_W, 32), (320, 448, 80, 160))
            # 2
            NATIVE_SURF.blit(self.sprite_sheet_surf, (x + 96, 64),
                             (320, 448, 80, 160))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x + 96 - NATIVE_W, 64), (320, 448, 80, 160))
            # 3
            NATIVE_SURF.blit(self.sprite_sheet_surf, (x + 160, 32),
                             (320, 448, 80, 160))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x + 160 - NATIVE_W, 32), (320, 448, 80, 160))
            # 4
            NATIVE_SURF.blit(self.sprite_sheet_surf, (x + 224, 16),
                             (320, 448, 80, 160))
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (x + 224 - NATIVE_W, 16), (320, 448, 80, 160))

        if self.bg4 == "blue_glow":
            NATIVE_SURF.blit(self.sprite_sheet_surf,
                             (0, 48), (0, 512, 320, 128))
        # endregion

        # region Draw all bg sprites
        for room in self.bg_layers:
            for item in room:
                # Only draw sprites that are in view
                if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                    if item["name"] == "actor":
                        item["obj"].draw()
                        continue
                    xd = item["xds"] - a.camera.rect.x
                    yd = item["yds"] - a.camera.rect.y
                    NATIVE_SURF.blit(self.sprite_sheet_surf,
                                     (xd, yd), item["region"])
        # endregion Draw all bg sprites

    def draw_fg(self):
        # Camera not ready? return
        if a.camera == None:
            return

        # region Draw all collision sprites
        for item in self.collision_draw_layer:
            # Only draw sprites that are in view
            if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                xd = item["xds"] - a.camera.rect.x
                yd = item["yds"] - a.camera.rect.y
                NATIVE_SURF.blit(self.sprite_sheet_surf,
                                 (xd, yd), item["region"])
        # endregion Draw all collision sprites

        # region Draw all fg sprites
        for room in self.fg_layers:
            for item in room:
                # Only draw sprites that are in view
                if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                    xd = item["xds"] - a.camera.rect.x
                    yd = item["yds"] - a.camera.rect.y
                    NATIVE_SURF.blit(self.sprite_sheet_surf,
                                     (xd, yd), item["region"])
        # endregion all fg sprites

    def update(self, dt):
        # Camera not ready? return
        if a.camera == None:
            return

        # region Draw all bg sprites
        for room in self.bg_layers:
            for item in room:
                # Only draw sprites that are in view
                if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                    if item["name"] == "actor":
                        item["obj"].update(dt)
        # endregion Draw all bg sprites
