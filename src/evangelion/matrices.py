"""Nuestra libreria de vectores y matrices (lo que en Python haria NumPy).

Un vector es una lista de numeros y una matriz es una lista de filas, donde
todas las filas tienen el mismo largo. Nada cambia la lista original.
"""

from .listas import Lista
from .matematica import absoluto, raiz
from .tablas import es_numero


def es_vector(valor) -> bool:
    return isinstance(valor, Lista) and all(es_numero(v) for v in valor)


def es_matriz(valor) -> bool:
    return (isinstance(valor, Lista) and len(valor) > 0 and all(es_vector(f) for f in valor)
            and all(len(f) == len(valor[0]) for f in valor) and len(valor[0]) > 0)


def forma(valor) -> Lista:
    """[filas, columnas] de una matriz o [largo] de un vector."""
    if es_matriz(valor):
        return Lista((len(valor), len(valor[0])))
    if isinstance(valor, Lista):
        return Lista((len(valor),))
    raise ValueError("necesita una lista o una matriz")


def operar(a, b, funcion):
    """Aplica la funcion elemento por elemento, como NumPy.
    Si uno de los dos es un solo numero, se usa con todos los elementos del otro."""
    if isinstance(a, Lista) and isinstance(b, Lista):
        if len(a) != len(b):
            raise ValueError(f"las listas no tienen el mismo largo ({len(a)} y {len(b)})")
        return Lista(operar(x, y, funcion) for x, y in zip(a, b))
    if isinstance(a, Lista):
        return Lista(operar(x, b, funcion) for x in a)
    if isinstance(b, Lista):
        return Lista(operar(a, y, funcion) for y in b)
    if not es_numero(a) or not es_numero(b):
        raise TypeError("las operaciones entre listas solo funcionan con números")
    return funcion(a, b)


def cada(a, funcion):
    """Aplica una funcion de un solo valor a todos los elementos (tambien en matrices)."""
    if isinstance(a, Lista):
        return Lista(cada(x, funcion) for x in a)
    if not es_numero(a):
        raise TypeError("solo funciona con números")
    return funcion(a)


def _revisar_tamano(*tamanos) -> None:
    for n in tamanos:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError(f"los tamaños van con enteros desde 1 y llegó {n}")


def ceros(filas: int, columnas: int = None) -> Lista:
    _revisar_tamano(filas, *(Lista() if columnas is None else Lista((columnas,))))
    if columnas is None:
        return Lista((0,)) * filas
    return Lista(Lista((0,)) * columnas for _ in range(filas))


def unos(filas: int, columnas: int = None) -> Lista:
    _revisar_tamano(filas, *(Lista() if columnas is None else Lista((columnas,))))
    if columnas is None:
        return Lista((1,)) * filas
    return Lista(Lista((1,)) * columnas for _ in range(filas))


def identidad(n: int) -> Lista:
    _revisar_tamano(n)
    return Lista(Lista(1 if i == j else 0 for j in range(n)) for i in range(n))


def transpuesta(m: Lista) -> Lista:
    """Las filas pasan a ser columnas. Un vector se vuelve una matriz de una columna."""
    if es_vector(m):
        return Lista(Lista((v,)) for v in m)
    _exigir_matriz(m, "transpuesta")
    return Lista(Lista(m[i][j] for i in range(len(m))) for j in range(len(m[0])))


def punto(a: Lista, b: Lista):
    """Producto punto de dos vectores: a1*b1 + a2*b2 + ..."""
    if not es_vector(a) or not es_vector(b):
        raise ValueError("necesita dos listas de números sin datos faltantes, como punto([1, 2], [3, 4])")
    if len(a) != len(b):
        raise ValueError(f"los vectores no tienen el mismo largo ({len(a)} y {len(b)})")
    return suma_de_productos(a, b)


def suma_de_productos(a: Lista, b: Lista):
    """El producto punto sin revisar nada: para los ciclos de los modelos, que ya revisaron sus datos."""
    total = 0
    for x, y in zip(a, b):
        total += x * y
    return total


def producto(a: Lista, b: Lista) -> Lista:
    """Producto de matrices: la fila i de a por la columna j de b.
    Un vector se toma como columna, asi producto(A, x) da otro vector."""
    if es_matriz(a) and es_vector(b):
        if len(a[0]) != len(b):
            raise ValueError(f"no se puede multiplicar una matriz de {len(a)}x{len(a[0])} "
                             f"por un vector de {len(b)}")
        return Lista(punto(fila, b) for fila in a)
    _exigir_matriz(a, "producto")
    _exigir_matriz(b, "producto")
    if len(a[0]) != len(b):
        raise ValueError(f"no se puede multiplicar una matriz de {len(a)}x{len(a[0])} "
                         f"por una de {len(b)}x{len(b[0])}: las columnas de la primera "
                         "tienen que ser las filas de la segunda")
    columnas = transpuesta(b)
    return Lista(Lista(punto(fila, columna) for columna in columnas) for fila in a)


def _exigir_matriz(m, funcion: str) -> None:
    if not es_matriz(m):
        raise ValueError("necesita una matriz (una lista de filas del mismo largo, "
                         "todas con números)")


def _exigir_cuadrada(m, funcion: str) -> None:
    _exigir_matriz(m, funcion)
    if len(m) != len(m[0]):
        raise ValueError(f"necesita una matriz cuadrada y esta es de {len(m)}x{len(m[0])}")


def _eliminacion(m: Lista, extra: Lista):
    """Eliminacion de Gauss-Jordan con pivoteo parcial sobre copias de m y extra.
    Devuelve (matriz escalonada reducida, extra transformada, determinante)."""
    n = len(m)
    a = Lista(Lista(float(v) for v in fila) for fila in m)
    b = Lista(Lista(float(v) for v in fila) for fila in extra)
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
        a[columna] = Lista(v / valor for v in a[columna])
        b[columna] = Lista(v / valor for v in b[columna])
        for i in range(n):
            if i != columna and a[i][columna] != 0:
                factor = a[i][columna]
                a[i] = Lista(x - factor * y for x, y in zip(a[i], a[columna]))
                b[i] = Lista(x - factor * y for x, y in zip(b[i], b[columna]))
    return a, b, determinante


def determinante(m: Lista):
    _exigir_cuadrada(m, "determinante")
    return _eliminacion(m, Lista(Lista() for _ in m))[2]


def inversa(m: Lista) -> Lista:
    _exigir_cuadrada(m, "inversa")
    _, inv, det = _eliminacion(m, identidad(len(m)))
    if inv is None:
        raise ValueError("la matriz no tiene inversa (su determinante es 0)")
    return inv


def resolver(a: Lista, b: Lista) -> Lista:
    """Resuelve el sistema A x = b y devuelve x."""
    _exigir_cuadrada(a, "resolver")
    if not es_vector(b) or len(b) != len(a):
        raise ValueError(f"necesita una lista de {len(a)} números al lado derecho")
    _, x, _ = _eliminacion(a, Lista(Lista((v,)) for v in b))
    if x is None:
        raise ValueError("el sistema no tiene una única solución (el determinante es 0)")
    return Lista(fila[0] for fila in x)


def norma(v: Lista):
    """El largo de un vector: raiz de la suma de cuadrados."""
    return raiz(punto(v, v))


def distancia(a: Lista, b: Lista):
    """Distancia euclidiana entre dos puntos."""
    return norma(operar(a, b, lambda x, y: x - y))
