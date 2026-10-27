"""El Visitor recorre el arbol y ejecuta el programa con nuestras librerias:
tablas (datos), matematica, matrices, aprendizaje (modelos) y graficas."""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from . import aprendizaje, graficas, matematica, matrices
from .errores import ErrorSemantico
from .generado.EvaParser import EvaParser
from .generado.EvaVisitor import EvaVisitor
from .simbolos import TablaSimbolos
from .tablas import Columna, Tabla, es_numero, escribir_csv, leer_csv

# Cada agregacion es un metodo de Columna con el mismo nombre
AGREGACIONES = ("suma", "media", "mediana", "minimo", "maximo", "desviacion", "contar")
SOLO_NUMEROS = {"suma", "media", "mediana", "desviacion"}
FUNCIONES = {"filas": (1, 1), "redondear": (1, 2), "absoluto": (1, 1),
             "mayusculas": (1, 1), "minusculas": (1, 1), "reemplazar": (3, 3)}
# Matematicas de un solo numero; tambien sirven con columnas y listas
MATEMATICAS = {"raiz": matematica.raiz, "exp": matematica.exp, "ln": matematica.ln,
               "log": matematica.log, "sen": matematica.sen, "cos": matematica.cos,
               "tan": matematica.tan, "piso": matematica.piso, "techo": matematica.techo,
               "factorial": matematica.factorial}
DOS_ARGUMENTOS = {"raiz", "log"}   # raiz(x, 3) y log(x, 2)
LISTAS = {"longitud": (1, 1), "agregar": (2, 2), "sacar": (1, 2), "contiene": (2, 2),
          "rango": (1, 3), "ordenada": (1, 1), "invertida": (1, 1), "unir": (2, 2),
          "claves": (1, 1), "valores": (1, 1), "texto": (1, 1), "numero": (1, 1),
          "columna": (2, 2), "tabla_de": (1, 1), "aleatorio": (0, 2), "semilla": (1, 1)}
MATRICES = {"ceros": (1, 2), "unos": (1, 2), "identidad": (1, 1), "transpuesta": (1, 1),
            "producto": (2, 2), "punto": (2, 2), "determinante": (1, 1), "inversa": (1, 1),
            "resolver": (2, 2), "forma": (1, 1), "norma": (1, 1)}
MODELOS = {"regresion": (3, 3), "arbol": (3, 4), "perceptron": (3, 5), "red_neuronal": (3, 7),
           "knn": (3, 4), "grupos": (3, 4), "predecir": (2, 2), "reglas": (1, 1),
           "dividir": (1, 3), "error_cuadratico": (2, 2), "r2": (2, 2), "exactitud": (2, 2),
           "correlacion": (2, 2)}
CON_TABLA = ("regresion", "arbol", "perceptron", "red_neuronal", "knn", "grupos", "dividir")
# Reciben una funcion escrita por el usuario
NUMERICOS = {"derivada": (2, 2), "biseccion": (3, 3), "newton": (2, 2), "mapear": (2, 2)}
TODAS = {**FUNCIONES, **{n: (1, 2 if n in DOS_ARGUMENTOS else 1) for n in MATEMATICAS},
         **LISTAS, **MATRICES, **MODELOS, **NUMERICOS}
MAX_PROFUNDIDAD = 100     # llamadas de funciones una dentro de otra (recursion)
SIN_RESULTADO = ("agregar", "semilla")   # cambian algo y no devuelven nada
CONSTANTES = {"pi": matematica.PI, "e": matematica.E}
MAX_VUELTAS = 1_000_000   # un ciclo que da mas vueltas seguramente nunca termina
ELEMENTOS_EN_PANTALLA = 20
TIPOS = ("entero", "real", "texto", "booleano")
GRAFICAS = graficas.TIPOS
OPCIONES_CARGA = ("separador", "codificacion", "encabezado")
OPCIONES_GRAFICA = ("eje_x", "eje_y", "serie", "titulo", "etiqueta_x", "etiqueta_y", "archivo",
                    "color", "intervalos", "ancho", "alto", "leyenda")
EJES = ("eje_x", "eje_y", "serie")
TEXTOS_GRAFICA = ("titulo", "etiqueta_x", "etiqueta_y", "archivo", "color")
ENTEROS_GRAFICA = {"intervalos": (1, 200), "ancho": (320, 4000), "alto": (240, 4000)}
COMPARADORES = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
                ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
FILAS_EN_PANTALLA = 12


@dataclass
class Funcion:
    """Una funcion definida en el programa con funcion nombre(a, b) { ... }."""
    nombre: str
    parametros: list
    cuerpo: object      # el nodo bloque del arbol, se visita en cada llamada


class Retorno(Exception):
    """retornar corta la funcion y sube el valor hasta donde se llamo."""

    def __init__(self, valor):
        super().__init__()
        self.valor = valor


@dataclass
class Agrupada:
    """Lo que deja SQUAD: una tabla con sus grupos, esperando a MAGI."""
    tabla: Tabla
    columnas: list


def clase_de(valor) -> str:
    if isinstance(valor, Tabla):
        return "tabla"
    if isinstance(valor, Agrupada):
        return "grupo"
    if isinstance(valor, Columna):
        return valor.clase()
    if valor is None:
        return "nulo"
    if isinstance(valor, bool):
        return "booleano"
    if isinstance(valor, list):
        return "lista"
    if isinstance(valor, dict):
        return "diccionario"
    if isinstance(valor, Funcion):
        return "funcion"
    return "numero" if es_numero(valor) else "texto"


def encaja(valor, clase: str) -> bool:
    """Una columna sin ningun dato (tabla vacia o todo faltante) encaja con cualquier clase."""
    return clase_de(valor) in (clase, "nulo") if isinstance(valor, Columna) else clase_de(valor) == clase


def describir(valor) -> str:
    clase = clase_de(valor)
    if isinstance(valor, Columna):
        return {"numero": "una columna de números", "texto": "una columna de texto",
                "booleano": "una columna de verdadero/falso", "nulo": "una columna vacía"}[clase]
    return {"tabla": "una tabla", "grupo": "una tabla agrupada", "numero": "un número",
            "texto": "un texto", "booleano": "un booleano", "nulo": "nulo",
            "lista": "una lista", "diccionario": "un diccionario", "funcion": "una función"}[clase]


def limpiar(nombre: str) -> str:
    """`Tipo de EVA` -> Tipo de EVA"""
    return nombre.strip("`")


def quitar_comillas(crudo: str) -> str:
    escapes = {"n": "\n", "t": "\t"}
    return re.sub(r'\\(["\\nt])', lambda m: escapes.get(m.group(1), m.group(1)), crudo[1:-1])


