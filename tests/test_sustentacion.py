"""Arreglos para la sustentacion: otros CSV (coma decimal, latin-1, separador equivocado),
mensajes de error mas claros, funciones del lenguaje como argumento y k vecinos / k-medias
mas rapidos pero con los mismos resultados."""

import math

import pytest

from evangelion import aprendizaje, matematica
from evangelion.analizador import analizar
from evangelion.listas import Lista, ordenada
from evangelion.tablas import Tabla, inferir, leer_csv

from test_fase2 import correr, datos, falla, valor  # noqa: F401  (datos es un fixture)


def v(codigo, nombre="r"):
    return valor(correr(codigo), nombre)


# --- 1. decimal: "," ---------------------------------------------------------------------------

def test_cargar_con_coma_decimal(datos):
    (datos / "excel.csv").write_text("x;y;ciudad\n1,5;3,1;Bogotá\n2,5;;Cali\n-3;1e2;Pasto\n", encoding="utf-8")
    t = v('r = cargar "excel.csv" con { separador: ";", decimal: "," }')
    assert t["x"].valores == [1.5, 2.5, -3.0]
    assert t["y"].valores == [3.1, None, 100.0]
    assert t["ciudad"].valores == ["Bogotá", "Cali", "Pasto"]
    assert v('t = cargar "excel.csv" con { separador: ";", decimal: "," }\nr = media(t.x)') == pytest.approx(1 / 3)


def test_sin_la_opcion_decimal_todo_sigue_igual(datos):
    (datos / "excel.csv").write_text("x;n\n1,5;1\n2,5;2\n", encoding="utf-8")
    t = v('r = cargar "excel.csv" con { separador: ";" }')
    assert t["x"].valores == ["1,5", "2,5"] and t["n"].valores == [1, 2]
    assert inferir(Lista(("1.5", "2"))) == [1.5, 2.0]
    assert inferir(Lista(("1.234,5", "2,5")), ",") == ["1.234,5", "2,5"]     # con punto de miles queda como texto


