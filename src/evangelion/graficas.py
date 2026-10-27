"""Fase 3: las graficas de HOLOGRAM, dibujadas a mano sobre un lienzo PNG o SVG.

El interprete revisa las opciones y arma una Grafica; aqui solo se calculan las
escalas, los ejes, la leyenda y las figuras. Las filas a las que les falta algun
dato de los ejes se saltan.
"""

from dataclasses import dataclass
from pathlib import Path

from .fuente import ALTO, ancho_texto
from .lienzo import LienzoPNG, LienzoSVG, color_rgb
from .matematica import piso, piso_log10, techo, techo_log2
from .tablas import Columna, es_numero, formatear

TIPOS = ("barras", "lineas", "histograma", "dispersion", "caja")
# los ejes que pide cada tipo; los demas son opcionales
OBLIGATORIOS = {"barras": ("eje_x", "eje_y"), "lineas": ("eje_x", "eje_y"), "histograma": ("eje_x",),
                "dispersion": ("eje_x", "eje_y"), "caja": ("eje_y",)}
# los ejes que tienen que ser numericos en cada tipo
NUMERICOS = {"barras": ("eje_y",), "lineas": ("eje_y",), "histograma": ("eje_x",),
             "dispersion": ("eje_x", "eje_y"), "caja": ("eje_y",)}

# Morado del EVA-01, naranja, verde del EVA-01, rojo del EVA-02, azul del EVA-00...
PALETA = ["#5b3a8e", "#e8710a", "#2a9d8f", "#c0392b", "#3b6fb6",
          "#8c6d1f", "#d4539e", "#6a8a2e", "#7f7f7f", "#17becf", "#a0522d", "#1f3a5f"]
COLORES = {"morado": "#5b3a8e", "naranja": "#e8710a", "verde": "#2a9d8f", "rojo": "#c0392b",
           "azul": "#3b6fb6", "amarillo": "#d4a017", "rosado": "#d4539e", "gris": "#6b6b6b",
           "negro": "#222222", "cafe": "#8c6d1f"}
TEXTO, SUAVE, REJILLA, EJE, FONDO = "#222222", "#555555", "#e4e4e4", "#444444", "#ffffff"


@dataclass
class Grafica:
    tipo: str
    x: Columna = None
    y: Columna = None
    serie: Columna = None
    titulo: str = ""
    etiqueta_x: str = None
    etiqueta_y: str = None
    color: str = None
    intervalos: int = None
    ancho: int = 960
    alto: int = 600
    leyenda: bool = True


def color_de(texto: str):
    """Un nombre de la lista COLORES o un '#rrggbb'. Si no sirve devuelve None."""
    texto = texto.strip().lower()
    if texto in COLORES:
        return COLORES[texto]
    if len(texto) == 7 and texto[0] == "#" and all(c in "0123456789abcdef" for c in texto[1:]):
        return texto
    return None


def aclarar(color: str, cuanto: float = 0.6) -> str:
    """Mezcla el color con blanco (para el relleno de las cajas)."""
    return "#" + "".join(f"{round(c + (255 - c) * cuanto):02x}" for c in color_rgb(color))


def guardar(grafica: Grafica, ruta) -> int:
    """Dibuja la grafica en el formato que diga la extension. Devuelve cuantas filas uso."""
    clase = LienzoSVG if Path(ruta).suffix.lower() == ".svg" else LienzoPNG
    lienzo, usadas = dibujar(grafica, clase)
    lienzo.guardar(ruta)
    return usadas


def dibujar(grafica: Grafica, clase=LienzoPNG):
    filas = _filas_completas(grafica)
    if not filas:
        raise ValueError("no quedó ninguna fila con datos en los ejes, no hay nada que dibujar")
    lienzo = clase(grafica.ancho, grafica.alto, FONDO)
    {"barras": _barras, "lineas": _lineas, "histograma": _histograma,
     "dispersion": _dispersion, "caja": _caja}[grafica.tipo](lienzo, grafica, filas)
    return lienzo, len(filas)


# --- Datos ----------------------------------------------------------------------

