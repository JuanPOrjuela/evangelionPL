"""Nuestra libreria de aprendizaje automatico (lo que en Python haria scikit-learn).

- regresion: minimos cuadrados, para predecir un numero.
- clasificar: k vecinos mas cercanos, para predecir una categoria.
- grupos: k-medias, para agrupar filas parecidas sin saber la respuesta.

Un modelo es un diccionario del lenguaje, asi se puede mostrar y revisar con
modelo.coeficientes o modelo["r2"].
"""

from . import matrices
from .matematica import Aleatorio, raiz
from .tablas import Columna, Tabla, es_numero

MAX_VUELTAS = 100
INTENTOS = 10


def _lista_de_variables(variables) -> list:
    if isinstance(variables, str):
        return [variables]
    if isinstance(variables, list) and variables and all(isinstance(v, str) for v in variables):
        return variables
    raise ValueError('las variables van como un texto o una lista de textos, por ejemplo ["edad", "peso"]')


def _revisar_columnas(tabla: Tabla, columnas: list, numericas: bool = True) -> None:
    if len(tabla) == 0:
        raise ValueError("la tabla está vacía")
    for c in columnas:
        if c not in tabla.columnas:
            raise ValueError(f"la columna '{c}' no existe en la tabla")
        valores = tabla[c].valores
        if any(v is None for v in valores):
            raise ValueError(f"la columna '{c}' tiene datos faltantes; quítalos antes con "
                             f"quitar faltantes [{c}]")
        if numericas and not all(es_numero(v) for v in valores):
            raise ValueError(f"la columna '{c}' tiene que ser numérica")


def _puntos(tabla: Tabla, variables: list) -> list:
    """Una lista por fila con los valores de las variables."""
    return [[tabla[c].valores[i] for c in variables] for i in range(len(tabla))]


def _escala(puntos: list):
    """Media y desviacion de cada variable, para que todas pesen igual en las distancias."""
    n, d = len(puntos), len(puntos[0])
    medias = [sum(p[j] for p in puntos) / n for j in range(d)]
    desviaciones = []
    for j in range(d):
        varianza = sum((p[j] - medias[j]) ** 2 for p in puntos) / n
        desviaciones.append(raiz(varianza) or 1.0)  # una variable constante no se escala
    return medias, desviaciones


def _escalar(puntos: list, medias: list, desviaciones: list) -> list:
    return [[(p[j] - medias[j]) / desviaciones[j] for j in range(len(p))] for p in puntos]


# --- Regresion lineal ------------------------------------------------------------

def regresion(tabla: Tabla, variables, objetivo: str) -> dict:
    """y = b0 + b1*x1 + b2*x2 + ...  Los coeficientes salen de las ecuaciones normales
    (X^T X) b = X^T y, que se resuelven con eliminacion de Gauss."""
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables + [objetivo])
    if len(tabla) <= len(variables):
        raise ValueError(f"para {len(variables)} variables hacen falta más de {len(variables)} filas")
    x = [[1] + p for p in _puntos(tabla, variables)]  # el 1 es para el intercepto b0
    y = tabla[objetivo].valores
    xt = matrices.transpuesta(x)
    try:
        coeficientes = matrices.resolver(matrices.producto(xt, x), matrices.producto(xt, y))
    except ValueError:
        raise ValueError("no se pudo ajustar la regresión: alguna variable es constante "
                         "o es una copia de otra")
    predichos = [matrices.punto(fila, coeficientes) for fila in x]
    return {"tipo": "regresion", "variables": variables, "objetivo": objetivo,
            "coeficientes": coeficientes, "r2": r2(y, predichos)}


# --- Clasificacion: k vecinos mas cercanos -----------------------------------------

