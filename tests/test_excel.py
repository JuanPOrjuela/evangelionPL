"""Lector de Excel (.xlsx) hecho a mano: el ZIP, el descompresor DEFLATE y el XML.
Aqui (en las pruebas, que no son parte del lenguaje) se usan zipfile y zlib de Python
solo para fabricar archivos de prueba y comparar resultados."""

import zipfile
import zlib
from pathlib import Path

import pytest

from evangelion.excel import _columna, _texto_xml, inflar, leer_xlsx
from evangelion.tablas import leer_archivo

from test_fase2 import correr, datos, falla, valor  # noqa: F401  (datos es un fixture)

RAIZ = Path(__file__).resolve().parents[1]


def v(codigo, nombre="r"):
    return valor(correr(codigo), nombre)


# --- El descompresor contra el compresor de Python ------------------------------------------

TEXTOS = {
    "vacio": b"",
    "corto": b"hola evangelion",
    "repetido": b"abcabcabcabc" * 5000,
    "una_letra": b"a" * 70000,                     # distancia 1, copias que se pisan
    "xml": b"".join(b'<row r="%d"><c r="A%d"><v>%d</v></c></row>' % (i, i, i * 7) for i in range(3000)),
    "bytes": bytes((i * 37 + i // 7) % 256 for i in range(50000)),
}
ESTRATEGIAS = {"normal": (6, zlib.Z_DEFAULT_STRATEGY), "fijo": (6, zlib.Z_FIXED),
               "solo_huffman": (6, zlib.Z_HUFFMAN_ONLY), "rle": (6, zlib.Z_RLE),
               "sin_comprimir": (0, zlib.Z_DEFAULT_STRATEGY), "maximo": (9, zlib.Z_DEFAULT_STRATEGY)}


@pytest.mark.parametrize("estrategia", ESTRATEGIAS)
@pytest.mark.parametrize("texto", TEXTOS)
def test_inflar_deshace_deflate(texto, estrategia):
    nivel, tipo = ESTRATEGIAS[estrategia]
    compresor = zlib.compressobj(nivel, zlib.DEFLATED, -15, 8, tipo)
    comprimido = compresor.compress(TEXTOS[texto]) + compresor.flush()
    assert inflar(comprimido) == TEXTOS[texto]


def test_inflar_avisa_si_los_datos_estan_danados():
    with pytest.raises(ValueError):
        inflar(b"\x07\xff\xff\xff")


# --- El XML ------------------------------------------------------------------------------

def test_letras_de_columna_y_marcas_del_xml():
    assert (_columna("A1"), _columna("B7"), _columna("Z3"), _columna("AA10"), _columna("AB2")) == (0, 1, 25, 26, 27)
    assert _texto_xml("Ana &amp; Luis &lt;3 &#233; &#xF1; &quot;si&quot;") == 'Ana & Luis <3 é ñ "si"'
    assert _texto_xml("&amp;lt;") == "&lt;"


# --- Un libro de Excel fabricado a mano -----------------------------------------------------

LIBRO = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Notas" sheetId="1" r:id="rId1"/><sheet name="Otra &amp; mas" sheetId="2" r:id="rId2"/></sheets>
</workbook>"""
RELACIONES = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships><Relationship Id="rId1" Type="worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="worksheet" Target="/xl/worksheets/hoja_b.xml"/></Relationships>"""
COMPARTIDOS = """<?xml version="1.0" encoding="UTF-8"?>
<sst count="5"><si><t>nombre</t></si><si><t>nota</t></si><si><t>aprobo</t></si>
<si><r><rPr><b/></rPr><t>Ana</t></r><r><t xml:space="preserve"> María</t></r></si><si><t>Luis &amp; Co</t></si></sst>"""
HOJA = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet><cols><col min="1" max="3" width="10"/></cols><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c><c r="D1" t="inlineStr"><is><t>ciudad</t></is></c></row>
<row r="2"><c r="A2" t="s" s="1"><v>3</v></c><c r="B2"><v>4.5</v></c><c r="C2" t="b"><v>1</v></c><c r="D2" t="str"><f>A1</f><v>Bogotá</v></c></row>
<row r="3" spans="1:4"><c r="A3" t="s"><v>4</v></c><c r="B3"><v>1.5E-2</v></c><c r="C3" t="b"><v>0</v></c></row>
<row r="4"><c r="A4" s="2"/></row>
<row r="6"><c r="B6"><v>3</v></c><c r="D6" t="inlineStr"><is><t>Cali</t></is></c></row>
</sheetData></worksheet>"""
HOJA_B = """<worksheet><sheetData><row><c><v>1</v></c><c><v>2</v></c></row><row><c><v>3</v></c><c><v>4</v></c></row></sheetData></worksheet>"""


def libro(ruta, comprimir=zipfile.ZIP_DEFLATED, con_compartidos=True):
    with zipfile.ZipFile(ruta, "w", comprimir) as z:
        z.writestr("xl/workbook.xml", LIBRO)
        z.writestr("xl/_rels/workbook.xml.rels", RELACIONES)
        if con_compartidos:
            z.writestr("xl/sharedStrings.xml", COMPARTIDOS)
        z.writestr("xl/worksheets/sheet1.xml", HOJA)
        z.writestr("xl/worksheets/hoja_b.xml", HOJA_B)
    return ruta


@pytest.mark.parametrize("comprimir", [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED])
def test_leer_xlsx_saca_las_celdas(tmp_path, comprimir):
    filas = leer_xlsx(libro(tmp_path / "notas.xlsx", comprimir))
    assert filas == [["nombre", "nota", "aprobo", "ciudad"],
                     ["Ana María", "4.5", "verdadero", "Bogotá"],
                     ["Luis & Co", "1.5E-2", "falso", ""],
                     ["", "3", "", "Cali"]]       # la fila 4 solo tenia formato: no cuenta


def test_la_tabla_del_excel_tiene_tipos(tmp_path):
    t = leer_archivo(libro(tmp_path / "notas.xlsx"))
    assert t.columnas == ["nombre", "nota", "aprobo", "ciudad"]
    assert t["nota"].valores == [4.5, 0.015, 3.0]
    assert t["nombre"].valores == ["Ana María", "Luis & Co", None]
    assert t["ciudad"].valores == ["Bogotá", None, "Cali"]


def test_escoger_la_hoja(tmp_path):
    ruta = libro(tmp_path / "notas.xlsx")
    b = leer_archivo(ruta, hoja="Otra & mas", encabezado=False)
    assert b.columnas == ["col1", "col2"] and b["col1"].valores == [1, 3]
    assert leer_archivo(ruta, hoja=2, encabezado=False)["col2"].valores == [2, 4]
    with pytest.raises(ValueError, match="las hojas son: Notas, Otra & mas"):
        leer_archivo(ruta, hoja="Nada")
    with pytest.raises(ValueError, match="la hoja 3 no existe"):
        leer_archivo(ruta, hoja=3)


def test_sin_textos_compartidos(tmp_path):
    # un libro que solo tiene numeros no trae sharedStrings.xml
    filas = leer_xlsx(libro(tmp_path / "x.xlsx", con_compartidos=False), hoja=2)
    assert filas == [["1", "2"], ["3", "4"]]


def test_un_archivo_que_no_es_excel(tmp_path):
    (tmp_path / "falso.xlsx").write_text("esto no es un zip", encoding="utf-8")
    with pytest.raises(ValueError, match="no es un archivo de Excel"):
        leer_xlsx(tmp_path / "falso.xlsx")


# --- Desde el lenguaje -----------------------------------------------------------------------

def test_cargar_un_xlsx_desde_el_lenguaje(datos):
    libro(datos / "notas.xlsx")
    assert v('t = cargar "notas.xlsx"\nr = media(t.nota)') == pytest.approx((4.5 + 0.015 + 3) / 3)
    assert v('t = cargar "notas.xlsx" con { hoja: 2, encabezado: falso }\nr = suma(t.col1)') == 4
    assert v('t = ENTRY_PLUG "notas.xlsx" |> AT_FIELD donde nota > 1\nr = filas(t)') == 2


def test_errores_claros_con_otros_formatos(datos):
    (datos / "viejo.xls").write_bytes(b"\xd0\xcf\x11\xe0")
    assert "Libro de Excel (.xlsx) o CSV" in falla('t = cargar "viejo.xls"')
    assert "solo sirve con archivos de Excel" in falla('t = cargar "p.csv" con { hoja: 1 }')
    libro(datos / "notas.xlsx")
    assert "no hay una hoja llamada" in falla('t = cargar "notas.xlsx" con { hoja: "Nada" }')


def test_el_excel_del_profe_da_lo_mismo_que_el_csv():
    excel = leer_archivo(RAIZ / "datos" / "data.xlsx")
    csv = leer_archivo(RAIZ / "datos" / "data.csv")
    assert excel.columnas == csv.columnas and len(excel) == 10280
    for nombre in csv.columnas:
        assert excel[nombre].valores == csv[nombre].valores
