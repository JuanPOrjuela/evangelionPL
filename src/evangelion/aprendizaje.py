"""Nuestra libreria de aprendizaje automatico (lo que en Python haria scikit-learn).

Prediccion (un numero):
- regresion: regresion lineal por minimos cuadrados.
- arbol: arbol de decision; con un objetivo numerico predice el promedio de la hoja.
Clasificacion (una categoria):
- arbol: arbol de decision con el indice de Gini.
- perceptron: una neurona con sigmoide entrenada con descenso de gradiente.
- red_neuronal: perceptron multicapa (una capa oculta) entrenado con retropropagacion.
- vecinos: k vecinos mas cercanos.
Agrupamiento (sin respuesta conocida):
- grupos: k-medias.

Un modelo es un diccionario del lenguaje, asi se puede mostrar y revisar con
modelo.coeficientes o modelo["r2"].
"""

from . import matrices
from .matematica import Aleatorio, exp, ln, raiz
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

def vecinos(tabla: Tabla, variables, objetivo: str, k: int = 3) -> dict:
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
    if not isinstance(modelo, dict) or modelo.get("tipo") not in PREDICTORES:
        raise ValueError("predecir() necesita un modelo hecho con regresion(), arbol(), "
                         "perceptron(), red_neuronal() o vecinos()")


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
    if modelo["tipo"] == "arbol":
        return _bajar_por_el_arbol(modelo["raiz"], dict(zip(modelo["variables"], punto)))
    escalado = _escalar([punto], modelo["medias"], modelo["desviaciones"])[0]
    if modelo["tipo"] == "vecinos":
        return _votar(modelo, escalado)
    if modelo["tipo"] == "perceptron":
        probabilidad = sigmoide(matrices.punto(modelo["pesos"], escalado) + modelo["sesgo"])
        return modelo["clases"][1] if probabilidad >= 0.5 else modelo["clases"][0]
    salida = _adelante(modelo, escalado)[1]
    return modelo["clases"][max(range(len(salida)), key=lambda c: salida[c])]


PREDICTORES = ("regresion", "arbol", "vecinos", "perceptron", "red_neuronal")


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


# --- Arbol de decision (CART) -----------------------------------------------------------
# En cada nodo se prueba cada variable y cada corte posible ("x <= umbral") y se queda
# el corte que deja los dos lados mas puros: menor indice de Gini al clasificar, o menor
# varianza al predecir un numero. Se para al llegar a la profundidad maxima o cuando
# ya no hay como mejorar.

def arbol(tabla: Tabla, variables, objetivo: str, profundidad: int = 4) -> dict:
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables)
    _revisar_columnas(tabla, [objetivo], numericas=False)
    if not isinstance(profundidad, int) or isinstance(profundidad, bool) or not 1 <= profundidad <= 20:
        raise ValueError("la profundidad va entre 1 y 20")
    etiquetas = list(tabla[objetivo].valores)
    clase = "regresion" if all(es_numero(e) for e in etiquetas) else "clasificacion"
    filas = [dict(zip(variables, p)) for p in _puntos(tabla, variables)]
    raiz_arbol = _crecer(filas, etiquetas, variables, clase, profundidad)
    modelo = {"tipo": "arbol", "clase": clase, "variables": variables, "objetivo": objetivo,
              "profundidad": profundidad, "raiz": raiz_arbol}
    predichos = [_bajar_por_el_arbol(raiz_arbol, f) for f in filas]
    if clase == "clasificacion":
        modelo["exactitud"] = exactitud(etiquetas, predichos)
    else:
        modelo["r2"] = r2(etiquetas, predichos)
    return modelo


def gini(etiquetas: list) -> float:
    """1 - suma de p^2: es 0 cuando todas las etiquetas son iguales."""
    n = len(etiquetas)
    return 1 - sum((c / n) ** 2 for c in _contar(etiquetas).values())