def clasificar(tabla: Tabla, variables, objetivo: str, k: int = 3) -> dict:
    """Guarda los puntos de entrenamiento; la prediccion se hace al llamar predecir()."""
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables)
    _revisar_columnas(tabla, [objetivo], numericas=False)
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= len(tabla):
        raise ValueError(f"k tiene que ser un entero entre 1 y {len(tabla)} (las filas de la tabla)")
    puntos = _puntos(tabla, variables)
    medias, desviaciones = _escala(puntos)
    return {"tipo": "vecinos", "variables": variables, "objetivo": objetivo, "k": k,
            "medias": medias, "desviaciones": desviaciones,
            "puntos": _escalar(puntos, medias, desviaciones),
            "etiquetas": list(tabla[objetivo].valores)}


def _votar(modelo: dict, punto: list):
    """La etiqueta que mas se repite entre los k puntos mas cercanos.
    Si hay empate gana la del vecino mas cercano."""
    distancias = sorted((matrices.distancia(punto, p), i) for i, p in enumerate(modelo["puntos"]))
    cercanos = [modelo["etiquetas"][i] for _, i in distancias[:modelo["k"]]]
    votos = {}
    for etiqueta in cercanos:
        votos[etiqueta] = votos.get(etiqueta, 0) + 1
    mas_votos = max(votos.values())
    return next(e for e in cercanos if votos[e] == mas_votos)


# --- Prediccion ----------------------------------------------------------------------

def _revisar_modelo(modelo) -> None:
    if not isinstance(modelo, dict) or modelo.get("tipo") not in ("regresion", "vecinos"):
        raise ValueError("predecir() necesita un modelo hecho con regresion() o clasificar()")


def predecir(modelo: dict, datos):
    """Con una tabla devuelve la misma tabla con la columna 'prediccion'.
    Con un numero o una lista de numeros devuelve una sola prediccion."""
    _revisar_modelo(modelo)
    variables = modelo["variables"]
    if isinstance(datos, Tabla):
        _revisar_columnas(datos, variables)
        puntos = _puntos(datos, variables)
        return datos.con_columna("prediccion", Columna([_predecir_uno(modelo, p) for p in puntos]))
    punto = [datos] if es_numero(datos) else datos
    if not matrices.es_vector(punto) or len(punto) != len(variables):
        raise ValueError(f"el modelo usa {len(variables)} variables ({', '.join(variables)}) "
                         f"y hay que darle {len(variables)} números")
    return _predecir_uno(modelo, punto)


def _predecir_uno(modelo: dict, punto: list):
    if modelo["tipo"] == "regresion":
        return matrices.punto([1] + punto, modelo["coeficientes"])
    escalado = _escalar([punto], modelo["medias"], modelo["desviaciones"])[0]
    return _votar(modelo, escalado)


# --- Agrupamiento: k-medias -----------------------------------------------------------

def grupos(tabla: Tabla, variables, k: int, semilla: int = 42) -> Tabla:
    """Reparte las filas en k grupos: cada fila va al centro mas cercano, cada centro se
    mueve al promedio de su grupo, y se repite hasta que nadie cambia de grupo.
    Devuelve la tabla con la columna 'grupo' (1, 2, ..., k)."""
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables)
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= len(tabla):
        raise ValueError(f"k tiene que ser un entero entre 1 y {len(tabla)} (las filas de la tabla)")
    puntos = _puntos(tabla, variables)
    puntos = _escalar(puntos, *_escala(puntos))
    azar = Aleatorio(semilla)

    # k-medias puede quedarse en una solucion mala segun donde empiece,
    # por eso se intenta varias veces y se deja la de grupos mas compactos
    mejor = None
    for _ in range(INTENTOS):
        asignacion, centros = _k_medias(puntos, _centros_iniciales(puntos, k, azar))
        dispersion = sum(matrices.distancia(p, centros[g]) ** 2 for p, g in zip(puntos, asignacion))
        if mejor is None or dispersion < mejor[0]:
            mejor = (dispersion, asignacion, centros)
    _, asignacion, centros = mejor

    # el grupo 1 es el de centro mas bajo en la primera variable, el 2 el siguiente, ...
    orden = sorted(range(k), key=lambda c: centros[c])
    numero = {c: i + 1 for i, c in enumerate(orden)}
    return tabla.con_columna("grupo", Columna([numero[g] for g in asignacion]))


