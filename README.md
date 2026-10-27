# EvangelionPL

- Julian Beltran
- Juan Orjuela
- Santiago Ortegon

Un lenguaje de dominio específico para analizar datos, con vocabulario de
*Neon Genesis Evangelion*. Proyecto de **Lenguajes de Programación y
Transducción** lo hicimos con ANTLR4 y Python.
El manejo de las tablas no usa pandas ni ninguna otra librería: lo hace una
librería propia que está en `src/evangelion/tablas.py`. Las gráficas tampoco usan
Matplotlib: se dibujan píxel por píxel y el PNG se arma desde cero.

Los datos entran por el `ENTRY_PLUG`, el `AT_FIELD` solo deja pasar las filas
que cumplen una condición y las `MAGI` hacen los cálculos. Si el programa corre,
el EVA-01 te felicita. Si no, aparece Gendo.

```
NERV "Resumen por piloto"

pruebas = ENTRY_PLUG "datos/pruebas_sincronizacion.csv"

por_piloto = pruebas
    |> EJECT faltantes [sincronizacion]
    |> AT_FIELD donde sincronizacion >= 40
    |> SQUAD por [piloto]
    |> MAGI pruebas = contar(), promedio = media(sincronizacion)
    |> FORMATION por [promedio desc]

MONITOR por_piloto
SEELE por_piloto como "salidas/resumen.csv"
```

## Qué está hecho

| Fase | Qué incluye | Estado |
|---|---|---|
| 1 | Gramática, lexer y parser, árbol de análisis, errores léxicos y sintácticos | Lista |
| 2 | Visitor, tabla de símbolos, ejecución sobre datos con la librería propia, agregaciones, exportar CSV, errores semánticos | Lista |
| 3 | Cinco tipos de gráfica en PNG o SVG con títulos, ejes y leyendas, caso de estudio con datos reales y pruebas de regresión | Lista |
| 3 (segunda parte) | Palabras en español, `sino si`, ciclos `mientras` y `para`, funciones con parámetros y retorno, listas y diccionarios, y librerías propias de matemáticas, métodos numéricos, matrices y aprendizaje automático (regresión lineal, árboles de decisión, perceptrón, red neuronal, k vecinos y k-medias) | Lista |

El manual completo (de usuario y técnico), con la tabla de tokens, la gramática en
EBNF, las reglas semánticas, cómo se dibujan las gráficas y el reporte de pruebas,
está en [`docs/manual_evangelionPL.pdf`](docs/manual_evangelionPL.pdf). El caso de
estudio está en [`caso_estudio/`](caso_estudio/README.md).

## Instalación

Hace falta Python 3.10 o superior. En Windows basta con:

```
instalar.bat
```

En Linux (o en una máquina virtual con Ubuntu):

```
bash instalar.sh
```

Cualquiera de los dos crea el entorno virtual, instala las dependencias y corre
las pruebas. En Ubuntu, si falta el paquete `python3-venv`, el script lo instala
y pide la contraseña de sudo. A mano sería:

```
python -m venv .venv
.venv\Scripts\activate              (en Linux: source .venv/bin/activate)
pip install antlr4-python3-runtime==4.13.2 pytest
```

No se necesita Java para usar el lenguaje: el lexer y el parser ya vienen
generados en `src/evangelion/generado/`.

## Cómo se usa

Desde la carpeta del proyecto:

```
eva ejemplos\01_primera_prueba.eva
```

o, que es lo mismo, `python run.py ejemplos/01_primera_prueba.eva`. En Linux:
`./eva.sh ejemplos/01_primera_prueba.eva`.

| Opción | Qué muestra |
|---|---|
| `--tokens` | Los tokens que entrega el lexer |
| `--arbol` | El árbol de análisis en texto |
| `--svg arbol.svg` | El árbol como dibujo (se abre en el navegador) |
| `--simbolos` | La tabla de símbolos al terminar |
| `--solo-analisis` | Revisa el programa sin ejecutarlo |

### Cuando todo sale bien

```
MONITOR mejores (5 filas x 4 columnas)
fecha       piloto  unidad  sincronizacion
2015-10-19  Shinji  EVA-01           93.50
2015-07-20  Asuka   EVA-02           92.70
2015-08-03  Asuka   EVA-02           86.60
2015-10-05  Shinji  EVA-01           80.10
2015-09-07  Rei     EVA-00           77.90

                    /\
                   /  \
                  / /\ \
                 / /  \ \
          ______/ /____\ \______
         /                      \
        /   _____        _____   \
       |    \####\      /####/    |
       |     '----'    '----'     |
        \                        /
         \      .--------.      /
          \     |VVVVVVVV|     /
           \    |^^^^^^^^|    /
            '.  '--------'  .'
              '-.________.-'
                  EVA - 01

  ¡Felicidades, Shinji! (omedetou!)
  Sincronización con el EVA-01 al 100 %: 01_primera_prueba.eva corrió sin errores.

    Operación : Primera prueba de sincronizacion
    Tokens    : 42
    Variables : pruebas, mejores
```

