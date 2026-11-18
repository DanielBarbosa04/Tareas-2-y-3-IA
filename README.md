# Búsqueda A\* en una cuadrícula: demo visual

Implementación de **A\*** sobre una cuadrícula con obstáculos, con una visualización paso a paso en Pygame que permite ver cómo se expande la frontera de búsqueda, comparada contra **BFS** (búsqueda no informada) sobre el mismo laberinto.

> **Video de la demo:** _(pega aquí el enlace)_

**Autor:** _(Daniel Alejandro Barbosa Ramírez)_ · **Materia:** _(Inteligencia Artificial)_ · **Opción elegida:** A (Búsqueda A\*)

---

## Ejecución

```bash
pip install -r requirements.txt
python main.py              # abre el visualizador (Pygame)
python main.py --consola    # demo de A* en consola, sin gráficos
python compare.py           # tabla comparativa en consola
pytest                      # pruebas
```

Requiere Python 3.9 o superior.

## Controles del visualizador

| Tecla | Acción |
|---|---|
| `Espacio` | Pausa / continuar (arranca en pausa) |
| `→` | Avanzar un solo paso |
| `↑` / `↓` | Cambiar la velocidad (1 a 300 pasos/s) |
| `R` | Reiniciar |
| `Tab` | Cambiar de modo: ambos / solo A\* / solo BFS |
| `V` | Mostrar valores g, h y f dentro de las celdas |
| `H` | Cambiar la heurística de A\*: `manhattan`, `inadmissible`, `zero` |
| `M` | Cambiar de laberinto: "U" y "Dos muros" |
| Mouse | Ver g, h y f de la celda bajo el cursor |
| `Esc` | Salir |

**Colores:** verde = frontera (open), azul = expandido (closed), naranja = nodo actual, amarillo = camino final.

## Cómo funciona A\*

A\* mantiene una **frontera** (nodos descubiertos pero aún no expandidos) y en cada paso **expande el nodo con menor f = g + h**:

- **g**: costo real desde el inicio hasta el nodo.
- **h**: estimación heurística del costo que falta hasta la meta.
- **f**: costo total estimado de un camino que pase por ese nodo.

Al expandir un nodo se calculan g, h y f de sus vecinos y se agregan a la frontera. El algoritmo termina al sacar la meta, y el camino se reconstruye hacia atrás con el diccionario `came_from`. Las ideas clave:

- A\* **no sigue un camino**: en cada paso elige el mejor nodo de *toda* la frontera, por eso en la animación el nodo actual a veces salta de un lado del mapa al otro.
- Con movimiento en 4 direcciones y costo 1 por paso, f solo cambia en múltiplos de 2: acercarse a la meta deja f igual (g sube 1, h baja 1) y alejarse la sube en 2.
- Desempate: ante igual f, se prefiere el menor h (el más cercano a la meta) y luego el más antiguo.

## Elección de la heurística

Se usa la **distancia Manhattan**: `h(n) = |fila_n − fila_meta| + |col_n − col_meta|`.

**Es admisible** (nunca sobreestima el costo real): con movimiento en 4 direcciones y costo 1 por paso, se necesitan como mínimo |Δfila| + |Δcol| pasos para llegar a la meta. Los obstáculos solo pueden alargar el camino, nunca acortarlo, así que h(n) ≤ costo real desde n.

**Es consistente** (h(n) ≤ 1 + h(vecino)): cada paso cambia h en ±1, por lo que cada nodo se expande una sola vez y su g ya es el mejor al expandirlo.

**Verificación numérica:** `tests/test_heuristics.py` calcula el costo real desde *cada* celda libre de ambos laberintos (con BFS) y comprueba que `manhattan(celda) ≤ costo real`.

### Las tres heurísticas incluidas

| Heurística | Definición | ¿Admisible? | Efecto |
|---|---|---|---|
| `manhattan` | \|Δfila\| + \|Δcol\| | Sí | Camino óptimo explorando pocos nodos |
| `inadmissible` | 3 × Manhattan | **No** (sobreestima) | Más codicioso: rápido, pero puede perder la optimalidad |
| `zero` | 0 | Sí | A\* se vuelve Dijkstra/BFS: óptimo pero explora todo |

## Resultados

Salida de `python compare.py`. "Expandidos" cuenta los nodos extraídos de la frontera (incluida la meta).

**Laberinto "U"** (221 celdas libres): la heurística apunta a la pared y A\* igual rodea y llega al óptimo.

| Algoritmo | Camino | Expandidos | ¿Óptimo? |
|---|---|---|---|
| BFS | 18 | 160 | sí |
| A\* Manhattan | 18 | **71** | sí |
| A\* inadmissible (×3) | 18 | 52 | sí |
| A\* zero | 18 | 160 | sí |