def _contar(etiquetas: list) -> dict:
    conteo = {}
    for e in etiquetas:
        conteo[e] = conteo.get(e, 0) + 1
    return conteo


def _varianza(valores: list) -> float:
    media = sum(valores) / len(valores)
    return sum((v - media) ** 2 for v in valores) / len(valores)


def _hoja(etiquetas: list, clase: str) -> dict:
    if clase == "regresion":
        return {"valor": sum(etiquetas) / len(etiquetas), "filas": len(etiquetas)}
    conteo = _contar(etiquetas)
    return {"valor": max(conteo, key=lambda e: conteo[e]), "filas": len(etiquetas)}


def _crecer(filas: list, etiquetas: list, variables: list, clase: str, profundidad: int) -> dict:
    impureza = gini if clase == "clasificacion" else _varianza
    actual = impureza(etiquetas)
    if profundidad == 0 or actual == 0 or len(etiquetas) < 4:
        return _hoja(etiquetas, clase)
    mejor = None   # (impureza ponderada, variable, umbral)
    n = len(etiquetas)
    for variable in variables:
        valores = sorted(set(f[variable] for f in filas))
        for a, b in zip(valores, valores[1:]):
            umbral = (a + b) / 2
            izquierda = [e for f, e in zip(filas, etiquetas) if f[variable] <= umbral]
            derecha = [e for f, e in zip(filas, etiquetas) if f[variable] > umbral]
            ponderada = (len(izquierda) * impureza(izquierda) + len(derecha) * impureza(derecha)) / n
            if mejor is None or ponderada < mejor[0]:
                mejor = (ponderada, variable, umbral)
    if mejor is None or mejor[0] >= actual - 1e-12:
        return _hoja(etiquetas, clase)
    _, variable, umbral = mejor
    izquierda = [i for i, f in enumerate(filas) if f[variable] <= umbral]
    derecha = [i for i, f in enumerate(filas) if f[variable] > umbral]
    si = _crecer([filas[i] for i in izquierda], [etiquetas[i] for i in izquierda],
                 variables, clase, profundidad - 1)
    sino = _crecer([filas[i] for i in derecha], [etiquetas[i] for i in derecha],
                   variables, clase, profundidad - 1)
    # poda: si los dos lados terminan diciendo lo mismo, la pregunta sobra
    if clase == "clasificacion" and "valor" in si and "valor" in sino and si["valor"] == sino["valor"]:
        return _hoja(etiquetas, clase)
    return {"variable": variable, "umbral": umbral, "si": si, "sino": sino}


def _bajar_por_el_arbol(nodo: dict, fila: dict):
    while "valor" not in nodo:
        nodo = nodo["si"] if fila[nodo["variable"]] <= nodo["umbral"] else nodo["sino"]
    return nodo["valor"]


def reglas(modelo: dict) -> list:
    """El arbol escrito como reglas de texto, una por hoja."""
    if not isinstance(modelo, dict) or modelo.get("tipo") != "arbol":
        raise ValueError("reglas() necesita un modelo hecho con arbol()")
    resultado = []

    def recorrer(nodo, limites):
        """limites guarda, por variable, el mayor 'mas que' y el menor 'hasta' del camino."""
        if "valor" in nodo:
            valor = nodo["valor"]
            texto = f"{valor:.4g}" if isinstance(valor, float) else str(valor)
            partes = []
            for variable, (desde, hasta) in limites.items():
                if desde is not None:
                    partes.append(f"{variable} > {desde:.4g}")
                if hasta is not None:
                    partes.append(f"{variable} <= {hasta:.4g}")
            resultado.append(f"si {' y '.join(partes) or 'siempre'} -> {texto} ({nodo['filas']} filas)")
            return
        variable, umbral = nodo["variable"], nodo["umbral"]
        desde, hasta = limites.get(variable, (None, None))
        recorrer(nodo["si"], {**limites, variable: (desde, umbral)})
        recorrer(nodo["sino"], {**limites, variable: (umbral, hasta)})

    recorrer(modelo["raiz"], {})
    return resultado


