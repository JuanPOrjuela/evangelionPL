"""Fase 2: el interprete, la tabla de simbolos y los errores semanticos."""

from pathlib import Path

import pytest

from evangelion.analizador import analizar
from evangelion.cli import main
from evangelion.errores import ErrorSemantico
from evangelion.interprete import Interprete, distancia
from evangelion.tablas import leer_csv

RAIZ = Path(__file__).resolve().parents[1]
VALIDOS = sorted((RAIZ / "ejemplos").glob("*.eva"))
CON_ERROR = sorted((RAIZ / "ejemplos" / "errores").glob("*.eva"))
SEMANTICOS = [r for r in CON_ERROR if r.name.startswith("sem")]

CSV = """piloto,unidad,sincronizacion,armonicos
Shinji,EVA-01,60,1.0
Shinji,EVA-01,80,1.2
Rei,EVA-00,50,
Rei,EVA-00,,0.9
Asuka,EVA-02,90,1.1
"""
CARGA = 't = ENTRY_PLUG "p.csv"'


@pytest.fixture
def datos(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "p.csv").write_text(CSV, encoding="utf-8")
    return tmp_path


def correr(codigo) -> Interprete:
    res = analizar(codigo)
    assert res.valido, [str(e) for e in res.errores]
    interprete = Interprete()
    interprete.ejecutar(res.arbol)
    return interprete


def valor(interprete, nombre):
    return interprete.simbolos.buscar(nombre).valor


def falla(codigo) -> str:
    with pytest.raises(ErrorSemantico) as info:
        correr(codigo)
    assert info.value.error.fase == "semantico"
    return info.value.error.mensaje


# --- Expresiones y tabla de simbolos -------------------------------------------

@pytest.mark.parametrize("expresion, esperado", [
    ("1 + 2 * 3", 7),
    ("(1 + 2) * 3", 9),
    ("2 ^ 3 ^ 2", 512),
    ("-2 ^ 2", -4),
    ("7 % 4", 3),
    ("10 / 4", 2.5),
    ('"EVA" + "-01"', "EVA-01"),
    ("3 > 2 y no (1 == 2)", True),
    ("falso o 2 <= 1", False),
    ("nulo == nulo", True),
    ("5 != nulo", True),
    ('mayusculas("nerv")', "NERV"),
    ("redondear(3.14159, 2)", 3.14),
    ("absoluto(-5)", 5),
])
def test_expresiones(expresion, esperado):
    assert valor(correr(f"x = {expresion}"), "x") == esperado


def test_la_tabla_de_simbolos_guarda_clase_y_linea(datos):
    interprete = correr(CARGA + '\nn = 5\n\nnombre = "Rei"\nlisto = verdadero')
    clases = {s: interprete.simbolos.buscar(s).clase for s in interprete.simbolos.nombres()}
    assert clases == {"t": "tabla", "n": "numero", "nombre": "texto", "listo": "booleano"}
    assert interprete.simbolos.buscar("nombre").linea == 4


def test_una_variable_se_puede_volver_a_asignar():
    assert valor(correr("x = 1\nx = x + 1"), "x") == 2


# --- Etapas ---------------------------------------------------------------------

def test_cargar_y_seleccionar(datos):
    t = valor(correr(CARGA + " |> TARGET [piloto, sincronizacion]"), "t")
    assert t.columnas == ["piloto", "sincronizacion"]
    assert len(t) == 5


def test_filtrar(datos):
    t = valor(correr(CARGA + ' |> AT_FIELD donde sincronizacion >= 60 y piloto != "Asuka"'), "t")
    assert t["sincronizacion"].valores == [60, 80]


def test_filtrar_por_nulo(datos):
    t = valor(correr(CARGA + " |> AT_FIELD donde sincronizacion == nulo"), "t")
    assert t["piloto"].valores == ["Rei"]
    t = valor(correr(CARGA + " |> AT_FIELD donde sincronizacion != nulo"), "t")
    assert len(t) == 4


def test_filtrar_una_tabla_que_ya_quedo_vacia(datos):
    t = valor(correr(CARGA + " |> AT_FIELD donde sincronizacion > 500 |> AT_FIELD donde armonicos > 1"), "t")
    assert len(t) == 0 and t.columnas == ["piloto", "unidad", "sincronizacion", "armonicos"]