def _filas_completas(g: Grafica) -> list:
    """Filas (x, y, serie) sin faltantes en las columnas que la grafica usa."""
    columnas = [c for c in (g.x, g.y, g.serie) if c is not None]
    largo = len(columnas[0])
    filas = []
    for i in range(largo):
        fila = tuple(c.valores[i] if c is not None else None for c in (g.x, g.y, g.serie))
        if all(c.valores[i] is not None for c in columnas):
            filas.append(fila)
    return filas


def etiqueta(valor) -> str:
    if isinstance(valor, float) and valor.is_integer() and abs(valor) < 1e15:
        return str(int(valor))
    return formatear(valor)


def _unicos(valores) -> list:
    vistos = []
    for v in valores:
        if v not in vistos:
            vistos.append(v)
    return vistos


def cuantil(ordenados: list, q: float) -> float:
    """Cuantil con interpolacion lineal entre los dos datos vecinos."""
    posicion = (len(ordenados) - 1) * q
    abajo = piso(posicion)
    arriba = min(abajo + 1, len(ordenados) - 1)
    return ordenados[abajo] + (ordenados[arriba] - ordenados[abajo]) * (posicion - abajo)


def marcas(minimo: float, maximo: float, cuantas: int = 5) -> list:
    """Valores redondos para las marcas de un eje (pasos de 1, 2, 2,5 o 5 por potencia de 10)."""
    if minimo == maximo:
        minimo, maximo = (minimo - 1, maximo + 1) if minimo != 0 else (0, 1)
    crudo = (maximo - minimo) / cuantas
    potencia = 10.0 ** piso_log10(crudo)
    paso = next(m * potencia for m in (1, 2, 2.5, 5, 10) if m * potencia >= crudo)
    inicio = piso(minimo / paso + 1e-9) * paso
    fin = techo(maximo / paso - 1e-9) * paso
    return [inicio + k * paso for k in range(round((fin - inicio) / paso) + 1)]


def numero(valor: float, paso: float) -> str:
    """Formato colombiano: punto para miles y coma para decimales. Millones con 'M'."""
    sufijo = ""
    if abs(paso) >= 1e6:
        valor, paso, sufijo = valor / 1e6, paso / 1e6, " M"
    decimales = 0
    while decimales < 4 and abs(round(paso, decimales) - paso) > 1e-9 * max(1, abs(paso)):
        decimales += 1
    texto = f"{abs(valor):.{decimales}f}".replace(".", ",")
    # el punto de miles solo desde 10.000, asi los años quedan como 1970 y no 1.970
    if abs(valor) >= 10000:
        texto = f"{abs(valor):,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    signo = "-" if valor < 0 and round(abs(valor), decimales) != 0 else ""
    return signo + texto + sufijo


# --- Marco: titulo, leyenda, ejes ------------------------------------------------

