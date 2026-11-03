"""Linea de comandos: analiza un programa .eva y, si esta bien, lo ejecuta."""

from . import consola
from .analizador import analizar, nombre_token
from .arbol import como_lisp, como_svg, como_texto
from .archivos import existe, nombre_archivo
from .errores import ErrorSemantico, formatear
from .interprete import Interprete
from .listas import Lista


AYUDA = """Uso: python run.py programa.eva [opciones]

  --tokens         muestra los tokens (fase 1)
  --arbol          muestra el árbol de análisis
  --lisp           árbol en una sola línea con paréntesis
  --svg SALIDA     guarda el árbol como dibujo .svg
  --simbolos       muestra la tabla de símbolos al terminar
  --solo-analisis  revisa el programa pero no lo ejecuta
  --color          pinta los mensajes si la terminal lo permite"""
INTERRUPTORES = ("--tokens", "--arbol", "--lisp", "--simbolos", "--solo-analisis", "--color")


def _leer_argumentos(argv):
    """Devuelve (archivo, opciones que se pidieron, salida del svg), o None si algo no se entiende."""
    archivo, opciones, svg = None, set(), None
    pendientes = iter(argv)
    for argumento in pendientes:
        if argumento in INTERRUPTORES:
            opciones.add(argumento)
        elif argumento == "--svg":
            svg = next(pendientes, None)
            if svg is None:
                return None
        elif argumento.startswith("-") or archivo is not None:
            return None
        else:
            archivo = argumento
    return None if archivo is None else (archivo, opciones, svg)


def main(argv=()) -> int:
    leidos = _leer_argumentos(argv)
    if leidos is None:
        print(AYUDA)
        return 2
    ruta, opciones, svg = leidos
    if "--color" in opciones:
        consola.activar_color()

    if not existe(ruta):
        print(f"No existe el archivo '{ruta}'.")
        return 2
    nombre = nombre_archivo(ruta)

    with open(ruta, encoding="utf-8") as archivo:
        fuente = archivo.read()
    res = analizar(fuente)

    if "--tokens" in opciones:
        print(f"TOKENS de {nombre}")
        print(f"{'#':>4}  {'LIN:COL':<8} {'TIPO':<18} LEXEMA")
        for i, t in enumerate(res.tokens, 1):
            print(f"{i:>4}  {f'{t.line}:{t.column + 1}':<8} {nombre_token(t.type):<18} {t.text}")
        print()

    if not res.valido:
        print(consola.fallo(formatear(res.errores, fuente, nombre), res.errores[0].linea))
        return 1

    if "--arbol" in opciones:
        print(f"ÁRBOL DE ANÁLISIS de {nombre}")
        print(como_texto(res.arbol))
    if "--lisp" in opciones:
        print(como_lisp(res.arbol) + "\n")
    if svg:
        with open(svg, "w", encoding="utf-8") as archivo:
            archivo.write(como_svg(res.arbol))
        print(f"Árbol guardado en {svg}\n")

    interprete = Interprete()
    if "--solo-analisis" not in opciones:
        try:
            interprete.ejecutar(res.arbol)
        except ErrorSemantico as e:
            print(consola.fallo(formatear(Lista((e.error,)), fuente, nombre), e.error.linea))
            return 1

    if "--simbolos" in opciones:
        print("TABLA DE SÍMBOLOS")
        print(interprete.simbolos.como_texto() + "\n")

    print(consola.exito(nombre, interprete.operacion, len(res.tokens),
                        interprete.simbolos.nombres(), interprete.reportes, interprete.graficas))
    return 0

