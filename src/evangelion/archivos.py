"""Lo poco que hace falta saber de una ruta, sin importar librerias de Python."""


def con_barras(ruta) -> str:
    """La ruta escrita con / aunque venga de Windows."""
    return str(ruta).replace("\\", "/")


def nombre_archivo(ruta) -> str:
    """carpeta/datos.csv -> datos.csv"""
    return con_barras(ruta).rpartition("/")[2]


def extension(ruta) -> str:
    """carpeta/Datos.CSV -> .csv (vacio si el nombre no tiene punto)"""
    nombre = nombre_archivo(ruta)
    punto = nombre.rfind(".")
    return nombre[punto:].lower() if punto > 0 else ""


def existe(ruta) -> bool:
    """Si se puede abrir, existe. Una carpeta no cuenta como archivo."""
    try:
        with open(ruta, "rb"):
            return True
    except OSError:
        return False