def test_columna_calculada(datos):
    t = valor(correr(CARGA + " |> SYNC doble = sincronizacion * 2, mas = doble + 1"), "t")
    assert t["mas"].valores == [121, 161, 101, None, 181]


def test_las_etapas_no_cambian_la_tabla_original(datos):
    interprete = correr(CARGA + "\nu = t |> SYNC doble = sincronizacion * 2 |> DUMMY_PLUG armonicos = 0.0 |> BATTERY 2")
    original = valor(interprete, "t")
    assert "doble" not in original.columnas
    assert len(original) == 5
    assert original["armonicos"].valores[2] is None


def test_ordenar_y_limitar(datos):
    t = valor(correr(CARGA + " |> FORMATION por [sincronizacion desc] |> BATTERY 2"), "t")
    assert t["piloto"].valores == ["Asuka", "Shinji"]


def test_ordenar_por_dos_columnas_deja_los_faltantes_al_final(datos):
    t = valor(correr(CARGA + " |> FORMATION por [piloto asc, sincronizacion desc]"), "t")
    assert t["sincronizacion"].valores == [90, 50, None, 80, 60]


def test_renombrar_y_quitar_columnas(datos):
    t = valor(correr(CARGA + " |> CODENAME [piloto -> `Nombre del piloto`] |> EJECT columnas [armonicos]"), "t")
    assert t.columnas == ["Nombre del piloto", "unidad", "sincronizacion"]


def test_faltantes_quitar_y_rellenar(datos):
    sin_faltantes = valor(correr(CARGA + " |> EJECT faltantes"), "t")
    assert len(sin_faltantes) == 3
    relleno = valor(correr(CARGA + " |> DUMMY_PLUG sincronizacion = 0, armonicos = 1.0"), "t")
    assert relleno["sincronizacion"].faltantes() == 0
    assert relleno["armonicos"].valores[2] == 1.0


def test_rellenar_con_el_promedio(datos):
    t = valor(correr(CARGA + " |> DUMMY_PLUG sincronizacion = media(sincronizacion)"), "t")
    assert t["sincronizacion"].valores[3] == 70


def test_duplicados(datos):
    t = valor(correr(CARGA + " |> EJECT duplicados [piloto]"), "t")
    assert t["piloto"].valores == ["Shinji", "Rei", "Asuka"]


def test_convertir_tipos(datos):
    t = valor(correr(CARGA + " |> EQUIP sincronizacion -> texto |> EQUIP armonicos -> entero"), "t")
    assert t["sincronizacion"].valores == ["60", "80", "50", None, "90"]
    assert t["armonicos"].valores == [1, 1, None, 0, 1]


def test_agrupar_y_resumir(datos):
    t = valor(correr(CARGA + " |> SQUAD por [piloto]"
                             " |> MAGI n = contar(), promedio = media(sincronizacion), tope = maximo(sincronizacion)"
                             " |> FORMATION por [piloto]"), "t")
    assert t.registros() == [
        {"piloto": "Asuka", "n": 1, "promedio": 90.0, "tope": 90},
        {"piloto": "Rei", "n": 2, "promedio": 50.0, "tope": 50},
        {"piloto": "Shinji", "n": 2, "promedio": 70.0, "tope": 80},
    ]


def test_resumir_sin_agrupar_da_una_fila(datos):
    t = valor(correr(CARGA + " |> MAGI total = suma(sincronizacion), n = contar(sincronizacion)"), "t")
    assert t.registros() == [{"total": 280, "n": 4}]


def test_agregacion_sobre_una_columna_de_otra_tabla(datos):
    interprete = correr(CARGA + "\nm = media(t.sincronizacion)\nn = filas(t)")
    assert valor(interprete, "m") == 70
    assert valor(interprete, "n") == 5


def test_diagnostico(datos):
    t = valor(correr(CARGA + " |> DIAGNOSTIC"), "t")
    fila = next(r for r in t.registros() if r["columna"] == "sincronizacion")
    assert (fila["clase"], fila["validos"], fila["faltantes"], fila["media"]) == ("numero", 4, 1, 70)


