"""Nuestra libreria de tablas, hecha a mano y sin dependencias.

Una Tabla guarda los datos por columnas y una Columna es una lista de valores
donde None significa "dato faltante". Ninguna operacion cambia la tabla
original: todas devuelven una nueva.
"""

from .listas import Lista, ordenada

PALABRAS_BOOLEANAS = {"verdadero": True, "si": True, "true": True,
                      "falso": False, "no": False, "false": False}


def _son_digitos(texto: str) -> bool:
    return texto != "" and all(c in "0123456789" for c in texto)


def es_entero_texto(texto: str) -> bool:
    """42, +7, -3"""
    return _son_digitos(texto[1:] if texto[:1] in ("+", "-") else texto)


def es_real_texto(texto: str, con_exponente: bool = True) -> bool:
    """3.5, -.5, 2., 1e-3"""
    numero = texto[1:] if texto[:1] in ("+", "-") else texto
    if con_exponente:
        base, hay_e, exponente = numero.replace("E", "e").partition("e")
        if hay_e and not es_entero_texto(exponente):
            return False
    else:
        base = numero
    entera, punto, decimales = base.partition(".")
    if not punto:
        return _son_digitos(entera)
    return (_son_digitos(entera) and (decimales == "" or _son_digitos(decimales))) or (entera == "" and _son_digitos(decimales))


def formatear(valor, decimales: int = 2) -> str:
    """Como se escribe un valor en pantalla."""
    if valor is None:
        return "nulo"
    if isinstance(valor, bool):
        return "verdadero" if valor else "falso"
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)


def es_numero(valor) -> bool:
    # en Python True y False tambien son int, por eso se descartan aparte
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def congelar(valor):
    """Una version que se puede meter en un set: las listas y los diccionarios
    (que Python no deja guardar en un set) pasan a tuplas."""
    if isinstance(valor, Lista):
        return ("lista",) + tuple(congelar(v) for v in valor)
    if isinstance(valor, dict):
        return ("diccionario",) + tuple(ordenada(((str(k), congelar(v)) for k, v in valor.items()), key=str))
    return valor


# --- Columna -------------------------------------------------------------------

