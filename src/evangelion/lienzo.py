"""Fase 3: lienzos donde se dibujan las graficas, hechos a mano.

Hay dos lienzos con los mismos metodos (rectangulo, linea, circulo y texto):
LienzoPNG pinta pixel por pixel y arma el archivo PNG desde cero, con su propio
compresor DEFLATE y sus propios CRC-32 y Adler-32; LienzoSVG escribe las mismas
figuras como texto SVG. Las graficas no saben en cual de los dos estan dibujando.
"""

from html import escape

from .fuente import ALTO, AVANCE, ancho_texto, pixeles_de


def color_rgb(color: str) -> tuple:
    """'#5b3a8e' -> (91, 58, 142)"""
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def _inicio_texto(x, texto, escala, ancla):
    ancho = ancho_texto(texto, escala)
    return {"izq": x, "centro": x - ancho // 2, "der": x - ancho}[ancla]


# --- Lienzo de pixeles ----------------------------------------------------------

class LienzoPNG:

    def __init__(self, ancho: int, alto: int, fondo: str = "#ffffff"):
        self.ancho, self.alto = ancho, alto
        self._paleta = []          # cada color usado, en orden; el pixel guarda su posicion
        self._indices = {}
        indice_fondo = self._indice(fondo)
        self.pixeles = bytearray([indice_fondo]) * (ancho * alto)

    def _indice(self, color: str) -> int:
        color = color.lower()
        if color not in self._indices:
            if len(self._paleta) == 256:
                raise ValueError("la gráfica usa más de 256 colores y el PNG con paleta no los admite.")
            self._indices[color] = len(self._paleta)
            self._paleta.append(color_rgb(color))
        return self._indices[color]

    def _punto(self, x: int, y: int, indice: int) -> None:
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            self.pixeles[y * self.ancho + x] = indice

    def rectangulo(self, x0, y0, x1, y1, color: str) -> None:
        """Rectangulo relleno; las esquinas se pueden dar en cualquier orden."""
        x0, x1 = sorted((round(x0), round(x1)))
        y0, y1 = sorted((round(y0), round(y1)))
        x0, x1 = max(x0, 0), min(x1, self.ancho - 1)
        y0, y1 = max(y0, 0), min(y1, self.alto - 1)
        if x0 > x1 or y0 > y1:
            return
        fila = bytes([self._indice(color)]) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            inicio = y * self.ancho + x0
            self.pixeles[inicio:inicio + len(fila)] = fila

    def borde(self, x0, y0, x1, y1, color: str) -> None:
        for a, b, c, d in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
            self.linea(a, b, c, d, color)

    def linea(self, x0, y0, x1, y1, color: str, grosor: int = 1) -> None:
        """Algoritmo de Bresenham. El grosor se logra pintando un cuadrito en cada paso."""
        indice = self._indice(color)
        x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        paso_x, paso_y = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        error = dx + dy
        desde = -(grosor // 2)
        while True:
            for i in range(desde, desde + grosor):
                for j in range(desde, desde + grosor):
                    self._punto(x0 + i, y0 + j, indice)
            if x0 == x1 and y0 == y1:
                return
            doble = 2 * error
            if doble >= dy:
                error += dy
                x0 += paso_x
            if doble <= dx:
                error += dx
                y0 += paso_y

    def circulo(self, cx, cy, radio, color: str, relleno: bool = True) -> None:
        indice = self._indice(color)
        cx, cy = round(cx), round(cy)
        for y in range(-radio, radio + 1):
            for x in range(-radio, radio + 1):
                distancia = x * x + y * y
                if distancia <= radio * radio + radio and (relleno or distancia >= (radio - 1) ** 2 + radio - 1):
                    self._punto(cx + x, cy + y, indice)

    def texto(self, x, y, texto: str, color: str, escala: int = 2,
              ancla: str = "izq", vertical: bool = False) -> None:
        """(x, y) es la esquina de arriba del renglon. En vertical se lee de abajo hacia arriba
        y entonces x, y marcan el centro del borde izquierdo del renglon girado."""
        indice = self._indice(color)
        if vertical:
            largo = ancho_texto(texto, escala)
            base_y = round(y) + largo // 2
            for n, letra in enumerate(texto):
                for gx, gy in pixeles_de(letra):
                    for i in range(escala):
                        for j in range(escala):
                            px = (n * AVANCE + gx) * escala + i
                            self._punto(round(x) + gy * escala + j, base_y - px, indice)
            return
        x = _inicio_texto(round(x), texto, escala, ancla)
        y = round(y)
        for n, letra in enumerate(texto):
            for gx, gy in pixeles_de(letra):
                inicio_x = x + (n * AVANCE + gx) * escala
                for j in range(escala):
                    for i in range(escala):
                        self._punto(inicio_x + i, y + gy * escala + j, indice)

    def guardar(self, ruta) -> None:
        with open(ruta, "wb") as archivo:
            archivo.write(self.como_png())

    def como_png(self) -> bytes:
        # cada fila empieza con el tipo de filtro; 0 = la fila va tal cual
        crudo = bytearray()
        for y in range(self.alto):
            crudo.append(0)
            crudo += self.pixeles[y * self.ancho:(y + 1) * self.ancho]
        paleta = b"".join(bytes(rgb) for rgb in self._paleta)
        # 8 bits por pixel, tipo de color 3 = con paleta
        cabecera = self.ancho.to_bytes(4, "big") + self.alto.to_bytes(4, "big") + bytes([8, 3, 0, 0, 0])
        return (b"\x89PNG\r\n\x1a\n" + _bloque(b"IHDR", cabecera) + _bloque(b"PLTE", paleta)
                + _bloque(b"IDAT", zlib_comprimir(bytes(crudo), self.ancho + 1)) + _bloque(b"IEND", b""))


# --- Lienzo SVG -----------------------------------------------------------------

class LienzoSVG:
    """Las mismas figuras pero en texto. La letra monoespaciada a 10*escala px
    mide casi lo mismo que la letra de pixeles, asi los textos caen en su sitio."""

    def __init__(self, ancho: int, alto: int, fondo: str = "#ffffff"):
        self.ancho, self.alto = ancho, alto
        self._partes = [f'<rect width="{ancho}" height="{alto}" fill="{fondo}"/>']

    def rectangulo(self, x0, y0, x1, y1, color: str) -> None:
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        self._partes.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0 + 1:.1f}" '
                            f'height="{y1 - y0 + 1:.1f}" fill="{color}"/>')

    def borde(self, x0, y0, x1, y1, color: str) -> None:
        self._partes.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" '
                            f'fill="none" stroke="{color}"/>')

    def linea(self, x0, y0, x1, y1, color: str, grosor: int = 1) -> None:
        self._partes.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                            f'stroke="{color}" stroke-width="{grosor}" stroke-linecap="square"/>')

    def circulo(self, cx, cy, radio, color: str, relleno: bool = True) -> None:
        pintura = f'fill="{color}"' if relleno else f'fill="none" stroke="{color}" stroke-width="1.5"'
        self._partes.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radio}" {pintura}/>')

    def texto(self, x, y, texto: str, color: str, escala: int = 2,
              ancla: str = "izq", vertical: bool = False) -> None:
        tamano = 10 * escala
        if vertical:
            cx, cy = x + ALTO * escala, y
            self._partes.append(f'<text x="{cx}" y="{cy}" font-size="{tamano}" fill="{color}" '
                                f'text-anchor="middle" transform="rotate(-90 {cx} {cy})">{escape(texto)}</text>')
            return
        x = _inicio_texto(x, texto, escala, ancla)
        self._partes.append(f'<text x="{x}" y="{y + ALTO * escala}" font-size="{tamano}" '
                            f'fill="{color}">{escape(texto)}</text>')

    def como_svg(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.ancho}" height="{self.alto}" '
                f'viewBox="0 0 {self.ancho} {self.alto}" font-family="Consolas, \'DejaVu Sans Mono\', monospace">\n'
                + "\n".join(self._partes) + "\n</svg>\n")

    def guardar(self, ruta) -> None:
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(self.como_svg())


