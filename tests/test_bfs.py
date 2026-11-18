import random
from src.grid import Grid
from src.astar import astar
from src.bfs import bfs
from src.heuristics import manhattan

def test_bfs_no_path():
    g = Grid(3, 3, [(0, 1), (1, 1), (2, 1)], (0, 0), (0, 2))
    assert bfs(g)[0] is None

def test_astar_matches_bfs_on_random_grids():
    """Ambos deben dar la misma longitud optima 
    A* nunca expande mas que BFS"""
    random.seed(1)
    for _ in range(200):
        rows, cols = 12, 12
        walls = {(r, c) for r in range(rows) for c in range(cols)
                 if random.random() < 0.25}
        start, goal = (0, 0), (rows - 1, cols - 1)
        walls -= {start, goal}
        g = Grid(rows, cols, walls, start, goal)
        pa, _ = astar(g, manhattan)
        pb, _ = bfs(g)
        assert (pa is None) == (pb is None)
        if pa:
            assert len(pa) == len(pb)