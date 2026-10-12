# Datos de práctica

Los dos archivos los armé yo para probar el lenguaje. Los nombres (pilotos,
unidades, ángeles y episodios) salen de la serie de TV, pero **las cifras son
inventadas**: no son datos oficiales de nada.

| Archivo | Separador | Qué trae |
|---|---|---|
| `pruebas_sincronizacion.csv` | `,` | 32 pruebas de sincronización: fecha, piloto, unidad, sincronización, armónicos y minutos de batería. Tiene faltantes y una fila repetida a propósito. |
| `combates.csv` | `;` | 25 participaciones de un EVA en un combate. Los nombres de columna tienen espacios y símbolos para practicar los acentos graves. |

El lenguaje carga cualquier CSV, así que se puede probar con otros datos
cambiando la ruta en `ENTRY_PLUG`.
