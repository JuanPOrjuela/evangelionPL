"""Nuestra libreria de vectores y matrices (lo que en Python haria NumPy).

Un vector es una lista de numeros y una matriz es una lista de filas, donde
todas las filas tienen el mismo largo. Nada cambia la lista original.
"""

from .matematica import absoluto, raiz
from .tablas import es_numero


def es_vector(valor) -> bool:
    return isinstance(valor, list) and all(es_numero(v) for v in valor)


def es_matriz(valor) -> bool:
    return (isinstance(valor, list) and len(valor) > 0 and all(es_vector(f) for f in valor)
            and all(len(f) == len(valor[0]) for f in valor) and len(valor[0]) > 0)


def forma(valor) -> list:
    """[filas, columnas] de una matriz o [largo] de un vector."""
    if es_matriz(valor):
        return [len(valor), len(valor[0])]
    if isinstance(valor, list):
        return [len(valor)]
    raise ValueError("forma() necesita una lista o una matriz")


def operar(a, b, funcion):
    """Aplica la funcion elemento por elemento, como NumPy.
    Si uno de los dos es un solo numero, se usa con todos los elementos del otro."""
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError(f"las listas no tienen el mismo largo ({len(a)} y {len(b)})")
        return [operar(x, y, funcion) for x, y in zip(a, b)]
    if isinstance(a, list):
        return [operar(x, b, funcion) for x in a]
    if isinstance(b, list):
        return [operar(a, y, funcion) for y in b]
    if not es_numero(a) or not es_numero(b):
        raise TypeError("las operaciones entre listas solo funcionan con números")
    return funcion(a, b)


def cada(a, funcion):
    """Aplica una funcion de un solo valor a todos los elementos (tambien en matrices)."""
    if isinstance(a, list):
        return [cada(x, funcion) for x in a]
    if not es_numero(a):
        raise TypeError("solo funciona con números")
    return funcion(a)


def ceros(filas: int, columnas: int = 0) -> list:
    if columnas == 0:
        return [0] * filas
    return [[0] * columnas for _ in range(filas)]


def unos(filas: int, columnas: int = 0) -> list:
    if columnas == 0:
        return [1] * filas
    return [[1] * columnas for _ in range(filas)]


def identidad(n: int) -> list:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def transpuesta(m: list) -> list:
    """Las filas pasan a ser columnas. Un vector se vuelve una matriz de una columna."""
    if es_vector(m):
        return [[v] for v in m]
    _exigir_matriz(m, "transpuesta")
    return [[m[i][j] for i in range(len(m))] for j in range(len(m[0]))]


def punto(a: list, b: list):
    """Producto punto de dos vectores: a1*b1 + a2*b2 + ..."""
    if not es_vector(a) or not es_vector(b):
        raise ValueError("punto() necesita dos listas de números")
    if len(a) != len(b):
        raise ValueError(f"los vectores no tienen el mismo largo ({len(a)} y {len(b)})")
    total = 0
    for x, y in zip(a, b):
        total += x * y
    return total


def producto(a: list, b: list) -> list:
    """Producto de matrices: la fila i de a por la columna j de b.
    Un vector se toma como columna, asi producto(A, x) da otro vector."""
    if es_matriz(a) and es_vector(b):
        if len(a[0]) != len(b):
            raise ValueError(f"no se puede multiplicar una matriz de {len(a)}x{len(a[0])} "
                             f"por un vector de {len(b)}")
        return [punto(fila, b) for fila in a]
    _exigir_matriz(a, "producto")
    _exigir_matriz(b, "producto")
    if len(a[0]) != len(b):
        raise ValueError(f"no se puede multiplicar una matriz de {len(a)}x{len(a[0])} "
                         f"por una de {len(b)}x{len(b[0])}: las columnas de la primera "
                         "tienen que ser las filas de la segunda")
    columnas = transpuesta(b)
    return [[punto(fila, columna) for columna in columnas] for fila in a]


def _exigir_matriz(m, funcion: str) -> None:
    if not es_matriz(m):
        raise ValueError(f"{funcion}() necesita una matriz (una lista de filas del mismo largo, "
                         "todas con números)")


def _exigir_cuadrada(m, funcion: str) -> None:
    _exigir_matriz(m, funcion)
    if len(m) != len(m[0]):
        raise ValueError(f"{funcion}() necesita una matriz cuadrada y esta es de {len(m)}x{len(m[0])}")


def _eliminacion(m: list, extra: list):
    """Eliminacion de Gauss-Jordan con pivoteo parcial sobre copias de m y extra.
    Devuelve (matriz escalonada reducida, extra transformada, determinante)."""
    n = len(m)
    a = [[float(v) for v in fila] for fila in m]
    b = [[float(v) for v in fila] for fila in extra]
    determinante = 1.0
    for columna in range(n):
        # el pivote es el numero mas grande de la columna, asi el error de redondeo es menor
        pivote = max(range(columna, n), key=lambda i: absoluto(a[i][columna]))
        if absoluto(a[pivote][columna]) < 1e-12:
            return None, None, 0.0
        if pivote != columna:
            a[columna], a[pivote] = a[pivote], a[columna]
            b[columna], b[pivote] = b[pivote], b[columna]
            determinante = -determinante
        valor = a[columna][columna]
        determinante *= valor
        a[columna] = [v / valor for v in a[columna]]
        b[columna] = [v / valor for v in b[columna]]
        for i in range(n):
            if i != columna and a[i][columna] != 0:
                factor = a[i][columna]
                a[i] = [x - factor * y for x, y in zip(a[i], a[columna])]
                b[i] = [x - factor * y for x, y in zip(b[i], b[columna])]
    return a, b, determinante


def determinante(m: list):
    _exigir_cuadrada(m, "determinante")
    return _eliminacion(m, [[] for _ in m])[2]


def inversa(m: list) -> list:
    _exigir_cuadrada(m, "inversa")
    _, inv, det = _eliminacion(m, identidad(len(m)))
    if inv is None:
        raise ValueError("la matriz no tiene inversa (su determinante es 0)")
    return inv


def resolver(a: list, b: list) -> list:
    """Resuelve el sistema A x = b y devuelve x."""
    _exigir_cuadrada(a, "resolver")
    if not es_vector(b) or len(b) != len(a):
        raise ValueError(f"resolver() necesita una lista de {len(a)} números al lado derecho")
    _, x, _ = _eliminacion(a, [[v] for v in b])
    if x is None:
        raise ValueError("el sistema no tiene una única solución (el determinante es 0)")
    return [fila[0] for fila in x]


def norma(v: list):
    """El largo de un vector: raiz de la suma de cuadrados."""
    return raiz(punto(v, v))


def distancia(a: list, b: list):
    """Distancia euclidiana entre dos puntos."""
    return norma(operar(a, b, lambda x, y: x - y))
