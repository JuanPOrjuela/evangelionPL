"""Formas de mostrar el arbol de analisis: texto, parentesis y dibujo SVG."""

from antlr4 import TerminalNode

from .lienzo import escape


def nombre_regla(nodo) -> str:
    """ExprAditivaContext -> exprAditiva (asi se ve la alternativa y no solo 'expresion')."""
    n = type(nodo).__name__.removesuffix("Context")
    return n[0].lower() + n[1:]


def _etiqueta(nodo) -> str:
    return nodo.getText() if isinstance(nodo, TerminalNode) else nombre_regla(nodo)


def _hijos(nodo) -> list:
    return [] if isinstance(nodo, TerminalNode) else (nodo.children or [])


def como_lisp(nodo) -> str:
    """Todo el arbol en una linea, con parentesis."""
    if isinstance(nodo, TerminalNode):
        return nodo.getText()
    return "(" + " ".join([nombre_regla(nodo)] + [como_lisp(h) for h in _hijos(nodo)]) + ")"


def como_texto(nodo, prefijo: str = "", ultimo: bool = True, raiz: bool = True) -> str:
    """Arbol con sangria, se lee de arriba hacia abajo."""
    if raiz:
        salida, nuevo = _etiqueta(nodo) + "\n", ""
    else:
        salida = f"{prefijo}{'`-- ' if ultimo else '|-- '}{_etiqueta(nodo)}\n"
        nuevo = prefijo + ("    " if ultimo else "|   ")
    hijos = _hijos(nodo)
    for i, hijo in enumerate(hijos):
        salida += como_texto(hijo, nuevo, i == len(hijos) - 1, raiz=False)
    return salida


# --- Dibujo en SVG -----------------------------------------------------------

ANCHO_LETRA = 7.2
ALTO_NIVEL = 46
MARGEN = 12


def como_svg(raiz) -> str:
    """Dibuja el arbol: las hojas se reparten de izquierda a derecha y cada
    padre queda centrado sobre sus hijos."""
    posiciones = {}   # id(nodo) -> (x, nivel)
    orden = []
    cursor = [MARGEN]

    def ubicar(nodo, nivel):
        ancho = len(_etiqueta(nodo)) * ANCHO_LETRA + 14
        hijos = _hijos(nodo)
        if not hijos:
            x = cursor[0] + ancho / 2
            cursor[0] += ancho
        else:
            inicio = cursor[0]
            for hijo in hijos:
                ubicar(hijo, nivel + 1)
            x = (posiciones[id(hijos[0])][0] + posiciones[id(hijos[-1])][0]) / 2
            # si la etiqueta del padre es mas ancha que sus hijos, le abrimos campo
            cursor[0] = max(cursor[0], inicio + ancho)
            x = max(x, inicio + ancho / 2)
        posiciones[id(nodo)] = (x, nivel)
        orden.append(nodo)

    ubicar(raiz, 0)

    niveles = max(nivel for _, nivel in posiciones.values())
    ancho_total = cursor[0] + MARGEN
    alto_total = niveles * ALTO_NIVEL + 40

    lineas, textos = [], []
    for nodo in orden:
        x, nivel = posiciones[id(nodo)]
        y = nivel * ALTO_NIVEL + 22
        for hijo in _hijos(nodo):
            hx, hnivel = posiciones[id(hijo)]
            lineas.append(f'<line x1="{x:.1f}" y1="{y + 6:.1f}" x2="{hx:.1f}" '
                          f'y2="{hnivel * ALTO_NIVEL + 10:.1f}"/>')
        clase = "hoja" if isinstance(nodo, TerminalNode) else "regla"
        textos.append(f'<text class="{clase}" x="{x:.1f}" y="{y:.1f}">{escape(_etiqueta(nodo))}</text>')

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho_total:.0f} {alto_total:.0f}" '
        f'width="{ancho_total:.0f}" height="{alto_total:.0f}">\n'
        '<style>\n'
        '  text { font-family: Consolas, "Courier New", monospace; font-size: 12px; text-anchor: middle; }\n'
        '  .regla { fill: #222; }\n'
        '  .hoja { fill: #222; font-weight: bold; }\n'
        '  line { stroke: #888; stroke-width: 1; }\n'
        '</style>\n'
        '<rect width="100%" height="100%" fill="white"/>\n'
        + "\n".join(lineas) + "\n" + "\n".join(textos) + "\n</svg>\n"
    )
