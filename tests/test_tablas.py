"""Pruebas de nuestra libreria de tablas, sin pasar por el lenguaje."""

import pytest

from evangelion.tablas import Columna, Tabla, escribir_csv, inferir, leer_csv, partir_csv


@pytest.fixture
def pilotos():
    return Tabla(["piloto", "unidad", "sinc"], {
        "piloto": ["Shinji", "Rei", "Asuka", "Rei", "Toji"],
        "unidad": ["EVA-01", "EVA-00", "EVA-02", "EVA-00", "EVA-03"],
        "sinc": [60, 50, 90, None, 30],
    })


# --- CSV ------------------------------------------------------------------------

def test_partir_csv_sencillo():
    assert partir_csv("a,b\n1,2\n") == [["a", "b"], ["1", "2"]]


def test_partir_csv_con_comillas():
    texto = 'nombre,frase\n"Ikari, Shinji","dijo ""no"" y\nse fue"\n'
    assert partir_csv(texto) == [["nombre", "frase"], ["Ikari, Shinji", 'dijo "no" y\nse fue']]


def test_partir_csv_otros_separadores_y_saltos_de_windows():
    assert partir_csv("a;b\r\n1;2\r\n\r\n3;4", ";") == [["a", "b"], ["1", "2"], ["3", "4"]]


def test_partir_csv_campos_vacios():
    assert partir_csv("a,,c\n,,\n") == [["a", "", "c"], ["", "", ""]]


@pytest.mark.parametrize("textos, esperado", [
    (["1", "20", "-3"], [1, 20, -3]),
    (["1", "2.5", ""], [1.0, 2.5, None]),
    (["1e3", ".5"], [1000.0, 0.5]),
    (["EVA-01", "7"], ["EVA-01", "7"]),
    (["2015-06-22", ""], ["2015-06-22", None]),
    (["nan", "1"], ["nan", "1"]),
])
def test_inferir_tipos(textos, esperado):
    assert inferir(textos) == esperado


def test_leer_y_escribir_csv(tmp_path):
    tabla = Tabla(["nombre", "valor", "ok", "nota"], {
        "nombre": ["Ikari, Shinji", 'el "tercer" elegido'],
        "valor": [1 / 3, None],
        "ok": [True, False],
        "nota": [7, 8],
    })
    escribir_csv(tabla, tmp_path / "t.csv")
    leida = leer_csv(tmp_path / "t.csv")
    assert leida.columnas == tabla.columnas
    assert leida["nombre"].valores == tabla["nombre"].valores
    assert leida["valor"].valores == [0.3333, None]
    assert leida["ok"].valores == ["verdadero", "falso"]
    assert leida["nota"].valores == [7, 8]


def test_leer_csv_con_errores(tmp_path):
    (tmp_path / "vacio.csv").write_text("", encoding="utf-8")
    (tmp_path / "chueco.csv").write_text("a,b\n1\n", encoding="utf-8")
    (tmp_path / "repetido.csv").write_text("a,a\n1,2\n", encoding="utf-8")
    for nombre in ("vacio.csv", "chueco.csv", "repetido.csv"):
        with pytest.raises(ValueError):
            leer_csv(tmp_path / nombre)


# --- Columna --------------------------------------------------------------------

def test_clase_de_una_columna():
    assert Columna([1, 2.5, None]).clase() == "numero"
    assert Columna(["a", None]).clase() == "texto"
    assert Columna([True, False]).clase() == "booleano"
    assert Columna([None, None]).clase() == "nulo"


def test_operaciones_fila_por_fila():
    a, b = Columna([1, 2, None]), Columna([10, 20, 30])
    assert (a + b).valores == [11, 22, None]
    assert (a * 2).valores == [2, 4, None]
    assert (10 - a).valores == [9, 8, None]
    assert (2 ** a).valores == [2, 4, None]
    assert (b / a).valores == [10.0, 10.0, None]
    assert (b / Columna([0, 5, 3])).valores == [None, 4.0, 10.0]
    assert (-a).valores == [-1, -2, None]


def test_comparaciones_y_logica():
    a = Columna([1, 5, None])
    assert (a > 2).valores == [False, True, False]
    assert (a == 1).valores == [True, False, False]
    assert (a != 1).valores == [False, True, True]
    assert ((a > 0) & (a < 3)).valores == [True, False, False]
    assert ((a > 2) | (a == 1)).valores == [True, True, False]
    assert (~(a > 2)).valores == [True, False, True]
    assert a.es_nulo().valores == [False, False, True]