# --- Perceptron con descenso de gradiente --------------------------------------------------

def sigmoide(z: float) -> float:
    """1 / (1 + e^-z), con cuidado de no desbordar exp() con numeros muy grandes."""
    if z >= 0:
        return 1 / (1 + exp(-z))
    ez = exp(z)
    return ez / (1 + ez)


def _revisar_entrenamiento(tasa, epocas) -> None:
    if not es_numero(tasa) or tasa <= 0:
        raise ValueError("la tasa de aprendizaje tiene que ser un número positivo, por ejemplo 0.1")
    if not isinstance(epocas, int) or isinstance(epocas, bool) or not 1 <= epocas <= 100000:
        raise ValueError("las épocas van entre 1 y 100000")


def _entropia(p: float, real: int) -> float:
    p = min(max(p, 1e-12), 1 - 1e-12)   # ln(0) no existe
    return -ln(p) if real == 1 else -ln(1 - p)


def perceptron(tabla: Tabla, variables, objetivo: str, tasa: float = 0.1, epocas: int = 500) -> dict:
    """Una neurona: p = sigmoide(w . x + b). La perdida es la entropia cruzada
    L = -[y ln(p) + (1 - y) ln(1 - p)] y sus derivadas parciales son
    dL/dw_j = (p - y) * x_j  y  dL/db = (p - y). En cada epoca se promedian sobre
    todas las filas y se da un paso en contra del gradiente: w_j = w_j - tasa * dL/dw_j."""
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables)
    _revisar_columnas(tabla, [objetivo], numericas=False)
    _revisar_entrenamiento(tasa, epocas)
    etiquetas = list(tabla[objetivo].valores)
    clases = sorted(set(etiquetas), key=str)
    if len(clases) != 2:
        raise ValueError(f"el perceptrón separa exactamente 2 clases y el objetivo tiene {len(clases)}; "
                         "para más clases usa red_neuronal() o arbol()")
    puntos = _puntos(tabla, variables)
    medias, desviaciones = _escala(puntos)
    x = _escalar(puntos, medias, desviaciones)
    y = [1 if e == clases[1] else 0 for e in etiquetas]
    n, d = len(x), len(variables)

    pesos, sesgo, perdidas = [0.0] * d, 0.0, []
    for _ in range(epocas):
        gradiente, gradiente_sesgo, perdida = [0.0] * d, 0.0, 0.0
        for fila, real in zip(x, y):
            p = sigmoide(matrices.punto(pesos, fila) + sesgo)
            error = p - real
            for j in range(d):
                gradiente[j] += error * fila[j]
            gradiente_sesgo += error
            perdida += _entropia(p, real)
        pesos = [w - tasa * g / n for w, g in zip(pesos, gradiente)]
        sesgo -= tasa * gradiente_sesgo / n
        perdidas.append(perdida / n)

    modelo = {"tipo": "perceptron", "variables": variables, "objetivo": objetivo, "clases": clases,
              "pesos": pesos, "sesgo": sesgo, "medias": medias, "desviaciones": desviaciones,
              "perdidas": perdidas, "perdida": perdidas[-1]}
    modelo["exactitud"] = exactitud(etiquetas, [_predecir_uno(modelo, p) for p in puntos])
    return modelo


# --- Red neuronal: perceptron multicapa con retropropagacion ----------------------------------