### Cuando algo falla

```
                .-''''''''''''-.
              .'  ////////////  '.
             /   //////////////   \
            |    .____.  .____.    |
            |  --|####|--|####|--  |
            |    '----'  '----'    |
             \       .----.       /
              \   .-'|_||_|'-.   /
          _____'-/  /|_||_|\  \-'_____
         /      /  / |_||_| \  \      \
        /      /  /   '--'   \  \      \
       /      /  /            \  \      \
      /      /__/              \__\      \
  ___/____________________________________\___

  ALERTA: sincronización fallida.
  Nivel de contaminación mental alto, el EVA no arranca.

  Error semántico en sem_02_columna_inexistente.eva, línea 3, columna 35
    'sincronisacion' no es una columna de la tabla ni una variable. ¿Quisiste decir 'sincronizacion'?
        3 | altas = pruebas |> AT_FIELD donde sincronisacion > 60
          |                                   ^

  Gendo: "Corrige la línea 3, Shinji. O vete."
```

Los errores pueden ser léxicos (un carácter que no existe), sintácticos (algo mal
escrito) o semánticos (bien escrito pero sin sentido, como promediar nombres).
Siempre dicen la línea y la columna.

## Instrucciones

Cada instrucción se puede escribir con su nombre de Evangelion o con una palabra
en español; las dos hacen lo mismo y se pueden mezclar en un programa.

| Evangelion | Español | Qué hace |
|---|---|---|
| `NERV "título"` | `programa "título"` | Nombre de la operación (opcional, primera línea) |
| `ENTRY_PLUG "archivo.csv"` | `cargar "archivo.csv"` | Carga un CSV. Acepta `con { separador: ";" }` |
| `TARGET [a, b]` | `seleccionar [a, b]` | Deja solo esas columnas |
| `AT_FIELD donde condición` | `filtrar donde condición` | Filtra filas |
| `SYNC col = expresión` | `crear col = expresión` | Crea columnas calculadas |
| `CODENAME [vieja -> nueva]` | `renombrar [vieja -> nueva]` | Renombra columnas |
| `FORMATION por [col desc]` | `ordenar por [col desc]` | Ordena |
| `EJECT duplicados \| faltantes \| columnas` | `quitar ...` | Elimina filas repetidas, filas con vacíos o columnas |
| `DUMMY_PLUG col = valor` | `rellenar col = valor` | Rellena vacíos |
| `EQUIP col -> tipo` | `convertir col -> tipo` | Convierte a entero, real, texto o booleano |
| `SQUAD por [a, b]` | `agrupar por [a, b]` | Agrupa (después va `resumir`) |
| `MAGI n = contar()` | `resumir n = contar()` | Resume: suma, media, mediana, minimo, maximo, desviacion, contar |
| `BATTERY n` | `limitar n` | Primeras n filas |
| `DIAGNOSTIC` | `diagnosticar` | Estadísticas de cada columna |
| `MONITOR flujo` | `mostrar flujo` | Muestra en pantalla |
| `SEELE flujo como "a.csv"` | `guardar flujo como "a.csv"` | Guarda en CSV |
| `PATTERN_BLUE c { } PATTERN_ORANGE { }` | `si c { } sino si c2 { } sino { }` | Condicional |
| `HOLOGRAM tipo de flujo { }` | `graficar tipo de flujo { }` | Dibuja una gráfica y la guarda en PNG o SVG |
| | `mientras c { }` | Repite mientras la condición sea verdadera |
| | `para i desde 1 hasta 10 { }` | Repite con un contador (incluye los dos extremos) |
| | `para x en lista { }` | Recorre una lista, un texto, las claves de un diccionario o las filas de una tabla |
| | `funcion f(a, b) { retornar ... }` | Define una función con parámetros que devuelve un resultado |

### Listas y diccionarios

```
pilotos = ["Shinji", "Asuka"]          # lista
agregar(pilotos, "Rei")
mostrar pilotos[0]                     # las posiciones empiezan en 0; -1 es el último
edades = {"Shinji": 14, Asuka: 14}     # diccionario (la clave puede ir sin comillas)
edades["Rei"] = 14
mostrar edades.Shinji                  # igual que edades["Shinji"]
mostrar [1, 2, 3] * 2                  # las cuentas con listas van elemento por elemento, como NumPy
```

Funciones de listas: `longitud`, `agregar`, `sacar`, `contiene`, `rango`, `ordenada`,
`invertida`, `unir`, `claves`, `valores`, `texto`, `numero`, `columna(tabla, "col")`,
`tabla_de({...})`, `aleatorio`, `semilla`. Las agregaciones (`suma`, `media`, ...)
también reciben listas.

