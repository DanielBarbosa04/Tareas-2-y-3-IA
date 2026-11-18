from src.grid import Grid
from src.astar import astar
from src.heuristics import manhattan, inadmissible


def test_open_grid_optimal():
    g = Grid(5, 5, [], (0, 0), (4, 4))
    path, _ = astar(g)
    assert len(path) - 1 == 8


def test_no_path():
    g = Grid(3, 3, [(0, 1), (1, 1), (2, 1)], (0, 0), (0, 2))
    path, _ = astar(g)
    assert path is None


def test_wall_detour():
    g = Grid.from_text("S.#.G\n..#..\n.....")
    path, _ = astar(g)
    assert len(path) - 1 == 8 and all(c not in g.walls for c in path)