def red_neuronal(tabla: Tabla, variables, objetivo: str, ocultas: int = 5, tasa: float = 0.5,
                 epocas: int = 300, semilla: int = 42) -> dict:
    """entradas -> capa oculta (sigmoide) -> salida (softmax, una neurona por clase).
    La retropropagacion usa la regla de la cadena para sacar la derivada parcial de la
    perdida respecto a cada peso, de la salida hacia atras:
      salida:  dL/dz2 = p - y             dL/dW2 = dL/dz2 * a1
      oculta:  dL/da1 = W2^T * dL/dz2     dL/dz1 = dL/da1 * a1 * (1 - a1)    dL/dW1 = dL/dz1 * x
    y cada peso se mueve un paso en contra de su derivada, fila por fila."""
    variables = _lista_de_variables(variables)
    _revisar_columnas(tabla, variables)
    _revisar_columnas(tabla, [objetivo], numericas=False)
    _revisar_entrenamiento(tasa, epocas)
    if not isinstance(ocultas, int) or isinstance(ocultas, bool) or not 1 <= ocultas <= 100:
        raise ValueError("las neuronas ocultas van entre 1 y 100")
    etiquetas = list(tabla[objetivo].valores)
    clases = sorted(set(etiquetas), key=str)
    if len(clases) < 2:
        raise ValueError("el objetivo necesita al menos 2 clases distintas")
    puntos = _puntos(tabla, variables)
    medias, desviaciones = _escala(puntos)
    x = _escalar(puntos, medias, desviaciones)
    d, c = len(variables), len(clases)

    # pesos iniciales pequenos y al azar, para que las neuronas no aprendan todas lo mismo
    azar = Aleatorio(semilla)
    modelo = {"tipo": "red_neuronal", "variables": variables, "objetivo": objetivo, "clases": clases,
              "medias": medias, "desviaciones": desviaciones,
              "w1": [[azar.siguiente() - 0.5 for _ in range(d)] for _ in range(ocultas)],
              "b1": [0.0] * ocultas,
              "w2": [[azar.siguiente() - 0.5 for _ in range(ocultas)] for _ in range(c)],
              "b2": [0.0] * c}
    perdidas = []
    for _ in range(epocas):
        perdida = 0.0
        for fila, etiqueta in zip(x, etiquetas):
            a1, p = _adelante(modelo, fila)
            real = [1 if clase == etiqueta else 0 for clase in clases]
            perdida += -ln(max(p[clases.index(etiqueta)], 1e-12))
            dz2 = [pk - yk for pk, yk in zip(p, real)]
            dz1 = [sum(modelo["w2"][k][h] * dz2[k] for k in range(c)) * a1[h] * (1 - a1[h])
                   for h in range(ocultas)]
            for k in range(c):
                for h in range(ocultas):
                    modelo["w2"][k][h] -= tasa * dz2[k] * a1[h]
                modelo["b2"][k] -= tasa * dz2[k]
            for h in range(ocultas):
                for j in range(d):
                    modelo["w1"][h][j] -= tasa * dz1[h] * fila[j]
                modelo["b1"][h] -= tasa * dz1[h]
        perdidas.append(perdida / len(x))
    modelo["perdidas"] = perdidas
    modelo["perdida"] = perdidas[-1]
    modelo["exactitud"] = exactitud(etiquetas, [_predecir_uno(modelo, p) for p in puntos])
    return modelo


def _adelante(modelo: dict, fila: list) -> tuple:
    """Pasa una fila por la red y devuelve (activaciones ocultas, probabilidad de cada clase)."""
    a1 = [sigmoide(matrices.punto(w, fila) + b) for w, b in zip(modelo["w1"], modelo["b1"])]
    z2 = [matrices.punto(w, a1) + b for w, b in zip(modelo["w2"], modelo["b2"])]
    mayor = max(z2)   # se resta el mayor para que exp() no se desborde; softmax no cambia
    potencias = [exp(z - mayor) for z in z2]
    total = sum(potencias)
    return a1, [v / total for v in potencias]


# --- Correlacion -----------------------------------------------------------------------------

def correlacion(a, b) -> float:
    """Coeficiente de Pearson: 1 suben juntos, -1 uno sube y el otro baja, 0 sin relacion lineal."""
    a, b = _pareja(a, b)
    if any(not es_numero(v) for v in a + b):
        raise ValueError("la correlación necesita números sin datos faltantes")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        raise ValueError("una de las dos variables es constante")
    return cov / raiz(va * vb)