class Marco:
    """Reparte el espacio del lienzo y traduce datos a pixeles."""

    def __init__(self, lienzo, g: Grafica, series=(), colores=()):
        self.lienzo, self.g = lienzo, g
        self.arriba = 18
        escala_titulo = 3 if ancho_texto(g.titulo, 3) <= lienzo.ancho - 40 else 2
        if g.titulo:
            lienzo.texto(lienzo.ancho / 2, self.arriba, g.titulo, TEXTO, escala_titulo, "centro")
            self.arriba += ALTO * escala_titulo + 16
        if g.leyenda and len(series) > 1:
            self.arriba = self._leyenda(series, colores, self.arriba) + 6
        self.arriba += 10
        self.izq, self.der, self.abajo = 70, lienzo.ancho - 30, lienzo.alto - 64

    def _leyenda(self, series, colores, y) -> int:
        """Los nombres de las series en renglones centrados debajo del titulo."""
        piezas = [(etiqueta(s), c) for s, c in zip(series, colores)]
        renglones, actual, ancho_actual = [], [], 0
        limite = self.lienzo.ancho - 60
        for texto, color in piezas:
            ancho = 18 + ancho_texto(texto, 2) + 22
            if actual and ancho_actual + ancho > limite:
                renglones.append((actual, ancho_actual))
                actual, ancho_actual = [], 0
            actual.append((texto, color, ancho))
            ancho_actual += ancho
        renglones.append((actual, ancho_actual))
        for piezas_renglon, total in renglones:
            x = (self.lienzo.ancho - total + 22) / 2
            for texto, color, ancho in piezas_renglon:
                self.lienzo.rectangulo(x, y + 1, x + 11, y + 12, color)
                self.lienzo.texto(x + 18, y, texto, SUAVE, 2)
                x += ancho
            y += 24
        return y

    # eje vertical numerico (todas las graficas lo tienen)
    def eje_y(self, minimo, maximo, etiqueta_eje):
        self.marcas_y = marcas(minimo, maximo)
        self.y_min, self.y_max = self.marcas_y[0], self.marcas_y[-1]
        paso = self.marcas_y[1] - self.marcas_y[0] if len(self.marcas_y) > 1 else 1
        textos = [numero(v, paso) for v in self.marcas_y]
        self.izq = 34 + max(ancho_texto(t, 2) for t in textos) + 12
        self._textos_y = textos
        self.etiqueta_y = etiqueta_eje

    def eje_x_numerico(self, minimo, maximo, etiqueta_eje, margen=0.0):
        """El eje x va justo de un extremo de los datos al otro (mas un margen opcional)
        y solo muestra las marcas redondas que caen adentro."""
        if minimo == maximo:
            minimo, maximo = minimo - 1, maximo + 1
        holgura = (maximo - minimo) * margen
        self.x_min, self.x_max = minimo - holgura, maximo + holgura
        todas = marcas(self.x_min, self.x_max, 8)
        paso = todas[1] - todas[0] if len(todas) > 1 else 1
        self.marcas_x = [v for v in todas if self.x_min - 1e-9 <= v <= self.x_max + 1e-9]
        self._textos_x = [numero(v, paso) for v in self.marcas_x]
        self.categorias = None
        self.etiqueta_x = etiqueta_eje

    def eje_x_categorias(self, categorias, etiqueta_eje):
        self.categorias = [etiqueta(c) for c in categorias]
        self.etiqueta_x = etiqueta_eje
        banda = (self.der - self.izq) / len(self.categorias)
        self.vertical = max(ancho_texto(c, 2) for c in self.categorias) > banda - 6
        if self.vertical:
            # los nombres largos van girados y el area de dibujo se encoge para que quepan
            self.categorias = [c if len(c) <= 18 else c[:17] + "." for c in self.categorias]
            largo = max(ancho_texto(c, 2) for c in self.categorias)
            self.abajo = self.lienzo.alto - 44 - largo - 10

    def px(self, x) -> float:
        return self.izq + (x - self.x_min) / (self.x_max - self.x_min) * (self.der - self.izq)

    def py(self, y) -> float:
        return self.abajo - (y - self.y_min) / (self.y_max - self.y_min) * (self.abajo - self.arriba)

    def banda(self, i):
        """Inicio y ancho de la franja de la categoria i."""
        ancho = (self.der - self.izq) / len(self.categorias)
        return self.izq + i * ancho, ancho

    def fondo(self):
        """Rejilla, marcas y textos de los ejes. Se dibuja antes que los datos."""
        lienzo = self.lienzo
        for valor, texto in zip(self.marcas_y, self._textos_y):
            y = self.py(valor)
            lienzo.linea(self.izq, y, self.der, y, REJILLA)
            lienzo.texto(self.izq - 8, y - ALTO, texto, SUAVE, 2, "der")
        if self.categorias is None:
            for valor, texto in zip(self.marcas_x, self._textos_x):
                x = self.px(valor)
                lienzo.linea(x, self.abajo, x, self.abajo + 5, EJE)
                lienzo.texto(x, self.abajo + 10, texto, SUAVE, 2, "centro")
        else:
            for i, texto in enumerate(self.categorias):
                inicio, ancho = self.banda(i)
                centro = inicio + ancho / 2
                if self.vertical:
                    largo = ancho_texto(texto, 2)
                    lienzo.texto(centro - ALTO, self.abajo + 10 + largo / 2, texto, SUAVE, 2, vertical=True)
                else:
                    lienzo.texto(centro, self.abajo + 10, texto, SUAVE, 2, "centro")
        if self.etiqueta_x:
            lienzo.texto((self.izq + self.der) / 2, lienzo.alto - 26, self.etiqueta_x, TEXTO, 2, "centro")
        if self.etiqueta_y:
            lienzo.texto(12, (self.arriba + self.abajo) / 2, self.etiqueta_y, TEXTO, 2, vertical=True)

    def ejes(self):
        """La linea de abajo y la de la izquierda, encima de todo."""
        cero = self.py(0) if self.y_min < 0 < self.y_max else self.abajo
        self.lienzo.linea(self.izq, cero, self.der, cero, EJE)
        self.lienzo.linea(self.izq, self.arriba, self.izq, self.abajo, EJE)


