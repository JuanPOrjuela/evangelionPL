"""Fase 1: tokens, arbol y errores lexicos y sintacticos."""

from pathlib import Path

import pytest

from evangelion.analizador import analizar, nombre_token
from evangelion.arbol import como_lisp, como_svg, como_texto

RAIZ = Path(__file__).resolve().parents[1]
VALIDOS = sorted((RAIZ / "ejemplos").glob("*.eva"))
ERRORES = sorted((RAIZ / "ejemplos" / "errores").glob("*.eva"))
FASES = {"lex": "lexico", "sin": "sintactico"}


def tipos(fuente):
    return [nombre_token(t.type) for t in analizar(fuente).tokens]


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


# --- Programas completos ------------------------------------------------------

@pytest.mark.parametrize("ruta", VALIDOS, ids=lambda r: r.name)
def test_los_ejemplos_son_validos(ruta):
    res = analizar(leer(ruta))
    assert res.valido, [str(e) for e in res.errores]


@pytest.mark.parametrize("ruta", [r for r in ERRORES if r.name[:3] in FASES], ids=lambda r: r.name)
def test_los_errores_se_detectan_en_su_fase(ruta):
    res = analizar(leer(ruta))
    assert not res.valido
    assert {e.fase for e in res.errores} == {FASES[ruta.name[:3]]}


@pytest.mark.parametrize("ruta", [r for r in ERRORES if r.name.startswith("sem")], ids=lambda r: r.name)
def test_los_errores_semanticos_pasan_la_fase_1(ruta):
    # estan bien escritos, lo que falla es el sentido
    assert analizar(leer(ruta)).valido


# --- Lexer ----------------------------------------------------------------------

@pytest.mark.parametrize("lexema, esperado", [
    ("NERV", "NERV"),
    ("ENTRY_PLUG", "ENTRY_PLUG"),
    ("AT_FIELD", "AT_FIELD"),
    ("DUMMY_PLUG", "DUMMY_PLUG"),
    ("PATTERN_BLUE", "PATTERN_BLUE"),
    ("donde", "DONDE"),
    ("verdadero", "VERDADERO"),
    ("42", "ENTERO"),
    ("3.14", "REAL"),
    ('"Tokio-3"', "CADENA"),
    ("piloto", "ID"),
    ("sincronización", "ID"),
    ("`Unidad EVA`", "ID_ESCAPADO"),
    ("|>", "TUBERIA"),
    ("->", "FLECHA"),
    ("==", "IGUAL_IGUAL"),
    ("<=", "MENOR_IGUAL"),
])
def test_cada_lexema_da_su_token(lexema, esperado):
    assert tipos(lexema) == [esperado]


def test_las_reservadas_distinguen_mayusculas():
    assert tipos("magi MAGI") == ["ID", "MAGI"]


def test_una_reservada_pegada_a_mas_letras_es_un_nombre():
    assert tipos("MAGI_2 dondequiera") == ["ID", "ID"]


def test_comentarios_y_espacios_no_llegan_al_parser():
    assert tipos("x = 1   # esto no cuenta\n\n") == ["ID", "IGUAL", "ENTERO"]


def test_el_real_no_se_parte_en_tres():
    assert tipos("x = 3.5") == ["ID", "IGUAL", "REAL"]


def test_caracter_invalido_con_su_posicion():
    res = analizar("x = 1\ny = 2 $ 3")
    assert [(e.fase, e.linea, e.columna) for e in res.errores] == [("lexico", 2, 6)]


def test_texto_sin_cerrar():
    res = analizar('MONITOR "hola')
    assert res.errores[0].fase == "lexico"
    assert "comilla" in res.errores[0].mensaje


# --- Parser ---------------------------------------------------------------------

def test_programa_vacio_es_valido():
    assert analizar("").valido
    assert analizar("# solo un comentario").valido


def test_la_multiplicacion_amarra_mas_que_la_suma():
    arbol = como_lisp(analizar("x = 1 + 2 * 3").arbol)
    assert "(exprAditiva (exprLiteral (literal 1)) + (exprMultiplicativa" in arbol


def test_la_potencia_asocia_a_la_derecha():
    arbol = como_lisp(analizar("x = 2 ^ 3 ^ 2").arbol)
    assert "(exprPotencia (exprLiteral (literal 2)) ^ (exprPotencia" in arbol


def test_el_y_amarra_mas_que_el_o():
    arbol = como_lisp(analizar("x = a o b y c").arbol)
    assert arbol.startswith("(programa (sentencia (asignacion (nombre x) = (flujo (fuente (exprO")


def test_el_no_cubre_toda_la_comparacion():
    arbol = como_lisp(analizar("x = no a == b").arbol)
    assert "(exprNo no (exprIgualdad" in arbol


def test_cada_etapa_tiene_su_nodo():
    arbol = como_lisp(analizar("x = t |> AT_FIELD donde a > 1 |> SQUAD por [b] |> MAGI n = contar()").arbol)
    for nodo in ("etapaFiltrar", "etapaAgrupar", "etapaResumir"):
        assert nodo in arbol


def test_la_grafica_se_reconoce():
    assert analizar('HOLOGRAM barras de t { eje_x: a, titulo: "hola" }').valido


def test_condicional_con_y_sin_alternativa():
    assert analizar("PATTERN_BLUE x > 1 { MONITOR x }").valido
    assert analizar("PATTERN_BLUE x > 1 { MONITOR x } PATTERN_ORANGE { MONITOR 0 }").valido


def test_el_error_sintactico_trae_linea_y_columna():
    res = analizar("x = 1\nz = t |> TARGET piloto]")
    error = res.errores[0]
    assert (error.fase, error.linea, error.columna) == ("sintactico", 2, 16)


def test_no_se_cuela_basura_al_final():
    assert not analizar("x = 1 )").valido


def test_mensaje_de_palabra_reservada():
    for codigo in ('MAGI = ENTRY_PLUG "a.csv"', 'SEELE = ENTRY_PLUG "a.csv"', "x = 1\ny = 2"):
        assert "palabra reservada" in analizar(codigo).errores[0].mensaje


def test_mensaje_de_etapa_que_no_existe():
    res = analizar("x = t |> FILTRAR donde a > 1")
    assert "una etapa" in res.errores[0].mensaje


# --- Arbol ----------------------------------------------------------------------

def test_arbol_en_texto_y_en_svg():
    arbol = analizar("x = t |> BATTERY 3").arbol
    texto = como_texto(arbol)
    assert texto.splitlines()[0] == "programa"
    assert "etapaLimitar" in texto
    svg = como_svg(arbol)
    assert svg.startswith("<svg") and "etapaLimitar" in svg
