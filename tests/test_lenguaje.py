"""Fase 3 (segunda parte): vocabulario en espanol, ciclos, funciones, listas y diccionarios,
y las librerias propias de matematicas, matrices y aprendizaje automatico."""

import math
import random
from pathlib import Path

import pytest

from evangelion import aprendizaje, matematica, matrices
from evangelion.analizador import analizar
from evangelion.tablas import Columna, Tabla

from test_fase2 import CARGA, correr, datos, falla, valor  # noqa: F401  (datos es un fixture)

RAIZ = Path(__file__).resolve().parents[1]


def v(codigo, nombre="r"):
    return valor(correr(codigo), nombre)


# --- Vocabulario en espanol ------------------------------------------------------

def test_las_palabras_en_espanol_hacen_lo_mismo_que_las_de_evangelion(datos):
    eva = valor(correr(CARGA + """
r = t |> AT_FIELD donde sincronizacion > 55 |> SQUAD por [piloto] |> MAGI n = contar()
      |> FORMATION por [piloto asc]"""), "r")
    espanol = valor(correr('t = cargar "p.csv"' + """
r = t |> filtrar donde sincronizacion > 55 |> agrupar por [piloto] |> resumir n = contar()
      |> ordenar por [piloto asc]"""), "r")
    assert eva.registros() == espanol.registros()


def test_las_dos_formas_se_pueden_mezclar(datos):
    i = correr('programa "x"\nt = ENTRY_PLUG "p.csv" |> seleccionar [piloto] |> BATTERY 2\nmostrar t')
    assert i.operacion == "x"
    assert len(valor(i, "t")) == 2


@pytest.mark.parametrize("palabra", ["mostrar", "si", "mientras", "para", "cargar", "resumir"])
def test_las_palabras_nuevas_son_reservadas(palabra):
    errores = analizar(f"{palabra} = 1").errores
    assert errores and "palabra reservada" in errores[0].mensaje


def test_mensaje_de_error_nombra_las_dos_formas():
    mensaje = analizar("x = 1 |> 5").errores[0].mensaje
    assert "seleccionar" in mensaje and "TARGET" in mensaje


# --- Condicionales y ciclos --------------------------------------------------------

@pytest.mark.parametrize("nota, esperado", [(4.8, "excelente"), (3.5, "aprobado"), (1.0, "reprobado")])
def test_sino_si(nota, esperado):
    assert v(f"""nota = {nota}
si nota >= 4.5 {{ r = "excelente" }} sino si nota >= 3 {{ r = "aprobado" }} sino {{ r = "reprobado" }}""") == esperado


def test_para_desde_hasta_incluye_los_dos_extremos():
    assert v("r = 0\npara i desde 1 hasta 100 { r = r + i }") == 5050


def test_para_desde_hasta_al_reves_no_da_vueltas():
    assert v("r = 0\npara i desde 5 hasta 1 { r = r + 1 }") == 0


def test_para_en_lista_texto_y_diccionario():
    assert v('r = 0\npara x en [3, 4, 5] { r = r + x }') == 12
    assert v('r = ""\npara letra en "eva" { r = letra + r }') == "ave"
    assert v('r = []\npara k en {"a": 1, "b": 2} { agregar(r, k) }') == ["a", "b"]


def test_para_en_tabla_da_cada_fila_como_diccionario(datos):
    assert v(CARGA + '\nr = 0\npara fila en t { si fila["piloto"] == "Shinji" { r = r + 1 } }') == 2


def test_mientras():
    assert v("r = 1\nmientras r < 1000 { r = r * 2 }") == 1024


def test_mientras_infinito_se_detiene(monkeypatch):
    monkeypatch.setattr("evangelion.interprete.MAX_VUELTAS", 50)
    assert "vueltas" in falla("x = 1\nmientras x > 0 { x = x + 1 }")


def test_la_condicion_del_ciclo_tiene_que_ser_booleana():
    assert "verdadero o falso" in falla("mientras 1 { x = 1 }")


def test_ciclos_anidados():
    assert v("r = 0\npara i desde 1 hasta 3 { para j desde 1 hasta 3 { r = r + i * j } }") == 36


# --- Listas y diccionarios ------------------------------------------------------------