def distancia(a: str, b: str) -> int:
    """Distancia de Levenshtein: cuantas letras hay que poner, quitar o cambiar
    para pasar de una palabra a la otra."""
    anterior = list(range(len(b) + 1))
    for i, letra_a in enumerate(a, 1):
        actual = [i]
        for j, letra_b in enumerate(b, 1):
            actual.append(min(anterior[j] + 1, actual[j - 1] + 1,
                              anterior[j - 1] + (letra_a != letra_b)))
        anterior = actual
    return anterior[-1]


def sugerir(nombre: str, opciones) -> str:
    opciones = [str(o) for o in opciones]
    if not opciones:
        return ""
    cercana = min(opciones, key=lambda o: distancia(nombre.lower(), o.lower()))
    diferencia = distancia(nombre.lower(), cercana.lower())
    if diferencia <= 2 and diferencia < len(nombre):
        return f" ¿Quisiste decir '{cercana}'?"
    return " Las que hay son: " + ", ".join(opciones[:10]) + "."


def texto_de(valor, dentro: bool = False) -> str:
    if valor is None:
        return "nulo"
    if isinstance(valor, bool):
        return "verdadero" if valor else "falso"
    if isinstance(valor, float):
        return str(round(valor, 4) + 0.0)   # el + 0.0 evita que salga "-0.0"
    if isinstance(valor, str) and dentro:
        return f'"{valor}"'
    if isinstance(valor, Tabla):
        return f"<tabla de {len(valor)} filas>"
    if isinstance(valor, Funcion):
        return f"<función {valor.nombre}({', '.join(valor.parametros)})>"
    if isinstance(valor, list):
        partes = [texto_de(v, True) for v in valor[:ELEMENTOS_EN_PANTALLA]]
        if len(valor) > ELEMENTOS_EN_PANTALLA:
            partes.append(f"... ({len(valor)} en total)")
        return "[" + ", ".join(partes) + "]"
    if isinstance(valor, dict):
        return "{" + ", ".join(f"{texto_de(k, True)}: {texto_de(v, True)}" for k, v in valor.items()) + "}"
    return str(valor)


def como_matriz(valor) -> str:
    """Una matriz se muestra fila por fila, con las columnas alineadas."""
    celdas = [[texto_de(v) for v in fila] for fila in valor]
    ancho = max(len(c) for fila in celdas for c in fila)
    return "\n".join("  [ " + "  ".join(c.rjust(ancho) for c in fila) + " ]" for fila in celdas)


