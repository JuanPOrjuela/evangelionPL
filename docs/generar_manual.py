"""Genera docs/manual_evangelionPL.pdf.

Arma el manual en HTML con cosas que salen del propio proyecto (los tokens,
el arbol, las salidas de los ejemplos) y lo imprime a PDF con Chrome o Edge.

    pip install pypdf
    python docs/generar_manual.py
"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from pypdf import PdfReader, PdfWriter

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
sys.path.insert(0, str(RAIZ / "src"))

from evangelion.analizador import analizar  # noqa: E402
from evangelion.arbol import como_svg, como_texto  # noqa: E402
from evangelion.cli import main  # noqa: E402
from evangelion.generado.EvaLexer import EvaLexer  # noqa: E402

TITULO = "evangelionPL: manual del lenguaje"
AUTOR = "Juan Pablo Orjuela Rojas"
EJEMPLO_ARBOL = "altas = pruebas |> AT_FIELD donde sincronizacion >= 60 |> BATTERY 5"

NAVEGADORES = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]

# (instruccion, que hace, de donde sale el nombre)
CATALOGO = [
    ('NERV "título"', "Le pone nombre a la operación. Es opcional y va en la primera línea.",
     "NERV es la organización que dirige todo."),
    ('ENTRY_PLUG "archivo.csv"', "Carga un archivo CSV como tabla.",
     "Es la cápsula por donde el piloto entra al EVA; aquí es por donde entran los datos."),
    ("TARGET [a, b]", "Deja solo las columnas de la lista.", "Fijar el blanco antes de disparar."),
    ("AT_FIELD donde condición", "Deja pasar solo las filas que cumplen la condición.",
     "El campo AT es la barrera que no deja pasar casi nada."),
    ("SYNC col = expresión", "Crea una columna calculada (o varias, separadas por coma).",
     "La sincronización entre piloto y EVA."),
    ("CODENAME [vieja -> nueva]", "Les cambia el nombre a las columnas.", "Los nombres clave."),
    ("FORMATION por [col desc]", "Ordena las filas; cada columna puede ir asc o desc.",
     "La formación en la que salen las unidades."),
    ("EJECT duplicados | faltantes | columnas", "Saca filas repetidas, filas con vacíos o columnas completas.",
     "La eyección de la cápsula."),
    ("DUMMY_PLUG col = valor", "Rellena los vacíos de una columna.",
     "El dummy plug reemplaza al piloto cuando falta."),
    ("EQUIP col -> tipo", "Convierte la columna a entero, real, texto o booleano.",
     "Los equipos (tipo B, tipo D) que le cambian al EVA."),
    ("SQUAD por [a, b]", "Arma los grupos. Después siempre va MAGI.", "El escuadrón."),
    ("MAGI n = contar(), m = media(col)", "Calcula un resumen por grupo, o de toda la tabla si no hay grupos.",
     "Las supercomputadoras que hacen todos los cálculos de NERV."),
    ("BATTERY n", "Deja las primeras n filas.", "La batería interna, que dura poquito."),
    ("DIAGNOSTIC", "Estadísticas de cada columna: válidos, faltantes, distintos, media, desviación, mínimo y máximo.",
     "El chequeo de la unidad."),
    ("MONITOR flujo", "Muestra una tabla o un valor en la terminal.", "Las pantallas del centro de mando."),
    ('SEELE flujo como "archivo.csv"', "Guarda una tabla en un CSV.", "El comité al que NERV le entrega informes."),
    ("PATTERN_BLUE cond { } PATTERN_ORANGE { }", "Condicional: ejecuta el primer bloque si se cumple y, si no, el segundo.",
     "Patrón azul es ángel confirmado; patrón naranja, sin identificar."),
    ("HOLOGRAM tipo de tabla { }", "Describe una gráfica. Por ahora solo se revisa; se dibuja en la fase 3.",
     "Los hologramas de las reuniones de SEELE."),
]

CATEGORIAS = {
    "NERV": "Instrucciones", "TARGET": "Etapas del flujo", "DONDE": "Conectores",
    "Y": "Lógicos y literales fijos", "TUBERIA": "Operadores y signos",
    "REAL": "Con lexema variable",
}

PATRONES = {
    "REAL": "dígitos, un punto y más dígitos: 0.75",
    "ENTERO": "uno o más dígitos: 42",
    "CADENA": 'texto entre comillas dobles: "Tokio-3"',
    "CADENA_SIN_CERRAR": "comilla que nunca se cierra; se reporta como error léxico",
    "ID": "letra o guion bajo seguido de letras, dígitos o guiones bajos: sync_01",
    "ID_ESCAPADO": "cualquier texto entre acentos graves: `Unidad EVA`",
    "COMENTARIO": "desde # hasta el final de la línea; se descarta",
    "ESPACIOS": "espacios, tabulaciones y saltos de línea; se descartan",
    "CARACTER_INVALIDO": "cualquier otro carácter; se reporta como error léxico",
}

REGLAS = [
    ("Variables", "Una variable tiene que estar asignada antes de usarse. Se puede volver a asignar."),
    ("Columnas", "Toda columna que se nombre en una etapa tiene que existir en la tabla que llega. "
                 "Si no existe, el error sugiere la que más se parece."),
    ("Nombres dentro de una etapa", "Primero se busca entre las columnas de la tabla y después entre las variables."),
    ("Aritmética", "+ - * / % ^ solo aceptan números. El + también pega dos textos. Dividir un valor por cero "
                   "es un error; dentro de una columna, esa fila queda como faltante."),
    ("Comparaciones", "< <= > >= comparan número con número o texto con texto. "
                      "== y != piden la misma clase a los dos lados, salvo que uno sea nulo."),
    ("Lógica", "y, o, no solo aceptan valores de verdadero/falso."),
    ("Condiciones", "La condición de AT_FIELD y la de PATTERN_BLUE tienen que dar verdadero o falso."),
    ("Etapas", "Una etapa solo se aplica a una tabla. Ninguna cambia la tabla original: devuelve una nueva."),
    ("Grupos", "Después de SQUAD la única etapa permitida es MAGI."),
    ("Agregaciones", "suma, media, mediana y desviacion piden una columna numérica; minimo, maximo y contar sirven con cualquiera."),
    ("Faltantes", "Una operación con un faltante da faltante y una comparación da falso. DUMMY_PLUG rellena "
                  "con un valor de la misma clase que la columna."),
    ("Conversión", "EQUIP falla si algún valor no encaja en el tipo nuevo. Los vacíos siguen vacíos."),
    ("Archivos", "ENTRY_PLUG falla si el archivo no existe. SEELE solo recibe tablas y solo escribe .csv."),
]

LIBRERIA = [
    ("Archivos CSV", "Lee el archivo carácter por carácter: respeta las comillas, acepta cualquier separador y "
                     "decide si cada columna es de enteros, de reales o de texto. Un campo vacío es un faltante. "
                     "También escribe el CSV de salida."),
    ("<code>Columna</code>", "Una lista de valores con las operaciones fila por fila (aritmética, comparaciones, "
                             "y, o, no), las estadísticas y las conversiones de tipo."),
    ("<code>Tabla</code>", "Varias columnas del mismo largo. Sabe seleccionar, filtrar, ordenar por varias columnas, "
                           "quitar duplicados y faltantes, agrupar, resumir y mostrarse alineada en la terminal."),
]

DECISIONES = [
    ("Faltantes", "Se guardan como None. No cuentan en ninguna estadística."),
    ("Media y mediana", "La media es la suma entre la cantidad de datos. La mediana es el dato del centro ya "
                        "ordenados, o el promedio de los dos del centro si la cantidad es par."),
    ("Desviación", "Es la muestral: la suma de las diferencias al cuadrado se divide entre n - 1 y se saca la raíz. "
                   "Con un solo dato no se puede calcular y da nulo."),
    ("Orden", "Se ordena de la última columna a la primera con un ordenamiento estable, y los faltantes van al final."),
    ("Grupos", "Salen en el orden en que aparecen en la tabla."),
    ("Tablas nuevas", "Ninguna operación cambia la tabla que recibe; siempre devuelve otra."),
]

CSS = """
@page { size: A4; margin: 24mm 22mm 22mm 22mm;
        @bottom-center { content: counter(page); font-family: Georgia, serif; font-size: 9pt; color: #555; } }
@page :first { @bottom-center { content: none; } }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 16pt; font-weight: normal; margin: 30pt 0 8pt; break-after: avoid; }
h2 { font-size: 11.5pt; margin: 16pt 0 5pt; break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; hyphens: auto; }
code, pre { font-family: Consolas, 'Courier New', monospace; }
code { font-size: 9pt; }
pre { font-size: 7.9pt; line-height: 1.3; margin: 6pt 0 11pt 10pt; white-space: pre-wrap; break-inside: avoid; }
pre.largo { break-inside: auto; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 12pt; font-size: 9.3pt; }
thead { display: table-header-group; }
th { text-align: left; font-weight: bold; border-top: 0.9pt solid #111; border-bottom: 0.5pt solid #111; padding: 3.5pt 6pt 3.5pt 0; }
td { vertical-align: top; padding: 3.5pt 6pt 3.5pt 0; border-bottom: 0.25pt solid #bbb; }
tr { break-inside: avoid; }
tbody tr:last-child td { border-bottom: 0.9pt solid #111; }
td code { font-size: 8.3pt; }
.portada { height: 235mm; display: flex; flex-direction: column; justify-content: center; }
.portada .nombre { font-size: 30pt; letter-spacing: 0.5pt; margin: 0; }
.portada .sub { font-size: 13pt; color: #444; margin: 6pt 0 0; }
.portada .datos { margin-top: 90mm; font-size: 10.5pt; line-height: 1.6; color: #333; }
.portada hr { border: none; border-top: 0.9pt solid #111; width: 38mm; margin: 14pt 0; }
.salto { break-before: page; }
.nota { font-size: 9.3pt; color: #444; }
figure { margin: 8pt 0 12pt; text-align: center; break-inside: avoid; }
figure svg { max-width: 100%; height: auto; }
figcaption { font-size: 9pt; color: #444; margin-top: 4pt; }
.flujo { font-family: Consolas, monospace; font-size: 8pt; text-align: center; margin: 10pt 0 12pt; }
"""


def correr(*argumentos) -> str:
    """Corre la linea de comandos y devuelve lo que imprimio."""
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        main(list(argumentos))
    return salida.getvalue().rstrip() + "\n"


def bloque(texto: str, largo: bool = False) -> str:
    clase = ' class="largo"' if largo else ""
    return f"<pre{clase}>{escape(texto.strip(chr(10)))}</pre>"


def tabla(encabezados, filas, anchos=None) -> str:
    cols = ""
    if anchos:
        cols = "<colgroup>" + "".join(f'<col style="width:{a}">' for a in anchos) + "</colgroup>"
    cabeza = "".join(f"<th>{e}</th>" for e in encabezados)
    cuerpo = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in fila) + "</tr>" for fila in filas)
    return f"<table>{cols}<thead><tr>{cabeza}</tr></thead><tbody>{cuerpo}</tbody></table>"


def tablas_de_tokens() -> str:
    """Las saca del lexer generado, asi no se desactualizan si cambia la gramatica."""
    fijos, variables, categoria = {}, [], ""
    for tipo, nombre in enumerate(EvaLexer.symbolicNames):
        if tipo == 0:
            continue
        categoria = CATEGORIAS.get(nombre, categoria)
        if nombre in PATRONES:
            variables.append((f"<code>{nombre}</code>", escape(PATRONES[nombre])))
            continue
        lexema = EvaLexer.literalNames[tipo][1:-1]
        texto = lexema if lexema == nombre else f"{nombre} {lexema}"
        fijos.setdefault(categoria, []).append(f"<code>{escape(texto)}</code>")

    filas = [(cat, ", ".join(tokens)) for cat, tokens in fijos.items()]
    return (tabla(["Categoría", "Tokens (nombre y lexema)"], filas, ["24%", "76%"])
            + tabla(["Token", "Qué reconoce"], variables, ["24%", "76%"]))


def solo_error(salida: str) -> str:
    """De la salida con Gendo deja solo el bloque del error."""
    lineas = salida.splitlines()
    inicio = next(i for i, linea in enumerate(lineas) if linea.startswith("  Error"))
    return "\n".join(lineas[inicio:-2])


def armar_html() -> str:
    os.chdir(RAIZ)
    ej = RAIZ / "ejemplos"
    primero = ej / "01_primera_prueba.eva"
    arbol = analizar(EJEMPLO_ARBOL).arbol
    svg = como_svg(arbol)
    (DOCS / "arbol_ejemplo.svg").write_text(svg, encoding="utf-8")

    tokens = correr(str(primero), "--tokens", "--solo-analisis").split("\n\n")[0]
    tokens = "\n".join(tokens.splitlines()[:16]) + "\n ..."
    simbolos = correr(str(ej / "04_seguimiento_de_asuka.eva"), "--simbolos")
    simbolos = simbolos[simbolos.index("TABLA DE SÍMBOLOS"):].split("\n\n")[0]

    errores = [(titulo, solo_error(correr(str(ej / "errores" / archivo))))
               for titulo, archivo in [
                   ("Léxico", "lex_01_caracter_invalido.eva"),
                   ("Sintáctico", "sin_02_etapa_inexistente.eva"),
                   ("Semántico", "sem_02_columna_inexistente.eva"),
                   ("Semántico", "sem_03_tipos_incompatibles.eva")]]

    catalogo = [(f"<code>{escape(i)}</code>", escape(q), escape(p)) for i, q, p in CATALOGO]
    precedencia = [
        ("1 (más fuerte)", "<code>( )</code>, llamadas, <code>tabla.columna</code>", "—"),
        ("2", "<code>^</code>", "derecha"),
        ("3", "<code>-</code> de signo", "—"),
        ("4", "<code>*  /  %</code>", "izquierda"),
        ("5", "<code>+  -</code>", "izquierda"),
        ("6", "<code>&lt;  &lt;=  &gt;  &gt;=</code>", "izquierda"),
        ("7", "<code>==  !=</code>", "izquierda"),
        ("8", "<code>no</code>", "—"),
        ("9", "<code>y</code>", "izquierda"),
        ("10 (más débil)", "<code>o</code>", "izquierda"),
    ]
    funciones = [
        ("<code>suma media mediana desviacion</code>", "Agregaciones sobre una columna numérica."),
        ("<code>minimo maximo contar</code>", "Agregaciones sobre cualquier columna. <code>contar()</code> sin columna cuenta filas."),
        ("<code>filas(tabla)</code>", "Cuántas filas tiene una tabla."),
        ("<code>redondear(x, n)</code>, <code>absoluto(x)</code>", "Para números o columnas numéricas."),
        ("<code>mayusculas(t)</code>, <code>minusculas(t)</code>", "Para textos o columnas de texto."),
    ]

    partes = [f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>{TITULO}</title><style>{CSS}</style></head><body>

<section class="portada">
  <p class="nombre">evangelionPL</p>
  <p class="sub">Manual del lenguaje. Fases 1 y 2</p>
  <hr>
  <div class="datos">
    {AUTOR}<br>
    Lenguajes de Programación y Transducción<br>
    Ciencias de la Computación e Inteligencia Artificial<br>
    Universidad Sergio Arboleda, 2026-2
  </div>
</section>

<h1 class="salto">1. Qué es evangelionPL</h1>
<p>evangelionPL es un lenguaje de dominio específico para trabajar con tablas de datos: cargar un CSV,
escoger columnas, filtrar filas, crear columnas calculadas, agrupar, sacar estadísticas y guardar el
resultado. Es lo que pide el proyecto del curso, solo que las instrucciones se llaman como cosas de
Neon Genesis Evangelion. Los datos entran por el <code>ENTRY_PLUG</code>, el <code>AT_FIELD</code> deja
pasar únicamente las filas que cumplen una condición y las <code>MAGI</code> hacen los cálculos.</p>
<p>La idea central es el flujo: se parte de una tabla y se le encadenan etapas con <code>|&gt;</code>.
Cada etapa recibe una tabla y entrega otra nueva, así que el programa se lee de arriba hacia abajo como
una lista de pasos. El lenguaje no pretende ser otro Python: solo sabe hacer estas operaciones, pero las
dice corto.</p>
<p>Está hecho con ANTLR4 y Python. Para manejar los datos no se usa pandas ni ninguna otra librería:
todo lo hace una librería propia de tablas, escrita para este proyecto. Este documento cubre las dos
primeras fases.</p>
{tabla(["Fase", "Qué pide el curso", "Estado"], [
    ("1", "Especificación del lenguaje, gramática, lexer y parser, árbol de análisis y errores léxicos y sintácticos.", "Completa"),
    ("2", "Visitor, tabla de símbolos, ejecución sobre datos, agregaciones, exportar a CSV y errores semánticos.", "Completa"),
    ("3", "Gráficas y caso de estudio final.", "Pendiente. <code>HOLOGRAM</code> ya se reconoce y se revisa, pero no dibuja."),
], ["8%", "62%", "30%"])}

<h2>Un primer programa</h2>
{bloque(primero.read_text(encoding="utf-8"))}
<p>Al ejecutarlo con <code>python run.py ejemplos/01_primera_prueba.eva</code> sale la tabla y, como
todo estuvo bien, el EVA-01 felicita:</p>
{bloque(correr(str(primero)))}

<h1>2. Catálogo de instrucciones</h1>
<p>Las instrucciones van en mayúscula y son términos de la serie. Los conectores (<code>donde</code>,
<code>por</code>, <code>como</code>, <code>con</code>, <code>de</code>) van en minúscula y en español.
La tercera columna cuenta por qué cada instrucción se llama así.</p>
{tabla(["Instrucción", "Qué hace", "Por qué ese nombre"], catalogo, ["33%", "37%", "30%"])}
<h2>Funciones</h2>
{tabla(["Función", "Uso"], funciones, ["42%", "58%"])}
<p class="nota">Los tipos de <code>EQUIP</code> son entero, real, texto y booleano. Los tipos de
<code>HOLOGRAM</code> son barras, lineas, histograma, dispersion y caja. Ninguno es palabra reservada:
se validan en la fase semántica, para que una columna pueda llamarse, por ejemplo, <code>texto</code>.</p>

<h1>3. Fase 1: análisis léxico</h1>
<p>Toda la gramática está en un solo archivo, <code>grammar/Eva.g4</code>: arriba las reglas
sintácticas y abajo las léxicas. De ahí ANTLR saca el lexer, que lee el archivo carácter por carácter y
entrega tokens. Estas tablas se generan a partir del lexer que produce ANTLR, así que siempre coinciden con la
gramática.</p>
{tablas_de_tokens()}
<h2>Decisiones del lexer</h2>
<p>Las palabras reservadas se declaran antes que <code>ID</code>. Cuando dos reglas reconocen el mismo
texto, ANTLR se queda con la primera, y por eso <code>MAGI</code> sale como instrucción y no como nombre.
Si el texto es más largo (<code>MAGI_2</code>) gana <code>ID</code>, porque siempre se prefiere el lexema
más largo. Las reservadas distinguen mayúsculas: <code>magi</code> es un nombre cualquiera.</p>
<p><code>REAL</code> va antes que <code>ENTERO</code> para que <code>3.5</code> no se parta en tres
tokens. Los comentarios y los espacios se descartan con <code>-&gt; skip</code> y el parser nunca los ve.</p>
<p>Las palabras <code>y</code>, <code>o</code> y <code>no</code> son operadores, así que no sirven como
nombres de variable. Para una columna que se llame así, o que tenga espacios, se usan acentos graves:
<code>`Unidad EVA`</code>.</p>
<p>Hay dos tokens que existen solo para atrapar errores: <code>CARACTER_INVALIDO</code> y
<code>CADENA_SIN_CERRAR</code>. Con ellos el lexer nunca se queda atascado y el error se reporta con la
línea y la columna exactas.</p>
<h2>Los tokens de un programa</h2>
<p>Con <code>--tokens</code> se ve lo que entrega el lexer. Estos son los primeros del ejemplo anterior:</p>
{bloque(tokens)}

<h1>4. Fase 1: análisis sintáctico</h1>
<p>Las reglas sintácticas son la primera parte de <code>grammar/Eva.g4</code> y de ellas sale el
parser. Esta es la gramática en EBNF:</p>
{bloque((DOCS / "gramatica.ebnf").read_text(encoding="utf-8"), largo=True)}
<h2>Precedencia de los operadores</h2>
{tabla(["Nivel", "Operadores", "Asociatividad"], precedencia, ["22%", "50%", "28%"])}
<p>En la EBNF la precedencia se ve por niveles (suma, término, potencia…). En el archivo
<code>.g4</code> es una sola regla <code>expresion</code> recursiva por la izquierda, y ANTLR saca la
precedencia del orden de las alternativas: la que está más arriba amarra más fuerte. Las dos formas
describen lo mismo, con una diferencia pequeña: el <code>.g4</code> también acepta un <code>no</code>
como operando (<code>a == no b</code>). La potencia es asociativa a la derecha, así que
<code>2 ^ 3 ^ 2</code> es 2 ^ 9, y <code>-2 ^ 2</code> da -4 como en matemáticas.</p>
<p>No hay punto y coma. Cada sentencia empieza con una instrucción o con <code>nombre =</code>, y con
eso el parser sabe dónde termina la anterior. La regla <code>programa</code> termina en <code>EOF</code>
para que no se pueda colar basura al final del archivo.</p>

<h2>Árbol de análisis</h2>
<p>Para esta línea:</p>
{bloque(EJEMPLO_ARBOL)}
<p>el parser arma el siguiente árbol. Se ve que la comparación quedó colgando de la etapa
<code>AT_FIELD</code> y que las dos etapas son hermanas dentro del mismo flujo.</p>
<figure>{svg}<figcaption>Árbol generado con <code>python run.py archivo.eva --svg arbol.svg</code></figcaption></figure>
<p>El mismo árbol en texto, con <code>--arbol</code>:</p>
{bloque(como_texto(arbol))}
<p class="nota">Los nodos llevan el nombre de la alternativa (<code>etapaFiltrar</code>,
<code>exprRelacional</code>) y no solo el de la regla. Esas etiquetas son las que después usa el Visitor:
ANTLR genera un método <code>visit</code> por cada una.</p>

<h1>5. Fase 2: semántica y ejecución</h1>
<p>Si el programa pasa la fase 1, el árbol se recorre con el patrón Visitor
(<code>src/evangelion/interprete.py</code>). La clase <code>Interprete</code> hereda del
<code>EvaVisitor</code> que genera ANTLR y tiene un método por cada tipo de nodo:
<code>visitEtapaFiltrar</code>, <code>visitExprAditiva</code>, <code>visitGuardar</code>… Cada método
revisa que lo que le llegó tenga sentido y después le pide el trabajo a la librería de tablas.</p>
<p class="flujo">programa .eva &rarr; lexer &rarr; tokens &rarr; parser &rarr; árbol &rarr; Visitor
(revisa y ejecuta) &rarr; librería de tablas &rarr; tablas y CSV</p>
<h2>Tabla de símbolos</h2>
<p>Cada asignación guarda en la tabla de símbolos el nombre, la clase del valor, el valor y la línea
donde se definió. Hay un solo ámbito global: lo que se asigna dentro de un <code>PATTERN_BLUE</code>
sigue existiendo afuera. Con <code>--simbolos</code> se imprime al terminar; así queda después del
ejemplo 04:</p>
{bloque(simbolos)}
<p>Las clases de valor son tabla, numero, texto, booleano y nulo. Una columna suelta
(<code>tabla.columna</code>) se puede usar dentro de una expresión, pero no guardar en una variable.</p>
<h2>Reglas semánticas</h2>
{tabla(["Sobre", "Regla"], [(a, escape(b)) for a, b in REGLAS], ["24%", "76%"])}

<h2>La librería de tablas</h2>
<p>Está en <code>src/evangelion/tablas.py</code> y no depende de nada externo. El intérprete nunca toca
los datos directamente: decide qué hay que hacer y se lo pide a esta librería. Tiene tres partes.</p>
{tabla(["Parte", "Qué hace"], LIBRERIA, ["24%", "76%"])}
<p>Algunas decisiones que tocó tomar al escribirla:</p>
{tabla(["Tema", "Cómo quedó"], DECISIONES, ["24%", "76%"])}
<p class="nota">Lo único que viene de afuera es el runtime de ANTLR4, que es la herramienta del curso, y
pytest, que solo corre las pruebas. Las sugerencias de los errores (<i>¿Quisiste decir…?</i>) usan una
distancia de Levenshtein escrita a mano.</p>

<h1>6. Errores</h1>
<p>Hay tres clases de error y todas dicen la línea y la columna, muestran la línea de código y ponen
una flecha debajo del sitio exacto. Los mensajes de ANTLR vienen en inglés
(<i>mismatched input…</i>), así que se traducen antes de mostrarlos. Cuando algo falla aparece el
comandante Ikari:</p>
{bloque(correr(str(ej / "errores" / "sin_01_falta_corchete.eva")))}
<p>Un ejemplo de cada clase (sin repetir el dibujo):</p>
{"".join(f"<h2>{t}</h2>" + bloque(e) for t, e in errores)}
<p class="nota">El error semántico solo aparece si el programa está bien escrito: primero se revisan
todos los errores léxicos y sintácticos, y la ejecución se detiene en el primer error semántico.</p>

<h1>7. Programas completos</h1>
<p>En <code>ejemplos/</code> hay {len(list(ej.glob('*.eva')))} programas que corren de principio a fin y
{len(list((ej / 'errores').glob('*.eva')))} con errores a propósito. Estos dos muestran casi todo el lenguaje.</p>
<h2>Resumen por piloto</h2>
{bloque((ej / "02_resumen_por_piloto.eva").read_text(encoding="utf-8"))}
{bloque(correr(str(ej / "02_resumen_por_piloto.eva")).split("                    /\\")[0])}
<p>El archivo <code>salidas/resumen_pilotos.csv</code> queda así:</p>
{bloque((RAIZ / "salidas" / "resumen_pilotos.csv").read_text(encoding="utf-8"))}
<h2>Informe de combates</h2>
{bloque((ej / "03_informe_de_combates.eva").read_text(encoding="utf-8"), largo=True)}
{bloque(correr(str(ej / "03_informe_de_combates.eva")).split("                    /\\")[0])}
<p class="nota">Los datos de <code>datos/</code> son de práctica: los nombres salen de la serie y las
cifras son inventadas.</p>

<h1>8. Cómo se usa</h1>
{bloque('''instalar.bat                                   (crea el entorno, instala y corre las pruebas)
eva ejemplos\\\\01_primera_prueba.eva             (ejecuta un programa)

python run.py programa.eva --tokens            (muestra los tokens)
python run.py programa.eva --arbol             (muestra el árbol en texto)
python run.py programa.eva --svg arbol.svg     (guarda el árbol como dibujo)
python run.py programa.eva --simbolos          (muestra la tabla de símbolos)
python run.py programa.eva --solo-analisis     (fase 1 sin ejecutar)

python -m pytest                               (corre las pruebas)
python regenerar.py                            (vuelve a generar lexer y parser)'''.replace(chr(92) * 2, chr(92)))}
<p>Las rutas de los CSV se leen desde la carpeta donde se ejecuta el comando, por eso los ejemplos se
corren parados en la raíz del proyecto.</p>
{tabla(["Carpeta", "Contenido"], [
    ("<code>grammar/</code>", "<code>Eva.g4</code>, la gramática de ANTLR con las reglas léxicas y sintácticas juntas."),
    ("<code>src/evangelion/</code>", "El analizador (fase 1), el intérprete, la tabla de símbolos y la librería de tablas (fase 2), los errores, el árbol y los dibujos de la terminal."),
    ("<code>src/evangelion/generado/</code>", "Lo que genera ANTLR. No se edita a mano."),
    ("<code>ejemplos/</code>", "Programas válidos y, en <code>errores/</code>, programas que deben fallar."),
    ("<code>datos/</code>, <code>salidas/</code>", "Los CSV de entrada y los reportes que escriben los programas."),
    ("<code>tests/</code>", "Pruebas con pytest de las dos fases."),
], ["34%", "66%"])}
<h2>Lo que falta</h2>
<p>Para la fase 3 queda dibujar las gráficas de <code>HOLOGRAM</code>, también con una librería propia,
y montar el caso de estudio final. Tampoco hay funciones definidas por el usuario ni ciclos; por ahora no hicieron falta
porque las etapas ya trabajan sobre toda la tabla.</p>
</body></html>"""]
    return "".join(partes)


def imprimir_pdf(html: Path, pdf: Path) -> None:
    navegador = next((n for n in NAVEGADORES if Path(n).exists()), None)
    if navegador is None:
        raise SystemExit("No encontre Chrome ni Edge para imprimir el PDF.")
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([
            navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--user-data-dir={perfil}", f"--print-to-pdf={pdf}", html.as_uri(),
        ], check=True, capture_output=True)


def poner_metadatos(pdf: Path) -> None:
    escritor = PdfWriter()
    escritor.append(PdfReader(pdf))
    escritor.add_metadata({"/Title": TITULO, "/Author": AUTOR,
                           "/Creator": "evangelionPL", "/Producer": "evangelionPL"})
    escritor.write(pdf)


def generar() -> None:
    html = DOCS / "manual.html"
    pdf = DOCS / "manual_evangelionPL.pdf"
    html.write_text(armar_html(), encoding="utf-8")
    imprimir_pdf(html, pdf)
    poner_metadatos(pdf)
    print(f"Manual generado: {pdf.relative_to(RAIZ)} ({len(PdfReader(pdf).pages)} páginas)")


if __name__ == "__main__":
    generar()
