"""Cuadricula con obstaculos. Las celdas son tuplas 
(fila, columna)"""

class Grid:
    def __init__(self, rows, cols, walls, start, goal):
        self.rows, self.cols = rows, cols
        self.walls = set(walls)
        self.start, self.goal = start, goal

    @classmethod
    def from_text(cls, text):
        """Crea una cuadricula desde texto: '#' pared, 'S' inicio, 
        'G' meta, '.' libre"""
        lines = [l for l in text.strip("\n").split("\n")]
        walls, start, goal = set(), None, None
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                if ch == "#":
                    walls.add((r, c))
                elif ch == "S":
                    start = (r, c)
                elif ch == "G":
                    goal = (r, c)
        return cls(len(lines), max(len(l) for l in lines), walls, start, goal)

    def in_bounds(self, cell):
        return 0 <= cell[0] < self.rows and 0 <= cell[1] < self.cols

    def neighbors(self, cell):
        """Vecinos transitables en 4 direcciones 
        (arriba, derecha, abajo, izquierda)"""
        r, c = cell
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nxt = (r + dr, c + dc)
            if self.in_bounds(nxt) and nxt not in self.walls:
                yield nxt

# Laberinto con una "U" frente a la meta: la heuristica apunta 
# directo a la pared, pero A* igual encuentra el camino optimo 
# rodeandola

U_MAZE = """
....................
....................
....................
.........#######....
.........#.....#....
.........#.....#....
..S......#..G..#....
.........#.....#....
.........#.....#....
.........#.....#....
....................
....................
"""


# Dos muros verticales. La heuristica Manhattan x3 (no admisible) 
# se deja engatusar: rodea el primer muro por arriba
# (parece prometedor) y termina dando un rodeo mucho mas largo
# que el camino optimo, que pasa por abajo en ambos muros
DOS_MUROS = """
....................
.......#............
.......#.......#....
.......#.......#....
.......#.......#....
.......#.......#....
..S....#.......#.G..
.......#.......#....
.......#.......#....
.......#.......#....
.......#.......#....
....................
"""

# (nombre, texto) - la tecla M del visualizador recorre esta lista
MAZES = [("U", U_MAZE), ("Dos muros", DOS_MUROS)]