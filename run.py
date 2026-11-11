"""Lanzador: python run.py ejemplos/01_primera_prueba.eva

Es el unico archivo con una importacion de Python, sys es la unica forma que da Python
de recibir lo que se escribe en la linea de comandos. El lenguaje no usa sys para nada mas.
"""

import sys

sys.path.insert(0, __file__.replace("\\", "/").rpartition("/")[0] + "/src")

from evangelion.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.setrecursionlimit(4000)    # cada llamada del lenguaje gasta unas 25 de Python
    sys.stdout.reconfigure(errors="replace")    # si la consola no conoce un caracter, que no se caiga
    sys.exit(main(sys.argv[1:]))
