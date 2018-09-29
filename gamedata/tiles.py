from consts import tile

tile_texture = {}
tile_solid = {
    0: False,
    1: True,
    2: True,
    3: True,
    4: True,
    5: True,
    6: True,
    7: True,
    8: True,
    9: True,
    10: False,

    11: True,
    12: True,
    13: True,
    14: True,
    15: True,
    16: True,
    17: True,
    18: True,

    19: True,
    20: True,
    21: True,
    22: True,
    23: True,
    24: True,
    25: True,
    }
tile_visible = { #Sprite tiles are not visible
    0: False,
    1: True,
    2: True,
    3: True,
    4: True,
    5: True,
    6: True,
    7: True,
    8: False,
    9: False,
    10: False,

    11: True,
    12: True,
    13: True,
    14: True,
    15: True,
    16: False,
    17: False,
    18: False,

    19: True,
    20: True,
    21: True,
    22: True,
    23: True,
    24: True,
    25: False,
    }
texture_type = { #air, wall, trigger, sprite
    0: tile.AIR,
    1: tile.WALL,
    2: tile.WALL,
    3: tile.WALL,
    4: tile.WALL,
    5: tile.END,
    6: tile.VERTICAL_DOOR,
    7: tile.HORIZONTAL_DOOR,
    8: tile.SPRITE,
    9: tile.SPRITE,
    10: tile.SPRITE,

    11: tile.WALL,
    12: tile.WALL,
    13: tile.WALL,
    14: tile.WALL,
    15: tile.END,
    16: tile.SPRITE,
    17: tile.SPRITE,
    18: tile.SPRITE,

    19: tile.WALL,
    20: tile.WALL,
    21: tile.WALL,
    22: tile.END,
    23: tile.VERTICAL_DOOR,
    24: tile.HORIZONTAL_DOOR,
    25: tile.SPRITE,
    }
