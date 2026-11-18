"""Heuristicas para cuadricula con movimiento en 
4 direcciones (costo 1 por paso)"""

def manhattan(a, b):
    """Admisible y consistente: se necesitan como minimo 
    |dx|+|dy| pasos"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def zero(a, b):
    """h = 0: A* se comporta como Dijkstra 
    (equivalente a BFS sin pesos)"""
    return 0

def inadmissible(a, b):
    """Manhattan x3: SOBREESTIMA el costo real, por lo que 
    deja de ser admisible"""
    return 3 * manhattan(a, b)

# La tecla H del visualizador recorre esta lista
ALL = [manhattan, inadmissible, zero]