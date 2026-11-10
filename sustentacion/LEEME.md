# Pruebas para la sustentación

Se corren desde la carpeta del proyecto, un archivo a la vez:

```
python run.py sustentacion/1_ciclos_y_estructuras.eva
```

| # | Archivo | Qué muestra | Tarda |
|---|---|---|---|
| 1 | `1_ciclos_y_estructuras.eva` | `para`, `mientras`, `si/sino si/sino`, listas, diccionarios, vectores, sistema de ecuaciones, recursión, `mapear` y `filtrar` | < 1 s |
| 2 | `2_csv_graficas_regresion_grupos.eva` | CSV del profe (`datos/data.csv`), resumen, correlación, regresión lineal con descenso de gradiente, gráfica de pérdida, dispersión y k-medias | ~12 s |
| 3 | `3_perceptron_xor.eva` | XOR: el perceptrón falla con las 4 activaciones (una recta no lo separa) y la red neuronal lo aprende; con AND el perceptrón sí acierta | ~1 s |
| 4 | `4_cambiar_metodo_numerico.eva` | Cambiar Taylor por otro método con `metodo()`, y raíces con bisección y Newton | < 1 s |
| 5 | `5_clasificacion.eva` | Árbol de decisión (Gini) con sus reglas, k vecinos y perceptrón, con exactitud | ~14 s |

Las gráficas quedan en `salidas/prueba2_*.png`.

## Si el profe pide cambiar algo en vivo

- **Otro CSV:** en la prueba 2, cambiar la ruta de `cargar` y los nombres de las columnas
  (`edad`, `ingreso_mensual`, `anios_esc`). Si el separador no es coma:
  `cargar "archivo.csv" con { separador: ";" }`. Un TXT con columnas también sirve.
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