def test_lista_indices_y_negativos():
    i = correr("x = [10, 20, 30]\na = x[0]\nb = x[-1]\nc = longitud(x)")
    assert (valor(i, "a"), valor(i, "b"), valor(i, "c")) == (10, 30, 3)


def test_cambiar_un_elemento():
    assert v("r = [1, 2, 3]\nr[1] = 20") == [1, 20, 3]
    assert v('r = {"a": 1}\nr["b"] = 2') == {"a": 1, "b": 2}
    assert v("r = [[1, 2], [3, 4]]\nr[1][0] = 9") == [[1, 2], [9, 4]]


def test_diccionario_con_claves_sin_comillas_y_con_punto():
    i = correr('d = {nombre: "Rei", edad: 14}\na = d.nombre\nb = d["edad"]')
    assert (valor(i, "a"), valor(i, "b")) == ("Rei", 14)


def test_funciones_de_listas():
    i = correr("""x = [3, 1, 2]
agregar(x, 0)
u = sacar(x)
od = ordenada(x)
w = invertida(x)
j = unir(x, [7])
c = contiene(x, 2)
r = rango(1, 5)
p = rango(10, 0, -5)""")
    assert valor(i, "u") == 0 and valor(i, "x") == [3, 1, 2]
    assert valor(i, "od") == [1, 2, 3] and valor(i, "w") == [2, 1, 3]
    assert valor(i, "j") == [3, 1, 2, 7] and valor(i, "c") is True
    assert valor(i, "r") == [1, 2, 3, 4, 5] and valor(i, "p") == [10, 5, 0]


def test_agregaciones_con_listas():
    i = correr("x = [2, 4, 9]\ns = suma(x)\nm = media(x)\nd = mediana(x)\nM = maximo(x)")
    assert [valor(i, n) for n in "smdM"] == [15, 5, 4, 9]


def test_cuentas_con_listas_como_numpy():
    assert v("r = [1, 2, 3] * 2") == [2, 4, 6]
    assert v("r = [1, 2, 3] + [10, 20, 30]") == [11, 22, 33]
    assert v("r = 10 - [1, 2]") == [9, 8]
    assert v("r = -[1, 2]") == [-1, -2]
    assert v("r = [[1, 2], [3, 4]] * 10") == [[10, 20], [30, 40]]


def test_errores_de_listas():
    assert "no existe" in falla("x = [1, 2]\nz = x[5]")
    assert "mismo largo" in falla("x = [1, 2] + [1, 2, 3]")
    assert "no está en el diccionario" in falla('d = {"a": 1}\nz = d["b"]')
    assert "no devuelve nada" in falla("x = []\nz = agregar(x, 1)")


def test_texto_y_numero():
    assert v("r = numero(\"3.5\") + 1") == 4.5
    assert v('r = numero("42")') == 42
    assert v('r = texto(5) + " pilotos"') == "5 pilotos"
    assert "no se pudo convertir" in falla('x = numero("hola")')


def test_columna_y_tabla_de(datos):
    i = correr(CARGA + '\nl = columna(t, "piloto")\nn = tabla_de({"x": [1, 2], "y": [3, 4]})')
    assert valor(i, "l")[0] == "Shinji"
    assert valor(i, "n").registros() == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]


def test_una_lista_se_puede_volver_columna(datos):
    t = v(CARGA + "\nr = t |> crear orden = rango(5)")
    assert t["orden"].valores == [1, 2, 3, 4, 5]


def test_aleatorio_se_repite_con_la_misma_semilla():
    a = v("semilla(7)\nr = [aleatorio(), aleatorio(1, 6)]")
    b = v("semilla(7)\nr = [aleatorio(), aleatorio(1, 6)]")
    assert a == b and 0 <= a[0] < 1 and 1 <= a[1] <= 6


# --- Libreria de matematicas -------------------------------------------------------------
# math de Python solo se usa aqui, en las pruebas, para comparar

@pytest.mark.parametrize("x", [0.001, 0.5, 1, 2, 10, 12345.678, 1e10])
def test_raiz_ln_y_exp_contra_python(x):
    assert matematica.raiz(x) == pytest.approx(math.sqrt(x), rel=1e-13)
    assert matematica.ln(x) == pytest.approx(math.log(x), rel=1e-12, abs=1e-14)
    if x < 700:
        assert matematica.exp(x) == pytest.approx(math.exp(x), rel=1e-12)