**Laberinto "Dos muros"** (221 celdas libres): aquí la heurística no admisible falla.

| Algoritmo | Camino | Expandidos | ¿Óptimo? |
|---|---|---|---|
| BFS | 25 | 210 | sí |
| A\* Manhattan | 25 | **110** | sí |
| A\* inadmissible (×3) | **35** | 108 | **no (+10)** |
| A\* zero | 25 | 210 | sí |

### Comparación contra BFS (búsqueda no informada)

- Ambos encuentran el camino óptimo, porque todos los pasos cuestan 1. **La ventaja de A\* no es la calidad del camino, sino cuántos nodos explora**: 56% menos en "U" (71 vs 160) y 48% menos en "Dos muros" (110 vs 210).
- BFS se expande como una onda circular desde el inicio, sin saber dónde está la meta. A\* concentra la búsqueda en la zona entre el inicio y la meta.
- No se comparan tiempos de ejecución: con ~220 celdas son prácticamente idénticos y dependen de la máquina. La métrica relevante es el número de nodos expandidos.

### Por qué falla la heurística no admisible

En f = g + 3h, el término h pesa tres veces más que g y A\* se vuelve casi codicioso. En "Dos muros" rodea el primer muro por arriba (parece acercarlo más rápido a la meta) y luego paga un rodeo largo en el segundo: 35 pasos en vez de 25. Demuestra por qué importa la admisibilidad: la garantía de optimalidad se pierde en cuanto h supera el costo real.

## Limitaciones

- Los resultados dependen del laberinto: con una heurística débil o pasillos muy estrechos, A\* puede acercarse a BFS. Los porcentajes de arriba son de estos dos laberintos, no una regla general.
- Que una heurística sea admisible garantiza la optimalidad, pero no que sea buena: `zero` es admisible y no ayuda en nada.
- Solo se implementó movimiento en 4 direcciones con costo uniforme. Con diagonales haría falta la distancia octil o Chebyshev.
- Existen varios caminos óptimos en estos laberintos (por ejemplo, por arriba o por abajo en la "U"); el algoritmo elige uno según el orden de desempate.

## Estructura del repositorio

```
A/
├── README.md
├── requirements.txt
├── main.py                 # punto de entrada (visualizador o --consola)
├── compare.py              # tabla comparativa en consola
├──
├── src/
│   ├── grid.py             # cuadrícula y laberintos (U, Dos muros)
│   ├── astar.py            # A* como generador de pasos
│   ├── bfs.py              # BFS como generador de pasos
│   ├── heuristics.py       # manhattan, inadmissible, zero
│   └── visualizer.py       # animación con Pygame
└── tests/
    ├── test_astar.py       # corrección de A*
    ├── test_bfs.py         # BFS y A* coinciden en 200 cuadrículas aleatorias
    └── test_heuristics.py  # admisibilidad numérica y caso no 
```

**Decisión de diseño:** A\* y BFS son *generadores* que entregan un paso por cada nodo expandido, con el mismo formato (`Step`). Así el visualizador anima ambos con el mismo código y la lógica del algoritmo queda separada de los gráficos.

## Pruebas

- A\* encuentra el camino óptimo en cuadrículas abiertas y con rodeos, y reporta correctamente cuando no hay camino.
- En 200 cuadrículas aleatorias, A\* (Manhattan) y BFS devuelven caminos de la misma longitud.
- Manhattan es admisible en todas las celdas de ambos laberintos; la heurística ×3 sobreestima en alguna celda y produce un camino subóptimo en "Dos muros".

## Capturas de pantalla

Capturas del visualizador al terminar cada búsqueda, con las tres heurísticas en los dos laberintos.

### Laberinto "U"

| Manhattan | Inadmissible (×3) | Zero |
|:---:|:---:|:---:|
| ![U con Manhattan](pruebas%20%28screenshots%29/u_manhattan.png) | ![U con inadmissible](pruebas%20%28screenshots%29/u_inadmissible.png) | ![U con zero](pruebas%20%28screenshots%29/u_zero.png) |
| 18 pasos · 71 nodos · óptimo | 18 pasos · 52 nodos · óptimo | 18 pasos · 160 nodos · óptimo |

### Laberinto "Dos muros"

| Manhattan | Inadmissible (×3) | Zero |
|:---:|:---:|:---:|
| ![Dos muros con Manhattan](pruebas%20%28screenshots%29/dosmuros_manhattan.png) | ![Dos muros con inadmissible](pruebas%20%28screenshots%29/dosmuros_inadmissible.png) | ![Dos muros con zero](pruebas%20%28screenshots%29/dosmuros_zero.png) |
| 25 pasos · 110 nodos · óptimo | **35 pasos** · 108 nodos · **no óptimo (+10)** | 25 pasos · 210 nodos · óptimo |