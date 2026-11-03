"""Fase 1: del texto fuente a los tokens y al arbol de analisis."""

from antlr4 import CommonTokenStream, InputStream, Token

from .errores import ErrorEva, RecolectorDeErrores
from .generado.EvaLexer import EvaLexer
from .generado.EvaParser import EvaParser
from .listas import Lista


class Resultado:
    def __init__(self, fuente: str):
        self.fuente = fuente
        self.tokens = Lista()
        self.arbol = None
        self.errores = Lista()

    @property
    def valido(self) -> bool:
        return not self.errores


def analizar(fuente: str) -> Resultado:
    """Corre el lexer y el parser. No lanza excepciones, devuelve los errores en una lista."""
    res = Resultado(fuente=fuente)

    lexer = EvaLexer(InputStream(fuente))
    lexer.removeErrorListeners()
    flujo = CommonTokenStream(lexer)
    flujo.fill()
    res.tokens = Lista(t for t in flujo.tokens if t.type != Token.EOF)

    lexicos = _errores_lexicos(res.tokens)

    escucha = RecolectorDeErrores()
    parser = EvaParser(flujo)
    parser.removeErrorListeners()
    parser.addErrorListener(escucha)
    res.arbol = parser.programa()

    # Un caracter invalido tambien confunde al parser, asi que si hay errores
    # lexicos mostramos solo esos para no repetir el mismo problema dos veces
    res.errores = lexicos if lexicos else _primero_por_linea(escucha.errores)
    return res


def _primero_por_linea(errores) -> Lista:
    """Despues del primer error el parser se pierde y reporta de mas en la misma linea."""
    vistas, filtrados = set(), Lista()
    for error in errores:
        if error.linea not in vistas:
            vistas.add(error.linea)
            filtrados.agregar(error)
    return filtrados


def _errores_lexicos(tokens) -> Lista:
    errores = Lista()
    for t in tokens:
        if t.type == EvaLexer.CARACTER_INVALIDO:
            errores.agregar(ErrorEva("lexico", t.line, t.column,
                                    f"el carácter '{t.text}' no pertenece al lenguaje."))
        elif t.type == EvaLexer.CADENA_SIN_CERRAR:
            errores.agregar(ErrorEva("lexico", t.line, t.column,
                                    "el texto no se cerró, falta la comilla del final."))
    return errores


def nombre_token(tipo: int) -> str:
    """4 -> 'MONITOR'"""
    nombres = EvaLexer.symbolicNames
    return nombres[tipo] if 0 < tipo < len(nombres) else f"<{tipo}>"