### Matemáticas, matrices y modelos

| Librería | Funciones |
|---|---|
| Matemáticas (`matematica.py`) | `raiz(x)`, `raiz(x, n)`, `exp`, `ln`, `log(x)`, `log(x, base)`, `sen`, `cos`, `tan`, `piso`, `techo`, `factorial`, `redondear`, `absoluto`, y las constantes `pi` y `e` |
| Métodos numéricos | `biseccion(f, a, b)` y `newton(f, x0)` (raíces de una función), `derivada(f, x)`, `mapear(f, lista o columna)` |
| Matrices (`matrices.py`) | `ceros`, `unos`, `identidad`, `transpuesta`, `producto`, `punto`, `determinante`, `inversa`, `resolver(A, b)`, `forma`, `norma` |
| Predicción | `regresion(tabla, variables, objetivo)` (regresión lineal), `arbol(...)` con un objetivo numérico |
| Clasificación | `arbol(tabla, variables, objetivo, profundidad)` y `reglas(arbol)`, `perceptron(tabla, variables, objetivo, tasa, epocas)`, `red_neuronal(tabla, variables, objetivo, ocultas, tasa, epocas)` y k vecinos con la etapa `PROFECIA objetivo por [a, b] vecinos k` (alias `pronosticar`) |
| Agrupamiento | `grupos(tabla, variables, k)` (k-medias) |
| Evaluación | `predecir(modelo, tabla)`, `dividir(tabla, 0.8)`, `error_cuadratico`, `r2`, `exactitud`, `correlacion` |

```
partes = dividir(datos, 0.8)
modelo = regresion(partes[0], ["energia", "pib"], "co2")
mostrar modelo.r2
resultado = predecir(modelo, partes[1])         # agrega la columna prediccion
decision = arbol(partes[0], ["energia", "pib"], "nivel", 3)
mostrar reglas(decision)                        # el árbol escrito como reglas "si ... -> ..."
neurona = perceptron(partes[0], ["energia", "pib"], "contamina_mucho", 0.5, 300)
mostrar neurona.perdidas                        # la pérdida de cada época
agrupados = grupos(datos, ["co2", "energia"], 3)  # agrega la columna grupo
```

### Funciones

```
funcion nivel(toneladas) {
    si toneladas > 3 { retornar "alto" }
    retornar "bajo"
}
datos = datos |> crear nivel = mapear(nivel, co2_per_capita)

funcion f(x) { retornar x ^ 2 - 2 }
mostrar biseccion(f, 0, 2)      # raíz de f entre 0 y 2: 1.4142...
```

Una función recibe parámetros, puede devolver cualquier valor (también una
tabla) y sus variables son locales: no cambian las de afuera. Puede llamarse a sí
misma (recursión, hasta 100 niveles).

Los ejemplos `06_listas_ciclos_y_matematicas.eva` y `07_matrices_y_modelos.eva`
muestran todo esto.

Las etapas se encadenan con `|>` y ninguna cambia la tabla original: cada una
devuelve una tabla nueva. Los comentarios empiezan con `#`.

## Gráficas

```
HOLOGRAM lineas de grandes {
    eje_x: año
    eje_y: co2_pc
    serie: pais
    titulo: "CO2 por persona, 1970-2023"
    etiqueta_y: "Toneladas por persona"
    archivo: "caso_estudio/resultados/g2_lineas_co2_por_persona.png"
}
```

![Gráfica de líneas del caso de estudio](caso_estudio/resultados/g2_lineas_co2_por_persona.png)

| Tipo | Pide | Qué dibuja |
|---|---|---|
| `barras` | `eje_x`, `eje_y` | Una barra por categoría con su valor encima; con `serie`, barras agrupadas |
| `lineas` | `eje_x`, `eje_y` | Una línea; con `serie`, una por grupo |
| `histograma` | `eje_x` | Cuántos datos caen en cada intervalo (`intervalos: n`) |
| `dispersion` | `eje_x`, `eje_y` | Un punto por fila; con `serie`, un color por grupo |
| `caja` | `eje_y` | Cuartiles, bigotes y atípicos; con `eje_x`, una caja por categoría |

Las demás opciones son `titulo`, `etiqueta_x`, `etiqueta_y`, `archivo` (`.png` o
`.svg`; si no se da, queda en `salidas/`), `color`, `ancho`, `alto` y `leyenda`.
El PNG lo escribe `lienzo.py`: su propio compresor DEFLATE, su CRC-32 y su
Adler-32, y una letra de píxeles de 5 x 7 dibujada a mano en `fuente.py`.

## Árbol de análisis

Con `--arbol` sale en la terminal y con `--svg` queda como dibujo:

```
eva --svg arbol.svg --solo-analisis ejemplos\01_primera_prueba.eva
```

