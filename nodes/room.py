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
        4: Collision layers may have actors, these will be moved to the draw update collision layer. Where stuffs are drawn and updated
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
        self.collision_draw_update_layer = [
            x for x in self.collision_layer if x != 0]
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
                    sprite_name = sprite["name"]
                    x = sprite["xds"]
                    y = sprite["yds"]
                    if sprite_name in a.game.actors:
                        actor = a.game.actors[sprite_name]()
                        actor.rect.x = x
                        actor.rect.y = y
                        actor.rect.y -= actor.rect.height - TILE_S
                        self.bg_layers[i][j] = {"name": "actor", "obj": actor}

        # Check if there are any actors in collision layer
        for i in range(len(self.collision_draw_update_layer)):
            sprite = self.collision_draw_update_layer[i]
            sprite_name = sprite["name"]
            x = sprite["xds"]
            y = sprite["yds"]
            if sprite_name in a.game.actors:
                actor = a.game.actors[sprite_name]()
                actor.rect.x = x
                actor.rect.y = y
                actor.rect.y -= actor.rect.height - TILE_S
                self.collision_draw_update_layer[i] = {
                    "name": "actor", "obj": actor}

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
        self.collision_draw_update_layer = [
            x for x in self.collision_layer if x != 0]
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
                        actor = a.game.actors[sprite_name]()
                        actor.rect.x = x
                        actor.rect.y = y
                        actor.rect.y -= actor.rect.height
                        self.bg_layers[i][j] = {"name": "actor", "obj": actor}

        # Check if there are any actors in collision layer
        for i in range(len(self.collision_draw_update_layer)):
            sprite = self.collision_draw_update_layer[i]
            sprite_name = sprite["name"]
            x = sprite["xds"]
            y = sprite["yds"]
            if sprite_name in a.game.actors:
                actor = a.game.actors[sprite_name]()
                actor.rect.x = x
                actor.rect.y = y
                actor.rect.y -= actor.rect.height - TILE_S
                self.collision_draw_update_layer[i] = {
                    "name": "actor", "obj": actor}

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
                # Found actor? Call their draw
                if item["name"] == "actor":
                    sprite = item["obj"]
                    if (a.camera.rect.x - sprite.rect.width <= sprite.rect.x < a.camera.rect.right) and (a.camera.rect.y - sprite.rect.height <= sprite.rect.y < a.camera.rect.bottom):
                        sprite.draw()
                        continue

                # Only draw sprites that are in view
                if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                    # Not actor? Draw normal
                    xd = item["xds"] - a.camera.rect.x
                    yd = item["yds"] - a.camera.rect.y
                    NATIVE_SURF.blit(self.sprite_sheet_surf,
                                     (xd, yd), item["region"])

        # region Draw all collision actor sprites
        for item in self.collision_draw_update_layer:
            # Found actor? Call their draw
            if item["name"] == "actor":
                sprite = item["obj"]
                if (a.camera.rect.x - sprite.rect.width <= sprite.rect.x < a.camera.rect.right) and (a.camera.rect.y - sprite.rect.height <= sprite.rect.y < a.camera.rect.bottom):
                    sprite.draw()
                    continue
        # endregion Draw all collision actor sprites
        # endregion Draw all bg sprites

    def draw_fg(self):
        # Camera not ready? return
        if a.camera == None:
            return

        # region Draw all collision sprites
        for item in self.collision_draw_update_layer:
            if item["name"] != "actor":
                # Only draw sprites that are in view
                if (a.camera.rect.x - item["region"][2] <= item["xds"] < a.camera.rect.right) and (a.camera.rect.y - item["region"][3] <= item["yds"] < a.camera.rect.bottom):
                    # Not actor? Draw normal
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

        # region Update all bg sprites
        for room in self.bg_layers:
            for item in room:
                if item["name"] == "actor":
                    sprite = item["obj"]
                    if (a.camera.rect.x - sprite.rect.width <= sprite.rect.x < a.camera.rect.right) and (a.camera.rect.y - sprite.rect.height <= sprite.rect.y < a.camera.rect.bottom):
                        sprite.update(dt)
                        continue
        # endregion Update all bg sprites

        # region Update all collision actors
        for item in self.collision_draw_update_layer:
            if item["name"] == "actor":
                sprite = item["obj"]
                if (a.camera.rect.x - sprite.rect.width <= sprite.rect.x < a.camera.rect.right) and (a.camera.rect.y - sprite.rect.height <= sprite.rect.y < a.camera.rect.bottom):
                    sprite.update(dt)
                    continue
        # endregion Update all collision actors
