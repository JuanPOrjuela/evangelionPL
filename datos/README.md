# Datos de práctica

Los dos primeros archivos los armé yo para probar el lenguaje. Los nombres (pilotos,
unidades, ángeles y episodios) salen de la serie de TV, pero **las cifras son
inventadas**: no son datos oficiales de nada.

| Archivo | Separador | Qué trae |
|---|---|---|
| `pruebas_sincronizacion.csv` | `,` | 32 pruebas de sincronización: fecha, piloto, unidad, sincronización, armónicos y minutos de batería. Tiene faltantes y una fila repetida a propósito. |
| `combates.csv` | `;` | 25 participaciones de un EVA en un combate. Los nombres de columna tienen espacios y símbolos para practicar los acentos graves. |

El lenguaje carga cualquier CSV, así que se puede probar con otros datos
cambiando la ruta en `ENTRY_PLUG`.

## Datos reales del caso de estudio

| Archivo | Separador | Qué trae |
|---|---|---|
| `co2_latam.csv` | `,` | Emisiones de CO2, población, PIB y energía de 12 países de América Latina, 1970-2023 (648 filas). Fuente: Our World in Data, licencia CC BY 4.0. Se vuelve a bajar con `python caso_estudio/descargar_datos.py`. Detalle de cada columna en [`caso_estudio/README.md`](../caso_estudio/README.md). |
