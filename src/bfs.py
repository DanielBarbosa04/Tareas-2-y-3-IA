"""BFS (busqueda no informada) como generador, 
con el mismo formato de Step que A*"""
from collections import deque
from .astar import Step, reconstruct_path

def bfs_steps(grid):
    start, goal = grid.start, grid.goal
    g = {start: 0}
    h = {start: 0}              # BFS no usa heurística
    came_from = {}
    open_set, closed = {start}, set()
    queue = deque([start])

    while queue:
        current = queue.popleft()
        open_set.discard(current)
        closed.add(current)

        done = current == goal
        path = reconstruct_path(came_from, current) if done else []
        yield Step(current, g, h, open_set, closed, came_from,
                   len(closed), done, path)
        if done:
            return

        for nb in grid.neighbors(current):
            if nb not in g:
                g[nb] = g[current] + 1
                h[nb] = 0
                came_from[nb] = current
                open_set.add(nb)
                queue.append(nb)

def bfs(grid):
    """Devuelve (camino, nodos_expandidos). Camino None si no existe."""
    last = None
    for last in bfs_steps(grid):
        pass
    if last is not None and last.done:
        return last.path, last.expanded_count
    return None, (last.expanded_count if last else 0)