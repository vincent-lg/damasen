"""Algorithms for path finding."""

import heapq
import itertools

import numpy as np

def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def compute_mst(entrances):
    graph = []

    # Create a complete graph where each node is an entrance
    for (i, p1), (j, p2) in itertools.combinations(enumerate(entrances), 2):
        dist = distance(p1, p2)
        graph.append((dist, i, j))  # Store edges as (cost, node1, node2)

    # Sort edges by distance (to process smallest first)
    graph.sort()

    # Prim's Algorithm - Initialize MST
    mst = []
    parent = {i: i for i in range(len(entrances))}  # Disjoint-set for union-find

    def find(n):
        while parent[n] != n:
            n = parent[n]
        return n

    def union(n1, n2):
        parent[find(n1)] = find(n2)

    for cost, i, j in graph:
        if find(i) != find(j):  # If they belong to different sets, connect them
            union(i, j)
            mst.append((entrances[i], entrances[j]))  # Store the connection

    return mst  # List of (start, end) points representing the MST connections


def dijkstra(grid, start, end):
    rows, cols = grid.shape
    costs = {start: 0}
    pq = [(0, start)]
    came_from = {start: None}

    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  # Straight moves (preferred)
        (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal moves (higher cost)
    ]

    while pq:
        current_cost, current = heapq.heappop(pq)

        if current == end:
            break  # We reached the destination

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
                new_cost = current_cost + (1 if abs(dx) + abs(dy) == 1 else 1.4)  # Prefer straight moves

                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))
                    came_from[neighbor] = current

    # Reconstruct path
    path = []
    current = end

    if current not in came_from:  # If end is unreachable
        print("No valid path found!")
        return []

    while current is not None:
        path.append(current)
        current = came_from.get(current, None)

    path.reverse()  # Reverse to start-to-end order

    return path


def compute_fov(player_x, player_y, radius, game_map):
    """
    Calculate Field of View (FOV) using a simple shadowcasting approach,
    directly updating a boolean los_mask.
    """
    # Create a boolean mask with the same shape as game_map
    los_mask = np.zeros(game_map.shape, dtype=bool)

def cast_light(
    map: np.ndarray,
    los_mask: np.ndarray,
    start_x: int,
    start_y: int,
    dx: int,
    dy: int,
    radius: int,
    blocks: list[int],
) -> np.ndarray:
    """Casts light in a given direction, returning a mask."""
    for r in range(1, radius + 1):
        x, y = start_x + r * dx, start_y + r * dy
        if 0 <= x < map.shape[1] and 0 <= y < map.shape[0]:
            los_mask[y, x] = True  # Mark as visible
            if map[y, x] in blocks:
                break
        else:
            break


#***
def recursive_shadowcast(
    map_array: np.ndarray,
    fov: np.ndarray,
    cx: int,
    cy: int,
    row: int,
    start: float,
    end: float,
    radius: int,
    blocking_tiles: list[int],
    xx: int,
    xy: int,
    yx: int,
    yy: int,
):
    """
    Recursive shadowcasting for a single octant.

    Parameters:
        map_array: 2D NumPy array representing the map.
                   Cells with value 1 are considered opaque.
        fov:       2D boolean NumPy array to mark visible tiles.
        cx, cy:    The player's position.
        row:       Current row (distance) being scanned.
        start:     Start slope.
        end:       End slope.
        radius:    Maximum radius for FOV.
        xx, xy, yx, yy:
                   Multipliers that transform coordinates to the current octant.
    """
    if start < end:
        return

    radius_squared = radius * radius

    for i in range(row, radius + 1):
        dx = -i - 1
        dy = -i
        new_start = start
        blocked = False

        while dx <= 0:
            dx += 1
            # Translate relative coordinates to map coordinates for the current octant.
            X = cx + dx * xx + dy * xy
            Y = cy + dx * yx + dy * yy

            # Calculate the slopes of the cell's left and right edges.
            left_slope = (dx - 0.5) / (dy + 0.5)
            right_slope = (dx + 0.5) / (dy - 0.5)

            # If the cell is completely outside the scanning slopes, skip it.
            if start < right_slope:
                continue
            elif end > left_slope:
                break

            # Check if the cell is within the light radius.
            if (dx * dx + dy * dy) < radius_squared:
                if 0 <= Y < map_array.shape[0] and 0 <= X < map_array.shape[1]:
                    fov[Y, X] = True

            if blocked:
                # If we are in a block, check if this cell is also blocked.
                if 0 <= Y < map_array.shape[0] and 0 <= X < map_array.shape[1] and map_array[Y, X] in blocking_tiles:
                    new_start = right_slope
                    continue
                else:
                    # The block has ended.
                    blocked = False
                    start = new_start
            else:
                # If the cell is blocked and we're not already in a block, recurse.
                if 0 <= Y < map_array.shape[0] and 0 <= X < map_array.shape[1] and map_array[Y, X] in blocking_tiles and i < radius:
                    blocked = True
                    # Recurse into the next row in this octant.
                    recursive_shadowcast(
                        map_array,
                        fov,
                        cx,
                        cy,
                        i + 1,
                        start,
                        left_slope,
                        radius,
                        blocking_tiles,
                        xx,
                        xy,
                        yx,
                        yy,
                    )
                    new_start = right_slope
        if blocked:
            # If the last cell in the row was blocked, no further cells in this row can be seen.
            break

def compute_fov(map_array: np.ndarray, player_x: int, player_y: int, radius: int, blocking_tiles: list[int]) -> np.ndarray:
    """
    Computes the field of view using recursive shadowcasting.

    Parameters:
        map_array: 2D NumPy array representing the map.
                   Cells with value 1 are walls (opaque).
        player_x, player_y: The player's position on the map.
        radius:    Maximum distance for the field of view.

    Returns:
        A 2D boolean NumPy array (same shape as map_array) with True for visible tiles.
    """
    fov = np.zeros_like(map_array, dtype=bool)

    # Mark the player's own tile as visible.
    if 0 <= player_y < map_array.shape[0] and 0 <= player_x < map_array.shape[1]:
        fov[player_y, player_x] = True

    # Multipliers for transforming coordinates into the eight octants.
    multipliers = [
        (1, 0, 0, 1),   # Octant 0
        (0, 1, 1, 0),   # Octant 1
        (-1, 0, 0, 1),  # Octant 2
        (0, -1, 1, 0),  # Octant 3
        (-1, 0, 0, -1), # Octant 4
        (0, -1, -1, 0), # Octant 5
        (1, 0, 0, -1),  # Octant 6
        (0, 1, -1, 0)   # Octant 7
    ]
    # Process each octant.
    for xx, xy, yx, yy in multipliers:
        recursive_shadowcast(map_array, fov, player_x, player_y, 1, 1.0, 0.0, radius, blocking_tiles, xx, xy, yx, yy)

    return fov
