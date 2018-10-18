import SETTINGS
import random
from GEOM import max_grid_distance

#There is some whack error handling. This is because this might be used manually by a human and therefore it needs some human-friendly feedback.
#This is the A* pathfinding algorithm for NPC movement and more
#G = Distance from start
#H = Distance to end
#F = G + H
#open/closedlist syntax = [G, H, F, parent]
#Parent is from where the node is checked.

def pathfind(start, end):
    """

    :param start: List[int]
    :param end: List[int]
    :return:
    """
    #print(start, end)
    '''== A* Pathfinding ==\npathfind(start, end) -> Shortest path from start to end\nFormat is list with tile objects'''
    openlist = {}
    closedlist = {}
    path = []
    error = False

    error = check_path_points_inside_map(start, end)

    if not error:
        start_point = [x for x in SETTINGS.all_tiles if x.map_pos == start]
        if len(start_point) == 0:
            print("Coudln't get a Tile for start", start)
            return path
        else:
            start_point = start_point[0]

        end_point = [x for x in SETTINGS.all_tiles if x.map_pos == end]
        if len(end_point) == 0:
            print("Coudln't get a Tile for end", end)
            return path
        else:
            end_point = end_point[0]
        
        #Report errors
        if SETTINGS.tile_solid[start_point.ID] and (start_point.type != 'hdoor' and start_point.type != 'vdoor'):
            print("=== WARNING: ===")
            print("Error! Start point in pathfinding is a solid block!")
            print(start_point.map_pos, start_point.ID)
            print()
            error = True
        if SETTINGS.tile_solid[end_point.ID] and (end_point.type != 'hdoor' and end_point.type != 'vdoor'):
            print("=== WARNING: ===")
            print("Error! End point in pathfinding is a solid block!")
            print(end_point.map_pos, end_point.ID)
            print()
            error = True

        if error:
            end_point = find_tile_near_position(end)
            if not end_point:
                end_point = find_tile_near_position(start)
            if end_point:
                print("Fallback to", end_point)
                error = False
                    
                

    if not error:
        #f_value has to be determined after creation of node.
        openlist[start_point] = [0, find_distance(start_point, end_point), 0, None]
        openlist[start_point][2] = f_value(start_point, openlist)
        current_point = start_point

        while current_point != end_point:
            try:
                current_point = min(openlist, key=lambda k: (openlist[k][2], openlist[k][1]))
            except:
                error = True
                break
            
            closedlist[current_point] = openlist[current_point]
            del openlist[current_point]

            #Find adjacent nodes
            #TODO refactor to user find_near_position or find_adjacenttiles??
            adjacent = []
            
            adj_up = [x for x in SETTINGS.all_tiles if x.map_pos[0] == current_point.map_pos[0] and x.map_pos[1] == current_point.map_pos[1]-1]
            adj_right = [x for x in SETTINGS.all_tiles if x.map_pos[0] == current_point.map_pos[0]+1 and x.map_pos[1] == current_point.map_pos[1]]
            adj_down = [x for x in SETTINGS.all_tiles if x.map_pos[0] == current_point.map_pos[0] and x.map_pos[1] == current_point.map_pos[1]+1]
            adj_left = [x for x in SETTINGS.all_tiles if x.map_pos[0] == current_point.map_pos[0]-1 and x.map_pos[1] == current_point.map_pos[1]]
            
            if adj_up:
                adjacent.append(adj_up[0])
            if adj_right:
                adjacent.append(adj_right[0])
            if adj_down:
                adjacent.append(adj_down[0])
            if adj_left:
                adjacent.append(adj_left[0])

            # Add adjacent nodes to `openlist` if they are not in `closedlist` and are not solid
            for adj in adjacent:
                
                if (adj.type == 'hdoor' or adj.type == 'vdoor' or not SETTINGS.tile_solid[adj.ID]) and adj not in closedlist:
                    if (adj in openlist and openlist[adj][0] > closedlist[current_point][0]+1) or adj not in openlist:
                        openlist[adj] = [closedlist[current_point][0]+1, find_distance(adj, end_point), 0, current_point]
                        openlist[adj][2] = f_value(adj, openlist)
        
        try:
            while closedlist[current_point][3] is not None:
                path.append(current_point)
                current_point = closedlist[current_point][3]
        except:
            pass
            
        path.append(start_point)
        path = list(reversed(path))

        if error:
            return closedlist
        else:
            return path

def find_near_position(position):
    adjacent_tiles = [x for x in SETTINGS.walkable_area if (x.map_pos[0] == position[0] + 1 or x.map_pos[0] == position[0] -1 or x.map_pos[0] == position[0])
                      and (x.map_pos[1] == position[1] + 1 or x.map_pos[1] == position[1] - 1 or x.map_pos[1] == position[1])]
    #convert coordinates to a tile
    chosen_tiles = [x for x in SETTINGS.all_tiles if x.map_pos in adjacent_tiles]

    if chosen_tiles:
        return random.choice(chosen_tiles)
    else:
        return None