class Columna:

    def __init__(self, valores, nombre: str = ""):
        self.valores = Lista(valores)
        self.nombre = nombre

    def __len__(self) -> int:
        return len(self.valores)

    def presentes(self) -> Lista:
        return Lista(v for v in self.valores if v is not None)

    def clase(self) -> str:
        """numero, texto o booleano, segun lo que tenga adentro. Vacia es 'nulo'."""
        presentes = self.presentes()
        if not presentes:
            return "nulo"
        if all(isinstance(v, bool) for v in presentes):
            return "booleano"
        if all(es_numero(v) for v in presentes):
            return "numero"
        return "texto"

    # Operaciones fila por fila. El otro lado puede ser una columna o un solo valor.

    def _con(self, otro, funcion, si_falta=None) -> "Columna":
        otros = otro.valores if isinstance(otro, Columna) else Lista((otro,)) * len(self.valores)
        resultado = Lista()
        for a, b in zip(self.valores, otros):
            if a is None or b is None:
                resultado.agregar(si_falta)
                continue
            try:
                r = funcion(a, b)
            except (ZeroDivisionError, OverflowError):
                r = None   # una division por cero deja el dato como faltante
            # la raiz de un negativo daria un complejo: tampoco es un dato valido
            resultado.agregar(None if isinstance(r, complex) else r)
        return Columna(resultado)

    def __add__(self, otro): return self._con(otro, lambda a, b: a + b)
    def __radd__(self, otro): return self._con(otro, lambda a, b: b + a)
    def __sub__(self, otro): return self._con(otro, lambda a, b: a - b)
    def __rsub__(self, otro): return self._con(otro, lambda a, b: b - a)
    def __mul__(self, otro): return self._con(otro, lambda a, b: a * b)
    def __rmul__(self, otro): return self._con(otro, lambda a, b: b * a)
    def __truediv__(self, otro): return self._con(otro, lambda a, b: a / b)
    def __rtruediv__(self, otro): return self._con(otro, lambda a, b: b / a)
    def __mod__(self, otro): return self._con(otro, lambda a, b: a % b)
    def __rmod__(self, otro): return self._con(otro, lambda a, b: b % a)
    def __pow__(self, otro): return self._con(otro, lambda a, b: a ** b)
    def __rpow__(self, otro): return self._con(otro, lambda a, b: b ** a)

    # Comparar contra un faltante da falso (y verdadero en el caso de !=)
    def __lt__(self, otro): return self._con(otro, lambda a, b: a < b, si_falta=False)
    def __le__(self, otro): return self._con(otro, lambda a, b: a <= b, si_falta=False)
    def __gt__(self, otro): return self._con(otro, lambda a, b: a > b, si_falta=False)
    def __ge__(self, otro): return self._con(otro, lambda a, b: a >= b, si_falta=False)
    def __eq__(self, otro): return self._con(otro, lambda a, b: a == b, si_falta=False)
    def __ne__(self, otro): return self._con(otro, lambda a, b: a != b, si_falta=True)

    def __and__(self, otro): return self._con(otro, lambda a, b: a and b)
    def __rand__(self, otro): return self._con(otro, lambda a, b: b and a)
    def __or__(self, otro): return self._con(otro, lambda a, b: a or b)
    def __ror__(self, otro): return self._con(otro, lambda a, b: b or a)

    def _cada(self, funcion) -> "Columna":
        return Columna(Lista(None if v is None else funcion(v) for v in self.valores))

    def __neg__(self): return self._cada(lambda v: -v)
    def __invert__(self): return self._cada(lambda v: not v)
    def __abs__(self): return self._cada(abs)

    def redondear(self, decimales: int = 0): return self._cada(lambda v: round(v, decimales))
    def mayusculas(self): return self._cada(str.upper)
    def minusculas(self): return self._cada(str.lower)
    def reemplazar(self, viejo, nuevo): return self._cada(lambda v: v.replace(viejo, nuevo))

    def es_nulo(self) -> "Columna":
        return Columna(Lista(v is None for v in self.valores))

    def rellenar(self, valor) -> "Columna":
        return Columna(Lista(valor if v is None else v for v in self.valores))

    def convertir(self, tipo: str) -> "Columna":
        """Pasa la columna a entero, real, texto o booleano. Si un valor no
        encaja lanza ValueError."""
        return self._cada(CONVERSORES[tipo])

    # Estadisticas. Los faltantes no cuentan.

    def contar(self) -> int:
        return len(self.presentes())

    def faltantes(self) -> int:
        return len(self.valores) - self.contar()

    def distintos(self) -> int:
        return len({congelar(v) for v in self.presentes()})

    def suma(self):
        return sum(self.presentes())

    def media(self):
        presentes = self.presentes()
        return sum(presentes) / len(presentes) if presentes else None

    def mediana(self):
        ordenados = ordenada(self.presentes())
        n = len(ordenados)
        if n == 0:
            return None
        mitad = n // 2
        if n % 2 == 1:
            return ordenados[mitad]
        return (ordenados[mitad - 1] + ordenados[mitad]) / 2

    def minimo(self):
        presentes = self.presentes()
        return min(presentes) if presentes else None

    def maximo(self):
        presentes = self.presentes()
        return max(presentes) if presentes else None

    def desviacion(self):
        """Desviacion estandar muestral: la suma de cuadrados se divide entre n - 1."""
        presentes = self.presentes()
        n = len(presentes)
        if n < 2:
            return None
        media = sum(presentes) / n
        return (sum((v - media) ** 2 for v in presentes) / (n - 1)) ** 0.5


