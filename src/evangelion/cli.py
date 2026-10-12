"""Linea de comandos: analiza un programa .eva y, si esta bien, lo ejecuta."""

import argparse
import sys
from pathlib import Path

from . import consola
from .analizador import analizar, nombre_token
from .arbol import como_lisp, como_svg, como_texto
from .errores import ErrorSemantico, formatear
from .interprete import Interprete


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="eva",
        description="evangelionPL: un lenguaje para analizar datos con vocabulario de Evangelion.",
    )
    p.add_argument("archivo", help="programa .eva")
    p.add_argument("--tokens", action="store_true", help="muestra los tokens (fase 1)")
    p.add_argument("--arbol", action="store_true", help="muestra el árbol de análisis")
    p.add_argument("--lisp", action="store_true", help="árbol en una sola línea con paréntesis")
    p.add_argument("--svg", metavar="SALIDA", help="guarda el árbol como dibujo .svg")
    p.add_argument("--simbolos", action="store_true", help="muestra la tabla de símbolos al terminar")
    p.add_argument("--solo-analisis", action="store_true", help="revisa el programa pero no lo ejecuta")
    args = p.parse_args(argv)

    consola.preparar_terminal()

    ruta = Path(args.archivo)
    if not ruta.is_file():
        print(f"No existe el archivo '{ruta}'.")
        return 2

    fuente = ruta.read_text(encoding="utf-8")
    res = analizar(fuente)

    if args.tokens:
        print(f"TOKENS de {ruta.name}")
        print(f"{'#':>4}  {'LIN:COL':<8} {'TIPO':<18} LEXEMA")
        for i, t in enumerate(res.tokens, 1):
            print(f"{i:>4}  {f'{t.line}:{t.column + 1}':<8} {nombre_token(t.type):<18} {t.text}")
        print()

    if not res.valido:
        print(consola.fallo(formatear(res.errores, fuente, ruta.name), res.errores[0].linea))
        return 1

    if args.arbol:
        print(f"ÁRBOL DE ANÁLISIS de {ruta.name}")
        print(como_texto(res.arbol))
    if args.lisp:
        print(como_lisp(res.arbol) + "\n")
    if args.svg:
        Path(args.svg).write_text(como_svg(res.arbol), encoding="utf-8")
        print(f"Árbol guardado en {args.svg}\n")

    interprete = Interprete()
    if not args.solo_analisis:
        try:
            interprete.ejecutar(res.arbol)
        except ErrorSemantico as e:
            print(consola.fallo(formatear([e.error], fuente, ruta.name), e.error.linea))
            return 1

    if args.simbolos:
        print("TABLA DE SÍMBOLOS")
        print(interprete.simbolos.como_texto() + "\n")

    print(consola.exito(ruta.name, interprete.operacion, len(res.tokens),
                        interprete.simbolos.nombres(), interprete.reportes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