def _rango(valores):
    return min(valores), max(valores)


def _colores(g: Grafica, cuantos: int) -> list:
    if cuantos == 1 and g.color:
        return [g.color]
    return [PALETA[i % len(PALETA)] for i in range(cuantos)]


def _nombre_x(g):
    return g.etiqueta_x if g.etiqueta_x is not None else (g.x.nombre if g.x is not None else "")


def _nombre_y(g, por_defecto=""):
    if g.etiqueta_y is not None:
        return g.etiqueta_y
    return g.y.nombre if g.y is not None else por_defecto


# --- Los cinco tipos -------------------------------------------------------------

def _barras(lienzo, g, filas):
    categorias = _unicos(f[0] for f in filas)
    series = _unicos(f[2] for f in filas) if g.serie is not None else [None]
    colores = _colores(g, len(series))
    # si una categoria aparece varias veces en la misma serie, sus valores se suman
    valores = {}
    for x, y, s in filas:
        valores[(x, s)] = valores.get((x, s), 0) + y

    marco = Marco(lienzo, g, series, colores)
    minimo, maximo = _rango(list(valores.values()))
    # con una sola serie cada barra lleva su valor encima, y se deja aire para el texto
    aire = 1.08 if len(series) == 1 else 1
    marco.eje_y(min(minimo, 0) * aire, max(maximo, 0) * aire, _nombre_y(g))
    marco.eje_x_categorias(categorias, _nombre_x(g))
    marco.fondo()
    cero = marco.py(0)
    # todas las etiquetas con los mismos decimales: ninguno desde 100, uno si no
    paso = 1 if max(abs(v) for v in valores.values()) >= 100 or all(
        isinstance(v, int) for v in valores.values()) else 0.1
    for i, categoria in enumerate(categorias):
        inicio, ancho = marco.banda(i)
        ancho_barra = ancho * 0.72 / len(series)
        x = inicio + ancho * 0.14
        for serie, color in zip(series, colores):
            if (categoria, serie) in valores:
                valor = valores[(categoria, serie)]
                lienzo.rectangulo(x + 1, marco.py(valor), x + ancho_barra - 1, cero, color)
                texto = numero(valor, paso)
                if len(series) == 1 and ancho_texto(texto, 2) <= ancho_barra + 8:
                    y_texto = marco.py(valor) - ALTO * 2 - 6 if valor >= 0 else marco.py(valor) + 6
                    lienzo.texto(x + ancho_barra / 2, y_texto, texto, SUAVE, 2, "centro")
            x += ancho_barra
    marco.ejes()


def _lineas(lienzo, g, filas):
    series = _unicos(f[2] for f in filas) if g.serie is not None else [None]
    colores = _colores(g, len(series))
    marco = Marco(lienzo, g, series, colores)
    marco.eje_y(*_rango([f[1] for f in filas]), _nombre_y(g))
    numerico = all(es_numero(f[0]) for f in filas)
    if numerico:
        marco.eje_x_numerico(*_rango([f[0] for f in filas]), _nombre_x(g))
        posicion = marco.px
    else:
        categorias = _unicos(f[0] for f in filas)
        marco.eje_x_categorias(categorias, _nombre_x(g))
        def posicion(x):
            inicio, ancho = marco.banda(categorias.index(x))
            return inicio + ancho / 2
    marco.fondo()
    for serie, color in zip(series, colores):
        puntos = [(x, y) for x, y, s in filas if s == serie]
        if numerico:
            puntos.sort(key=lambda p: p[0])
        pixeles = [(posicion(x), marco.py(y)) for x, y in puntos]
        for (x0, y0), (x1, y1) in zip(pixeles, pixeles[1:]):
            lienzo.linea(x0, y0, x1, y1, color, 3)
        if len(pixeles) <= 40:
            for x, y in pixeles:
                lienzo.circulo(x, y, 4, color)
    marco.ejes()


