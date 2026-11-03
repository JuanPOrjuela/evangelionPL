"""Lo que se ve en la terminal: el EVA-01 si todo sale bien y Gendo si algo falla."""

from .listas import Lista, partir

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


_con_color = False


def activar_color() -> None:
    global _con_color
    _con_color = True


def _pintar(texto: str, color: str) -> str:
    if not _con_color:
        return texto
    return "\n".join(f"\033[{color}m{linea}\033[0m" for linea in partir(texto, "\n"))


def exito(archivo: str, operacion: str, tokens: int, variables: Lista, reportes: Lista,
          graficas: Lista = ()) -> str:
    datos = Lista()
    if operacion:
        datos.agregar(f"    Operación : {operacion}")
    datos.agregar(f"    Tokens    : {tokens}")
    if variables:
        datos.agregar(f"    Variables : {', '.join(variables)}")
    if reportes:
        datos.agregar(f"    Reportes  : {', '.join(reportes)}")
    if graficas:
        datos.agregar(f"    Gráficas  : {', '.join(graficas)}")

    mensaje = (
        "  ¡Felicidades, Shinji! (omedetou!)\n"
        f"  Sincronización con el EVA-01 al 100 %: {archivo} corrió sin errores."
    )
    return "\n".join(Lista((_pintar(EVA_01, MORADO), _pintar(mensaje, VERDE), "", *datos, "")))


def fallo(detalle: str, linea: int) -> str:
    alerta = (
        "  ALERTA: sincronización fallida.\n"
        "  Nivel de contaminación mental alto, el EVA no arranca."
    )
    frase = f'  Gendo: "Corrige la línea {linea}, Shinji. O vete."'
    return "\n".join(Lista((_pintar(GENDO, NARANJA), _pintar(alerta, ROJO), "", detalle, "", frase, "")))