def _a_booleano(valor):
    if isinstance(valor, bool):
        return valor
    if es_numero(valor):
        return valor != 0
    if str(valor).strip().lower() not in PALABRAS_BOOLEANAS:
        raise ValueError(valor)
    return PALABRAS_BOOLEANAS[str(valor).strip().lower()]


CONVERSORES = {
    "entero": lambda v: int(float(v)),
    "real": float,
    "texto": lambda v: formatear(v) if isinstance(v, bool) else str(v),
    "booleano": _a_booleano,
}


# --- Tabla ---------------------------------------------------------------------

class Tabla:

    def __init__(self, columnas, datos):
        self.columnas = Lista(columnas)
        self._datos = {c: Lista(datos[c]) for c in self.columnas}

    @classmethod
    def de_registros(cls, registros, columnas) -> "Tabla":
        """Arma la tabla a partir de una lista de diccionarios, uno por fila."""
        return cls(columnas, {c: Lista(r.get(c) for r in registros) for c in columnas})

    def __len__(self) -> int:
        return len(self._datos[self.columnas[0]]) if self.columnas else 0

    def __getitem__(self, nombre: str) -> Columna:
        return Columna(self._datos[nombre], nombre)

    def filas(self) -> Lista:
        return Lista(Lista(self._datos[c][i] for c in self.columnas) for i in range(len(self)))

    def registros(self) -> Lista:
        return Lista(dict(zip(self.columnas, fila)) for fila in self.filas())

    def _tomar(self, indices) -> "Tabla":
        return Tabla(self.columnas, {c: Lista(self._datos[c][i] for i in indices) for c in self.columnas})

    def seleccionar(self, columnas) -> "Tabla":
        return Tabla(columnas, self._datos)

    def sin_columnas(self, columnas) -> "Tabla":
        return self.seleccionar(Lista(c for c in self.columnas if c not in columnas))

    def renombrar(self, cambios: dict) -> "Tabla":
        nuevas = Lista(cambios.get(c, c) for c in self.columnas)
        return Tabla(nuevas, {cambios.get(c, c): self._datos[c] for c in self.columnas})

    def con_columna(self, nombre: str, valores) -> "Tabla":
        """Agrega la columna, o la reemplaza si ya existia. Un solo valor se repite en todas las filas."""
        datos = dict(self._datos)
        datos[nombre] = valores.valores if isinstance(valores, Columna) else Lista((valores,)) * len(self)
        columnas = self.columnas if nombre in self.columnas else self.columnas + Lista((nombre,))
        return Tabla(columnas, datos)

    def filtrar(self, condicion: Columna) -> "Tabla":
        return self._tomar(Lista(i for i, cumple in enumerate(condicion.valores) if cumple is True))

    def primeras(self, n: int) -> "Tabla":
        return self._tomar(range(min(n, len(self))))

    def ordenar(self, columnas, ascendentes) -> "Tabla":
        """Ordena por varias columnas. Los faltantes siempre quedan al final."""
        indices = Lista(range(len(self)))
        # se ordena de la ultima columna a la primera: como sort no desordena
        # los empates, al final manda la primera
        for columna, ascendente in reversed(Lista(zip(columnas, ascendentes))):
            valores = self._datos[columna]
            con_dato = Lista(i for i in indices if valores[i] is not None)
            sin_dato = Lista(i for i in indices if valores[i] is None)
            indices = ordenada(con_dato, key=lambda i: valores[i], reverse=not ascendente) + sin_dato
        return self._tomar(indices)

    def sin_duplicados(self, columnas=None) -> "Tabla":
        """Deja la primera fila de cada combinacion repetida."""
        columnas = columnas or self.columnas
        vistas, indices = set(), Lista()
        for i in range(len(self)):
            clave = tuple(congelar(self._datos[c][i]) for c in columnas)
            if clave not in vistas:
                vistas.add(clave)
                indices.agregar(i)
        return self._tomar(indices)

    def sin_faltantes(self, columnas=None) -> "Tabla":
        columnas = columnas or self.columnas
        return self._tomar(Lista(i for i in range(len(self))
                            if all(self._datos[c][i] is not None for c in columnas)))

    def resumir(self, claves, calculos) -> "Tabla":
        """Agrupa por las claves y calcula un resumen de cada grupo.

        calculos es una lista de (nombre, funcion, columna). Si la columna es
        None se cuentan las filas. Sin claves sale una sola fila con toda la tabla.
        Los grupos salen en el orden en que aparecen.
        """
        grupos = {}
        for i in range(len(self)):
            clave = tuple(self._datos[c][i] for c in claves)
            grupos.setdefault(clave, Lista()).agregar(i)
        if not claves:
            grupos = {(): Lista(range(len(self)))}

        registros = Lista()
        for clave, indices in grupos.items():
            grupo = self._tomar(indices)
            registro = dict(zip(claves, clave))
            for nombre, funcion, columna in calculos:
                registro[nombre] = len(grupo) if columna is None else getattr(grupo[columna], funcion)()
            registros.agregar(registro)
        return Tabla.de_registros(registros, Lista(claves) + Lista(nombre for nombre, _, _ in calculos))

    def predecir_knn(self, objetivo: str, predictoras: Lista, k: int) -> "Columna":
        """Predice la columna `objetivo` para cada fila con el algoritmo de los k
        vecinos mas cercanos, usando distancia euclidiana sobre las `predictoras`
        normalizadas a [0, 1]. Es leave-one-out: cada fila se predice con las demas
        filas de la tabla, nunca consigo misma.

        Si el objetivo es numerico se promedia el valor de los k vecinos, si es
        texto o booleano se toma el mas frecuente. Una fila con algun dato faltante
        en las predictoras no se puede predecir (sale None), y una fila con el
        objetivo faltante no puede servir de vecina de nadie.
        """
        # normalizar cada predictora a [0, 1]; una columna constante no aporta nada
        # a la distancia, por eso se evita la division por cero dejandola en 0
        rangos = {}
        for columna in predictoras:
            minimo, maximo = self[columna].minimo(), self[columna].maximo()
            rangos[columna] = (minimo, maximo - minimo if maximo != minimo else 1)

        def normalizar(indice: int, columna: str):
            valor = self._datos[columna][indice]
            if valor is None:
                return None
            minimo, amplitud = rangos[columna]
            return (valor - minimo) / amplitud

        vectores = Lista(Lista(normalizar(i, columna) for columna in predictoras) for i in range(len(self)))
        objetivos = self._datos[objetivo]
        es_numerico = self[objetivo].clase() == "numero"

        # solo sirven de vecinas las filas con todas las predictoras y el objetivo presentes
        candidatos = Lista(i for i in range(len(self))
                     if objetivos[i] is not None and None not in vectores[i])

        predicciones = Lista()
        for i in range(len(self)):
            if None in vectores[i]:
                predicciones.agregar(None)   # sin predictoras completas no se puede predecir
                continue
            distancias = Lista()
            for j in candidatos:
                if j == i:
                    continue   # leave-one-out: una fila nunca es vecina de si misma
                suma = sum((a - b) ** 2 for a, b in zip(vectores[i], vectores[j]))
                distancias.agregar((suma ** 0.5, objetivos[j]))
            vecinos = Lista(valor for _, valor in ordenada(distancias, key=lambda par: par[0])[:k])
            if not vecinos:
                predicciones.agregar(None)
            elif es_numerico:
                predicciones.agregar(Columna(vecinos).media())
            else:
                conteo = {}
                for valor in vecinos:
                    conteo[valor] = conteo.get(valor, 0) + 1
                predicciones.agregar(max(conteo, key=conteo.get))
        return Columna(predicciones, nombre=f"{objetivo}_prediccion")

    def como_texto(self) -> str:
        """La tabla lista para imprimir: numeros a la derecha y textos a la izquierda."""
        bloques = Lista()
        for nombre in self.columnas:
            columna = self[nombre]
            celdas = Lista(formatear(v) for v in columna.valores)
            ancho = max(len(nombre), *(len(c) for c in celdas)) if celdas else len(nombre)
            alinear = str.rjust if columna.clase() == "numero" else str.ljust
            bloques.agregar(Lista((alinear(nombre, ancho),)) + Lista(alinear(c, ancho) for c in celdas))
        return "\n".join("  ".join(linea).rstrip() for linea in zip(*bloques))


