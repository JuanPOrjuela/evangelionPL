# Pruebas para la sustentación

Se corren desde la carpeta del proyecto, un archivo a la vez:

```
python run.py sustentacion/1_ciclos_y_estructuras.eva
```

| # | Archivo | Qué muestra | Tarda |
|---|---|---|---|
| 1 | `1_ciclos_y_estructuras.eva` | `para`, `mientras`, `si/sino si/sino`, listas, diccionarios, vectores, sistema de ecuaciones, recursión, `mapear` y `filtrar` | < 1 s |
| 2 | `2_csv_graficas_regresion_grupos.eva` | CSV del profe (`datos/data.csv`), resumen, correlación, regresión lineal con descenso de gradiente, gráfica de pérdida, dispersión y k-medias | ~5 s |
| 3 | `3_perceptron_xor.eva` | XOR: el perceptrón falla con las 4 activaciones (una recta no lo separa) y la red neuronal lo aprende; con AND el perceptrón sí acierta | ~1 s |
| 4 | `4_cambiar_metodo_numerico.eva` | Cambiar Taylor por otro método con `metodo()`, y raíces con bisección y Newton | < 1 s |
| 5 | `5_clasificacion.eva` | Árbol de decisión (Gini) con sus reglas, k vecinos y perceptrón, con exactitud | ~6 s |

Las gráficas quedan en `salidas/prueba2_*.png`.

## Si el profe pide cambiar algo en vivo

- **Otro CSV:** en la prueba 2, cambiar la ruta de `cargar` y los nombres de las columnas
  (`edad`, `ingreso_mensual`, `anios_esc`). Si el separador no es coma:
  `cargar "archivo.csv" con { separador: ";" }` (si se equivoca de separador, el error dice
  cuál usar). Decimales con coma, como los guarda Excel en español:
  `cargar "archivo.csv" con { separador: ";", decimal: "," }`. Un CSV guardado en latin-1
  (ANSI) se lee solo. Un TXT con columnas también sirve (tabulado: `separador: "	"`).
- **Otra regresión:** `regresion(tabla, ["x1", "x2"], "y", tasa, epocas)`. Más variables van en la lista.
- **Otro número de grupos:** el último número de `grupos(muestra, [...], 3)`.
- **Otra activación del perceptrón:** `"escalon"`, `"lineal"`, `"tanh"` o `"sigmoide"`.
- **Más neuronas o épocas en la red:** `red_neuronal(tabla, vars, objetivo, ocultas, tasa, epocas)`.
- **Cambiar el método numérico:** una línea antes de usar la función:

  | Función | Por defecto | Otro método |
  |---|---|---|
  | `sen`, `cos` | `"taylor"` (serie) | `"duplicacion"`: se parte el ángulo hasta que es casi 0 y se dobla con sen(2a) = 2 sen(a) cos(a) |
  | `exp` | `"taylor"` (serie) | `"newton"`: resuelve ln(y) = x con y = y·(1 + x − ln y) |
  | `ln` | `"serie"` | `"newton"`: resuelve eʸ = m con y = y − 1 + m/eʸ |
  | `raiz` | `"newton"` | `"biseccion"`: parte el intervalo [0, x] a la mitad |

  Ejemplo: `metodo("sen", "duplicacion")`. Para ver cuál está activo: `mostrar metodo("sen")`.
  Todo lo que usa esa función cambia también (por ejemplo `tanh` y la sigmoide usan `exp`).
  El código está en `src/evangelion/matematica.py` (`METODOS`, `sen`, `_duplicar_angulo`,
  `_exp_newton`, `_ln_newton`, `_raiz_biseccion`).

## Dónde está cada cosa en el código

- Descenso de gradiente de la regresión ("square trick"): `src/evangelion/aprendizaje.py`, función `regresion`.
- Perceptrón y red neuronal (derivadas y retropropagación): `aprendizaje.py`, `perceptron` y `red_neuronal`.
- Árbol con Gini: `aprendizaje.py`, `arbol`, `gini` y `_crecer`.
- k-medias: `aprendizaje.py`, `grupos` y `_k_medias`.
- Taylor, Newton y bisección: `src/evangelion/matematica.py`.

`pregunta_escalar_regresion.eva` es el ejemplo que muestra por qué se escalan los datos:
sin escalar, el descenso de gradiente se desborda (termina con error a propósito).

## Trampas que conviene saber antes de la demo

Todo esto se probó con programas el 10 y 11-nov-2026.

### Nombres que no se pueden usar tal cual