def test_decimal_con_valores_que_no_sirven(datos):
    (datos / "excel.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    assert 'decimal va con ","' in falla('t = cargar "excel.csv" con { decimal: "x" }')
    assert "no pueden ser los dos" in falla('t = cargar "excel.csv" con { decimal: "," }')


# --- 2. latin-1 --------------------------------------------------------------------------------

def test_un_csv_en_latin1_se_lee_sin_pedir_la_codificacion(datos):
    (datos / "ansi.csv").write_bytes("nombre,año\nJosé,2001\nMaría,2002\n".encode("latin-1"))
    t = v('r = cargar "ansi.csv"')
    assert t.columnas == ["nombre", "año"]
    assert t["nombre"].valores == ["José", "María"]
    assert v('r = cargar "ansi.csv" con { codificacion: "latin-1" }')["nombre"].valores == ["José", "María"]


def test_codificacion_equivocada_da_un_mensaje_en_espanol(datos):
    (datos / "ansi.csv").write_bytes("nombre\nJosé\n".encode("latin-1"))
    mensaje = falla('t = cargar "ansi.csv" con { codificacion: "utf-8" }')
    assert "no está en utf-8" in mensaje and "latin-1" in mensaje and "codec" not in mensaje
    assert "no existe" in falla('t = cargar "ansi.csv" con { codificacion: "klingon" }')


def test_utf8_con_bom_sigue_funcionando(datos):
    (datos / "bom.csv").write_bytes("año,valor\n2001,1.5\n".encode("utf-8-sig"))
    assert v('r = cargar "bom.csv"').columnas == ["año", "valor"]


# --- 3. separador equivocado ------------------------------------------------------------------

def test_separador_equivocado_sugiere_el_correcto(datos):
    (datos / "pc.csv").write_text("x;y\n1;2\n", encoding="utf-8")
    (datos / "tab.txt").write_text("x\ty\n1\t2\n", encoding="utf-8")
    (datos / "coma.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    assert 'separador: ";"' in falla('t = cargar "pc.csv"')
    assert 'separador: "\\t"' in falla('t = cargar "tab.txt"')
    assert 'separador: ","' in falla('t = cargar "coma.csv" con { separador: ";" }')
    assert v('r = cargar "tab.txt" con { separador: "\\t" }').columnas == ["x", "y"]


def test_un_archivo_de_una_sola_columna_se_sigue_leyendo(datos):
    (datos / "una.csv").write_text("valor\n1\n2\n", encoding="utf-8")
    assert v('r = cargar "una.csv"')["valor"].valores == [1, 2]


# --- 4. ruta que no existe ---------------------------------------------------------------------

def test_archivo_que_no_existe_dice_desde_donde_se_buscan_las_rutas(datos):
    mensaje = falla('t = cargar "datos/no_esta.csv"')
    assert "no existe el archivo 'datos/no_esta.csv'" in mensaje
    assert "desde la carpeta donde corres el programa" in mensaje


# --- 5. aviso de la regresion ------------------------------------------------------------------

DATOS_REGRESION = 't = tabla_de({"x": [1, 2, 3, 4, 5, 6, 7, 8], "z": [3, 5, 7.5, 9, 11, 13.2, 15, 17]})\n'


def test_regresion_avisa_si_la_tasa_es_muy_grande_y_no_cambia_el_resultado(capsys):
    modelo = v(DATOS_REGRESION + 'r = regresion(t, ["x"], "z", 1.5, 200)')
    salida = capsys.readouterr().out
    assert "AVISO" in salida and "tasa parece muy grande" in salida and "0.001" in salida
    tabla = Tabla(Lista(("x", "z")), {"x": Lista(range(1, 9)), "z": Lista((3, 5, 7.5, 9, 11, 13.2, 15, 17))})
    directo = aprendizaje.regresion(tabla, Lista(("x",)), "z", 1.5, 200)
    assert modelo["coeficientes"] == directo["coeficientes"] and modelo["r2"] == directo["r2"] < 0


def test_regresion_que_sale_bien_no_avisa(capsys):
    modelo = v(DATOS_REGRESION + 'r = regresion(t, ["x"], "z", 0.01, 3000)')
    assert modelo["r2"] > 0.9
    assert "AVISO" not in capsys.readouterr().out


# --- 6. mensajes --------------------------------------------------------------------------------

def test_numero_convierte_una_columna_de_texto(datos):
    (datos / "excel.csv").write_text("x;n\n1,5;1\n2,5;2\n;3\n", encoding="utf-8")
    t = v('r = cargar "excel.csv" con { separador: ";" } |> crear x = numero(reemplazar(x, ",", "."))')
    assert t["x"].valores == [1.5, 2.5, None]


def test_numero_no_muestra_objetos_de_python(datos):
    mensaje = falla('t = cargar "p.csv" |> crear x = numero(piloto)')
    assert "no se pudo convertir \"Shinji\"" in mensaje
    assert "object at" not in falla("x = numero([1, 2])")
    assert "llegó una lista" in falla("x = numero([1, 2])")


def test_correlacion_distingue_texto_de_celdas_vacias(datos):
    texto = falla('t = cargar "p.csv"\nx = correlacion(t.sincronizacion, t.piloto)')
    assert "tiene texto" in texto and "faltantes" not in texto
    vacias = falla('t = cargar "p.csv"\nx = correlacion(t.sincronizacion, t.armonicos)')
    assert "celdas vacías" in vacias and "quitar faltantes" in vacias
    limpio = v('t = cargar "p.csv" |> quitar faltantes [sincronizacion, armonicos]\n'
               'r = correlacion(t.sincronizacion, t.armonicos)')
    assert -1 <= limpio <= 1


def test_los_errores_de_matrices_no_repiten_el_nombre():
    for codigo, nombre in (("x = determinante([[1, 2, 3], [4, 5, 6]])", "determinante"),
                           ("x = inversa([1, 2])", "inversa"), ('x = punto([1, 2], "a")', "punto"),
                           ("x = forma(3)", "forma"), ("x = resolver([[1, 2], [3, 4]], [1])", "resolver")):
        mensaje = falla(codigo)
        assert mensaje.count(nombre + "()") == 1, mensaje
    assert "matriz cuadrada y esta es de 2x3" in falla("x = determinante([[1, 2, 3], [4, 5, 6]])")


def test_punto_y_norma_reciben_columnas(datos):
    assert v('t = tabla_de({"a": [1, 2, 3], "b": [4, 5, 6]})\nr = punto(t.a, t.b)') == 32
    assert v('t = tabla_de({"a": [3, 4]})\nr = norma(t.a)') == pytest.approx(5)
    assert "sin datos faltantes" in falla('t = cargar "p.csv"\nx = punto(t.sincronizacion, t.armonicos)')


# --- 7. funciones del lenguaje como argumento ---------------------------------------------------

def test_las_funciones_del_lenguaje_se_pueden_pasar_como_argumento():
    assert v("r = derivada(sen, 0)") == pytest.approx(1, abs=1e-6)
    assert v("r = mapear(raiz, [4, 9, 16])") == [pytest.approx(2), pytest.approx(3), pytest.approx(4)]
    assert v("r = biseccion(cos, 1, 2)") == pytest.approx(math.pi / 2, abs=1e-8)
    assert v("r = newton(cos, 1)") == pytest.approx(math.pi / 2, abs=1e-8)
    assert v("f = exp\nr = f(1)") == pytest.approx(math.e)
    assert v("r = texto(sen)") == "<función sen(x)>"


def test_mapear_con_funcion_del_lenguaje_sobre_una_columna(datos):
    t = v('r = tabla_de({"a": [4, 9]}) |> crear b = mapear(raiz, a)')
    assert t["b"].valores == [pytest.approx(2), pytest.approx(3)]


def test_una_variable_o_columna_con_nombre_de_funcion_sigue_ganando(datos):
    assert v("sen = 5\nr = sen + 1") == 6
    assert v('r = tabla_de({"exp": [1, 2]}) |> crear b = exp * 2')["b"].valores == [2, 4]
    assert "no se ha declarado" in falla("x = seno")
    assert "derivada():" in falla("x = derivada(ln, -1)")


def test_metodo_tambien_cambia_las_funciones_pasadas_como_argumento():
    assert v('metodo("raiz", "biseccion")\nr = mapear(raiz, [2])')[0] == pytest.approx(2 ** 0.5, rel=1e-12)


# --- 8. palabra reservada como nombre de columna -------------------------------------------------

@pytest.mark.parametrize("palabra", ["y", "o", "de", "por", "desde"])
def test_columna_con_nombre_reservado_dice_como_escribirla(palabra):
    errores = analizar(f"mostrar media(t.{palabra})").errores
    assert errores and "palabra reservada" in errores[0].mensaje
    assert f"`{palabra}`" in errores[0].mensaje and "otro nombre" in errores[0].mensaje


def test_variable_con_nombre_reservado_sugiere_otro_nombre():
    mensaje = analizar("y = [1, 2]").errores[0].mensaje
    assert "palabra reservada" in mensaje and "otro nombre" in mensaje


def test_un_nombre_que_falta_sin_reservada_no_habla_de_reservadas():
    errores = analizar("mostrar media(t.)").errores
    assert errores and "palabra reservada" not in errores[0].mensaje


def test_la_columna_reservada_funciona_entre_acentos_graves(datos):
    (datos / "xy.csv").write_text("x,y\n1,2\n2,4\n3,7\n", encoding="utf-8")
    assert v('t = cargar "xy.csv"\nr = media(t.`y`)') == pytest.approx(13 / 3)


# --- 9. k vecinos y k-medias mas rapidos, mismos resultados --------------------------------------

def test_lista_insertar():
    lista = Lista((1, 2, 4))
    lista.insertar(2, 3)
    lista.insertar(0, 0)
    lista.insertar(5, 5)
    assert lista == [0, 1, 2, 3, 4, 5] and len(lista) == 6
    assert Lista(reversed(lista)) == [5, 4, 3, 2, 1, 0]      # los enlaces hacia atras quedaron bien
    assert lista[3] == 3 and lista[-1] == 5
    vacia = Lista()
    vacia.insertar(0, "a")
    assert vacia == ["a"]
    with pytest.raises(IndexError):
        lista.insertar(9, 1)


def _knn_ordenando_todo(tabla, objetivo, predictoras, k):
    """La version de antes: ordena todas las distancias y toma las k primeras."""
    rangos = {}
    for c in predictoras:
        minimo, maximo = tabla[c].minimo(), tabla[c].maximo()
        rangos[c] = (minimo, maximo - minimo if maximo != minimo else 1)
    filas = len(tabla)
    vectores = [[None if tabla[c].valores[i] is None else (tabla[c].valores[i] - rangos[c][0]) / rangos[c][1]
                 for c in predictoras] for i in range(filas)]
    objetivos = tabla[objetivo].valores
    numerico = tabla[objetivo].clase() == "numero"
    candidatos = [i for i in range(filas) if objetivos[i] is not None and None not in vectores[i]]
    predicciones = []
    for i in range(filas):
        if None in vectores[i]:
            predicciones.append(None)
            continue
        distancias = [(sum((a - b) ** 2 for a, b in zip(vectores[i], vectores[j])) ** 0.5, objetivos[j])
                      for j in candidatos if j != i]
        vecinos = [valor for _, valor in ordenada(distancias, key=lambda par: par[0])[:k]]
        if not vecinos:
            predicciones.append(None)
        elif numerico:
            predicciones.append(sum(vecinos) / len(vecinos))
        else:
            conteo = {}
            for valor in vecinos:
                conteo[valor] = conteo.get(valor, 0) + 1
            predicciones.append(max(conteo, key=conteo.get))
    return predicciones


def _tabla_al_azar(filas, semilla, con_huecos=True):
    azar = matematica.Aleatorio(semilla)
    # pocos valores distintos, para que haya muchos empates de distancia
    x = Lista(azar.entero(0, 6) for _ in range(filas))
    z = Lista(azar.entero(0, 4) / 2 for _ in range(filas))
    clase = Lista("abc"[azar.entero(0, 2)] for _ in range(filas))
    numero = Lista(azar.entero(0, 100) for _ in range(filas))
    if con_huecos:
        x[3], z[7], clase[5], numero[11] = None, None, None, None
    return Tabla(Lista(("x", "z", "clase", "numero")), {"x": x, "z": z, "clase": clase, "numero": numero})


@pytest.mark.parametrize("k", [1, 2, 3, 5, 10, 39])
def test_knn_da_lo_mismo_que_ordenando_todas_las_distancias(k):
    tabla = _tabla_al_azar(60, semilla=k)
    for objetivo in ("clase", "numero"):
        rapido = tabla.predecir_knn(objetivo, Lista(("x", "z")), k).valores
        assert rapido == _knn_ordenando_todo(tabla, objetivo, ("x", "z"), k)


def _k_medias_con_distancias(puntos, centros):
    """La version de antes: mide la distancia de cada punto a cada centro."""
    asignacion = None
    for _ in range(aprendizaje.MAX_VUELTAS):
        nueva = [min(range(len(centros)), key=lambda c: aprendizaje.matrices.distancia(p, centros[c])) for p in puntos]
        if nueva == asignacion:
            break
        asignacion = nueva
        for c in range(len(centros)):
            miembros = [p for p, g in zip(puntos, asignacion) if g == c]
            if miembros:
                centros[c] = Lista(sum(m[j] for m in miembros) / len(miembros) for j in range(len(miembros[0])))
    return asignacion, centros


def _centros_con_todas_las_distancias(puntos, k, azar):
    centros = Lista((puntos[azar.entero(0, len(puntos) - 1)],))
    while len(centros) < k:
        pesos = [min(aprendizaje.matrices.distancia(p, c) for c in centros) ** 2 for p in puntos]
        total = sum(pesos)
        if total == 0:
            centros.agregar(puntos[len(centros)])
            continue
        meta, acumulado = azar.siguiente() * total, 0
        for p, peso in zip(puntos, pesos):
            acumulado += peso
            if acumulado >= meta and peso > 0:
                centros.agregar(p)
                break
    return Lista(Lista(c) for c in centros)


@pytest.mark.parametrize("k", [1, 2, 3, 5, 8])
@pytest.mark.parametrize("metodo_raiz", ["newton", "biseccion"])
def test_k_medias_da_lo_mismo_que_midiendo_todas_las_distancias(k, metodo_raiz):
    tabla = _tabla_al_azar(50, semilla=10 + k, con_huecos=False)
    puntos = aprendizaje._puntos(tabla, Lista(("x", "z", "numero")))
    puntos = aprendizaje._escalar(puntos, *aprendizaje._escala(puntos))
    matematica.metodo("raiz", metodo_raiz)
    try:
        nuevos = aprendizaje._centros_iniciales(puntos, k, matematica.Aleatorio(7))
        viejos = _centros_con_todas_las_distancias(puntos, k, matematica.Aleatorio(7))
        assert nuevos == viejos
        asignacion, centros = aprendizaje._k_medias(puntos, nuevos)
        esperada, esperados = _k_medias_con_distancias(puntos, viejos)
        assert asignacion == esperada and centros == esperados
    finally:
        matematica.reiniciar_metodos()


def test_grupos_con_puntos_repetidos_y_mas_grupos_que_puntos_distintos():
    tabla = Tabla(Lista(("a", "b")), {"a": Lista((1, 1, 1, 2, 2, 2, 9, 9, 1, 2)), "b": Lista((0, 0, 0, 0, 0, 0, 5, 5, 0, 0))})
    for k in (2, 3, 5):
        grupo = aprendizaje.grupos(tabla, Lista(("a", "b")), k)["grupo"].valores
        assert len(grupo) == 10 and all(1 <= g <= k for g in grupo)
    dos = aprendizaje.grupos(tabla, Lista(("a", "b")), 2)["grupo"].valores
    assert dos == [1, 1, 1, 1, 1, 1, 2, 2, 1, 1]
