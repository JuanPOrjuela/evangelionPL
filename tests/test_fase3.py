"""Fase 3: lienzos, formato PNG hecho a mano, graficas y caso de estudio."""

import binascii
import shutil
import struct
import zlib
from pathlib import Path

import pytest

from evangelion import graficas
from evangelion.cli import main
from evangelion.fuente import _LETRAS, ancho_texto, pixeles_de
from evangelion.graficas import Grafica, cuantil, marcas, numero
from evangelion.lienzo import LienzoPNG, LienzoSVG, adler32, crc32, deflate, zlib_comprimir
from evangelion.tablas import Columna

from test_fase2 import CARGA, correr, datos, falla  # noqa: F401  (datos es un fixture)

RAIZ = Path(__file__).resolve().parents[1]


def leer_png(ruta):
    """Abre un PNG con zlib de Python (solo en las pruebas) para revisar el nuestro."""
    contenido = Path(ruta).read_bytes()
    assert contenido[:8] == b"\x89PNG\r\n\x1a\n"
    bloques, i = {}, 8
    while i < len(contenido):
        largo, = struct.unpack(">I", contenido[i:i + 4])
        tipo, datos_bloque = contenido[i + 4:i + 8], contenido[i + 8:i + 8 + largo]
        crc, = struct.unpack(">I", contenido[i + 8 + largo:i + 12 + largo])
        assert crc == binascii.crc32(tipo + datos_bloque), f"CRC malo en {tipo}"
        bloques[tipo] = datos_bloque
        i += 12 + largo
    ancho, alto = struct.unpack(">II", bloques[b"IHDR"][:8])
    crudo = zlib.decompress(bloques[b"IDAT"])
    assert len(crudo) == alto * (ancho + 1)
    return ancho, alto, bloques[b"PLTE"], crudo


# --- El formato PNG por dentro ---------------------------------------------------

@pytest.mark.parametrize("prueba", [b"", b"a", b"abcabcabc" * 50, bytes(range(256)) * 20, b"\x00" * 70000],
                         ids=["vacio", "una_letra", "repetido", "todos_los_bytes", "ceros"])
def test_nuestro_deflate_lo_entiende_zlib(prueba):
    assert zlib.decompress(zlib_comprimir(prueba, 64)) == prueba


def test_crc_y_adler_dan_lo_mismo_que_la_libreria_estandar():
    for texto in (b"", b"IEND", b"evangelionPL" * 1000):
        assert crc32(texto) == binascii.crc32(texto)
        assert adler32(texto) == zlib.adler32(texto)


def test_deflate_comprime_las_zonas_de_un_color():
    assert len(deflate(b"\x07" * 100000)) < 1000


def test_el_lienzo_png_pinta_donde_debe(tmp_path):
    lienzo = LienzoPNG(40, 30)
    lienzo.rectangulo(10, 5, 19, 9, "#ff0000")
    lienzo.linea(0, 29, 39, 29, "#0000ff")
    lienzo.guardar(tmp_path / "a.png")
    ancho, alto, paleta, crudo = leer_png(tmp_path / "a.png")
    assert (ancho, alto) == (40, 30)
    colores = [tuple(paleta[i:i + 3]) for i in range(0, len(paleta), 3)]

    def pixel(x, y):
        return colores[crudo[y * 41 + 1 + x]]   # cada fila empieza con el byte del filtro

    assert pixel(0, 0) == (255, 255, 255)
    assert pixel(15, 7) == (255, 0, 0) and pixel(20, 7) == (255, 255, 255)
    assert pixel(39, 29) == (0, 0, 255)


def test_el_lienzo_no_se_sale_de_los_bordes():
    lienzo = LienzoPNG(10, 10)
    lienzo.rectangulo(-50, -50, 50, 50, "#000000")
    lienzo.circulo(0, 0, 30, "#ff0000")
    lienzo.texto(-100, 5, "fuera", "#00ff00")
    assert len(lienzo.pixeles) == 100


def test_el_lienzo_svg_escribe_las_figuras():
    lienzo = LienzoSVG(100, 50)
    lienzo.linea(0, 0, 10, 10, "#123456")
    lienzo.texto(5, 5, "a < b & c", "#000000")
    svg = lienzo.como_svg()
    assert svg.startswith("<svg") and 'stroke="#123456"' in svg and "a &lt; b &amp; c" in svg


# --- La letra de pixeles ---------------------------------------------------------

def test_todas_las_letras_miden_cinco_de_ancho():
    for letra, dibujo in _LETRAS.items():
        filas = dibujo.split("|")
        assert len(filas) in (7, 9), letra
        assert all(len(f) == 5 for f in filas), letra


def test_letra_desconocida_sale_como_interrogacion():
    assert pixeles_de("@") == pixeles_de("?")
    assert pixeles_de("Á") == pixeles_de("A")
    assert ancho_texto("abc", 2) == (3 * 6 - 1) * 2


# --- Calculos de las graficas ------------------------------------------------------

def test_marcas_redondas():
    assert marcas(0, 10) == [0, 2, 4, 6, 8, 10]
    assert marcas(0.26, 6.63) == [0, 2, 4, 6, 8]
    assert marcas(0.26, 6.63, 8) == [0, 1, 2, 3, 4, 5, 6, 7]
    assert marcas(5, 5) == [4, 4.5, 5, 5.5, 6]


def test_numeros_con_formato_colombiano():
    assert numero(1970, 10) == "1970"
    assert numero(25000, 5000) == "25.000"
    assert numero(2.5, 0.5) == "2,5"
    assert numero(3_000_000, 1_000_000) == "3 M"
    assert numero(-0.0, 1) == "0"