@pytest.mark.parametrize("x", [-100, -3.5, -1, 0, 0.3, 1.5707963, 3.14159, 50])
def test_seno_coseno_contra_python(x):
    assert matematica.sen(x) == pytest.approx(math.sin(x), abs=1e-12)
    assert matematica.cos(x) == pytest.approx(math.cos(x), abs=1e-12)


def test_piso_techo_y_logs():
    assert [matematica.piso(2.7), matematica.piso(-2.3), matematica.techo(2.1), matematica.techo(-2.9)] == [2, -3, 3, -2]
    assert matematica.raiz(27, 3) == pytest.approx(3)
    assert matematica.raiz(-8, 3) == pytest.approx(-2)
    assert [matematica.piso_log10(x) for x in (0.05, 1, 999, 1000, 1001)] == [-2, 0, 2, 3, 3]
    assert [matematica.techo_log2(n) for n in (1, 2, 3, 8, 9)] == [0, 1, 2, 3, 4]
    assert matematica.factorial(20) == math.factorial(20)


def test_errores_de_matematicas():
    assert "logaritmo" in falla("x = ln(0)")
    assert "negativo" in falla("x = raiz(-4)")
    assert "factorial" in falla("x = factorial(2.5)")


def test_matematicas_en_el_lenguaje(datos):
    assert v("r = redondear(sen(pi / 6), 6)") == 0.5
    assert v("r = log(8, 2)") == pytest.approx(3)
    assert v("r = raiz([4, 9])") == [2, 3]
    # en una columna, lo imposible queda como dato faltante en vez de romper el programa
    t = v(CARGA + "\nr = t |> crear x = ln(sincronizacion - 60)")
    assert t["x"].valores[0] is None and t["x"].valores[1] == pytest.approx(math.log(20))


def test_ninguna_libreria_propia_importa_math():
    for archivo in (RAIZ / "src" / "evangelion").glob("*.py"):
        codigo = archivo.read_text(encoding="utf-8")
        for prohibido in ("import math", "import struct", "import numpy", "import pandas",
                          "import matplotlib", "import statistics", "import random", "import zlib"):
            assert prohibido not in codigo, f"{archivo.name} usa {prohibido}"


# --- Libreria de matrices -----------------------------------------------------------------

def test_producto_transpuesta_e_identidad():
    a = [[1, 2, 3], [4, 5, 6]]
    assert matrices.transpuesta(a) == [[1, 4], [2, 5], [3, 6]]
    assert matrices.producto(a, matrices.transpuesta(a)) == [[14, 32], [32, 77]]
    assert matrices.producto(a, [1, 0, -1]) == [-2, -2]
    assert matrices.producto(matrices.identidad(2), a) == a


def test_determinante_inversa_y_resolver():
    a = [[4, 7, 2], [3, 6, 1], [2, 5, 3]]
    assert matrices.determinante(a) == pytest.approx(9)
    identidad = matrices.producto(a, matrices.inversa(a))
    for i in range(3):
        for j in range(3):
            assert identidad[i][j] == pytest.approx(1 if i == j else 0, abs=1e-12)
    x = matrices.resolver(a, [1, 2, 3])
    assert matrices.producto(a, x) == pytest.approx([1, 2, 3])


def test_matriz_sin_inversa():
    assert "no tiene inversa" in falla("x = inversa([[1, 2], [2, 4]])")
    assert "cuadrada" in falla("x = determinante([[1, 2, 3]])")
    assert "multiplicar" in falla("x = producto([[1, 2]], [[1, 2]])")


def test_matrices_en_el_lenguaje():
    i = correr("a = [[2, 1], [1, 3]]\nd = determinante(a)\nx = resolver(a, [5, 10])\nf = forma(a)")
    assert valor(i, "d") == pytest.approx(5)
    assert valor(i, "x") == pytest.approx([1, 3])
    assert valor(i, "f") == [2, 2]


# --- Libreria de aprendizaje ----------------------------------------------------------------

