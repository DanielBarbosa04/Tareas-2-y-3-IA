"""Punto de entrada.
    python main.py             abre el visualizador (Pygame)
    python main.py --consola   demo de A* en consola, sin graficos
"""
import argparse

from src.grid import Grid, U_MAZE, MAZES
from src.astar import astar, astar_steps

def draw(grid, closed=(), path=()):
    """Dibujo en consola: # pared, S inicio, G meta, 
    * camino, o expandido"""
    for r in range(grid.rows):
        row = ""
        for c in range(grid.cols):
            cell = (r, c)
            if cell in grid.walls: row += "#"
            elif cell == grid.start: row += "S"
            elif cell == grid.goal: row += "G"
            elif cell in path: row += "*"
            elif cell in closed: row += "o"
            else: row += "."
        print(row)

def console_demo(grid):
    print("Primeros 5 nodos expandidos por A*:")
    for step in astar_steps(grid):
        print(f"  #{step.expanded_count}: {step.current}  "
              f"g={step.g[step.current]} h={step.h[step.current]} "
              f"f={step.g[step.current] + step.h[step.current]}")
        if step.expanded_count == 5:
            break

    path, expanded = astar(grid)
    print(f"\nCamino: {len(path) - 1} pasos | Nodos expandidos: {expanded}\n")
    last = None
    for last in astar_steps(grid):
        pass
    draw(grid, last.closed, set(path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo de A* vs BFS")
    parser.add_argument("--consola", action="store_true",
                        help="ejecuta la demo en consola, sin Pygame")
    args = parser.parse_args()

    grid = Grid.from_text(U_MAZE)
    if args.consola:
        console_demo(grid)
    else:
        from src.visualizer import Visualizer   # import tardio: Pygame solo si hace falta
        Visualizer(MAZES).run()