"""Visualizador con Pygame: anima A* y BFS paso a paso 
sobre la cuadricula

Controles:
    1. Espacio ........ pausa / continuar
    2. Flecha derecha . avanzar un paso (pausa la animacion)
    3. Arriba / Abajo . cambiar velocidad
    4. R .............. reiniciar
    5. Tab ............ cambiar modo: ambos / solo A* / 
    solo BFS (reinicia)
    6. V .............. mostrar valores g, h, f dentro de las celdas
    7. H .............. cambiar heuristica de A* (manhattan / 
    inadmissible / zero)
    8. M .............. cambiar de laberinto
    9. Mouse .......... ver g, h, f de la celda bajo el cursor
    10. Esc ............ salir
"""
import pygame

from .astar import astar_steps
from .bfs import bfs, bfs_steps
from .grid import Grid
from .heuristics import ALL as HEURISTICS

WIDTH, HEIGHT = 1200, 680
TITLE_H = 64
INFO_H = 96
SUMMARY_H = 64
SPEEDS = [1, 2, 5, 10, 20, 50, 100, 300]   # pasos (nodos expandidos) por segundo
MODES = ["both", "astar", "bfs"]

COLORS = {
    "bg": (24, 26, 33),
    "free": (236, 239, 244),
    "wall": (46, 52, 64),
    "closed": (143, 188, 235),
    "open": (163, 214, 140),
    "current": (255, 152, 67),
    "path": (250, 214, 70),
    "start": (50, 100, 225),
    "goal": (215, 65, 65),
    "line": (196, 200, 210),
    "route": (190, 110, 20),
    "text": (230, 232, 238),
    "muted": (140, 146, 160),
    "cell_text": (35, 40, 50),
    "white": (255, 255, 255),
    "good": (130, 205, 130),
    "bad": (245, 115, 105),
}

STATE_LABEL = {
    "wall": "pared",
    "path": "camino final",
    "current": "nodo actual",
    "open": "en frontera",
    "closed": "expandida",
    "free": "sin descubrir",
}


class Searcher:
    """Envuelve un generador de pasos (A* o BFS) y recuerda su estado."""

    def __init__(self, name, factory, informed):
        self.name = name
        self.factory = factory
        self.informed = informed    # True si usa heuristica (muestra f = g + h)
        self.reset()

    def reset(self):
        self.gen = self.factory()
        self.step = None            # ultimo Step recibido (None = aun no empieza)
        self.finished = False
        self.found = False

    def advance(self):
        if self.finished:
            return
        try:
            self.step = next(self.gen)
        except StopIteration:
            self.finished = True    # se agoto la frontera sin llegar a la meta
            return
        if self.step.done:
            self.finished = True
            self.found = True

    def state_of(self, grid, cell):
        """Estado logico de una celda (sin considerar inicio/meta)."""
        if cell in grid.walls:
            return "wall"
        st = self.step
        if st is None:
            return "free"
        if st.done and cell in st.path:
            return "path"
        if cell == st.current and not st.done:
            return "current"
        if cell in st.open:
            return "open"
        if cell in st.closed:
            return "closed"
        return "free"


