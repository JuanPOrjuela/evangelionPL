"""Fase 2: el Visitor recorre el arbol y ejecuta el programa con pandas."""

import difflib
import operator
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .errores import ErrorSemantico
from .generado.EvaParser import EvaParser
from .generado.EvaVisitor import EvaVisitor
from .simbolos import TablaSimbolos

AGREGACIONES = {
    "suma": "sum", "media": "mean", "mediana": "median", "minimo": "min",
    "maximo": "max", "desviacion": "std", "contar": "count",
}
SOLO_NUMEROS = {"suma", "media", "mediana", "desviacion"}
FUNCIONES = {"filas": (1, 1), "redondear": (1, 2), "absoluto": (1, 1),
             "mayusculas": (1, 1), "minusculas": (1, 1)}
TIPOS = ("entero", "real", "texto", "booleano")
GRAFICAS = ("barras", "lineas", "histograma", "dispersion", "caja")
OPCIONES_CARGA = ("separador", "codificacion", "encabezado")
OPCIONES_GRAFICA = ("eje_x", "eje_y", "titulo", "archivo")
COMPARADORES = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
FILAS_EN_PANTALLA = 12


@dataclass
class Agrupada:
    """Lo que deja SQUAD: una tabla con sus grupos, esperando a MAGI."""
    tabla: pd.DataFrame
    columnas: list


def clase_de(valor) -> str:
    if isinstance(valor, pd.DataFrame):
        return "tabla"
    if isinstance(valor, Agrupada):
        return "grupo"
    if isinstance(valor, pd.Series):
        if pd.api.types.is_bool_dtype(valor):
            return "booleano"
        return "numero" if pd.api.types.is_numeric_dtype(valor) else "texto"
    if valor is None:
        return "nulo"
    if isinstance(valor, (bool, np.bool_)):
        return "booleano"
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return "numero"
    return "texto"


def describir(valor) -> str:
    clase = clase_de(valor)
    if isinstance(valor, pd.Series):
        return {"numero": "una columna de números", "texto": "una columna de texto",
                "booleano": "una columna de verdadero/falso"}[clase]
    return {"tabla": "una tabla", "grupo": "una tabla agrupada", "numero": "un número",
            "texto": "un texto", "booleano": "un booleano", "nulo": "nulo"}[clase]


def limpiar(nombre: str) -> str:
    """`Tipo de EVA` -> Tipo de EVA"""
    return nombre.strip("`")


def quitar_comillas(crudo: str) -> str:
    escapes = {"n": "\n", "t": "\t"}
    return re.sub(r'\\(["\\nt])', lambda m: escapes.get(m.group(1), m.group(1)), crudo[1:-1])


def sugerir(nombre: str, opciones) -> str:
    opciones = [str(o) for o in opciones]
    parecidas = difflib.get_close_matches(nombre, opciones, n=1)
    if parecidas:
        return f" ¿Quisiste decir '{parecidas[0]}'?"
    if opciones:
        return " Las que hay son: " + ", ".join(opciones[:10]) + "."
    return ""