def test_regresion_encuentra_la_recta_exacta():
    t = Tabla(["x", "z", "y"], {"x": [1, 2, 3, 4, 5], "z": [0, 1, 0, 1, 1],
                                "y": [2 * x + 3 * z + 1 for x, z in zip([1, 2, 3, 4, 5], [0, 1, 0, 1, 1])]})
    modelo = aprendizaje.regresion(t, ["x", "z"], "y")
    assert modelo["coeficientes"] == pytest.approx([1, 2, 3])
    assert modelo["r2"] == pytest.approx(1)
    assert aprendizaje.predecir(modelo, [10, 1]) == pytest.approx(24)


def test_regresion_con_ruido_se_acerca():
    azar = random.Random(1)
    xs = [i / 10 for i in range(200)]
    t = Tabla(["x", "y"], {"x": xs, "y": [5 - 0.5 * x + azar.gauss(0, 0.1) for x in xs]})
    b0, b1 = aprendizaje.regresion(t, "x", "y")["coeficientes"]
    assert b0 == pytest.approx(5, abs=0.05) and b1 == pytest.approx(-0.5, abs=0.01)


def test_vecinos_clasifica_dos_nubes():
    t = Tabla(["a", "b", "clase"], {"a": [0, 1, 0, 1, 10, 11, 10, 11], "b": [0, 0, 1, 1, 10, 10, 11, 11],
                                    "clase": ["azul"] * 4 + ["rojo"] * 4})
    modelo = aprendizaje.vecinos(t, ["a", "b"], "clase", 3)
    nuevos = Tabla(["a", "b"], {"a": [0.5, 10.5], "b": [0.2, 9.8]})
    assert aprendizaje.predecir(modelo, nuevos)["prediccion"].valores == ["azul", "rojo"]


def test_k_medias_separa_tres_grupos():
    puntos = [(0, 0), (0, 1), (1, 0), (20, 20), (21, 20), (20, 21), (40, 0), (41, 1), (40, 1)]
    t = Tabla(["x", "y"], {"x": [p[0] for p in puntos], "y": [p[1] for p in puntos]})
    grupos = aprendizaje.grupos(t, ["x", "y"], 3)["grupo"].valores
    assert grupos == [1, 1, 1, 2, 2, 2, 3, 3, 3]


def test_dividir_no_pierde_filas_y_se_repite():
    t = Tabla(["x"], {"x": list(range(10))})
    a, b = aprendizaje.dividir(t, 0.7)
    assert len(a) == 7 and len(b) == 3
    assert sorted(a["x"].valores + b["x"].valores) == list(range(10))
    assert aprendizaje.dividir(t, 0.7)[0]["x"].valores == a["x"].valores


def test_metricas():
    assert aprendizaje.error_cuadratico([1, 2, 3], [1, 2, 5]) == pytest.approx(4 / 3)
    assert aprendizaje.r2([1, 2, 3], [1, 2, 3]) == 1
    assert aprendizaje.exactitud(Columna(["a", "b", "a"]), ["a", "a", "a"]) == pytest.approx(2 / 3)


def test_modelos_en_el_lenguaje(datos):
    i = correr(CARGA + """
limpia = t |> quitar faltantes
m = regresion(limpia, "sincronizacion", "armonicos")
p = predecir(m, limpia)
c = vecinos(limpia, ["sincronizacion", "armonicos"], "piloto", 1)
q = predecir(c, limpia)
g = grupos(limpia, "sincronizacion", 2)""")
    assert valor(i, "m")["tipo"] == "regresion" and "prediccion" in valor(i, "p").columnas
    assert valor(i, "q")["prediccion"].valores == valor(i, "q")["piloto"].valores
    assert sorted(set(valor(i, "g")["grupo"].valores)) == [1, 2]


def test_errores_de_modelos(datos):
    assert "faltantes" in falla(CARGA + '\nm = regresion(t, "sincronizacion", "armonicos")')
    limpia = CARGA + "\nl = t |> quitar faltantes"
    assert "numérica" in falla(limpia + '\nm = regresion(l, "piloto", "armonicos")')
    assert "modelo" in falla("m = predecir(5, 3)")
    assert "k tiene que ser" in falla(limpia + '\nm = grupos(l, "sincronizacion", 50)')


# --- Funciones del usuario ------------------------------------------------------------------

def test_funcion_con_parametros_y_retorno():
    assert v("funcion promedio(a, b) { retornar (a + b) / 2 }\nr = promedio(4, 10)") == 7


