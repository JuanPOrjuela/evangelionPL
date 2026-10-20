"""Fase 2: el Visitor recorre el arbol y ejecuta el programa con nuestra libreria de tablas."""

import operator
import re
from dataclasses import dataclass
from pathlib import Path

from . import graficas
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
TIPOS = ("entero", "real", "texto", "booleano")
GRAFICAS = graficas.TIPOS
OPCIONES_CARGA = ("separador", "codificacion", "encabezado")
OPCIONES_GRAFICA = ("eje_x", "eje_y", "serie", "titulo", "etiqueta_x", "etiqueta_y", "archivo",
                    "color", "intervalos", "ancho", "alto", "leyenda")
EJES = ("eje_x", "eje_y", "serie")
TEXTOS_GRAFICA = ("titulo", "etiqueta_x", "etiqueta_y", "archivo", "color")
ENTEROS_GRAFICA = {"intervalos": (1, 200), "ancho": (320, 4000), "alto": (240, 4000)}
COMPARADORES = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
FILAS_EN_PANTALLA = 12


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
            "texto": "un texto", "booleano": "un booleano", "nulo": "nulo"}[clase]


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


def texto_de(valor) -> str:
    if valor is None:
        return "nulo"
    if isinstance(valor, bool):
        return "verdadero" if valor else "falso"
    if isinstance(valor, float):
        return str(round(valor, 4))
    return str(valor)


class Interprete(EvaVisitor):

    def __init__(self):
        self.simbolos = TablaSimbolos()
        self.operacion = ""
        self.reportes = []       # archivos que escribio SEELE
        self.graficas = []       # archivos que dibujo HOLOGRAM
        self._entrada = None     # lo que recibe la etapa que se esta ejecutando
        self._tabla = None       # tabla cuyas columnas se pueden nombrar ahora

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
                                              "Usa TARGET para sacar una tabla con esa columna.")
        self.simbolos.definir(nombre, clase_de(valor), valor, ctx.start.line)

    def visitMostrar(self, ctx):
        valor = self.visit(ctx.flujo())
        if isinstance(valor, Columna):
            nombre = valor.nombre or "columna"
            valor = Tabla([nombre], {nombre: valor.valores})
        # si el flujo es solo un nombre lo usamos de titulo
        texto = ctx.flujo().getText()
        titulo = " " + texto if re.fullmatch(r"[^\W\d]\w*", texto) else ""
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

    def visitCondicional(self, ctx):
        condicion = self.visit(ctx.expresion())
        if not isinstance(condicion, bool):
            raise ErrorSemantico(ctx.expresion(), "la condición de PATTERN_BLUE tiene que dar verdadero "
                                                  f"o falso, y dio {describir(condicion)}.")
        if condicion:
            self.visit(ctx.bloque(0))
        elif ctx.PATTERN_ORANGE():
            self.visit(ctx.bloque(1))

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
        return tabla.seleccionar(self._columnas(tabla, ctx.listaColumnas()))

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
            nuevo = limpiar(renombre.nombre(1).getText())
            if nuevo in tabla.columnas and nuevo != viejo:
                raise ErrorSemantico(renombre.nombre(1), f"ya hay una columna llamada '{nuevo}'.")
            cambios[viejo] = nuevo
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
        return tabla.sin_columnas(self._columnas(tabla, ctx.listaColumnas()))

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
        if simbolo.clase != "tabla":
            raise ErrorSemantico(ctx, f"'{nombre}' es {describir(simbolo.valor)}, no tiene columnas.")
        return simbolo.valor[self._columna(simbolo.valor, ctx.nombre(1))]

    def visitExprPotencia(self, ctx):
        a, b, _ = self._operandos(ctx)
        self._exigir(ctx, "^", "numero", a, b)
        return a ** b

    def visitExprNegativo(self, ctx):
        valor = self.visit(ctx.expresion())
        self._exigir(ctx, "-", "numero", valor)
        return -valor

    def visitExprMultiplicativa(self, ctx):
        a, b, operador = self._operandos(ctx)
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
        if not encaja(a, clase_de(b)) and not encaja(b, clase_de(a)) or clase_de(a) == "tabla":
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
        nombre = ctx.ID().getText()
        args = [self.visit(e) for e in ctx.expresion()]

        if nombre in AGREGACIONES:
            if len(args) != 1 or not isinstance(args[0], Columna):
                raise ErrorSemantico(ctx, f"{nombre}() necesita una columna, "
                                          f"por ejemplo {nombre}(tabla.columna).")
            if nombre in SOLO_NUMEROS and not encaja(args[0], "numero"):
                raise ErrorSemantico(ctx, f"tipos incompatibles: {nombre}() necesita números "
                                          f"y recibió {describir(args[0])}.")
            return getattr(args[0], nombre)()

        if nombre not in FUNCIONES:
            raise ErrorSemantico(ctx, f"la función '{nombre}' no existe."
                                 + sugerir(nombre, [*FUNCIONES, *AGREGACIONES]))
        minimo, maximo = FUNCIONES[nombre]
        if not minimo <= len(args) <= maximo:
            raise ErrorSemantico(ctx, f"{nombre}() recibió {len(args)} argumentos y no es lo que espera.")
        return self._llamar(ctx, nombre, args)

    def _llamar(self, ctx, nombre, args):
        valor = args[0]
        if nombre == "filas":
            if not isinstance(valor, Tabla):
                raise ErrorSemantico(ctx, f"filas() necesita una tabla y recibió {describir(valor)}.")
            return len(valor)

        if nombre in ("redondear", "absoluto"):
            self._exigir(ctx, nombre + "()", "numero", *args)
            if nombre == "absoluto":
                return abs(valor)
            decimales = args[1] if len(args) == 2 else 0
            if not isinstance(decimales, int):
                raise ErrorSemantico(ctx, "los decimales de redondear() van como un número entero.")
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