# --- El formato PNG por dentro ---------------------------------------------------

def _tabla_crc() -> list:
    tabla = []
    for n in range(256):
        c = n
        for _ in range(8):
            c = 0xEDB88320 ^ (c >> 1) if c & 1 else c >> 1
        tabla.append(c)
    return tabla


_CRC = _tabla_crc()


def crc32(datos: bytes) -> int:
    c = 0xFFFFFFFF
    for byte in datos:
        c = _CRC[(c ^ byte) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


def adler32(datos: bytes) -> int:
    a, b = 1, 0
    # se suma por tramos para no sacar el modulo en cada byte
    for inicio in range(0, len(datos), 5552):
        for byte in datos[inicio:inicio + 5552]:
            a += byte
            b += a
        a %= 65521
        b %= 65521
    return (b << 16) | a


def _bloque(tipo: bytes, datos: bytes) -> bytes:
    """Un bloque PNG: largo, tipo, datos y el CRC de tipo + datos."""
    return len(datos).to_bytes(4, "big") + tipo + datos + crc32(tipo + datos).to_bytes(4, "big")


# --- DEFLATE con los codigos de Huffman fijos (RFC 1951, seccion 3.2.6) ---------

_BASE_LARGO = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
               35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258]
_EXTRA_LARGO = [0] * 8 + [1] * 4 + [2] * 4 + [3] * 4 + [4] * 4 + [5] * 4 + [0]
_BASE_DISTANCIA = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385,
                   513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577]
