"""Lo que se ve en la terminal: el EVA-01 si todo sale bien y Gendo si algo falla."""

import os
import sys

EVA_01 = r"""
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
"""

GENDO = r"""
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
"""

MORADO, VERDE, ROJO, NARANJA = "35", "32", "31", "33"


def _con_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _pintar(texto: str, color: str) -> str:
    if not _con_color():
        return texto
    return "\n".join(f"\033[{color}m{linea}\033[0m" for linea in texto.split("\n"))


def preparar_terminal() -> None:
    if os.name == "nt" and _con_color():
        os.system("")  # con esto la consola de Windows entiende los colores
    # si la consola no conoce algun caracter, que no se caiga el programa
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")


def exito(archivo: str, operacion: str, tokens: int, variables: list, reportes: list,
          graficas: list = ()) -> str:
    datos = []
    if operacion:
        datos.append(f"    Operación : {operacion}")
    datos.append(f"    Tokens    : {tokens}")
    if variables:
        datos.append(f"    Variables : {', '.join(variables)}")
    if reportes:
        datos.append(f"    Reportes  : {', '.join(reportes)}")
    if graficas:
        datos.append(f"    Gráficas  : {', '.join(graficas)}")

    mensaje = (
        "  ¡Felicidades, Shinji! (omedetou!)\n"
        f"  Sincronización con el EVA-01 al 100 %: {archivo} corrió sin errores."
    )
    return "\n".join([_pintar(EVA_01, MORADO), _pintar(mensaje, VERDE), "", *datos, ""])


def fallo(detalle: str, linea: int) -> str:
    alerta = (
        "  ALERTA: sincronización fallida.\n"
        "  Nivel de contaminación mental alto, el EVA no arranca."
    )
    frase = f'  Gendo: "Corrige la línea {linea}, Shinji. O vete."'
    return "\n".join([_pintar(GENDO, NARANJA), _pintar(alerta, ROJO), "", detalle, "", frase, ""])
