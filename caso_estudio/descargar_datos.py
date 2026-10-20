"""Baja los datos del caso de estudio y deja solo lo que se usa.

Fuente: Our World in Data, "CO2 and Greenhouse Gas Emissions"
(https://github.com/owid/co2-data), licencia CC BY 4.0. El archivo completo
pesa unos 14 MB, asi que aqui solo se recortan filas (12 paises de America
Latina, 1970-2023) y columnas. La limpieza y los calculos los hace el
programa en evangelionPL, no este script.

Uso:  python caso_estudio/descargar_datos.py
"""

import csv
import io
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
SALIDA = Path(__file__).resolve().parents[1] / "datos" / "co2_latam.csv"
PAISES = ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica",
          "Ecuador", "Mexico", "Paraguay", "Peru", "Uruguay", "Venezuela"]
DESDE, HASTA = 1970, 2023
COLUMNAS = ["country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita",
            "coal_co2", "oil_co2", "gas_co2", "cement_co2", "energy_per_capita", "share_global_co2"]


def main() -> None:
    print(f"Bajando {URL} ...")
    with urllib.request.urlopen(URL, timeout=120) as respuesta:
        texto = respuesta.read().decode("utf-8")
    filas = [f for f in csv.DictReader(io.StringIO(texto))
             if f["country"] in PAISES and DESDE <= int(f["year"]) <= HASTA]
    SALIDA.parent.mkdir(exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, extrasaction="ignore", lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"Listo: {SALIDA} ({len(filas)} filas, {len(COLUMNAS)} columnas)")


if __name__ == "__main__":
    main()