def test_funcion_recursiva():
    assert v("""funcion fact(n) {
    si n <= 1 { retornar 1 }
    retornar n * fact(n - 1)
}
r = fact(10)""") == 3628800


def test_retornar_corta_ciclos():
    assert v("""funcion primero_mayor(lista, limite) {
    para x en lista { si x > limite { retornar x } }
    retornar nulo
}
r = primero_mayor([1, 5, 9, 12], 6)""") == 9


def test_las_variables_de_la_funcion_son_locales():
    i = correr("x = 1\nfuncion f(a) { x = a * 100\n retornar x }\nr = f(2)")
    assert valor(i, "r") == 200 and valor(i, "x") == 1


def test_la_funcion_ve_las_variables_globales():
    assert v("iva = 0.19\nfuncion con_iva(p) { retornar p * (1 + iva) }\nr = con_iva(100)") == pytest.approx(119)


def test_funcion_que_recibe_y_devuelve_una_tabla(datos):
    t = v(CARGA + """
funcion de_piloto(tabla, nombre) {
    retornar tabla |> filtrar donde piloto == nombre |> seleccionar [piloto, sincronizacion]
}
r = de_piloto(t, "Shinji")""")
    assert len(t) == 2 and t.columnas == ["piloto", "sincronizacion"]


def test_funcion_sin_retornar_devuelve_nulo():
    assert v("funcion nada() { x = 1 }\nr = nada()") is None


def test_errores_de_funciones():
    assert "recibe 2 argumentos" in falla("funcion f(a, b) { retornar a }\nx = f(1)")
    assert "solo puede ir dentro de una función" in falla("retornar 5")
    assert "ya es una función del lenguaje" in falla("funcion media(a) { retornar a }")
    assert "repetido" in falla("funcion f(a, a) { retornar a }")
    assert "recursión" in falla("funcion f(n) { retornar f(n + 1) }\nx = f(1)")


def test_mapear_con_lista_y_columna(datos):
    assert v("funcion doble(x) { retornar x * 2 }\nr = mapear(doble, [1, 2, 3])") == [2, 4, 6]
    t = v(CARGA + """
funcion nivel(s) { si s >= 80 { retornar "alto" } retornar "bajo" }
r = t |> crear n = mapear(nivel, sincronizacion)""")
    assert t["n"].valores == ["bajo", "alto", "bajo", None, "alto"]


# --- Metodos numericos con funciones del usuario -----------------------------------------------

def test_raices_por_biseccion_y_newton():
    codigo = "funcion f(x) { retornar x ^ 2 - 2 }\n"
    assert v(codigo + "r = biseccion(f, 0, 2)") == pytest.approx(math.sqrt(2), abs=1e-10)
    assert v(codigo + "r = newton(f, 1)") == pytest.approx(math.sqrt(2), abs=1e-10)
    assert v(codigo + "r = derivada(f, 3)") == pytest.approx(6, abs=1e-6)
    assert "mismo signo" in falla(codigo + "r = biseccion(f, 2, 3)")
    assert "recibe primero una función" in falla("r = newton(5, 1)")


# --- Arbol, perceptron, red neuronal y correlacion ----------------------------------------------

def test_arbol_encuentra_el_corte():
    t = Tabla(["x", "clase"], {"x": [1, 2, 3, 4, 10, 11, 12, 13], "clase": ["a"] * 4 + ["b"] * 4})
    modelo = aprendizaje.arbol(t, "x", "clase")
    assert modelo["raiz"]["umbral"] == 7 and modelo["exactitud"] == 1
    assert aprendizaje.reglas(modelo) == ["si x <= 7 -> a (4 filas)", "si x > 7 -> b (4 filas)"]


def test_arbol_con_dos_variables_y_profundidad():
    # la clase depende de x y de y a la vez: hace falta profundidad 2
    puntos = [(x, y) for x in range(4) for y in range(4)]
    t = Tabla(["x", "y", "c"], {"x": [p[0] for p in puntos], "y": [p[1] for p in puntos],
                                "c": ["si" if p[0] >= 2 and p[1] >= 2 else "no" for p in puntos]})
    assert aprendizaje.arbol(t, ["x", "y"], "c", 1)["exactitud"] < 1
    assert aprendizaje.arbol(t, ["x", "y"], "c", 2)["exactitud"] == 1