def check_path_points_inside_map(start, end):
    """
    :param start: List[int]
    :param end: List[int]
    :return:
    """
    error = False
    # Reports if a node is outside the map
    if start[0] > max(SETTINGS.all_tiles, key=lambda x: x.map_pos).map_pos[0] or start[1] > \
            max(SETTINGS.all_tiles, key=lambda x: x.map_pos).map_pos[1]:
        print("=== WARNING: ===")
        print("Start point in path finding is outside map!")
        error = True
    elif end[0] > max(SETTINGS.all_tiles, key=lambda x: x.map_pos).map_pos[0] or end[1] > \
            max(SETTINGS.all_tiles, key=lambda x: x.map_pos).map_pos[1]:
        print("=== WARNING: ===")
        print("End point in path finding is outside map!")
        error = True
    return error

# position List[int]
def get_adjacent_tiles(position, tile_radius = 1):
    adjacent_tiles = [
        x for x in SETTINGS.walkable_area if
        (
                position[0] + tile_radius >= x.map_pos[0] >= position[0] - tile_radius
        ) and (
                position[1] + tile_radius >= x.map_pos[1] >= position[1] - tile_radius
        )
    ]

    return adjacent_tiles


def get_adjacent_walkable_tiles(position, tile_radius = 1):
    adjacent_tiles = get_adjacent_tiles(position, tile_radius)
    walkable_tiles = [x for x in adjacent_tiles if x not in SETTINGS.all_solid_tiles]
    # perhaps also need to consider?
    # adj.type == HORIZONTAL_DOOR or adj.type == VERTICAL_DOOR or not gamedata.tiles.tile_solid[adj.ID]
    if len(walkable_tiles) == 0:
        print("No walkable adjacent tiles!")
        return adjacent_tiles

    return walkable_tiles


# position List[int] - returns  tile
def find_tile_near_position(position, tile_radius = 1):
    """

    :param position: List[int]
    :param tile_radius: int
    :return:
    """
    adjacent_tiles = get_adjacent_tiles(position, tile_radius = tile_radius)
    return random.choice(adjacent_tiles)


# position List[int] - returns  tile
def find_walkable_tile_near_position(position, tile_radius = 1):
    """

    :param position: List[int]
    :param tile_radius: int
    :return:
    """
    walkable_adjacent_tiles = get_adjacent_walkable_tiles(position, tile_radius = tile_radius)
    if len(walkable_adjacent_tiles) > 0:
        return random.choice(walkable_adjacent_tiles)
    return position


def find_distance(point, end):
    x = point.map_pos[0] + point.map_pos[1]
    y = end.map_pos[0] + end.map_pos[1]
    h = abs(x - y)
    return h


def f_value(point, openlist):
    f = openlist[point][2] = openlist[point][0] + openlist[point][1]
    return f

def random_point(start):
    #cpos = Current pos
    closedlist = []
    cpos = start
    closedlist.append(cpos)
    for x in range(random.randint(50,200)):
        #adjacent = up, right, down, left
        adjacent = [[cpos[0], cpos[1]-1],
                    [cpos[0]+1, cpos[1]],
                    [cpos[0], cpos[1]+1],
                    [cpos[0]-1, cpos[1]]]
        
        ranadj = random.choice(adjacent)
        ranadj_tile = [x for x in SETTINGS.all_tiles if ranadj == x.map_pos]
        
        if not SETTINGS.tile_solid[ranadj_tile[0].ID] and ranadj not in closedlist:
            cpos = ranadj
            closedlist.append(cpos)

    return cpos


def round_up(a):
    return int(a + 0.5)


def has_line_of_sight(map_pos_a, map_pos_b):

    if map_pos_a == map_pos_b:
        return True

    dda_list = SETTINGS.walkable_area + [x for x in SETTINGS.all_solid_tiles if x.type == 'sprite']

    # DDA Algorithm
    x1, y1 = map_pos_a[0], map_pos_a[1]
    x2, y2 = map_pos_b[0], map_pos_b[1]

    # If the coords are negative, start from map_pos_b instead of map_pos_a
    if x1 > x2 or (x1 == x2 and y1 > y2):
        temp1, temp2 = x1, y1
        x1, y1 = x2, y2
        x2, y2 = temp1, temp2

    x, y = x1, y1
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    length = dx if dx > dy else dy
    # Make sure, you won't divide by 0
    if length == 0:
        length = 0.001

    xinc = (x2 - x1) / float(length)
    yinc = (y2 - y1) / float(length)

    # Extend DDA algorithm
    for i in range(int(length)):
        if i > SETTINGS.render:
            break
        x += xinc
        y += yinc
        mapx = round_up(x)
        mapy = round_up(y)

        # If line of sight hits a wall
        next_wall = [tile for tile in dda_list if tile.map_pos == [mapx, mapy]]

        if not next_wall:
            break
        else:
            next_wall = next_wall[0]

        if SETTINGS.tile_visible[next_wall.ID]:
            # TODO check for closed doors?
            if next_wall.type != "hdoor" and next_wall.type != "vdoor":
                break
            elif next_wall.type == "hdoor" or next_wall.type == "vdoor":
                if next_wall.solid:
                    break
        # if player is spotted
        if mapx == x2 and mapy == y2:
            return True

    return False


