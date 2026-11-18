"""Comparacion en consola: BFS y A* con cada heuristica, 
en cada laberinto"""
import time

from src.grid import Grid, MAZES
from src.astar import astar
from src.bfs import bfs
from src.heuristics import ALL as HEURISTICS

def measure(fn):
    t = time.perf_counter()
    path, expanded = fn()
    ms = (time.perf_counter() - t) * 1000
    return len(path) - 1, expanded, ms

if __name__ == "__main__":
    for name, text in MAZES:
        grid = Grid.from_text(text)
        free = grid.rows * grid.cols - len(grid.walls)
        print(f"\n=== Laberinto: {name} ({free} celdas libres) ===")
        print(f"{'algoritmo':<20}{'camino':>8}{'expandidos':>12}{'optimo?':>9}")
        opt, n_bfs, _ = measure(lambda: bfs(grid))
        print(f"{'BFS':<20}{opt:>8}{n_bfs:>12}{'si':>9}")
        for h in HEURISTICS:
            length, n, _ = measure(lambda: astar(grid, h))
            ok = "si" if length == opt else f"NO (+{length - opt})"
            print(f"{'A* ' + h.__name__:<20}{length:>8}{n:>12}{ok:>9}")