def escalar(valor):
    """numpy devuelve sus propios tipos, los pasamos a los de Python."""
    return valor.item() if hasattr(valor, "item") else valor


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
        self.graficas = []       # graficas revisadas, se dibujan en la fase 3
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
        if isinstance(valor, pd.Series):
            raise ErrorSemantico(ctx.flujo(), "una columna suelta no se puede guardar en una variable. "
                                              "Usa TARGET para sacar una tabla con esa columna.")
        self.simbolos.definir(nombre, clase_de(valor), valor, ctx.start.line)

    def visitMostrar(self, ctx):
        valor = self.visit(ctx.flujo())
        if isinstance(valor, pd.Series):
            valor = valor.to_frame()
        # si el flujo es solo un nombre lo usamos de titulo
        texto = ctx.flujo().getText()
        titulo = " " + texto if re.fullmatch(r"[^\W\d]\w*", texto) else ""
        if not isinstance(valor, pd.DataFrame):
            print(f"MONITOR{titulo}: {texto_de(valor)}\n")
            return
        filas, columnas = valor.shape
        print(f"MONITOR{titulo} ({filas} {'fila' if filas == 1 else 'filas'} x {columnas} columnas)")
        print(valor.head(FILAS_EN_PANTALLA).to_string(
            index=False, na_rep="nulo", float_format=lambda x: f"{x:.2f}"))
        if filas > FILAS_EN_PANTALLA:
            print(f"... y {filas - FILAS_EN_PANTALLA} filas más")
        print()

    def visitGuardar(self, ctx):
        valor = self.visit(ctx.flujo())
        if not isinstance(valor, pd.DataFrame):
            raise ErrorSemantico(ctx.flujo(), f"SEELE solo recibe tablas y aquí llegó {describir(valor)}.")
        ruta = Path(quitar_comillas(ctx.CADENA().getText()))
        if ruta.suffix.lower() != ".csv":
            raise ErrorSemantico(ctx.CADENA().symbol, "por ahora los reportes solo se guardan en .csv.")
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            valor.round(4).to_csv(ruta, index=False, encoding="utf-8")
        except OSError as error:
            raise ErrorSemantico(ctx.CADENA().symbol, f"no se pudo escribir '{ruta}': {error}.")
        self.reportes.append(ruta.as_posix())
        print(f"SEELE recibió el reporte {ruta.as_posix()} ({len(valor)} filas)\n")

    def visitGraficar(self, ctx):
        tipo = ctx.ID().getText()
        if tipo not in GRAFICAS:
            raise ErrorSemantico(ctx.ID().symbol, f"no existe la gráfica '{tipo}'." + sugerir(tipo, GRAFICAS))
        tabla = self.visit(ctx.flujo())
        if not isinstance(tabla, pd.DataFrame):
            raise ErrorSemantico(ctx.flujo(), f"HOLOGRAM necesita una tabla y aquí llegó {describir(tabla)}.")
        # los ejes nombran columnas, por eso las opciones se evaluan dentro de la tabla
        self._opciones(ctx.opcion(), OPCIONES_GRAFICA, tabla)
        self.graficas.append(tipo)
        print(f"HOLOGRAM: gráfica de {tipo} revisada, el dibujo queda para la fase 3\n")

    def visitCondicional(self, ctx):
        condicion = self.visit(ctx.expresion())
        if clase_de(condicion) != "booleano" or isinstance(condicion, pd.Series):
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
        con_encabezado = opciones.get("encabezado", True)
        try:
            tabla = pd.read_csv(ruta, sep=opciones.get("separador", ","),
                                encoding=opciones.get("codificacion", "utf-8"),
                                header=0 if con_encabezado else None)
        except (ValueError, LookupError, TypeError) as error:
            raise ErrorSemantico(ctx, f"no se pudo leer '{ruta}': {error}.")
        if not con_encabezado:
            tabla.columns = [f"col{i + 1}" for i in range(len(tabla.columns))]
        return tabla

    def _opciones(self, opciones, permitidas, tabla=None) -> dict:
        valores = {}
        for opcion in opciones:
            nombre = opcion.ID().getText()
            if nombre not in permitidas:
                raise ErrorSemantico(opcion, f"la opción '{nombre}' no existe." + sugerir(nombre, permitidas))
            valores[nombre] = self._evaluar_en(tabla, opcion.expresion())
        return valores

    # --- Etapas --------------------------------------------------------------

    def _tabla_de_entrada(self, ctx) -> pd.DataFrame:
        etapa = ctx.start.text
        if isinstance(self._entrada, Agrupada):
            raise ErrorSemantico(ctx, f"después de SQUAD tiene que venir MAGI, no {etapa}.")
        if not isinstance(self._entrada, pd.DataFrame):
            raise ErrorSemantico(ctx, f"{etapa} solo funciona sobre una tabla "
                                      f"y aquí llegó {describir(self._entrada)}.")
        return self._entrada

    def _columna(self, tabla, ctx) -> str:
        nombre = limpiar(ctx.getText())
        if nombre not in tabla.columns:
            raise ErrorSemantico(ctx, f"la columna '{nombre}' no existe en la tabla."
                                 + sugerir(nombre, tabla.columns))
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
        return tabla[self._columnas(tabla, ctx.listaColumnas())]

    def visitEtapaFiltrar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        condicion = self._evaluar_en(tabla, ctx.expresion())
        if clase_de(condicion) != "booleano":
            raise ErrorSemantico(ctx.expresion(), "la condición de AT_FIELD tiene que dar verdadero "
                                                  f"o falso, y dio {describir(condicion)}.")
        if isinstance(condicion, pd.Series):
            return tabla[condicion].reset_index(drop=True)
        return tabla if condicion else tabla.iloc[0:0]

    def visitEtapaCrear(self, ctx):
        tabla = self._tabla_de_entrada(ctx).copy()
        for nueva in ctx.columnaNueva():
            valor = self._evaluar_en(tabla, nueva.expresion())
            if isinstance(valor, pd.DataFrame):
                raise ErrorSemantico(nueva.expresion(), "una tabla no cabe dentro de una columna.")
            tabla[limpiar(nueva.nombre().getText())] = valor
        return tabla

    def visitEtapaRenombrar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        cambios = {}
        for renombre in ctx.renombre():
            viejo = self._columna(tabla, renombre.nombre(0))
            nuevo = limpiar(renombre.nombre(1).getText())
            if nuevo in tabla.columns and nuevo != viejo:
                raise ErrorSemantico(renombre.nombre(1), f"ya hay una columna llamada '{nuevo}'.")
            cambios[viejo] = nuevo
        return tabla.rename(columns=cambios)

    def visitEtapaOrdenar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = [self._columna(tabla, c.nombre()) for c in ctx.criterio()]
        ascendente = [c.DESC() is None for c in ctx.criterio()]
        return tabla.sort_values(columnas, ascending=ascendente, kind="stable").reset_index(drop=True)

    def visitEtapaQuitarDuplicados(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas()) if ctx.listaColumnas() else None
        return tabla.drop_duplicates(subset=columnas).reset_index(drop=True)

    def visitEtapaQuitarFaltantes(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        columnas = self._columnas(tabla, ctx.listaColumnas()) if ctx.listaColumnas() else None
        return tabla.dropna(subset=columnas).reset_index(drop=True)

    def visitEtapaQuitarColumnas(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        return tabla.drop(columns=self._columnas(tabla, ctx.listaColumnas()))

    def visitEtapaRellenar(self, ctx):
        tabla = self._tabla_de_entrada(ctx).copy()
        for relleno in ctx.columnaNueva():
            columna = self._columna(tabla, relleno.nombre())
            valor = self._evaluar_en(tabla, relleno.expresion())
            if isinstance(valor, (pd.Series, pd.DataFrame)) or valor is None:
                raise ErrorSemantico(relleno.expresion(), "el relleno de DUMMY_PLUG tiene que ser un solo valor.")
            if clase_de(valor) != clase_de(tabla[columna]):
                raise ErrorSemantico(relleno.expresion(),
                                     f"tipos incompatibles: '{columna}' es {describir(tabla[columna])} "
                                     f"y se quiso rellenar con {describir(valor)}.")
            tabla[columna] = tabla[columna].fillna(valor)
        return tabla

    def visitEtapaConvertir(self, ctx):
        tabla = self._tabla_de_entrada(ctx).copy()
        columna = self._columna(tabla, ctx.nombre())
        tipo = ctx.ID().getText()
        if tipo not in TIPOS:
            raise ErrorSemantico(ctx.ID().symbol, f"el tipo '{tipo}' no existe." + sugerir(tipo, TIPOS))
        serie = tabla[columna]
        if tipo in ("entero", "booleano") and serie.isna().any():
            raise ErrorSemantico(ctx.nombre(), f"'{columna}' tiene faltantes y así no se puede pasar "
                                               f"a {tipo}. Rellénalos antes con DUMMY_PLUG.")
        try:
            tabla[columna] = self._convertir(serie, tipo)
        except (ValueError, TypeError):
            raise ErrorSemantico(ctx.nombre(), f"no se pudo convertir '{columna}' a {tipo}, "
                                               "hay valores que no encajan.")
        return tabla

    @staticmethod
    def _convertir(serie, tipo):
        if tipo == "entero":
            return pd.to_numeric(serie).astype("int64")
        if tipo == "real":
            return pd.to_numeric(serie).astype("float64")
        if tipo == "texto":
            return serie.map(lambda v: v if pd.isna(v) else str(v))
        if clase_de(serie) == "numero":
            return serie != 0
        palabras = {"verdadero": True, "si": True, "true": True, "falso": False, "no": False, "false": False}
        convertida = serie.astype(str).str.lower().map(palabras)
        if convertida.isna().any():
            raise ValueError
        return convertida.astype(bool)

    def visitEtapaAgrupar(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        return Agrupada(tabla, self._columnas(tabla, ctx.listaColumnas()))

    def visitEtapaResumir(self, ctx):
        entrada = self._entrada
        if isinstance(entrada, Agrupada):
            tabla, claves = entrada.tabla, entrada.columnas
        elif isinstance(entrada, pd.DataFrame):
            tabla, claves = entrada, []
        else:
            raise ErrorSemantico(ctx, f"MAGI solo funciona sobre una tabla y aquí llegó {describir(entrada)}.")

        grupos = tabla.groupby(claves, dropna=False) if claves else None
        resultado = {}
        for agregacion in ctx.agregacion():
            nombre = limpiar(agregacion.nombre(0).getText())
            funcion = agregacion.ID().getText()
            if funcion not in AGREGACIONES:
                raise ErrorSemantico(agregacion.ID().symbol, f"MAGI no conoce el cálculo '{funcion}'."
                                     + sugerir(funcion, AGREGACIONES))
            if nombre in claves or nombre in resultado:
                raise ErrorSemantico(agregacion, f"ya hay una columna llamada '{nombre}' en el resumen.")

            if len(agregacion.nombre()) == 1:
                # sin columna solo tiene sentido contar las filas
                if funcion != "contar":
                    raise ErrorSemantico(agregacion, f"{funcion}() necesita el nombre de una columna.")
                resultado[nombre] = grupos.size() if grupos is not None else len(tabla)
                continue

            columna = self._columna(tabla, agregacion.nombre(1))
            if funcion in SOLO_NUMEROS and clase_de(tabla[columna]) != "numero":
                raise ErrorSemantico(agregacion.nombre(1),
                                     f"tipos incompatibles: {funcion}() necesita números "
                                     f"y '{columna}' es {describir(tabla[columna])}.")
            origen = grupos[columna] if grupos is not None else tabla[columna]
            resultado[nombre] = getattr(origen, AGREGACIONES[funcion])()

        if grupos is None:
            return pd.DataFrame([resultado])
        return pd.DataFrame(resultado).reset_index()

    def visitEtapaLimitar(self, ctx):
        return self._tabla_de_entrada(ctx).head(int(ctx.ENTERO().getText()))

    def visitEtapaDiagnostico(self, ctx):
        tabla = self._tabla_de_entrada(ctx)
        filas = []
        for columna in tabla.columns:
            serie = tabla[columna]
            fila = {"columna": columna, "clase": clase_de(serie), "validos": serie.count(),
                    "faltantes": serie.isna().sum(), "distintos": serie.nunique()}
            if fila["clase"] == "numero":
                fila.update(media=serie.mean(), desviacion=serie.std(),
                            minimo=serie.min(), maximo=serie.max())
            filas.append(fila)
        return pd.DataFrame(filas, columns=["columna", "clase", "validos", "faltantes", "distintos",
                                            "media", "desviacion", "minimo", "maximo"])

    # --- Expresiones ---------------------------------------------------------

    def _exigir(self, ctx, operador: str, clase: str, *valores) -> None:
        necesita = {"numero": "números", "booleano": "valores de verdadero/falso"}[clase]
        for valor in valores:
            if clase_de(valor) != clase:
                raise ErrorSemantico(ctx, f"tipos incompatibles: '{operador}' necesita {necesita} "
                                          f"y recibió {describir(valor)}.")

    def _operandos(self, ctx):
        return self.visit(ctx.expresion(0)), self.visit(ctx.expresion(1)), ctx.getChild(1).getText()

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
        if self._tabla is not None and nombre in self._tabla.columns:
            return self._tabla[nombre]
        simbolo = self.simbolos.buscar(nombre)
        if simbolo is not None:
            return simbolo.valor
        if self._tabla is not None:
            raise ErrorSemantico(ctx, f"'{nombre}' no es una columna de la tabla ni una variable."
                                 + sugerir(nombre, self._tabla.columns))
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
        if not isinstance(b, pd.Series) and b == 0:
            raise ErrorSemantico(ctx.expresion(1), "no se puede dividir por cero.")
        return a / b if operador == "/" else a % b

    def visitExprAditiva(self, ctx):
        a, b, operador = self._operandos(ctx)
        # el + tambien sirve para pegar textos
        if operador == "+" and clase_de(a) == "texto" and clase_de(b) == "texto":
            return a + b
        self._exigir(ctx, operador, "numero", a, b)
        return a + b if operador == "+" else a - b

    def visitExprRelacional(self, ctx):
        a, b, operador = self._operandos(ctx)
        clases = (clase_de(a), clase_de(b))
        if clases not in (("numero", "numero"), ("texto", "texto")):
            raise ErrorSemantico(ctx, f"tipos incompatibles: no se puede comparar {describir(a)} "
                                      f"con {describir(b)} usando '{operador}'.")
        return COMPARADORES[operador](a, b)

    def visitExprIgualdad(self, ctx):
        a, b, operador = self._operandos(ctx)
        if a is None or b is None:
            otro = b if a is None else a
            es_nulo = otro.isna() if isinstance(otro, pd.Series) else otro is None
            return es_nulo if operador == "==" else ~es_nulo if isinstance(otro, pd.Series) else not es_nulo
        if clase_de(a) != clase_de(b) or clase_de(a) == "tabla":
            raise ErrorSemantico(ctx, f"tipos incompatibles: no se puede comparar {describir(a)} "
                                      f"con {describir(b)} usando '{operador}'.")
        return a == b if operador == "==" else a != b

    def visitExprNo(self, ctx):
        valor = self.visit(ctx.expresion())
        self._exigir(ctx, "no", "booleano", valor)
        return ~valor if isinstance(valor, pd.Series) else not valor

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
            if len(args) != 1 or not isinstance(args[0], pd.Series):
                raise ErrorSemantico(ctx, f"{nombre}() necesita una columna, "
                                          f"por ejemplo {nombre}(tabla.columna).")
            if nombre in SOLO_NUMEROS and clase_de(args[0]) != "numero":
                raise ErrorSemantico(ctx, f"tipos incompatibles: {nombre}() necesita números "
                                          f"y recibió {describir(args[0])}.")
            return escalar(getattr(args[0], AGREGACIONES[nombre])())

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
            if not isinstance(valor, pd.DataFrame):
                raise ErrorSemantico(ctx, f"filas() necesita una tabla y recibió {describir(valor)}.")
            return len(valor)

        if nombre in ("redondear", "absoluto"):
            self._exigir(ctx, nombre + "()", "numero", *args)
            if nombre == "absoluto":
                return abs(valor)
            decimales = args[1] if len(args) == 2 else 0
            if not isinstance(decimales, int):
                raise ErrorSemantico(ctx, "los decimales de redondear() van como un número entero.")
            return valor.round(decimales) if isinstance(valor, pd.Series) else round(valor, decimales)

        if clase_de(valor) != "texto":
            raise ErrorSemantico(ctx, f"{nombre}() necesita texto y recibió {describir(valor)}.")
        if isinstance(valor, pd.Series):
            return valor.str.upper() if nombre == "mayusculas" else valor.str.lower()
        return valor.upper() if nombre == "mayusculas" else valor.lower()
