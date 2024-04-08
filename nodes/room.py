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

        # Dicts of regions for drawing all bg AND ACTOR - ACTOR DRAW AND UPDATE THEMSELVES
        # I cannot separate this becase a fire on layer 3 should be drawn on layer 3 and be updated too
        # It is just like the other bg sprite but it needs to draw and update itself
        self.bg_draw_update_layers = self.room_data["BG_LAYERS"]

        # Actors (enemies, goblins)
        self.actor_layer = self.room_data["ACTOR_LAYER"]

        # The lookup map for static solid tiles
        self.collision_layer = self.room_data["COLLISION_LAYER"]

        # Dicts of region for drawing fg
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

        # Check if there are any actors in bg_draw_update_layers
        for i in range(len(self.bg_draw_update_layers)):
            room = self.bg_draw_update_layers[i]
            for j in range(len(room)):
                sprite = room[j]
                if sprite != 0:
                    sprite_name = sprite["name"]
                    x = sprite["xds"]
                    y = sprite["yds"]
                    # Found?
                    if sprite_name in a.game.actors:
                        # Instance
                        actor = a.game.actors[sprite_name]()
                        actor.rect.x = x
                        actor.rect.y = y
                        actor.rect.y -= actor.rect.height - TILE_S
                        # Replace the dict with this instance in bg_draw_update_layers
                        self.bg_draw_update_layers[i][j] = {
                            "name": "actor", "obj": actor}

        # region Turn dict to actual instances actors
        for i in range(len(self.actor_layer)):
            obj = self.actor_layer[i]
            instance = a.game.actors[obj["name"]]()
            instance.rect.x = obj["xds"]
            instance.rect.y = obj["yds"]
            instance.rect.y -= instance.rect.height - TILE_S
            self.actor_layer[i] = instance
        # endregion Turn dict to actual instances actors

    def set_name(self, name):
        # Get new room name
        self.name = name

        # Use room name to read json
        self.room_data = {}
        with open(JSONS_PATHS[self.name], 'r') as data:
            self.room_data = load(data)

        # Dicts of regions for drawing all bg AND ACTOR - ACTOR DRAW AND UPDATE THEMSELVES
        self.bg_draw_update_layers = self.room_data["BG_LAYERS"]

        # Actors (enemies, goblins)
        self.actor_layer = self.room_data["ACTOR_LAYER"]

        # The lookup map for static solid tiles
        self.collision_layer = self.room_data["COLLISION_LAYER"]

        # Dicts of region for drawing fg
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

        # Check if there are any actors in bg_draw_update_layers
        for i in range(len(self.bg_draw_update_layers)):
            room = self.bg_draw_update_layers[i]
            for j in range(len(room)):
                sprite = room[j]
                if sprite != 0:
                    sprite_name = sprite["name"]
                    x = sprite["xds"]
                    y = sprite["yds"]
                    # Found?
                    if sprite_name in a.game.actors:
                        # Instance
                        actor = a.game.actors[sprite_name]()
                        actor.rect.x = x
                        actor.rect.y = y
                        actor.rect.y -= actor.rect.height - TILE_S
                        # Replace the dict with this instance in bg_draw_update_layers
                        self.bg_draw_update_layers[i][j] = {
                            "name": "actor", "obj": actor}

        # region Turn dict to actual instances actors
        for i in range(len(self.actor_layer)):
            obj = self.actor_layer[i]
            instance = a.game.actors[obj["name"]]()
            instance.rect.x = obj["xds"]
            instance.rect.y = obj["yds"]
            instance.rect.y -= instance.rect.height - TILE_S
            self.actor_layer[i] = instance
        # endregion Turn dict to actual instances actors

    def draw_bg(self):
        # Camera not ready? return
        if a.camera == None:
            return

        # Each names are unique ids, be sure to add the available bg in json manually
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

        # region Draw all collision sprites
        # Unpack cam position tl
        cam_x = a.camera.rect.x
        cam_y = a.camera.rect.y

        # Turn coord into tu
        cam_x_tu = cam_x // TILE_S
        cam_y_tu = cam_y // TILE_S

        # Turn tu into index, by sub cam offset
        cam_x_tu = int(cam_x_tu - self.x_tu)
        cam_y_tu = int(cam_y_tu - self.y_tu)

        for room in self.bg_draw_update_layers:
            for item in room:
                # Iterate over rows
                for row in range(12):
                    # Iterate over columns
                    for col in range(21):
                        # Calculate index for the current tile
                        index = (cam_y_tu + row) * self.w_tu + (cam_x_tu + col)

                        # Makes sure its in index
                        if 0 <= index < len(room):
                            # Get item and grab its draw pos
                            item = self.room[index]

                            # Find air? Continue
                            if item == 0:
                                continue

                            # Found actor?
                            if item["name"] == "actor":
                                sprite = item["obj"]
                                sprite.draw()
                                continue

                            # Find item? Draw
                            item_xd = item["xds"] - a.camera.rect.x
                            item_yd = item["yds"] - a.camera.rect.y

                            # Draw the tile
                            NATIVE_SURF.blit(self.sprite_sheet_surf,
                                             (item_xd, item_yd), item["region"])
        # endregion Draw bg_draw_update_layers (some bg sprites are classes, fire, water)

        # region Draw actors
        for actor in self.actor_layer:
            if a.camera.rect.colliderect(actor.rect):
                actor.draw()
        # endregion Draw actors

    def draw_fg(self):
        # Camera not ready? return
        if a.camera == None:
            return

        # region Draw all collision sprites
        # Unpack cam position tl
        cam_x = a.camera.rect.x
        cam_y = a.camera.rect.y

        # Turn coord into tu
        cam_x_tu = cam_x // TILE_S
        cam_y_tu = cam_y // TILE_S

        # Turn tu into index, by sub cam offset
        cam_x_tu = int(cam_x_tu - self.x_tu)
        cam_y_tu = int(cam_y_tu - self.y_tu)

        # Iterate over rows
        for row in range(12):
            # Iterate over columns
            for col in range(21):
                # Calculate index for the current tile
                index = (cam_y_tu + row) * self.w_tu + (cam_x_tu + col)

                # Makes sure its in index
                if 0 <= index < len(self.collision_layer):
                    # Get item and grab its draw pos
                    item = self.collision_layer[index]

                    # Find air? Continue
                    if item == 0:
                        continue

                    # Find item? Draw
                    item_xd = item["xds"] - a.camera.rect.x
                    item_yd = item["yds"] - a.camera.rect.y

                    # Draw the tile
                    NATIVE_SURF.blit(self.sprite_sheet_surf,
                                     (item_xd, item_yd), item["region"])

        # region Draw all fg sprites
        for room in self.fg_layers:
            for item in room:
                # Iterate over rows
                for row in range(12):
                    # Iterate over columns
                    for col in range(21):
                        # Calculate index for the current tile
                        index = (cam_y_tu + row) * self.w_tu + (cam_x_tu + col)

                        # Makes sure its in index
                        if 0 <= index < len(room):
                            # Get item and grab its draw pos
                            item = self.room[index]

                            # Find air? Continue
                            if item == 0:
                                continue

                            # Find item? Draw
                            item_xd = item["xds"] - a.camera.rect.x
                            item_yd = item["yds"] - a.camera.rect.y

                            # Draw the tile
                            NATIVE_SURF.blit(self.sprite_sheet_surf,
                                             (item_xd, item_yd), item["region"])
        # endregion all fg sprites

    def update(self, dt):
        # Camera not ready? return
        if a.camera == None:
            return

        # Unpack cam position tl
        cam_x = a.camera.rect.x
        cam_y = a.camera.rect.y

        # Turn coord into tu
        cam_x_tu = cam_x // TILE_S
        cam_y_tu = cam_y // TILE_S

        # Turn tu into index, by sub cam offset
        cam_x_tu = int(cam_x_tu - self.x_tu)
        cam_y_tu = int(cam_y_tu - self.y_tu)

        # region Update all bg sprites (some bg sprites are classes, fire, water)
        for room in self.bg_draw_update_layers:
            for item in room:
                # Iterate over rows
                for row in range(12):
                    # Iterate over columns
                    for col in range(21):
                        # Calculate index for the current tile
                        index = (cam_y_tu + row) * self.w_tu + (cam_x_tu + col)

                        # Makes sure its in index
                        if 0 <= index < len(room):
                            # Get item and grab its draw pos
                            item = self.room[index]

                            # Find air? Continue
                            if item == 0:
                                continue

                            # Found actor?
                            if item["name"] == "actor":
                                sprite = item["obj"]
                                sprite.update(dt)
                                continue
        # endregion Update all bg sprites (some bg sprites are classes, fire, water)

        # region Update actors
        for actor in self.actor_layer:
            if a.camera.rect.colliderect(actor.rect):
                actor.update(dt)
        # endregion Update actors