def test_cuartiles_con_interpolacion():
    datos_ = [1, 2, 3, 4]
    assert (cuantil(datos_, 0), cuantil(datos_, 0.5), cuantil(datos_, 1)) == (1, 2.5, 4)
    assert cuantil(datos_, 0.25) == 1.75


@pytest.mark.parametrize("tipo", graficas.TIPOS)
def test_cada_tipo_se_dibuja_en_png_y_svg(tipo, tmp_path):
    categorias = tipo in ("barras", "caja")
    x = Columna(["a", "b", "a", "c", "b", "a"] if categorias else [1, 2, 3, 4, 5, 6], "x")
    y = None if tipo == "histograma" else Columna([3, 1.5, 4, None, 5, 9], "y")
    serie = Columna(["s1", "s2", "s1", "s2", "s1", "s2"], "s") if tipo in ("lineas", "dispersion") else None
    g = Grafica(tipo, x=x, y=y, serie=serie, titulo=f"Prueba de {tipo}", ancho=500, alto=320)
    # la fila con el faltante en y solo se salta cuando la grafica usa y
    assert graficas.guardar(g, tmp_path / "g.png") == (6 if tipo == "histograma" else 5)
    assert leer_png(tmp_path / "g.png")[:2] == (500, 320)
    graficas.guardar(g, tmp_path / "g.svg")
    assert "<svg" in (tmp_path / "g.svg").read_text(encoding="utf-8")


def test_sin_datos_no_hay_grafica():
    with pytest.raises(ValueError):
        graficas.dibujar(Grafica("barras", x=Columna(["a"], "x"), y=Columna([None], "y")))


# --- HOLOGRAM desde el lenguaje ----------------------------------------------------

def test_hologram_guarda_donde_se_le_dice(datos):
    interprete = correr(CARGA + '\nHOLOGRAM caja de t { eje_x: piloto, eje_y: sincronizacion, '
                                'archivo: "graficas/caja.png", titulo: "Cajas", color: "verde" }')
    assert interprete.graficas == ["graficas/caja.png"]
    assert leer_png(datos / "graficas" / "caja.png")[:2] == (960, 600)


def test_hologram_con_serie_tamano_y_svg(datos):
    correr(CARGA + '\nHOLOGRAM lineas de t |> SYNC n = sincronizacion { eje_x: armonicos, eje_y: n, '
                   'serie: piloto, ancho: 640, alto: 400, leyenda: falso, archivo: "l.svg" }')
    assert 'width="640"' in (datos / "l.svg").read_text(encoding="utf-8")


@pytest.mark.parametrize("opciones, mensaje", [
    ("eje_x: piloto", "necesita eje_y"),
    ("eje_y: sincronizacion", "necesita eje_x"),
    ("eje_x: piloto, eje_y: piloto", "tiene que ser numérico"),
    ('eje_x: "piloto", eje_y: sincronizacion', "tiene que ser una columna"),
    ("eje_x: piloto, eje_y: sincronizacion, titulo: 5", "va entre comillas"),
    ('eje_x: piloto, eje_y: sincronizacion, archivo: "g.jpg"', ".png o en .svg"),
    ('eje_x: piloto, eje_y: sincronizacion, color: "fucsia"', "no existe"),
    ("eje_x: piloto, eje_y: sincronizacion, ancho: 10", "entre 320 y 4000"),
    ("eje_x: piloto, eje_y: sincronizacion, leyenda: 1", "verdadero o falso"),
    ("eje_x: piloto, eje_y: sincronizacion, ejex: 1", "¿Quisiste decir"),
    ("eje_x: pilot, eje_y: sincronizacion", "¿Quisiste decir 'piloto'?"),
])
def test_errores_de_hologram(datos, opciones, mensaje):
    assert mensaje in falla(CARGA + f"\nHOLOGRAM barras de t {{ {opciones} }}")


def test_histograma_pide_intervalos_enteros(datos):
    assert "número entero" in falla(CARGA + "\nHOLOGRAM histograma de t { eje_x: sincronizacion, intervalos: 2.5 }")


def test_reemplazar_texto(datos):
    interprete = correr(CARGA + ' |> SYNC piloto = reemplazar(piloto, "Shinji", "Ikari")')
    assert "Ikari" in interprete.simbolos.buscar("t").valor["piloto"].valores
    assert "reemplazar() va así" in falla(CARGA + " |> SYNC piloto = reemplazar(piloto, 1, 2)")


# --- Caso de estudio de punta a punta -----------------------------------------------

def test_el_caso_de_estudio_corre_y_deja_todo(tmp_path, monkeypatch, capsys):
    shutil.copytree(RAIZ / "datos", tmp_path / "datos")
    shutil.copytree(RAIZ / "caso_estudio", tmp_path / "caso_estudio", ignore=shutil.ignore_patterns("resultados"))
    monkeypatch.chdir(tmp_path)
    assert main(["caso_estudio/co2_latam.eva"]) == 0
    salida = capsys.readouterr().out
    assert "Felicidades" in salida
    resultados = tmp_path / "caso_estudio" / "resultados"
    pngs = sorted(p.name for p in resultados.glob("*.png"))
    assert len(pngs) >= 4
    assert {p.split("_")[1] for p in pngs} == set(graficas.TIPOS)
    for png in pngs:
        leer_png(resultados / png)
    assert (resultados / "emisiones_2023.csv").is_file()
    assert "Colombia emite menos CO2 por persona" in salida
