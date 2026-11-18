from src.grid import Grid, MAZES
from src.astar import astar
from src.bfs import bfs
from src.heuristics import manhattan, inadmissible

def true_cost(grid, cell):
    """Costo real (pasos) de cell a la meta, usando BFS. 
    None si no hay camino"""
    g2 = Grid(grid.rows, grid.cols, grid.walls, cell, grid.goal)
    path, _ = bfs(g2)
    return None if path is None else len(path) - 1

def free_cells(grid):
    return [(r, c) for r in range(grid.rows) for c in range(grid.cols)
            if (r, c) not in grid.walls]

def test_manhattan_is_admissible_on_every_cell():
    """h(n) <= costo real desde n, para TODAS las celdas de cada 
    laberinto"""
    for _, text in MAZES:
        grid = Grid.from_text(text)
        for cell in free_cells(grid):
            real = true_cost(grid, cell)
            if real is not None:
                assert manhattan(cell, grid.goal) <= real

def test_inadmissible_overestimates_somewhere():
    grid = Grid.from_text(dict(MAZES)["Dos muros"])
    over = [c for c in free_cells(grid)
            if true_cost(grid, c) is not None
            and inadmissible(c, grid.goal) > true_cost(grid, c)]
    assert len(over) > 0


def test_astar_manhattan_optimal_in_all_mazes():
    for _, text in MAZES:
        grid = Grid.from_text(text)
        assert len(astar(grid, manhattan)[0]) == len(bfs(grid)[0])


def test_inadmissible_is_suboptimal_in_dos_muros():
    grid = Grid.from_text(dict(MAZES)["Dos muros"])
    assert len(astar(grid, inadmissible)[0]) > len(bfs(grid)[0])