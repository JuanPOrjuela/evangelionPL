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

## Datos del profesor

| Archivo | Separador | Qué trae |
|---|---|---|
| `data.csv` | `,` | 10.280 personas: id, edad, nivel_edu, ingreso_mensual, sex, anios_esc. Sale de `data.xlsx`, que entregó el profesor (el lenguaje solo lee CSV y TXT). Trae la errata "Prrimaria", que los programas corrigen con `reemplazar`. Lo usan `ejemplos/10_*`, `ejemplos/11_*` y las pruebas de `sustentacion/`. |