## Estructura

```
grammar/              Eva.g4 (reglas léxicas y sintácticas juntas)
src/evangelion/
    analizador.py     fase 1: tokens y árbol
    interprete.py     fase 2: Visitor que revisa y ejecuta el programa
    tablas.py         librería propia: tablas, columnas, estadísticas y CSV
    matematica.py     librería propia: raíz, exp, ln, seno, coseno, piso, azar...
    matrices.py       librería propia: vectores y matrices (como NumPy)
    aprendizaje.py    librería propia: regresión, árboles, perceptrón, red neuronal, k vecinos y k-medias
    graficas.py       fase 3: ejes, escalas, leyenda y los cinco tipos de gráfica
    lienzo.py         fase 3: dibujo en píxeles, formato PNG y SVG
    fuente.py         la letra de píxeles de las gráficas
    simbolos.py       tabla de símbolos
    errores.py        errores en español con línea y columna
    arbol.py          árbol en texto, paréntesis y SVG
    consola.py        el EVA-01 y Gendo
    cli.py            línea de comandos
    generado/         lo que genera ANTLR (no se edita)
ejemplos/             programas .eva válidos
ejemplos/errores/     programas que deben fallar (lex_, sin_, sem_)
datos/                CSV de práctica y los datos reales del caso de estudio
caso_estudio/         programa, documento, script de descarga y resultados del caso final
tests/                pruebas con pytest
docs/                 manual en PDF y gramática EBNF
```

## Librería propia

Todo lo que se hace con los datos está escrito a mano en `tablas.py`:

- Leer y escribir CSV (con comillas, otros separadores y detección de números).
- `Columna`: operaciones fila por fila, comparaciones y manejo de faltantes.
- Estadísticas: suma, media, mediana, mínimo, máximo, desviación estándar y conteos.
- `Tabla`: seleccionar, filtrar, ordenar por varias columnas, quitar duplicados y
  faltantes, agrupar y resumir, y mostrarse alineada en la terminal.

Lo mismo con las gráficas: escalas, cuartiles, dibujo, letra y formato PNG están
escritos a mano. Las matemáticas no usan el módulo `math`: la raíz sale del método
de Newton, `exp`, `ln`, seno y coseno de series de Taylor, y el azar de un generador
congruencial con semilla. Las matrices se invierten y los sistemas se resuelven con
eliminación de Gauss-Jordan, y las raíces de una función con bisección o
Newton-Raphson. En aprendizaje automático: la regresión lineal sale de las
ecuaciones normales; el árbol de decisión (CART) prueba cada corte posible y se
queda con el de menor índice de Gini (o menor varianza si predice un número); el
perceptrón y la red neuronal se entrenan con descenso de gradiente usando las
derivadas parciales de la entropía cruzada (en la red, con retropropagación por la
regla de la cadena); además hay k vecinos y k-medias. Las ideas de estos
algoritmos siguen los libros *Grokking Machine Learning* (Serrano, caps. 3, 5, 6,
9, 10 y apéndice B) y *Grokking Artificial Intelligence Algorithms* (Hurbans,
caps. 8 y 9).

Lo único que viene de afuera es el runtime de ANTLR4, que es la herramienta que
pide el curso, y pytest, que solo se usa para correr las pruebas. Las dependencias
están en `pyproject.toml`.

## Pruebas

```
python -m pytest
```

Son 313 pruebas: tokens, precedencia, forma del árbol, cada etapa del flujo
comparada con el resultado esperado, los errores de las tres clases, la librería
de tablas por separado, los ejemplos completos de punta a punta y, en la fase 3,
el compresor y el PNG comparados con la librería estándar de Python, los cinco
tipos de gráfica, las opciones de `HOLOGRAM` y el caso de estudio completo. Las
matemáticas propias se comparan contra `math` de Python (solo dentro de las
pruebas) y hay una prueba que revisa que ningún archivo del lenguaje importe
`math`, `numpy`, `pandas` ni `matplotlib`. Los modelos se prueban con casos de
respuesta conocida (una recta exacta, dos nubes de puntos, el XOR que un perceptrón
solo no puede separar y la red sí) y el gradiente del perceptrón se compara con
la derivada numérica. Las
pruebas de las fases 1 y 2 siguen corriendo, así que sirven de regresión.

## Cambiar la gramática

Si se edita `grammar/Eva.g4` hay que volver a generar el lexer y el parser. :

```
python regenerar.py
```

## Sobre los datos

`pruebas_sincronizacion.csv` y `combates.csv` son de práctica: los nombres salen
de la serie y las cifras son inventadas. `co2_latam.csv` sí es real: viene de Our
World in Data (CC BY 4.0) y se vuelve a bajar con `python caso_estudio/descargar_datos.py`.
El lenguaje carga cualquier CSV.

---
