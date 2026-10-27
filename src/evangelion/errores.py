"""Errores del lenguaje: los juntamos y los pasamos a español."""

from dataclasses import dataclass

from antlr4 import Token
from antlr4.error.ErrorListener import ErrorListener

from .generado.EvaLexer import EvaLexer


@dataclass
class ErrorEva:
    fase: str      # lexico, sintactico o semantico
    linea: int     # empieza en 1
    columna: int   # empieza en 0, al mostrarla se le suma 1
    mensaje: str

    def __str__(self) -> str:
        return f"[{self.fase}] linea {self.linea}, columna {self.columna + 1}: {self.mensaje}"


class ErrorSemantico(Exception):
    """Lo lanza el interprete cuando el programa esta bien escrito pero no tiene sentido."""

    def __init__(self, ctx, mensaje: str):
        # sirve con un nodo del arbol o con un token suelto
        token = ctx if isinstance(ctx, Token) else ctx.start
        self.error = ErrorEva("semantico", token.line, token.column, mensaje)
        super().__init__(mensaje)


# Las instrucciones que tienen dos nombres (Evangelion y espanol)
ALIAS = {"NERV": "programa", "ENTRY_PLUG": "cargar", "MONITOR": "mostrar", "SEELE": "guardar",
         "HOLOGRAM": "graficar", "PATTERN_BLUE": "si", "PATTERN_ORANGE": "sino",
         "TARGET": "seleccionar", "AT_FIELD": "filtrar", "SYNC": "crear", "CODENAME": "renombrar",
         "FORMATION": "ordenar", "EJECT": "quitar", "DUMMY_PLUG": "rellenar", "EQUIP": "convertir",
         "SQUAD": "agrupar", "MAGI": "resumir", "BATTERY": "limitar", "DIAGNOSTIC": "diagnosticar",
         "PROFECIA": "pronosticar"}

# Las palabras reservadas salen del lexer generado: 'MAGI', 'donde', ... mas los alias
RESERVADAS = ({n[1:-1] for n in EvaLexer.literalNames if n[1:-1].replace("_", "").isalpha()}
              | set(ALIAS) | set(ALIAS.values()))

# Como se le dice a cada token cuando ANTLR lo nombra en un mensaje
NOMBRES = {
    "ID": "un nombre",
    "ID_ESCAPADO": "un nombre entre acentos graves",
    "CADENA": "un texto entre comillas",
    "ENTERO": "un número entero",
    "REAL": "un número con decimales",
    "<EOF>": "el final del archivo",
    "EOF": "el final del archivo",
    **{eva: f"'{es}' ({eva})" for eva, es in ALIAS.items()},
}


class RecolectorDeErrores(ErrorListener):
    """Guarda los errores sintacticos en una lista en vez de imprimirlos en ingles."""

    def __init__(self):
        super().__init__()
        self.errores: list[ErrorEva] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        texto = getattr(offendingSymbol, "text", None)
        # caso tipico: SEELE = ... (se quiso usar una reservada como variable)
        anterior = recognizer.getTokenStream().LT(-1)
        if texto == "=" and anterior is not None and anterior.text in RESERVADAS:
            self.errores.append(ErrorEva("sintactico", anterior.line, anterior.column,
                                         _es_reservada(anterior.text)))
            return
        self.errores.append(ErrorEva("sintactico", line, column, traducir(msg, texto)))


def _es_reservada(texto: str) -> str:
    return (f"'{texto}' es una palabra reservada y no sirve como nombre. "
            f"Si es una columna, escríbela entre acentos graves: `{texto}`.")


def traducir(msg: str, texto) -> str:
    crudo = msg.split("expecting", 1)[1] if "expecting" in msg else ""

    if texto in RESERVADAS and " ID" in crudo:
        return _es_reservada(texto)
    if msg.startswith(("mismatched input", "extraneous input")):
        return f"no se esperaba {_citar(texto)}. Aquí debería ir {_esperado(crudo)}."
    if msg.startswith("missing"):
        falta = msg[len("missing"):].split(" at ")[0]
        return f"falta {_esperado(falta)} antes de {_citar(texto)}."
    if msg.startswith("no viable alternative"):
        return f"no entiendo la instrucción cerca de {_citar(texto)}."
    return msg


def _citar(texto) -> str:
    if texto is None or texto == "<EOF>":
        return "el final del archivo"
    return f"'{texto}'"


def _esperado(crudo: str) -> str:
    crudo = crudo.strip()
    if crudo.startswith("{") and crudo.endswith("}"):
        crudo = crudo[1:-1]
    opciones = [o.strip() for o in crudo.split(", ")]

    # Si ANTLR lista muchas opciones el mensaje no se entiende, mejor resumir
    if "TARGET" in opciones:
        return "una etapa (seleccionar, filtrar, crear, agrupar, resumir... o TARGET, AT_FIELD, SYNC, SQUAD, MAGI...)"
    if "MONITOR" in opciones:
        return ("una instrucción (una asignación, mostrar, guardar, graficar, si, mientras, para... "
                "o MONITOR, SEELE, HOLOGRAM, PATTERN_BLUE)")
    if len(opciones) > 8:
        return "un valor o una expresión"

    opciones = [NOMBRES.get(o, o) for o in opciones]
    if len(opciones) == 1:
        return opciones[0]
    return ", ".join(opciones[:-1]) + " o " + opciones[-1]


def formatear(errores: list, fuente: str, archivo: str = "<entrada>") -> str:
    """Cada error con su linea de codigo y una flecha debajo de la columna."""
    lineas = fuente.splitlines()
    partes = []
    for err in errores:
        partes.append(f"  Error {_fase(err.fase)} en {archivo}, línea {err.linea}, columna {err.columna + 1}")
        partes.append(f"    {err.mensaje}")
        if 0 < err.linea <= len(lineas):
            codigo = lineas[err.linea - 1].replace("\t", " ")
            partes.append(f"      {err.linea:>3} | {codigo}")
            partes.append(f"          | {' ' * err.columna}^")
        partes.append("")
    return "\n".join(partes).rstrip("\n")


def _fase(fase: str) -> str:
    return {"lexico": "léxico", "sintactico": "sintáctico", "semantico": "semántico"}[fase]
