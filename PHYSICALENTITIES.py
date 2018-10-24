from typing import Tuple
import pygame


class PhysicalEntity:
    
    def __init__(self, map_pos: Tuple[int, int], solid: bool, rect: pygame.Rect, pos: Tuple[float, float]):
        
        self.map_pos = map_pos  # {tuple}
        self.pos = pos  # {tuple}
        self.rect = rect  # {Rect}
        self.solid = solid  # {bool}

        # self.ID = ID  # {int} this will be set for us when adding to the list of physical entities
        # self.distance = # this will be computed for us