class Visualizer:
    def __init__(self, mazes):
        """mazes: lista de (nombre, texto) como MAZES en grid.py."""
        pygame.font.init()
        self.mazes = mazes
        self.maze_idx = 0
        self.heur_idx = 0
        self.mode_idx = 0
        self.speed_idx = 2
        self.show_values = False
        self.mouse = (-1, -1)

        pick = "consolas,dejavusansmono,couriernew,monospace"
        self.f_title = pygame.font.SysFont(pick, 24, bold=True)
        self.f_text = pygame.font.SysFont(pick, 16)
        self.f_big = pygame.font.SysFont(pick, 16, bold=True)
        self.f_small = pygame.font.SysFont(pick, 11)
        self.build()

    # ---------- logica ----------
    def build(self):
        """Crea cuadricula y buscadores para el laberinto y la heuristica actuales."""
        grid = Grid.from_text(self.mazes[self.maze_idx][1])
        heuristic = HEURISTICS[self.heur_idx]
        self.grid = grid
        self.heuristic = heuristic
        # Referencia: BFS completo (sin animar) para saber cual es el camino optimo
        self.ref_path, self.ref_expanded = bfs(grid)
        self.astar = Searcher(
            f"A* ({heuristic.__name__})",
            lambda: astar_steps(grid, heuristic), informed=True)
        self.bfs = Searcher("BFS", lambda: bfs_steps(grid), informed=False)
        self.acc = 0.0
        self.paused = True

    def active(self):
        mode = MODES[self.mode_idx]
        if mode == "both":
            return [self.astar, self.bfs]
        return [self.astar] if mode == "astar" else [self.bfs]

    def reset(self):
        self.astar.reset()
        self.bfs.reset()
        self.acc = 0.0
        self.paused = True

    def step_all(self):
        for s in self.active():
            s.advance()

    def on_key(self, key):
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_RIGHT:
            self.paused = True
            self.step_all()
        elif key == pygame.K_UP:
            self.speed_idx = min(self.speed_idx + 1, len(SPEEDS) - 1)
        elif key == pygame.K_DOWN:
            self.speed_idx = max(self.speed_idx - 1, 0)
        elif key == pygame.K_r:
            self.reset()
        elif key == pygame.K_TAB:
            self.mode_idx = (self.mode_idx + 1) % len(MODES)
            self.reset()
        elif key == pygame.K_v:
            self.show_values = not self.show_values
        elif key == pygame.K_h:
            self.heur_idx = (self.heur_idx + 1) % len(HEURISTICS)
            self.build()
        elif key == pygame.K_m:
            self.maze_idx = (self.maze_idx + 1) % len(self.mazes)
            self.build()

    def layout(self):
        """Lista de (searcher, gx, gy, cs): esquina de la cuadricula y tamano de celda."""
        active = self.active()
        panel_w = WIDTH // len(active)
        avail_h = HEIGHT - TITLE_H - INFO_H - SUMMARY_H
        cs = min((panel_w - 24) // self.grid.cols, avail_h // self.grid.rows)
        gy = TITLE_H + (avail_h - cs * self.grid.rows) // 2
        out = []
        for i, s in enumerate(active):
            gx = i * panel_w + (panel_w - cs * self.grid.cols) // 2
            out.append((s, gx, gy, cs))
        return out

    def hovered(self):
        """Devuelve (searcher, celda) bajo el mouse, o None."""
        mx, my = self.mouse
        for s, gx, gy, cs in self.layout():
            c, r = (mx - gx) // cs, (my - gy) // cs
            if 0 <= r < self.grid.rows and 0 <= c < self.grid.cols:
                return s, (r, c)
        return None

    def hover_text(self):
        hv = self.hovered()
        if hv is None:
            return "Pasa el mouse sobre una celda para ver sus valores g, h y f"
        s, cell = hv
        if s.step is None:
            return f"[{s.name}] celda {cell}: aun no hay datos (Espacio o flecha derecha)"
        state = STATE_LABEL[s.state_of(self.grid, cell)]
        if cell not in s.step.g:
            return f"[{s.name}] celda {cell}: {state}"
        g, h = s.step.g[cell], s.step.h[cell]
        if s.informed:
            return f"[{s.name}] celda {cell}: g={g} h={h} f=g+h={g + h} ({state})"
        return f"[{s.name}] celda {cell}: distancia desde el inicio g={g} ({state})"

    def status_text(self, s):
        st = s.step
        if st is None:
            return "Listo para comenzar"
        base = f"Expandidos: {st.expanded_count}   Frontera: {len(st.open)}"
        if s.found:
            return base + f"   META: camino de {len(st.path) - 1} pasos"
        if s.finished:
            return base + "   Sin camino"
        return base + "   Buscando..."

    def summary_lines(self):
        """Resumen final (lista de (texto, color)): se muestra cuando A* y los
        paneles activos terminaron. Compara contra BFS, que siempre es optimo aqui."""
        if self.astar not in self.active():
            return []
        if not all(s.finished for s in self.active()):
            return []
        if not self.astar.found:
            return [("A* no encontro camino", COLORS["muted"])]
        if self.ref_path is None:
            return []

        na = self.astar.step.expanded_count
        nb = self.ref_expanded
        len_a = len(self.astar.step.path) - 1
        len_opt = len(self.ref_path) - 1

        if na < nb:
            line1 = f"A* expandio {na} nodos vs {nb} de BFS ({round(100 * (1 - na / nb))}% menos)"
        elif na > nb:
            line1 = f"A* expandio {na} nodos vs {nb} de BFS ({round(100 * (na / nb - 1))}% mas)"
        else:
            line1 = f"A* expandio {na} nodos, igual que BFS ({nb})"

        if len_a == len_opt:
            line2 = (f"Camino de {len_a} pasos: es OPTIMO (igual que el de BFS)", COLORS["good"])
        else:
            line2 = (f"Camino de {len_a} pasos, pero el optimo es {len_opt} "
                     f"(+{len_a - len_opt}): la heuristica NO es admisible", COLORS["bad"])
        return [(line1, COLORS["text"]), line2]

    # ---------- dibujo ----------
    def draw_text(self, screen, text, font, color, pos, center=False):
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        screen.blit(img, rect)

    def draw_cell_values(self, screen, s, cell, rect):
        st = s.step
        if st is None or cell not in st.g or rect.w < 22:
            return
        g, h = st.g[cell], st.h[cell]
        color = COLORS["cell_text"]
        if not s.informed:
            self.draw_text(screen, str(g), self.f_text, color, rect.center, center=True)
        elif rect.w >= 36:
            self.draw_text(screen, str(g), self.f_small, color, (rect.x + 3, rect.y + 2))
            hs = self.f_small.render(str(h), True, color)
            screen.blit(hs, (rect.right - hs.get_width() - 3, rect.y + 2))
            self.draw_text(screen, str(g + h), self.f_big, color,
                           (rect.centerx, rect.centery + 5), center=True)
        else:
            self.draw_text(screen, str(g + h), self.f_small, color, rect.center, center=True)

    def draw_panel(self, screen, s, gx, gy, cs, hover_cell):
        grid = self.grid
        panel_w = WIDTH // len(self.active())
        px = gx - (panel_w - cs * grid.cols) // 2
        self.draw_text(screen, s.name, self.f_title, COLORS["text"], (px + 16, 8))
        self.draw_text(screen, self.status_text(s), self.f_text, COLORS["muted"], (px + 16, 38))

        for r in range(grid.rows):
            for c in range(grid.cols):
                cell = (r, c)
                rect = pygame.Rect(gx + c * cs, gy + r * cs, cs, cs)
                pygame.draw.rect(screen, COLORS[s.state_of(grid, cell)], rect)
                pygame.draw.rect(screen, COLORS["line"], rect, 1)
                if self.show_values and cell not in grid.walls:
                    self.draw_cell_values(screen, s, cell, rect)
                if cell in (grid.start, grid.goal):
                    inner = rect.inflate(-cs // 3, -cs // 3)
                    key = "start" if cell == grid.start else "goal"
                    pygame.draw.rect(screen, COLORS[key], inner, border_radius=4)
                    self.draw_text(screen, "S" if key == "start" else "G", self.f_big,
                                   COLORS["white"], inner.center, center=True)

        if s.found:   # linea que recorre el camino final
            pts = [(gx + c * cs + cs // 2, gy + r * cs + cs // 2) for r, c in s.step.path]
            pygame.draw.lines(screen, COLORS["route"], False, pts, 3)

        if hover_cell is not None:
            r, c = hover_cell
            pygame.draw.rect(screen, COLORS["white"],
                             pygame.Rect(gx + c * cs, gy + r * cs, cs, cs), 3)

    def draw_summary(self, screen):
        lines = self.summary_lines()
        if not lines:
            return
        _, _, gy, cs = self.layout()[0]
        y = gy + cs * self.grid.rows + 14
        for text, color in lines:
            self.draw_text(screen, text, self.f_big, color, (WIDTH // 2, y + 8), center=True)
            y += 24

    def draw_info_bar(self, screen):
        y0 = HEIGHT - INFO_H
        pygame.draw.line(screen, COLORS["muted"], (0, y0), (WIDTH, y0), 1)
        self.draw_text(screen, self.hover_text(), self.f_text, COLORS["text"], (16, y0 + 8))

        x = 16
        legend = [("frontera (open)", "open"), ("expandido (closed)", "closed"),
                  ("nodo actual", "current"), ("camino final", "path")]
        for label, key in legend:
            pygame.draw.rect(screen, COLORS[key], pygame.Rect(x, y0 + 38, 14, 14))
            self.draw_text(screen, label, self.f_text, COLORS["muted"], (x + 20, y0 + 36))
            x += 40 + 9 * len(label)
        estado = "PAUSA" if self.paused else "CORRIENDO"
        self.draw_text(screen, f"{estado} | velocidad: {SPEEDS[self.speed_idx]} pasos/s",
                       self.f_big, COLORS["text"], (WIDTH - 360, y0 + 36))

        self.draw_text(screen,
                       "Espacio: pausa | Der: paso | Arriba/Abajo: velocidad | R: reiniciar | "
                       "Tab: modo | V: valores | H: heuristica | M: laberinto",
                       self.f_text, COLORS["muted"], (16, y0 + 66))

    def draw(self, screen):
        screen.fill(COLORS["bg"])
        hv = self.hovered()
        for s, gx, gy, cs in self.layout():
            cell = hv[1] if hv is not None and hv[0] is s else None
            self.draw_panel(screen, s, gx, gy, cs, cell)
        label = self.f_text.render(f"Laberinto: {self.mazes[self.maze_idx][0]}",
                                   True, COLORS["muted"])
        screen.blit(label, (WIDTH - label.get_width() - 16, 10))
        self.draw_summary(screen)
        self.draw_info_bar(screen)

    # ---------- bucle principal ----------
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("A* vs BFS - visualizador de busqueda")
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.on_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse = event.pos
            if not self.paused:
                self.acc += dt * SPEEDS[self.speed_idx]
                while self.acc >= 1:
                    self.step_all()
                    self.acc -= 1
            self.draw(screen)
            pygame.display.flip()
        pygame.quit()