def _histograma(lienzo, g, filas):
    datos = sorted(f[0] for f in filas)
    # regla de Sturges si no se dice cuantos intervalos
    intervalos = g.intervalos or techo_log2(len(datos)) + 1
    minimo, maximo = datos[0], datos[-1]
    if minimo == maximo:
        minimo, maximo = minimo - 0.5, maximo + 0.5
    ancho = (maximo - minimo) / intervalos
    conteos = [0] * intervalos
    for valor in datos:
        conteos[min(int((valor - minimo) / ancho), intervalos - 1)] += 1

    color = g.color or PALETA[0]
    marco = Marco(lienzo, g)
    marco.eje_y(0, max(conteos), _nombre_y(g, "Frecuencia"))
    marco.eje_x_numerico(minimo, maximo, _nombre_x(g))
    marco.fondo()
    for i, conteo in enumerate(conteos):
        if conteo:
            x0, x1 = marco.px(minimo + i * ancho), marco.px(minimo + (i + 1) * ancho)
            lienzo.rectangulo(x0 + 1, marco.py(conteo), x1 - 1, marco.abajo, color)
    marco.ejes()


def _dispersion(lienzo, g, filas):
    series = _unicos(f[2] for f in filas) if g.serie is not None else [None]
    colores = _colores(g, len(series))
    marco = Marco(lienzo, g, series, colores)
    marco.eje_y(*_rango([f[1] for f in filas]), _nombre_y(g))
    marco.eje_x_numerico(*_rango([f[0] for f in filas]), _nombre_x(g), margen=0.03)
    marco.fondo()
    for serie, color in zip(series, colores):
        for x, y, s in filas:
            if s == serie:
                lienzo.circulo(marco.px(x), marco.py(y), 4, color)
    marco.ejes()


def _caja(lienzo, g, filas):
    # sin eje_x sale una sola caja con toda la columna
    grupos = _unicos(f[0] for f in filas) if g.x is not None else [g.y.nombre or "datos"]
    datos = {grupo: sorted(y for x, y, _ in filas if g.x is None or x == grupo) for grupo in grupos}
    color = g.color or PALETA[0]

    marco = Marco(lienzo, g)
    marco.eje_y(*_rango([f[1] for f in filas]), _nombre_y(g))
    marco.eje_x_categorias(grupos, _nombre_x(g) if g.x is not None else "")
    marco.fondo()
    for i, grupo in enumerate(grupos):
        valores = datos[grupo]
        q1, mediana, q3 = (cuantil(valores, q) for q in (0.25, 0.5, 0.75))
        rango = q3 - q1
        # los bigotes llegan hasta el dato mas lejano que no se pase de 1,5 veces el rango
        dentro = [v for v in valores if q1 - 1.5 * rango <= v <= q3 + 1.5 * rango]
        inicio, ancho = marco.banda(i)
        centro, medio = inicio + ancho / 2, min(ancho * 0.3, 60)
        lienzo.linea(centro, marco.py(dentro[0]), centro, marco.py(dentro[-1]), EJE)
        for extremo in (dentro[0], dentro[-1]):
            lienzo.linea(centro - medio / 2, marco.py(extremo), centro + medio / 2, marco.py(extremo), EJE)
        lienzo.rectangulo(centro - medio, marco.py(q3), centro + medio, marco.py(q1), aclarar(color))
        lienzo.borde(round(centro - medio), round(marco.py(q3)), round(centro + medio), round(marco.py(q1)), color)
        lienzo.linea(centro - medio, marco.py(mediana), centro + medio, marco.py(mediana), color, 3)
        for v in valores:
            if v not in dentro:
                lienzo.circulo(centro, marco.py(v), 4, color, relleno=False)
    marco.ejes()