`y`, `o`, `no`, `de`, `en`, `por`, `con`, `como`, `si`, `para`, `desde`, `hasta`, `asc`,
`desc` y `columnas` son palabras del lenguaje. Si un CSV trae una columna `y`:

```
mostrar media(t.`y`)                      # entre acentos graves
regresion(t, ["x"], "y", 0.01, 1000)      # entre comillas también sirve
```

Para variables propias, usar otro nombre (`u`, `v`, `objetivo`...).

### Columnas como listas

`t.edad` es una columna de la tabla. Para indexarla o pasarla a `punto()`, se saca como lista:

```
edades = columna(t, "edad")
mostrar edades[0]                         # los índices empiezan en 0
mostrar punto(columna(t, "x"), columna(t, "y"))
```

`media(t.edad)` y `correlacion(t.a, t.b)` sí reciben la columna directo.

### Rutas

Las rutas se buscan desde la carpeta donde se corre el programa: correr siempre desde la raíz
del proyecto. En Windows, escribir la ruta con `/` (`"C:/Users/.../datos.csv"`) o con `\`;
una `\` sola rompe el texto.

### Regresión: por qué b y m cambian con las épocas

Cada época usa un solo punto al azar con tasa fija (el "square trick" del cap. 3), así que el
resultado se mueve alrededor del de mínimos cuadrados y más épocas no siempre lo acercan.
Con los datos del profe (`ingreso_mensual` contra `anios_esc`), mínimos cuadrados da
b = 1463,46 y m = 600,28 (r² = 0,1715):

| tasa | épocas | b, m | r² |
|---|---|---|---|
| 0.01 | 1000 | 2073, 540 | — |
| 0.01 | 10 000 | 1842, 509 | — |
| 0.001 | 50 000 | 1512,5, 589,6 | 0,1713 (~9 s) |
| 0.5 | — | −8928, 2453 | −3,59 |

Una tasa grande hace que salte de un lado a otro. Si la regresión no mejora (r² negativo o la
pérdida final mayor que la inicial), el programa imprime un AVISO que sugiere bajar la tasa.

### Cramer a mano

No hay función `cramer()`, pero sale con `determinante()` (da lo mismo que `resolver()`):

```
a = [[2, 1], [1, 3]]                      # 2x + y = 5 ; x + 3y = 10
d = determinante(a)
mostrar [determinante([[5, 1], [10, 3]]) / d, determinante([[2, 5], [1, 10]]) / d]   # [1.0, 3.0]
```

### Cosas que tardan

| Qué | Tamaño | Tarda |
|---|---|---|
| `grupos(..., k)` | 1500 filas, k = 2 / 3 / 5 / 10 | 0,8 / 1,1 / 1,8 / 4,1 s |
| `pronosticar ... vecinos` | 600 / 1500 filas, k = 5 | 0,2 / 1,2 s |
| `para i desde 1 hasta 1000000` | — | 17 s (más de 1 000 000 vueltas no se permite) |
| `fib(22)` recursivo | — | 3 s (la recursión se corta a 100 niveles) |

En la demo: mejor no quitar los `limitar` (sin ellos no se ha medido después de acelerar
k-medias y k vecinos), ciclos de hasta unas 100 000 vueltas y `fib` hasta 20. No existen `romper` ni `continuar`.

### Otros detalles

- Las funciones del lenguaje se pueden pasar como argumento: `derivada(sen, 0)`,
  `mapear(raiz, [4, 9])`, `biseccion(cos, 1, 2)`. Respetan el `metodo()` elegido.
- `rango(3)` da `[1, 2, 3]` y `rango(0, 3)` da `[0, 1, 2, 3]`: incluye los dos extremos.
  Para recorrer una lista: `para i desde 0 hasta longitud(l) - 1`.
- `mostrar` enseña 4 decimales; para ver diferencias muy pequeñas, multiplicar
  (la prueba 4 multiplica por `10 ^ 15`). No hay literales como `1e-5`: escribir `0.00001`.
- XOR con el perceptrón lineal, tanh o sigmoide deja los pesos en `[0.0, 0.0]`. No es que no
  haya entrenado: en XOR las cuatro esquinas se compensan y el gradiente lleva los pesos a 0
  (ningún plano inclinado acierta más que uno plano).
  La red neuronal sí lo aprende con 2 o más neuronas ocultas y 1000 épocas o más
  (con 1 neurona o 100 épocas se queda en 0,5).
- `barras` sobre una tabla sin resumir suma los valores; para promedios, resumir antes.
- Un `.xlsx` hay que guardarlo antes como CSV (`datos/data.csv` ya está convertido).