def test_arbol_de_regresion_predice_promedios():
    t = Tabla(["x", "y"], {"x": [1, 2, 3, 10, 11, 12], "y": [5, 5, 5, 20, 22, 24]})
    modelo = aprendizaje.arbol(t, "x", "y", 1)
    assert modelo["clase"] == "regresion"
    assert aprendizaje.predecir(modelo, 2) == 5 and aprendizaje.predecir(modelo, 11) == 22


def test_gini():
    assert aprendizaje.gini(["a", "a"]) == 0
    assert aprendizaje.gini(["a", "b"]) == 0.5


def test_perceptron_separa_y_la_perdida_baja():
    t = Tabla(["a", "b", "c"], {"a": [0, 1, 0, 1, 5, 6, 5, 6], "b": [0, 0, 1, 1, 5, 5, 6, 6],
                                "c": [False] * 4 + [True] * 4})
    modelo = aprendizaje.perceptron(t, ["a", "b"], "c", 0.5, 200)
    assert modelo["exactitud"] == 1
    assert modelo["perdidas"][-1] < modelo["perdidas"][0]
    assert all(b <= a + 1e-12 for a, b in zip(modelo["perdidas"], modelo["perdidas"][1:]))
    assert aprendizaje.predecir(modelo, [5.5, 5.5]) is True


def test_perceptron_gradiente_coincide_con_la_derivada_numerica():
    # con una sola epoca, el paso que da es -tasa * gradiente; se compara con la derivada numerica
    t = Tabla(["x", "c"], {"x": [-2, -1, 1, 3], "c": [0, 0, 1, 1]})
    modelo = aprendizaje.perceptron(t, "x", "c", 1.0, 1)
    medias, desv = aprendizaje._escala([[x] for x in [-2, -1, 1, 3]])
    xs = [(x - medias[0]) / desv[0] for x in [-2, -1, 1, 3]]

    def perdida(w):
        return sum(aprendizaje._entropia(aprendizaje.sigmoide(w * x), y) for x, y in zip(xs, [0, 0, 1, 1])) / 4

    h = 1e-6
    numerica = (perdida(h) - perdida(-h)) / (2 * h)
    assert modelo["pesos"][0] == pytest.approx(-numerica, rel=1e-5)


def test_perceptron_necesita_dos_clases():
    t = Tabla(["x", "c"], {"x": [1, 2, 3], "c": ["a", "b", "c"]})
    with pytest.raises(ValueError, match="exactamente 2 clases"):
        aprendizaje.perceptron(t, "x", "c")


def test_red_neuronal_aprende_xor():
    # XOR no se puede separar con una linea (un perceptron solo no puede), la red si
    t = Tabla(["a", "b", "c"], {"a": [0, 0, 1, 1] * 5, "b": [0, 1, 0, 1] * 5, "c": ["no", "si", "si", "no"] * 5})
    red = aprendizaje.red_neuronal(t, ["a", "b"], "c", 4, 0.5, 400)
    assert red["exactitud"] == 1
    assert red["perdida"] < red["perdidas"][0]
    assert aprendizaje.perceptron(t, ["a", "b"], "c", 0.5, 400)["exactitud"] < 1


def test_correlacion():
    assert aprendizaje.correlacion([1, 2, 3], [2, 4, 6]) == pytest.approx(1)
    assert aprendizaje.correlacion([1, 2, 3], [3, 2, 1]) == pytest.approx(-1)
    assert "constante" in falla("x = correlacion([1, 1], [1, 2])")


def test_modelos_nuevos_en_el_lenguaje(datos):
    i = correr(CARGA + """
limpia = t |> quitar faltantes |> crear alta = sincronizacion > 70
a = arbol(limpia, "sincronizacion", "piloto", 2)
reg = reglas(a)
p = perceptron(limpia, ["sincronizacion", "armonicos"], "alta")
red = red_neuronal(limpia, "sincronizacion", "piloto", 3, 0.5, 50)
q = predecir(red, limpia)""")
    assert valor(i, "a")["tipo"] == "arbol" and all(r.startswith("si ") for r in valor(i, "reg"))
    assert valor(i, "p")["exactitud"] == 1
    assert "prediccion" in valor(i, "q").columnas