def _k_medias(puntos: list, centros: list) -> tuple:
    asignacion = None
    for _ in range(MAX_VUELTAS):
        nueva = [min(range(len(centros)), key=lambda c: matrices.distancia(p, centros[c])) for p in puntos]
        if nueva == asignacion:
            break
        asignacion = nueva
        for c in range(len(centros)):
            miembros = [p for p, g in zip(puntos, asignacion) if g == c]
            if miembros:  # un grupo vacio deja su centro donde estaba
                centros[c] = [sum(m[j] for m in miembros) / len(miembros) for j in range(len(miembros[0]))]
    return asignacion, centros


def _centros_iniciales(puntos: list, k: int, azar: Aleatorio) -> list:
    """k-medias++: el primer centro al azar y cada siguiente con mas probabilidad
    entre mas lejos este de los centros que ya hay."""
    centros = [puntos[azar.entero(0, len(puntos) - 1)]]
    while len(centros) < k:
        pesos = [min(matrices.distancia(p, c) for c in centros) ** 2 for p in puntos]
        total = sum(pesos)
        if total == 0:  # todos los puntos que quedan son iguales a algun centro
            centros.append(puntos[len(centros)])
            continue
        meta, acumulado = azar.siguiente() * total, 0
        for p, peso in zip(puntos, pesos):
            acumulado += peso
            if acumulado >= meta and peso > 0:
                centros.append(p)
                break
    return [list(c) for c in centros]


# --- Entrenamiento y prueba -------------------------------------------------------------

def dividir(tabla: Tabla, proporcion: float = 0.8, semilla: int = 42) -> list:
    """Baraja las filas y devuelve [entrenamiento, prueba]."""
    if not es_numero(proporcion) or not 0 < proporcion < 1:
        raise ValueError("la proporción va entre 0 y 1, por ejemplo 0.8")
    if len(tabla) < 2:
        raise ValueError("hacen falta al menos 2 filas para dividir la tabla")
    orden = Aleatorio(semilla).barajar(range(len(tabla)))
    corte = min(max(round(len(tabla) * proporcion), 1), len(tabla) - 1)
    return [tabla._tomar(sorted(orden[:corte])), tabla._tomar(sorted(orden[corte:]))]


# --- Metricas ---------------------------------------------------------------------------

def _pareja(reales, predichos) -> tuple:
    reales = reales.valores if isinstance(reales, Columna) else reales
    predichos = predichos.valores if isinstance(predichos, Columna) else predichos
    if not isinstance(reales, list) or not isinstance(predichos, list):
        raise ValueError("las métricas comparan dos columnas o dos listas")
    if len(reales) != len(predichos) or not reales:
        raise ValueError(f"los reales y los predichos tienen que tener el mismo largo "
                         f"({len(reales)} y {len(predichos)})")
    return reales, predichos


def error_cuadratico(reales, predichos):
    """Promedio de (real - predicho)^2. Entre mas pequeno, mejor."""
    reales, predichos = _pareja(reales, predichos)
    return sum((r - p) ** 2 for r, p in zip(reales, predichos)) / len(reales)


def r2(reales, predichos):
    """Que parte de la variacion explica el modelo: 1 es perfecto, 0 es igual que adivinar la media."""
    reales, predichos = _pareja(reales, predichos)
    media = sum(reales) / len(reales)
    total = sum((r - media) ** 2 for r in reales)
    residual = sum((r - p) ** 2 for r, p in zip(reales, predichos))
    return 1 - residual / total if total else 1.0


def exactitud(reales, predichos):
    """Que fraccion de las predicciones acerto."""
    reales, predichos = _pareja(reales, predichos)
    return sum(1 for r, p in zip(reales, predichos) if r == p) / len(reales)