def test_opciones_de_carga(datos):
    (datos / "q.csv").write_text("Rei;50\nAsuka;90\n", encoding="utf-8")
    t = valor(correr('t = ENTRY_PLUG "q.csv" con { separador: ";", encabezado: falso }'), "t")
    assert t.columnas == ["col1", "col2"]
    assert len(t) == 2


# --- Sentencias -----------------------------------------------------------------

def test_guardar_escribe_el_csv(datos):
    interprete = correr(CARGA + ' |> SQUAD por [unidad] |> MAGI n = contar()\nSEELE t como "salidas/n.csv"')
    guardado = leer_csv(datos / "salidas" / "n.csv")
    assert guardado.columnas == ["unidad", "n"]
    assert guardado["n"].suma() == 5
    assert interprete.reportes == ["salidas/n.csv"]


def test_mostrar(datos, capsys):
    correr(CARGA + "\nMONITOR t |> BATTERY 1\nMONITOR filas(t)")
    salida = capsys.readouterr().out
    assert "1 fila x 4 columnas" in salida
    assert "Shinji" in salida and "MONITOR: 5" in salida


def test_el_condicional_elige_la_rama():
    codigo = "x = 5\nPATTERN_BLUE x > %d { r = 1 } PATTERN_ORANGE { r = 2 }"
    assert valor(correr(codigo % 3), "r") == 1
    assert valor(correr(codigo % 9), "r") == 2


def test_la_grafica_se_revisa_pero_no_se_dibuja(datos, capsys):
    interprete = correr(CARGA + "\nHOLOGRAM barras de t { eje_x: piloto, eje_y: sincronizacion }")
    assert interprete.graficas == ["barras"]
    assert "fase 3" in capsys.readouterr().out


# --- Errores semanticos ---------------------------------------------------------

def test_variable_no_declarada():
    assert "no se ha declarado" in falla("MONITOR angel")


def test_columna_inexistente_con_sugerencia(datos):
    mensaje = falla(CARGA + " |> TARGET [pilto]")
    assert "no existe" in mensaje and "'piloto'" in mensaje


def test_distancia_entre_palabras():
    assert distancia("piloto", "piloto") == 0
    assert distancia("pilto", "piloto") == 1
    assert distancia("sincronisacion", "sincronizacion") == 1
    assert distancia("", "eva") == 3


def test_archivo_inexistente():
    assert "no existe el archivo" in falla('t = ENTRY_PLUG "no_esta.csv"')


def test_archivo_mal_formado(datos):
    (datos / "malo.csv").write_text("a,b\n1,2,3\n", encoding="utf-8")
    assert "no se pudo leer" in falla('t = ENTRY_PLUG "malo.csv"')


@pytest.mark.parametrize("expresion", ['"EVA" * 2', '1 + "uno"', "no 5", "verdadero y 3", '3 < "tres"', '1 == "1"'])
def test_tipos_incompatibles(expresion):
    assert "tipos incompatibles" in falla(f"x = {expresion}")


def test_tipos_incompatibles_en_columnas(datos):
    assert "tipos incompatibles" in falla(CARGA + " |> SYNC x = piloto - 1")
    assert "tipos incompatibles" in falla(CARGA + " |> MAGI x = suma(piloto)")
    assert "tipos incompatibles" in falla(CARGA + ' |> DUMMY_PLUG sincronizacion = "nada"')


def test_division_por_cero(datos):
    assert "cero" in falla("x = 4 / 0")
    # dentro de una columna no se detiene el programa, el dato queda faltante
    t = valor(correr(CARGA + " |> SYNC x = 100 / (sincronizacion - 60)"), "t")
    assert t["x"].valores == [None, 5.0, -10.0, None, 100 / 30]


def test_una_etapa_necesita_una_tabla():
    assert "solo funciona sobre una tabla" in falla("x = 5 |> BATTERY 2")


def test_squad_necesita_magi(datos):
    assert "MAGI" in falla(CARGA + " |> SQUAD por [piloto]")
    assert "MAGI" in falla(CARGA + " |> SQUAD por [piloto] |> BATTERY 1")


