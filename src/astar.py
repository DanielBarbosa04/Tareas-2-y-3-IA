"""A* implementado como generador: cada `yield` es 
un paso (un nodo expandido)"""
import heapq
from dataclasses import dataclass, field

from .heuristics import manhattan


@dataclass
class Step:
    """Instantanea del algoritmo tras expandir un nodo"""
    current: tuple          # nodo que se acaba de expandir
    g: dict                 # costo real desde el inicio, por nodo
    h: dict                 # valor heuristico, por nodo
    open: set               # frontera (nodos descubiertos, aun no expandidos)
    closed: set             # nodos ya expandidos
    came_from: dict         # para reconstruir el camino
    expanded_count: int
    done: bool = False
    path: list = field(default_factory=list)


def reconstruct_path(came_from, node):
    path = [node]
    while node in came_from:
        node = came_from[node]
        path.append(node)
    return path[::-1]


def astar_steps(grid, heuristic=manhattan):
    start, goal = grid.start, grid.goal
    g = {start: 0}
    h = {start: heuristic(start, goal)}
    came_from = {}
    open_set, closed = {start}, set()
    counter = 0  # desempata entradas con igual f y h en el heap
    heap = [(h[start], h[start], counter, start)]

    while heap:
        f, _, _, current = heapq.heappop(heap)
        if current in closed:       # entrada vieja (se encontró mejor camino)
            continue
        open_set.discard(current)
        closed.add(current)

        done = current == goal
        path = reconstruct_path(came_from, current) if done else []
        yield Step(current, g, h, open_set, closed, came_from,
                   len(closed), done, path)
        if done:
            return

        for nb in grid.neighbors(current):
            new_g = g[current] + 1
            if nb not in g or new_g < g[nb]:
                g[nb] = new_g
                h[nb] = heuristic(nb, goal)
                came_from[nb] = current
                open_set.add(nb)
                counter += 1
                heapq.heappush(heap, (new_g + h[nb], h[nb], counter, nb))


def astar(grid, heuristic=manhattan):
    """Version no animada: devuelve (camino, nodos_expandidos)
    Camino None si no existe"""
    last = None
    for last in astar_steps(grid, heuristic):
        pass
    if last is not None and last.done:
        return last.path, last.expanded_count
    return None, (last.expanded_count if last else 0)