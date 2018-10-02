from collections import namedtuple


class NpcSide(namedtuple("NpcSide", "name,degree_min,degree_max,player_in_view,stand_index")):
    # overriding equality to compare
    # the name value
    def __eq__(self, obj):
        return self.name == obj


FRONT = "front"
FRONT_LEFT = "frontleft"
LEFT = "left"
BACK_LEFT = "backleft"
BACK = "back"
BACK_RIGHT = "backright"
RIGHT = "right"
FRONT_RIGHT = "frontright"

SIDE_FRONT = NpcSide(FRONT, 337.5, 22.5, True, 0)
SIDE_FRONT_LEFT = NpcSide(FRONT_LEFT, 22.5, 67.5, True, 7)
SIDE_LEFT = NpcSide(LEFT, 67.5, 112.5, False, 6)
SIDE_BACK_LEFT = NpcSide(BACK_LEFT, 112.5, 157.5, False, 5)
SIDE_BACK = NpcSide(BACK, 157.5, 202.5, False, 4)
SIDE_BACK_RIGHT = NpcSide(BACK_RIGHT, 202.5, 247.5, False, 3)
SIDE_RIGHT = NpcSide(RIGHT, 247.5, 292.5, False, 2)
SIDE_FRONT_RIGHT = NpcSide(FRONT_RIGHT, 292.5, 337.5, True, 1)