def test_la_condicion_debe_ser_booleana(datos):
    assert "verdadero o falso" in falla("PATTERN_BLUE 5 { x = 1 }")
    assert "verdadero o falso" in falla(CARGA + " |> AT_FIELD donde sincronizacion + 1")


def test_funcion_tipo_y_grafica_desconocidos(datos):
    assert "no existe" in falla("x = promedio(3)")
    assert "no existe" in falla(CARGA + " |> EQUIP piloto -> fecha")
    assert "no existe" in falla(CARGA + "\nHOLOGRAM torta de t")
    assert "MAGI no conoce" in falla(CARGA + " |> MAGI x = promedio(sincronizacion)")


def test_convertir_un_texto_que_no_es_numero(datos):
    assert "no se pudo convertir" in falla(CARGA + " |> EQUIP piloto -> entero")


def test_columnas_de_distinto_largo(datos):
    assert "filas" in falla(CARGA + "\nu = t |> BATTERY 2 |> SYNC x = sincronizacion + t.sincronizacion")


def test_el_error_semantico_trae_linea_y_columna(datos):
    with pytest.raises(ErrorSemantico) as info:
        correr(CARGA + "\n\nMONITOR t |> TARGET [piloto, edad]")
    assert (info.value.error.linea, info.value.error.columna) == (3, 29)


@pytest.mark.parametrize("ruta", SEMANTICOS, ids=lambda r: r.name)
def test_ejemplos_con_error_semantico(ruta, carpeta):
    falla(ruta.read_text(encoding="utf-8"))


# --- De punta a punta, por la linea de comandos ---------------------------------

@pytest.mark.parametrize("ruta", VALIDOS, ids=lambda r: r.name)
def test_los_ejemplos_corren_y_felicitan(ruta, carpeta, capsys):
    assert main([str(ruta)]) == 0
    salida = capsys.readouterr().out
    assert "¡Felicidades, Shinji!" in salida
    assert "EVA - 01" in salida


def test_los_tres_programas_exportan_sus_reportes(carpeta, capsys):
    for nombre in ("02_resumen_por_piloto", "03_informe_de_combates", "04_seguimiento_de_asuka"):
        assert main([str(RAIZ / "ejemplos" / f"{nombre}.eva")]) == 0
    reportes = sorted(p.name for p in (carpeta / "salidas").glob("*.csv"))
    assert reportes == ["alerta_asuka.csv", "combates_criticos.csv", "dano_por_unidad.csv", "resumen_pilotos.csv"]
    resumen = leer_csv(carpeta / "salidas" / "resumen_pilotos.csv")
    assert set(resumen["piloto"].valores) == {"Shinji", "Rei", "Asuka", "Toji", "Kaworu"}
    # los mismos numeros que se sacan a mano del CSV de pruebas
    kaworu = next(r for r in resumen.registros() if r["piloto"] == "Kaworu")
    assert (kaworu["pruebas"], kaworu["promedio"], kaworu["variacion"]) == (1, 98.0, None)


@pytest.mark.parametrize("ruta", CON_ERROR, ids=lambda r: r.name)
def test_los_errores_muestran_a_gendo(ruta, carpeta, capsys):
    assert main([str(ruta)]) == 1
    salida = capsys.readouterr().out
    assert "|####|--|####|" in salida   # las gafas de Gendo
    assert "sincronización fallida" in salida
    assert "línea" in salida and "columna" in salida
    assert "Felicidades" not in salida


def test_archivo_que_no_existe(capsys):
    assert main(["no_existe.eva"]) == 2


def test_banderas_de_la_cli(carpeta, capsys):
    ruta = str(RAIZ / "ejemplos" / "01_primera_prueba.eva")
    assert main([ruta, "--tokens", "--arbol", "--simbolos", "--svg", "arbol.svg"]) == 0
    salida = capsys.readouterr().out
    assert "ENTRY_PLUG" in salida and "etapaFiltrar" in salida and "TABLA DE SÍMBOLOS" in salida
    assert (carpeta / "arbol.svg").read_text(encoding="utf-8").startswith("<svg")