class Interprete(EvaVisitor):

    def __init__(self):
        self.simbolos = TablaSimbolos()
        self.operacion = ""
        self.reportes = []       # archivos que escribio SEELE
        self.graficas = []       # archivos que dibujo HOLOGRAM
        self._entrada = None     # lo que recibe la etapa que se esta ejecutando
        self._tabla = None       # tabla cuyas columnas se pueden nombrar ahora
        self.azar = matematica.Aleatorio()
        # cada llamada del lenguaje usa unas 25 llamadas de Python al recorrer el arbol
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 30 * MAX_PROFUNDIDAD + 1000))

    def ejecutar(self, arbol) -> None:
        self.visit(arbol)

    # --- Sentencias ----------------------------------------------------------

    def visitPrograma(self, ctx):
        if ctx.cabecera():
            self.operacion = quitar_comillas(ctx.cabecera().CADENA().getText())
        for sentencia in ctx.sentencia():
            self.visit(sentencia)

    def visitAsignacion(self, ctx):
        nombre = limpiar(ctx.nombre().getText())
        valor = self.visit(ctx.flujo())
        if isinstance(valor, Columna):
            raise ErrorSemantico(ctx.flujo(), "una columna suelta no se puede guardar en una variable. "
                                              "Usa TARGET para sacar una tabla con esa columna "
                                              "o columna(tabla, \"nombre\") para tener una lista.")
        if not ctx.indice():
            self.simbolos.definir(nombre, clase_de(valor), valor, ctx.start.line)
            return
        # lista[1] = 5 o datos["clave"] = 5: se cambia un elemento de lo que ya existe
        simbolo = self.simbolos.buscar(nombre)
        if simbolo is None:
            raise ErrorSemantico(ctx.nombre(), f"la variable '{nombre}' no se ha declarado."
                                 + sugerir(nombre, self.simbolos.nombres()))
        contenedor = simbolo.valor
        indices = ctx.indice()
        for indice in indices[:-1]:
            contenedor = self._elemento(indice, contenedor, self.visit(indice.expresion()))
        ultimo = indices[-1]
        clave = self.visit(ultimo.expresion())
        if isinstance(contenedor, list):
            contenedor[self._posicion(ultimo, contenedor, clave)] = valor
        elif isinstance(contenedor, dict):
            self._revisar_clave(ultimo, clave)
            contenedor[clave] = valor
        else:
            raise ErrorSemantico(ultimo, f"solo se puede cambiar un elemento de una lista o de un "
                                         f"diccionario, y aquí hay {describir(contenedor)}.")

    def visitMostrar(self, ctx):
        valor = self.visit(ctx.flujo())
        if isinstance(valor, Columna):
            nombre = valor.nombre or "columna"
            valor = Tabla([nombre], {nombre: valor.valores})
        # si el flujo es solo un nombre lo usamos de titulo
        texto = ctx.flujo().getText()
        titulo = " " + texto if re.fullmatch(r"[^\W\d]\w*", texto) else ""
        textos = isinstance(valor, list) and valor and all(isinstance(v, str) for v in valor)
        if textos and len(texto_de(valor)) > 100:
            # una lista larga de textos (como las reglas de un arbol) va una por linea
            print(f"MONITOR{titulo} ({len(valor)} elementos)")
            print("\n".join(f"  {v}" for v in valor) + "\n")
            return
        if matrices.es_matriz(valor) and len(valor) > 1:
            print(f"MONITOR{titulo} (matriz de {len(valor)}x{len(valor[0])})")
            print(como_matriz(valor) + "\n")
            return
        if not isinstance(valor, Tabla):
            print(f"MONITOR{titulo}: {texto_de(valor)}\n")
            return
        filas, columnas = len(valor), len(valor.columnas)
        print(f"MONITOR{titulo} ({filas} {'fila' if filas == 1 else 'filas'} x {columnas} columnas)")
        print(valor.primeras(FILAS_EN_PANTALLA).como_texto())
        if filas > FILAS_EN_PANTALLA:
            print(f"... y {filas - FILAS_EN_PANTALLA} filas más")
        print()

    def visitGuardar(self, ctx):
        valor = self.visit(ctx.flujo())
        if not isinstance(valor, Tabla):
            raise ErrorSemantico(ctx.flujo(), f"SEELE solo recibe tablas y aquí llegó {describir(valor)}.")
        ruta = Path(quitar_comillas(ctx.CADENA().getText()))
        if ruta.suffix.lower() != ".csv":
            raise ErrorSemantico(ctx.CADENA().symbol, "por ahora los reportes solo se guardan en .csv.")
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            escribir_csv(valor, ruta)
        except OSError as error:
            raise ErrorSemantico(ctx.CADENA().symbol, f"no se pudo escribir '{ruta}': {error}.")
        self.reportes.append(ruta.as_posix())
        print(f"SEELE recibió el reporte {ruta.as_posix()} ({len(valor)} filas)\n")

    def visitGraficar(self, ctx):
        tipo = ctx.ID().getText()
        if tipo not in GRAFICAS:
            raise ErrorSemantico(ctx.ID().symbol, f"no existe la gráfica '{tipo}'." + sugerir(tipo, GRAFICAS))
        tabla = self.visit(ctx.flujo())
        if not isinstance(tabla, Tabla):
            raise ErrorSemantico(ctx.flujo(), f"HOLOGRAM necesita una tabla y aquí llegó {describir(tabla)}.")
        # los ejes nombran columnas, por eso las opciones se evaluan dentro de la tabla
        valores = self._opciones(ctx.opcion(), OPCIONES_GRAFICA, tabla)
        donde = {o.ID().getText(): o for o in ctx.opcion()}
        grafica = self._armar_grafica(ctx, tipo, valores, donde)

        ruta = Path(valores.get("archivo") or f"salidas/{tipo}_{len(self.graficas) + 1}.png")
        if ruta.suffix.lower() not in (".png", ".svg"):
            raise ErrorSemantico(donde["archivo"], "las gráficas se guardan en .png o en .svg.")
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            usadas = graficas.guardar(grafica, ruta)
        except ValueError as error:
            raise ErrorSemantico(ctx, f"HOLOGRAM no pudo dibujar la gráfica: {error}.")
        except OSError as error:
            raise ErrorSemantico(ctx, f"no se pudo escribir '{ruta}': {error}.")
        self.graficas.append(ruta.as_posix())
        print(f"HOLOGRAM proyectó la gráfica de {tipo} en {ruta.as_posix()} ({usadas} filas)\n")

    def _armar_grafica(self, ctx, tipo, valores, donde) -> graficas.Grafica:
        """Revisa que cada opcion tenga el tipo que le toca y arma la Grafica."""
        faltan = [eje for eje in graficas.OBLIGATORIOS[tipo] if eje not in valores]
        if faltan:
            raise ErrorSemantico(ctx, f"la gráfica de {tipo} necesita {' y '.join(faltan)}.")
        for eje in EJES:
            if eje in valores and not isinstance(valores[eje], Columna):
                raise ErrorSemantico(donde[eje], f"{eje} tiene que ser una columna de la tabla "
                                                 f"y aquí llegó {describir(valores[eje])}.")
        for eje in graficas.NUMERICOS[tipo]:
            if eje in valores and not encaja(valores[eje], "numero"):
                raise ErrorSemantico(donde[eje], f"tipos incompatibles: en la gráfica de {tipo} el {eje} "
                                                 f"tiene que ser numérico y '{valores[eje].nombre}' es "
                                                 f"{describir(valores[eje])}.")
        for opcion in TEXTOS_GRAFICA:
            if opcion in valores and not isinstance(valores[opcion], str):
                raise ErrorSemantico(donde[opcion], f"{opcion} va entre comillas, como texto.")
        for opcion, (minimo, maximo) in ENTEROS_GRAFICA.items():
            valor = valores.get(opcion)
            if valor is not None and (not isinstance(valor, int) or isinstance(valor, bool)
                                      or not minimo <= valor <= maximo):
                raise ErrorSemantico(donde[opcion], f"{opcion} tiene que ser un número entero "
                                                    f"entre {minimo} y {maximo}.")
        if "leyenda" in valores and not isinstance(valores["leyenda"], bool):
            raise ErrorSemantico(donde["leyenda"], "leyenda va con verdadero o falso.")
        color = None
        if "color" in valores:
            color = graficas.color_de(valores["color"])
            if color is None:
                raise ErrorSemantico(donde["color"], f"el color '{valores['color']}' no existe. Usa uno "
                                                     f"de {', '.join(graficas.COLORES)} o un '#rrggbb'.")
        return graficas.Grafica(
            tipo, x=valores.get("eje_x"), y=valores.get("eje_y"), serie=valores.get("serie"),
            titulo=valores.get("titulo", ""), etiqueta_x=valores.get("etiqueta_x"),
            etiqueta_y=valores.get("etiqueta_y"), color=color, intervalos=valores.get("intervalos"),
            ancho=valores.get("ancho", 960), alto=valores.get("alto", 600),
            leyenda=valores.get("leyenda", True))

    def _condicion(self, ctx, expresion) -> bool:
        condicion = self.visit(expresion)
        if not isinstance(condicion, bool):
            raise ErrorSemantico(expresion, f"la condición de {ctx.start.text} tiene que dar verdadero "
                                            f"o falso, y dio {describir(condicion)}.")
        return condicion

    def visitCondicional(self, ctx):
        if self._condicion(ctx, ctx.expresion()):
            self.visit(ctx.bloque(0))
        elif ctx.condicional():     # sino si ...
            self.visit(ctx.condicional())
        elif ctx.PATTERN_ORANGE():
            self.visit(ctx.bloque(1))

    def visitMientras(self, ctx):
        vueltas = 0
        while self._condicion(ctx, ctx.expresion()):
            vueltas += 1
            if vueltas > MAX_VUELTAS:
                raise ErrorSemantico(ctx, f"el ciclo ya dio más de {MAX_VUELTAS} vueltas; "
                                          "revisa que la condición alguna vez se vuelva falsa.")
            self.visit(ctx.bloque())

    def visitPara(self, ctx):
        nombre = limpiar(ctx.nombre().getText())
        if ctx.EN():
            coleccion = self.visit(ctx.expresion(0))
            if isinstance(coleccion, Tabla):
                elementos = coleccion.registros()   # cada fila llega como un diccionario
            elif isinstance(coleccion, Columna):
                elementos = coleccion.valores
            elif isinstance(coleccion, (list, dict, str)):
                elementos = list(coleccion)         # de un diccionario se recorren las claves
            else:
                raise ErrorSemantico(ctx.expresion(0), "para ... en necesita una lista, un diccionario, "
                                                       f"un texto o una tabla, y llegó {describir(coleccion)}.")
        else:
            desde, hasta = self.visit(ctx.expresion(0)), self.visit(ctx.expresion(1))
            for valor, expresion in ((desde, ctx.expresion(0)), (hasta, ctx.expresion(1))):
                if not matematica.es_entero(valor):
                    raise ErrorSemantico(expresion, f"desde y hasta van con números enteros "
                                                    f"y aquí llegó {describir(valor)}.")
            if hasta - desde > MAX_VUELTAS:
                raise ErrorSemantico(ctx, f"el ciclo daría más de {MAX_VUELTAS} vueltas.")
            elementos = range(desde, hasta + 1)
        for elemento in elementos:
            self.simbolos.definir(nombre, clase_de(elemento), elemento, ctx.start.line)
            self.visit(ctx.bloque())

    def visitLlamada(self, ctx):
        self._llamada(ctx)

    # --- Funciones del usuario -------------------------------------------------

    def visitFuncion(self, ctx):
        nombre = ctx.ID().getText()
        if nombre in TODAS or nombre in AGREGACIONES:
            raise ErrorSemantico(ctx.ID().symbol, f"'{nombre}' ya es una función del lenguaje; "
                                                  "ponle otro nombre a la tuya.")
        parametros = [limpiar(n.getText()) for n in ctx.nombre()]
        repetidos = {p for p in parametros if parametros.count(p) > 1}
        if repetidos:
            raise ErrorSemantico(ctx, f"el parámetro '{repetidos.pop()}' está repetido.")
        self.simbolos.definir(nombre, "funcion", Funcion(nombre, parametros, ctx.bloque()), ctx.start.line)

    def visitRetornar(self, ctx):
        if self.simbolos.profundidad == 0:
            raise ErrorSemantico(ctx, "retornar solo puede ir dentro de una función.")
        valor = self.visit(ctx.flujo())
        if isinstance(valor, Columna) and self._tabla is None:
            valor = list(valor.valores)
        raise Retorno(valor)

    def _invocar(self, ctx, funcion: Funcion, args: list):
        if len(args) != len(funcion.parametros):
            raise ErrorSemantico(ctx, f"{funcion.nombre}() recibe {len(funcion.parametros)} argumentos "
                                      f"({', '.join(funcion.parametros) or 'ninguno'}) y le llegaron {len(args)}.")
        if self.simbolos.profundidad >= MAX_PROFUNDIDAD:
            raise ErrorSemantico(ctx, f"{funcion.nombre}() se llamó a sí misma más de {MAX_PROFUNDIDAD} "
                                      "veces seguidas; revisa que la recursión tenga un caso que la detenga.")
        # dentro de la funcion no se ven las columnas de la etapa que la llamo
        guardado = self._tabla, self._entrada
        self._tabla = self._entrada = None
        self.simbolos.entrar()
        try:
            for parametro, valor in zip(funcion.parametros, args):
                self.simbolos.definir(parametro, clase_de(valor), valor, ctx.start.line)
            self.visit(funcion.cuerpo)
            return None     # una funcion sin retornar devuelve nulo
        except Retorno as retorno:
            return retorno.valor
        finally:
            self.simbolos.salir()
            self._tabla, self._entrada = guardado

    def _como_python(self, ctx, funcion, nombre: str):
        """Envuelve una funcion del usuario para que la usen los metodos numericos."""
        if not isinstance(funcion, Funcion):
            raise ErrorSemantico(ctx, f"{nombre}() recibe primero una función, por ejemplo {nombre}(f, ...), "
                                      f"y llegó {describir(funcion)}.")

        def llamar(x):
            resultado = self._invocar(ctx, funcion, [x])
            if not es_numero(resultado):
                raise ErrorSemantico(ctx, f"{funcion.nombre}() tiene que devolver un número para "
                                          f"{nombre}() y devolvió {describir(resultado)}.")
            return resultado
        return llamar

    def _numerico(self, ctx, nombre, args):
        if nombre == "mapear":
            # aplica la funcion a cada elemento; con una columna devuelve otra columna
            if not isinstance(args[0], Funcion) or not isinstance(args[1], (list, Columna)):
                raise ValueError("va así: mapear(funcion, lista) o mapear(funcion, columna)")
            if isinstance(args[1], Columna):
                return Columna([None if x is None else self._invocar(ctx, args[0], [x])
                                for x in args[1].valores])
            return [self._invocar(ctx, args[0], [x]) for x in args[1]]
        f = self._como_python(ctx, args[0], nombre)
        self._exigir(ctx, nombre + "()", "numero", *args[1:])
        return getattr(matematica, nombre)(f, *args[1:])

    def visitBloque(self, ctx):
        for sentencia in ctx.sentencia():
            self.visit(sentencia)

    # --- Flujo y carga -------------------------------------------------------

    def visitFlujo(self, ctx):
        valor = self.visit(ctx.fuente())
        for etapa in ctx.etapa():
            self._entrada = valor
            valor = self.visit(etapa)
        if isinstance(valor, Agrupada):
            raise ErrorSemantico(ctx.etapa()[-1], "SQUAD arma los grupos pero no calcula nada, "
                                                  "después tiene que venir MAGI.")
        return valor

    def visitFuente(self, ctx):
        return self.visit(ctx.getChild(0))

    def visitCarga(self, ctx):
        ruta = quitar_comillas(ctx.CADENA().getText())
        opciones = self._opciones(ctx.opcion(), OPCIONES_CARGA)
        if not Path(ruta).is_file():
            raise ErrorSemantico(ctx.CADENA().symbol, f"no existe el archivo '{ruta}'.")
        try:
            return leer_csv(ruta, separador=opciones.get("separador", ","),
                            codificacion=opciones.get("codificacion", "utf-8"),
                            encabezado=opciones.get("encabezado", True) is not False)
        except (ValueError, LookupError, TypeError, OSError) as error:
            raise ErrorSemantico(ctx, f"no se pudo leer '{ruta}': {error}.")

    def _opciones(self, opciones, permitidas, tabla=None) -> dict:
        valores = {}
        for opcion in opciones:
            nombre = opcion.ID().getText()
            if nombre not in permitidas:
                raise ErrorSemantico(opcion, f"la opción '{nombre}' no existe." + sugerir(nombre, permitidas))
            valores[nombre] = self._evaluar_en(tabla, opcion.expresion())
        return valores

    # --- Etapas --------------------------------------------------------------

    def _tabla_de_entrada(self, ctx) -> Tabla:
        etapa = ctx.start.text
        if isinstance(self._entrada, Agrupada):
            raise ErrorSemantico(ctx, f"después de SQUAD tiene que venir MAGI, no {etapa}.")
        if not isinstance(self._entrada, Tabla):
            raise ErrorSemantico(ctx, f"{etapa} solo funciona sobre una tabla "
                                      f"y aquí llegó {describir(self._entrada)}.")
        return self._entrada

    def _columna(self, tabla, ctx) -> str:
        nombre = limpiar(ctx.getText())
        if nombre not in tabla.columnas:
            raise ErrorSemantico(ctx, f"la columna '{nombre}' no existe en la tabla."
                                 + sugerir(nombre, tabla.columnas))
        return nombre

    def _columnas(self, tabla, lista) -> list:
        return [self._columna(tabla, n) for n in lista.nombre()]

    def _evaluar_en(self, tabla, expresion):
        anterior, self._tabla = self._tabla, tabla
        try:
            return self.visit(expresion)
        finally:
            self._tabla = anterior

    def visitEtapaSeleccionar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas())
        self._sin_repetidas(ctx.listaColumnas(), columnas)
        return tabla.seleccionar(columnas)

    @staticmethod
    def _sin_repetidas(ctx, nombres) -> None:
        repetidas = [n for i, n in enumerate(nombres) if n in nombres[:i]]
        if repetidas:
            raise ErrorSemantico(ctx, f"la columna '{repetidas[0]}' está repetida en la lista.")

    def visitEtapaFiltrar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        condicion = self._evaluar_en(tabla, ctx.expresion())
        if not encaja(condicion, "booleano"):
            raise ErrorSemantico(ctx.expresion(), "la condición de AT_FIELD tiene que dar verdadero "
                                                  f"o falso, y dio {describir(condicion)}.")
        if isinstance(condicion, Columna):
            return tabla.filtrar(condicion)
        return tabla if condicion else tabla.primeras(0)

    def visitEtapaCrear(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        for nueva in ctx.columnaNueva():
            valor = self._evaluar_en(tabla, nueva.expresion())
            if isinstance(valor, Tabla):
                raise ErrorSemantico(nueva.expresion(), "una tabla no cabe dentro de una columna.")
            if isinstance(valor, list):
                # una lista con un valor por fila se vuelve la columna
                valor = Columna(valor)
            if isinstance(valor, Columna) and len(valor) != len(tabla):
                raise ErrorSemantico(nueva.expresion(), f"la columna nueva tiene {len(valor)} filas "
                                                        f"y la tabla tiene {len(tabla)}.")
            # la tabla se va actualizando para que una columna pueda usar la anterior
            tabla = tabla.con_columna(limpiar(nueva.nombre().getText()), valor)
        return tabla

    def visitEtapaRenombrar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        cambios = {}
        for renombre in ctx.renombre():
            viejo = self._columna(tabla, renombre.nombre(0))
            if viejo in cambios:
                raise ErrorSemantico(renombre.nombre(0), f"la columna '{viejo}' se renombra dos veces.")
            cambios[viejo] = limpiar(renombre.nombre(1).getText())
        # se mira como quedan todas juntas, asi [a -> b, b -> a] intercambia los nombres
        finales = [cambios.get(c, c) for c in tabla.columnas]
        for renombre in ctx.renombre():
            nuevo = limpiar(renombre.nombre(1).getText())
            if finales.count(nuevo) > 1:
                raise ErrorSemantico(renombre.nombre(1), f"quedarían dos columnas llamadas '{nuevo}'.")
        return tabla.renombrar(cambios)

    def visitEtapaOrdenar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = [self._columna(tabla, c.nombre()) for c in ctx.criterio()]
        ascendentes = [c.DESC() is None for c in ctx.criterio()]
        try:
            return tabla.ordenar(columnas, ascendentes)
        except TypeError:
            raise ErrorSemantico(ctx, "no se puede ordenar una columna que mezcla números y textos.")

    def visitEtapaQuitarDuplicados(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas()) if ctx.listaColumnas() else None
        return tabla.sin_duplicados(columnas)

    def visitEtapaQuitarFaltantes(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas()) if ctx.listaColumnas() else None
        return tabla.sin_faltantes(columnas)

    def visitEtapaQuitarColumnas(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas())
        if set(columnas) >= set(tabla.columnas):
            raise ErrorSemantico(ctx.listaColumnas(), "no se pueden quitar todas las columnas: "
                                                      "la tabla quedaría vacía.")
        return tabla.sin_columnas(columnas)

    def visitEtapaRellenar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        for relleno in ctx.columnaNueva():
            columna = self._columna(tabla, relleno.nombre())
            valor = self._evaluar_en(tabla, relleno.expresion())
            if isinstance(valor, (Columna, Tabla)) or valor is None:
                raise ErrorSemantico(relleno.expresion(), "el relleno de DUMMY_PLUG tiene que ser un solo valor.")
            # una columna vacia se puede rellenar con lo que sea
            if clase_de(tabla[columna]) not in (clase_de(valor), "nulo"):
                raise ErrorSemantico(relleno.expresion(),
                                     f"tipos incompatibles: '{columna}' es {describir(tabla[columna])} "
                                     f"y se quiso rellenar con {describir(valor)}.")
            tabla = tabla.con_columna(columna, tabla[columna].rellenar(valor))
        return tabla

    def visitEtapaConvertir(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columna = self._columna(tabla, ctx.nombre())
        tipo = ctx.ID().getText()
        if tipo not in TIPOS:
            raise ErrorSemantico(ctx.ID().symbol, f"el tipo '{tipo}' no existe." + sugerir(tipo, TIPOS))
        try:
            return tabla.con_columna(columna, tabla[columna].convertir(tipo))
        except (ValueError, TypeError, OverflowError):
            raise ErrorSemantico(ctx.nombre(), f"no se pudo convertir '{columna}' a {tipo}, "
                                               "hay valores que no encajan.")

    def visitEtapaAgrupar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        return Agrupada(tabla, self._columnas(tabla, ctx.listaColumnas()))

    def visitEtapaResumir(self, ctx):
        entrada = self._entrada
        if isinstance(entrada, Agrupada):
            tabla, claves = entrada.tabla, entrada.columnas
        elif isinstance(entrada, Tabla):
            tabla, claves = entrada, []
        else:
            raise ErrorSemantico(ctx, f"MAGI solo funciona sobre una tabla y aquí llegó {describir(entrada)}.")

        calculos = []   # (nombre, funcion, columna)
        for agregacion in ctx.agregacion():
            nombre = limpiar(agregacion.nombre(0).getText())
            funcion = agregacion.ID().getText()
            if funcion not in AGREGACIONES:
                raise ErrorSemantico(agregacion.ID().symbol, f"MAGI no conoce el cálculo '{funcion}'."
                                     + sugerir(funcion, AGREGACIONES))
            if nombre in claves or nombre in [c[0] for c in calculos]:
                raise ErrorSemantico(agregacion, f"ya hay una columna llamada '{nombre}' en el resumen.")

            if len(agregacion.nombre()) == 1:
                # sin columna solo tiene sentido contar las filas
                if funcion != "contar":
                    raise ErrorSemantico(agregacion, f"{funcion}() necesita el nombre de una columna.")
                calculos.append((nombre, funcion, None))
                continue

            columna = self._columna(tabla, agregacion.nombre(1))
            if funcion in SOLO_NUMEROS and not encaja(tabla[columna], "numero"):
                raise ErrorSemantico(agregacion.nombre(1),
                                     f"tipos incompatibles: {funcion}() necesita números "
                                     f"y '{columna}' es {describir(tabla[columna])}.")
            calculos.append((nombre, funcion, columna))

        return tabla.resumir(claves, calculos)

    def visitEtapaLimitar(self, ctx):
        return self._tabla_de_entrada(ctx).primeras(int(ctx.ENTERO().getText()))

    def visitEtapaDiagnostico(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        filas = []
        for nombre in tabla.columnas:
            columna = tabla[nombre]
            fila = {"columna": nombre, "clase": columna.clase(), "validos": columna.contar(),
                    "faltantes": columna.faltantes(), "distintos": columna.distintos()}
            if fila["clase"] == "numero":
                fila.update(media=columna.media(), desviacion=columna.desviacion(),
                            minimo=columna.minimo(), maximo=columna.maximo())
            filas.append(fila)
        return Tabla.de_registros(filas, ["columna", "clase", "validos", "faltantes", "distintos",
                                          "media", "desviacion", "minimo", "maximo"])

    def visitEtapaProfecia(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        objetivo = self._columna(tabla, ctx.nombre())
        predictoras = self._columnas(tabla, ctx.listaColumnas())
        for columna in predictoras:
            if not encaja(tabla[columna], "numero"):
                raise ErrorSemantico(ctx.listaColumnas(), "tipos incompatibles: PROFECIA necesita números en "
                                     f"las columnas predictoras y '{columna}' es {describir(tabla[columna])}.")
        if objetivo in predictoras:
            raise ErrorSemantico(ctx.nombre(), f"'{objetivo}' no puede ser a la vez el objetivo y una predictora.")

        k = int(ctx.ENTERO().getText())
        if k < 1:
            raise ErrorSemantico(ctx.ENTERO().symbol, "VECINOS necesita un número de al menos 1.")
        if k >= len(tabla):
            raise ErrorSemantico(ctx.ENTERO().symbol, f"VECINOS pide {k} pero la tabla solo tiene "
                                                       f"{len(tabla)} filas.")

        prediccion = tabla.predecir_knn(objetivo, predictoras, k)
        return tabla.con_columna(f"{objetivo}_prediccion", prediccion)

    # --- Expresiones ---------------------------------------------------------

    def _exigir(self, ctx, operador: str, clase: str, *valores) -> None:
        necesita = {"numero": "números", "booleano": "valores de verdadero/falso"}[clase]
        for valor in valores:
            if not encaja(valor, clase):
                raise ErrorSemantico(ctx, f"tipos incompatibles: '{operador}' necesita {necesita} "
                                          f"y recibió {describir(valor)}.")

    def _operandos(self, ctx):
        a, b = self.visit(ctx.expresion(0)), self.visit(ctx.expresion(1))
        if isinstance(a, Columna) and isinstance(b, Columna) and len(a) != len(b):
            raise ErrorSemantico(ctx, f"las dos columnas no tienen las mismas filas ({len(a)} y {len(b)}).")
        return a, b, ctx.getChild(1).getText()

    def visitExprParentesis(self, ctx):
        return self.visit(ctx.expresion())

    def visitExprLiteral(self, ctx):
        token = ctx.start
        if token.type == EvaParser.ENTERO:
            return int(token.text)
        if token.type == EvaParser.REAL:
            return float(token.text)
        if token.type == EvaParser.CADENA:
            return quitar_comillas(token.text)
        if token.type == EvaParser.NULO:
            return None
        return token.type == EvaParser.VERDADERO

    def visitExprNombre(self, ctx):
        nombre = limpiar(ctx.getText())
        # dentro de una etapa primero se busca entre las columnas de la tabla
        if self._tabla is not None and nombre in self._tabla.columnas:
            return self._tabla[nombre]
        simbolo = self.simbolos.buscar(nombre)
        if simbolo is not None:
            return simbolo.valor
        if nombre in CONSTANTES:
            return CONSTANTES[nombre]
        if self._tabla is not None:
            raise ErrorSemantico(ctx, f"'{nombre}' no es una columna de la tabla ni una variable."
                                 + sugerir(nombre, self._tabla.columnas))
        raise ErrorSemantico(ctx, f"la variable '{nombre}' no se ha declarado."
                             + sugerir(nombre, self.simbolos.nombres()))

    def visitExprColumnaDe(self, ctx):
        nombre = limpiar(ctx.nombre(0).getText())
        simbolo = self.simbolos.buscar(nombre)
        if simbolo is None:
            raise ErrorSemantico(ctx, f"la variable '{nombre}' no se ha declarado."
                                 + sugerir(nombre, self.simbolos.nombres()))
        if isinstance(simbolo.valor, dict):
            # modelo.r2 es lo mismo que modelo["r2"]
            return self._elemento(ctx.nombre(1), simbolo.valor, limpiar(ctx.nombre(1).getText()))
        if simbolo.clase != "tabla":
            raise ErrorSemantico(ctx, f"'{nombre}' es {describir(simbolo.valor)}, no tiene columnas.")
        return simbolo.valor[self._columna(simbolo.valor, ctx.nombre(1))]

    def visitExprIndice(self, ctx):
        contenedor = self.visit(ctx.expresion(0))
        return self._elemento(ctx.expresion(1), contenedor, self.visit(ctx.expresion(1)))

    def visitExprLista(self, ctx):
        return [self.visit(e) for e in ctx.expresion()]

    def visitExprDiccionario(self, ctx):
        diccionario = {}
        for par in ctx.par():
            clave = quitar_comillas(par.CADENA().getText()) if par.CADENA() else limpiar(par.nombre().getText())
            diccionario[clave] = self.visit(par.expresion())
        return diccionario

    def _posicion(self, ctx, lista, indice) -> int:
        """Las posiciones empiezan en 0; con negativos se cuenta desde el final (-1 es el ultimo)."""
        if not matematica.es_entero(indice):
            raise ErrorSemantico(ctx, f"la posición va con un número entero y llegó {describir(indice)}.")
        if not -len(lista) <= indice < len(lista):
            raise ErrorSemantico(ctx, f"la posición {indice} no existe: hay {len(lista)} "
                                      f"elementos (de 0 a {len(lista) - 1}).")
        return indice

    def _revisar_clave(self, ctx, clave) -> None:
        if not isinstance(clave, (str, int)) or isinstance(clave, bool):
            raise ErrorSemantico(ctx, f"las claves de un diccionario son textos o enteros y llegó {describir(clave)}.")

    def _elemento(self, ctx, contenedor, clave):
        if isinstance(contenedor, (list, str)):
            return contenedor[self._posicion(ctx, contenedor, clave)]
        if isinstance(contenedor, dict):
            self._revisar_clave(ctx, clave)
            if clave not in contenedor:
                raise ErrorSemantico(ctx, f"la clave '{clave}' no está en el diccionario."
                                     + sugerir(str(clave), contenedor))
            return contenedor[clave]
        if isinstance(contenedor, Tabla):
            if isinstance(clave, str):
                if clave not in contenedor.columnas:
                    raise ErrorSemantico(ctx, f"la columna '{clave}' no existe en la tabla."
                                         + sugerir(clave, contenedor.columnas))
                return list(contenedor[clave].valores)
            # tabla[0] es la primera fila, como un diccionario
            registros = contenedor.registros()
            return registros[self._posicion(ctx, registros, clave)]
        raise ErrorSemantico(ctx, f"con [ ] se sacan elementos de una lista, un diccionario, un texto "
                                  f"o una tabla, y aquí hay {describir(contenedor)}.")

    def _con_listas(self, ctx, a, b, operador):
        """Entre listas (o lista y numero) las cuentas se hacen elemento por elemento."""
        funciones = {"+": lambda x, y: x + y, "-": lambda x, y: x - y, "*": lambda x, y: x * y,
                     "/": lambda x, y: x / y, "%": lambda x, y: x % y, "^": lambda x, y: x ** y}
        try:
            return matrices.operar(a, b, funciones[operador])
        except ZeroDivisionError:
            raise ErrorSemantico(ctx, "no se puede dividir por cero.")
        except (ValueError, TypeError) as error:
            raise ErrorSemantico(ctx, f"'{operador}' entre listas: {error}.")

    def visitExprPotencia(self, ctx):
        a, b, _ = self._operandos(ctx)
        if isinstance(a, list) or isinstance(b, list):
            return self._con_listas(ctx, a, b, "^")
        self._exigir(ctx, "^", "numero", a, b)
        if isinstance(a, Columna) or isinstance(b, Columna):
            return a ** b
        try:
            resultado = a ** b
        except ZeroDivisionError:
            raise ErrorSemantico(ctx, "cero elevado a un número negativo es una división por cero.")
        except OverflowError:
            raise ErrorSemantico(ctx, "el resultado de la potencia es demasiado grande.")
        # Python devuelve un numero complejo, pero el lenguaje solo maneja reales
        if isinstance(resultado, complex):
            raise ErrorSemantico(ctx, "un número negativo no se puede elevar a una potencia con decimales.")
        return resultado

    def visitExprNegativo(self, ctx):
        valor = self.visit(ctx.expresion())
        if isinstance(valor, list):
            return self._con_listas(ctx, valor, -1, "*")
        self._exigir(ctx, "-", "numero", valor)
        return -valor

    def visitExprMultiplicativa(self, ctx):
        a, b, operador = self._operandos(ctx)
        if isinstance(a, list) or isinstance(b, list):
            return self._con_listas(ctx, a, b, operador)
        self._exigir(ctx, operador, "numero", a, b)
        if operador == "*":
            return a * b
        if not isinstance(b, Columna) and b == 0:
            raise ErrorSemantico(ctx.expresion(1), "no se puede dividir por cero.")
        return a / b if operador == "/" else a % b

    def visitExprAditiva(self, ctx):
        a, b, operador = self._operandos(ctx)
        # el + tambien sirve para pegar textos
        if operador == "+" and "texto" in (clase_de(a), clase_de(b)) and encaja(a, "texto") and encaja(b, "texto"):
            return a + b
        if isinstance(a, list) or isinstance(b, list):
            return self._con_listas(ctx, a, b, operador)
        self._exigir(ctx, operador, "numero", a, b)
        return a + b if operador == "+" else a - b

    def visitExprRelacional(self, ctx):
        a, b, operador = self._operandos(ctx)
        if not any(encaja(a, clase) and encaja(b, clase) for clase in ("numero", "texto")):
            raise ErrorSemantico(ctx, f"tipos incompatibles: no se puede comparar {describir(a)} "
                                      f"con {describir(b)} usando '{operador}'.")
        return COMPARADORES[operador](a, b)

    def visitExprIgualdad(self, ctx):
        a, b, operador = self._operandos(ctx)
        if a is None or b is None:
            # comparar con nulo es preguntar si el dato falta
            otro = b if a is None else a
            if isinstance(otro, Columna):
                return otro.es_nulo() if operador == "==" else ~otro.es_nulo()
            return (otro is None) == (operador == "==")
        if not encaja(a, clase_de(b)) and not encaja(b, clase_de(a)) or "tabla" in (clase_de(a), clase_de(b)):
            raise ErrorSemantico(ctx, f"tipos incompatibles: no se puede comparar {describir(a)} "
                                      f"con {describir(b)} usando '{operador}'.")
        return a == b if operador == "==" else a != b

    def visitExprNo(self, ctx):
        valor = self.visit(ctx.expresion())
        self._exigir(ctx, "no", "booleano", valor)
        return ~valor if isinstance(valor, Columna) else not valor

    def visitExprY(self, ctx):
        a, b, _ = self._operandos(ctx)
        self._exigir(ctx, "y", "booleano", a, b)
        return a & b

    def visitExprO(self, ctx):
        a, b, _ = self._operandos(ctx)
        self._exigir(ctx, "o", "booleano", a, b)
        return a | b

    def visitExprLlamada(self, ctx):
        if ctx.ID().getText() in SIN_RESULTADO:
            raise ErrorSemantico(ctx, f"{ctx.ID().getText()}() cambia algo pero no devuelve nada; "
                                      "va sola en su línea.")
        return self._llamada(ctx)

    def _llamada(self, ctx):
        nombre = ctx.ID().getText()
        args = [self.visit(e) for e in ctx.expresion()]

        simbolo = self.simbolos.buscar(nombre)
        if simbolo is not None and isinstance(simbolo.valor, Funcion):
            return self._invocar(ctx, simbolo.valor, args)

        if nombre in AGREGACIONES:
            if len(args) == 1 and isinstance(args[0], list):
                args = [Columna(args[0])]    # una lista se resume igual que una columna
            if len(args) != 1 or not isinstance(args[0], Columna):
                raise ErrorSemantico(ctx, f"{nombre}() necesita una columna o una lista, "
                                          f"por ejemplo {nombre}(tabla.columna).")
            if nombre in SOLO_NUMEROS and not encaja(args[0], "numero"):
                raise ErrorSemantico(ctx, f"tipos incompatibles: {nombre}() necesita números "
                                          f"y recibió {describir(args[0])}.")
            try:
                return getattr(args[0], nombre)()
            except TypeError:
                raise ErrorSemantico(ctx, f"{nombre}() no puede comparar números con textos; "
                                          "los valores tienen que ser todos del mismo tipo.")

        if nombre not in TODAS:
            raise ErrorSemantico(ctx, f"la función '{nombre}' no existe."
                                 + sugerir(nombre, [*TODAS, *AGREGACIONES]))
        minimo, maximo = TODAS[nombre]
        if not minimo <= len(args) <= maximo:
            cuantos = str(minimo) if minimo == maximo else f"entre {minimo} y {maximo}"
            raise ErrorSemantico(ctx, f"{nombre}() recibe {cuantos} argumentos y le llegaron {len(args)}.")
        try:
            if nombre in MATEMATICAS:
                return self._matematica(ctx, nombre, args)
            if nombre in LISTAS:
                return self._lista(ctx, nombre, args)
            if nombre in MATRICES:
                return getattr(matrices, nombre)(*args)
            if nombre in MODELOS:
                return self._modelo(nombre, args)
            if nombre in NUMERICOS:
                return self._numerico(ctx, nombre, args)
        except (ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
            raise ErrorSemantico(ctx, f"{nombre}(): {error}.")
        return self._llamar(ctx, nombre, args)

    def _matematica(self, ctx, nombre, args):
        funcion = MATEMATICAS[nombre]
        valor, extra = args[0], args[1:]
        self._exigir(ctx, nombre + "()", "numero", *extra)
        if isinstance(valor, list):
            return matrices.cada(valor, lambda v: funcion(v, *extra))
        self._exigir(ctx, nombre + "()", "numero", valor)
        if isinstance(valor, Columna):
            def segura(v):
                # en una columna un calculo imposible deja el dato como faltante
                try:
                    return funcion(v, *extra)
                except (ValueError, OverflowError, ZeroDivisionError):
                    return None
            return valor._cada(segura)
        return funcion(valor, *extra)

    def _lista(self, ctx, nombre, args):
        primero = args[0] if args else None
        if nombre == "longitud":
            if isinstance(primero, (list, dict, str, Tabla, Columna)):
                return len(primero)
            raise ValueError(f"necesita una lista, un diccionario, un texto o una tabla y llegó {describir(primero)}")
        if nombre == "aleatorio":
            if not args:
                return self.azar.siguiente()
            if len(args) == 2 and all(matematica.es_entero(a) for a in args) and args[0] <= args[1]:
                return self.azar.entero(args[0], args[1])
            raise ValueError("va sin nada (un número entre 0 y 1) o con dos enteros, como aleatorio(1, 6)")
        if nombre == "semilla":
            if not matematica.es_entero(primero):
                raise ValueError("la semilla es un número entero")
            self.azar = matematica.Aleatorio(primero)
            return None
        if nombre == "rango":
            if not all(matematica.es_entero(a) for a in args):
                raise ValueError("va con números enteros")
            desde, hasta = (1, args[0]) if len(args) == 1 else (args[0], args[1])
            paso = args[2] if len(args) == 3 else 1
            if paso == 0:
                raise ValueError("el paso no puede ser 0")
            if (hasta - desde) / paso > MAX_VUELTAS:
                raise ValueError(f"la lista tendría más de {MAX_VUELTAS} números")
            return list(range(desde, hasta + (1 if paso > 0 else -1), paso))
        if nombre == "texto":
            return texto_de(primero)
        if nombre == "numero":
            return self._a_numero(primero)
        if nombre == "tabla_de":
            if (not isinstance(primero, dict) or not primero
                    or not all(isinstance(v, list) for v in primero.values())
                    or len({len(v) for v in primero.values()}) != 1):
                raise ValueError("necesita un diccionario de listas del mismo largo, "
                                 'por ejemplo tabla_de({"x": [1, 2], "y": [3, 4]})')
            return Tabla([str(c) for c in primero], {str(c): v for c, v in primero.items()})
        if nombre == "columna":
            if not isinstance(primero, Tabla) or not isinstance(args[1], str):
                raise ValueError('va así: columna(tabla, "nombre")')
            if args[1] not in primero.columnas:
                raise ValueError(f"la columna '{args[1]}' no existe en la tabla")
            return list(primero[args[1]].valores)
        if nombre in ("claves", "valores"):
            if not isinstance(primero, dict):
                raise ValueError(f"necesita un diccionario y llegó {describir(primero)}")
            return list(primero.keys() if nombre == "claves" else primero.values())
        if nombre == "contiene":
            if isinstance(primero, str) and isinstance(args[1], str) or isinstance(primero, (list, dict)):
                return args[1] in primero
            raise ValueError("busca dentro de una lista, un diccionario o un texto")
        if not isinstance(primero, list):
            raise ValueError(f"necesita una lista y llegó {describir(primero)}")
        if nombre == "agregar":
            primero.append(args[1])
            return None
        if nombre == "sacar":
            if not primero:
                raise ValueError("la lista está vacía")
            return primero.pop(self._posicion(ctx, primero, args[1] if len(args) == 2 else -1))
        if nombre == "ordenada":
            try:
                return sorted(primero)
            except TypeError:
                raise ValueError("no se puede ordenar una lista que mezcla tipos (números con textos, "
                                 "listas o nulos)")
        if nombre == "invertida":
            return primero[::-1]
        if not isinstance(args[1], list):
            raise ValueError("une dos listas")
        return primero + args[1]   # unir

    @staticmethod
    def _a_numero(valor):
        if es_numero(valor):
            return valor
        if isinstance(valor, str):
            texto = valor.strip()
            if re.fullmatch(r"[+-]?\d+", texto):
                return int(texto)
            if re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)", texto):
                return float(texto)
        raise ValueError(f"no se pudo convertir {texto_de(valor, True)} en número")

    def _modelo(self, nombre, args):
        if nombre in CON_TABLA and not isinstance(args[0], Tabla):
            raise ValueError(f"el primer argumento tiene que ser una tabla y llegó {describir(args[0])}")
        return getattr(aprendizaje, nombre)(*args)

    def _llamar(self, ctx, nombre, args):
        valor = args[0]
        if nombre == "filas":
            if not isinstance(valor, Tabla):
                raise ErrorSemantico(ctx, f"filas() necesita una tabla y recibió {describir(valor)}.")
            return len(valor)

        if nombre in ("redondear", "absoluto"):
            decimales = args[1] if len(args) == 2 else 0
            if not matematica.es_entero(decimales):
                raise ErrorSemantico(ctx, "los decimales de redondear() van como un número entero.")
            if isinstance(valor, list):
                funcion = matematica.absoluto if nombre == "absoluto" else lambda v: round(v, decimales)
                try:
                    return matrices.cada(valor, funcion)
                except TypeError:
                    raise ErrorSemantico(ctx, f"{nombre}() con una lista necesita que todo sean números.")
            self._exigir(ctx, nombre + "()", "numero", *args)
            if nombre == "absoluto":
                return abs(valor)
            return valor.redondear(decimales) if isinstance(valor, Columna) else round(valor, decimales)

        if not encaja(valor, "texto"):
            raise ErrorSemantico(ctx, f"{nombre}() necesita texto y recibió {describir(valor)}.")
        if nombre == "reemplazar":
            viejo, nuevo = args[1], args[2]
            if not isinstance(viejo, str) or not isinstance(nuevo, str):
                raise ErrorSemantico(ctx, 'reemplazar() va así: reemplazar(columna, "texto viejo", "texto nuevo").')
            return valor.reemplazar(viejo, nuevo) if isinstance(valor, Columna) else valor.replace(viejo, nuevo)
        if isinstance(valor, Columna):
            return valor.mayusculas() if nombre == "mayusculas" else valor.minusculas()
        return valor.upper() if nombre == "mayusculas" else valor.lower()