_EXTRA_DISTANCIA = [0, 0, 0, 0] + [n // 2 for n in range(2, 28)]


def _invertir(codigo: int, bits: int) -> int:
    # DEFLATE guarda los codigos de Huffman empezando por el bit mas alto
    resultado = 0
    for _ in range(bits):
        resultado = (resultado << 1) | (codigo & 1)
        codigo >>= 1
    return resultado


def _codigos_fijos() -> list:
    codigos = []
    for simbolo in range(288):
        if simbolo < 144:
            codigo, bits = 0x30 + simbolo, 8
        elif simbolo < 256:
            codigo, bits = 0x190 + simbolo - 144, 9
        elif simbolo < 280:
            codigo, bits = simbolo - 256, 7
        else:
            codigo, bits = 0xC0 + simbolo - 280, 8
        codigos.append((_invertir(codigo, bits), bits))
    return codigos


_LITERALES = _codigos_fijos()
_DISTANCIAS = [(_invertir(d, 5), 5) for d in range(30)]
_SIMBOLO_LARGO = [0] * 259      # largo -> posicion en _BASE_LARGO
_SIMBOLO_DISTANCIA = {}
for _n, _base in enumerate(_BASE_LARGO):
    for _largo in range(_base, min(_base + (1 << _EXTRA_LARGO[_n]), 259)):
        _SIMBOLO_LARGO[_largo] = _n


def _simbolo_distancia(distancia: int) -> int:
    if distancia not in _SIMBOLO_DISTANCIA:
        n = max(i for i, base in enumerate(_BASE_DISTANCIA) if base <= distancia)
        _SIMBOLO_DISTANCIA[distancia] = n
    return _SIMBOLO_DISTANCIA[distancia]


def _largo_igual(datos: bytes, i: int, distancia: int) -> int:
    """Cuantos bytes desde i repiten lo que habia `distancia` bytes atras (maximo 258).
    Compara tramos enteros en vez de byte por byte y busca el corte por mitades."""
    tope = min(258, len(datos) - i)
    if distancia == 1:
        patron = datos[i - 1:i] * tope
        def igual(n): return datos[i:i + n] == patron[:n]
    elif distancia >= tope:
        def igual(n): return datos[i:i + n] == datos[i - distancia:i - distancia + n]
    else:
        return _largo_igual_lento(datos, i, distancia, tope)
    bajo, alto = 0, tope
    while bajo < alto:
        medio = (bajo + alto + 1) // 2
        if igual(medio):
            bajo = medio
        else:
            alto = medio - 1
    return bajo


def _largo_igual_lento(datos, i, distancia, tope):
    n = 0
    while n < tope and datos[i + n] == datos[i + n - distancia]:
        n += 1
    return n


def deflate(datos: bytes, fila: int = 0) -> bytes:
    """Comprime con LZ77 y Huffman fijo. Busca repeticiones en dos sitios que en una
    grafica casi siempre aciertan: el byte anterior (zonas de un solo color) y el mismo
    punto de la fila de arriba (cuando `fila` dice cuanto mide una fila)."""
    salida = bytearray()
    acumulado, cuantos = 0, 0

    def escribir(valor, bits):
        nonlocal acumulado, cuantos
        acumulado |= valor << cuantos
        cuantos += bits
        while cuantos >= 8:
            salida.append(acumulado & 0xFF)
            acumulado >>= 8
            cuantos -= 8

    escribir(1, 1)        # ultimo bloque
    escribir(1, 2)        # tipo 01 = Huffman fijo
    distancias = [1] + ([fila] if 1 < fila <= 32768 else [])
    i = 0
    while i < len(datos):
        mejor, mejor_distancia = 0, 0
        for distancia in distancias:
            if distancia <= i:
                largo = _largo_igual(datos, i, distancia)
                if largo > mejor:
                    mejor, mejor_distancia = largo, distancia
        if mejor >= 3:
            n = _SIMBOLO_LARGO[mejor]
            escribir(*_LITERALES[257 + n])
            escribir(mejor - _BASE_LARGO[n], _EXTRA_LARGO[n])
            d = _simbolo_distancia(mejor_distancia)
            escribir(*_DISTANCIAS[d])
            escribir(mejor_distancia - _BASE_DISTANCIA[d], _EXTRA_DISTANCIA[d])
            i += mejor
        else:
            escribir(*_LITERALES[datos[i]])
            i += 1
    escribir(*_LITERALES[256])   # fin del bloque
    if cuantos:
        salida.append(acumulado & 0xFF)
    return bytes(salida)


def zlib_comprimir(datos: bytes, fila: int = 0) -> bytes:
    """El formato zlib que pide PNG: dos bytes de cabecera, DEFLATE y el Adler-32."""
    return b"\x78\x01" + deflate(datos, fila) + adler32(datos).to_bytes(4, "big")