# --- Archivos CSV --------------------------------------------------------------

def partir_csv(texto: str, separador: str = ",") -> Lista:
    """Parte el texto en filas y campos. Lo que va entre comillas dobles puede
    traer el separador o saltos de linea, y "" es una comilla escrita."""
    filas, fila, campo = Lista(), Lista(), Lista()
    entre_comillas = False
    i = 0
    while i < len(texto):
        c = texto[i]
        if entre_comillas:
            if c == '"' and texto[i + 1:i + 2] == '"':
                campo.agregar('"')
                i += 1
            elif c == '"':
                entre_comillas = False
            else:
                campo.agregar(c)
        elif c == '"':
            entre_comillas = True
        elif texto.startswith(separador, i):
            fila.agregar("".join(campo))
            campo = Lista()
            i += len(separador) - 1
        elif c in "\r\n":
            if c == "\r" and texto[i + 1:i + 2] == "\n":
                i += 1
            fila.agregar("".join(campo))
            filas.agregar(fila)
            fila, campo = Lista(), Lista()
        else:
            campo.agregar(c)
        i += 1
    if campo or fila:
        fila.agregar("".join(campo))
        filas.agregar(fila)
    return Lista(f for f in filas if f != Lista(("",)))   # las lineas en blanco no cuentan