def test_estadisticas():
    c = Columna([2, 4, 4, 4, 5, 5, 7, 9, None])
    assert (c.contar(), c.faltantes(), c.distintos()) == (8, 1, 5)
    assert (c.suma(), c.media(), c.mediana()) == (40, 5, 4.5)
    assert (c.minimo(), c.maximo()) == (2, 9)
    # suma de cuadrados 32, entre n - 1 = 7
    assert c.desviacion() == pytest.approx((32 / 7) ** 0.5)
    assert Columna([1, 3, 2]).mediana() == 2


def test_estadisticas_sin_datos():
    vacia = Columna([None])
    assert (vacia.contar(), vacia.suma()) == (0, 0)
    assert vacia.media() is None and vacia.mediana() is None and vacia.minimo() is None
    assert Columna([5]).desviacion() is None


def test_convertir():
    assert Columna(["1", "2.9", None]).convertir("entero").valores == [1, 2, None]
    assert Columna([1, 0, 2.5]).convertir("booleano").valores == [True, False, True]
    assert Columna(["si", "No", "VERDADERO"]).convertir("booleano").valores == [True, False, True]
    assert Columna([1, True]).convertir("texto").valores == ["1", "verdadero"]
    with pytest.raises(ValueError):
        Columna(["Rei"]).convertir("real")
    with pytest.raises(ValueError):
        Columna(["quizas"]).convertir("booleano")


# --- Tabla ----------------------------------------------------------------------

def test_seleccionar_renombrar_y_quitar(pilotos):
    assert pilotos.seleccionar(["sinc", "piloto"]).columnas == ["sinc", "piloto"]
    assert pilotos.sin_columnas(["unidad"]).columnas == ["piloto", "sinc"]
    assert pilotos.renombrar({"sinc": "sincronizacion"}).columnas == ["piloto", "unidad", "sincronizacion"]
    assert pilotos.columnas == ["piloto", "unidad", "sinc"]


def test_filtrar_y_primeras(pilotos):
    altas = pilotos.filtrar(pilotos["sinc"] >= 60)
    assert altas["piloto"].valores == ["Shinji", "Asuka"]
    assert len(pilotos.primeras(2)) == 2 and len(pilotos.primeras(99)) == 5


def test_con_columna_no_toca_la_original(pilotos):
    nueva = pilotos.con_columna("doble", pilotos["sinc"] * 2).con_columna("base", "NERV")
    assert nueva["doble"].valores == [120, 100, 180, None, 60]
    assert nueva["base"].valores == ["NERV"] * 5
    assert pilotos.columnas == ["piloto", "unidad", "sinc"]


def test_ordenar(pilotos):
    assert pilotos.ordenar(["sinc"], [True])["sinc"].valores == [30, 50, 60, 90, None]
    assert pilotos.ordenar(["sinc"], [False])["sinc"].valores == [90, 60, 50, 30, None]
    por_dos = pilotos.ordenar(["unidad", "sinc"], [True, False])
    assert por_dos["sinc"].valores == [50, None, 60, 90, 30]


def test_duplicados_y_faltantes(pilotos):
    assert pilotos.sin_duplicados(["piloto"])["piloto"].valores == ["Shinji", "Rei", "Asuka", "Toji"]
    assert len(pilotos.sin_duplicados()) == 5
    assert len(pilotos.sin_faltantes()) == 4
    assert len(pilotos.sin_faltantes(["piloto"])) == 5


def test_resumir_por_grupos(pilotos):
    resumen = pilotos.resumir(["unidad"], [("n", "contar", None), ("total", "suma", "sinc"),
                                           ("promedio", "media", "sinc")])
    assert resumen.columnas == ["unidad", "n", "total", "promedio"]
    assert resumen.registros()[1] == {"unidad": "EVA-00", "n": 2, "total": 50, "promedio": 50.0}
    assert resumen["unidad"].valores == ["EVA-01", "EVA-00", "EVA-02", "EVA-03"]


def test_resumir_sin_grupos_y_tabla_vacia(pilotos):
    assert pilotos.resumir([], [("n", "contar", None)]).registros() == [{"n": 5}]
    vacia = pilotos.primeras(0)
    assert len(vacia.resumir(["unidad"], [("n", "contar", None)])) == 0


def test_como_texto(pilotos):
    lineas = pilotos.con_columna("mitad", pilotos["sinc"] / 2).primeras(2).como_texto().splitlines()
    assert lineas == [
        "piloto  unidad  sinc  mitad",
        "Shinji  EVA-01    60  30.00",
        "Rei     EVA-00    50  25.00",
    ]
