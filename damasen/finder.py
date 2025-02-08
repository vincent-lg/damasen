"""Algorithms for path finding."""

import heapq
import itertools

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