def inferir(textos: Lista) -> Lista:
    """Decide si una columna es de enteros, de reales o de texto. Vacio = faltante."""
    limpios = Lista(t.strip() for t in textos)
    for patron, convertir in ((es_entero_texto, int), (es_real_texto, float)):
        if all(t == "" or patron(t) for t in limpios):
            return Lista(None if t == "" else convertir(t) for t in limpios)
    return Lista(None if t == "" else t for t in textos)


def leer_csv(ruta, separador: str = ",", codificacion: str = "utf-8", encabezado: bool = True) -> Tabla:
    if not isinstance(separador, str) or separador == "":
        raise ValueError("el separador tiene que ser un texto de al menos un carácter")
    with open(ruta, encoding=codificacion, newline="") as archivo:
        filas = partir_csv(archivo.read().lstrip("﻿"), separador)
    if not filas:
        raise ValueError("el archivo está vacío")

    if encabezado:
        nombres, filas = Lista(n.strip() for n in filas[0]), filas[1:]
    else:
        nombres = Lista(f"col{i + 1}" for i in range(len(filas[0])))
    if len(set(nombres)) != len(nombres):
        raise ValueError("hay nombres de columna repetidos")
    for numero, fila in enumerate(filas, start=2 if encabezado else 1):
        if len(fila) != len(nombres):
            raise ValueError(f"la fila {numero} trae {len(fila)} datos y se esperaban {len(nombres)}")

    return Tabla(nombres, {nombre: inferir(Lista(fila[i] for fila in filas))
                           for i, nombre in enumerate(nombres)})


def escribir_csv(tabla: Tabla, ruta, decimales: int = 4) -> None:
    def celda(valor) -> str:
        if valor is None:
            return ""
        texto = str(round(valor, decimales)) if isinstance(valor, float) else formatear(valor)
        if any(c in texto for c in ',"\r\n'):
            texto = '"' + texto.replace('"', '""') + '"'
        return texto

    lineas = Lista((tabla.columnas,)) + tabla.filas()
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        for linea in lineas:
            archivo.write(",".join(celda(v) for v in linea) + "\n")
