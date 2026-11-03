"""Lo que se ve en la terminal: el EVA-01 si todo sale bien y Gendo si algo falla."""

from .listas import Lista, partir

EVA_01 = r"""
                             /\
                            /||\
                            /||\
                           / || \
                           / || \
                          /  ||  \
                    _____/   ||   \_____
                 .-'     \   ||   /     '-.
        __     .'         \  ||  /         '.     __
       \  \__ /  __________\ || /__________  \ __/  /
        \    |   \#########.\||/.#########/   |    /
         \   |    '-.#####/  ||  \#####.-'    |   /
          \__|       '---'   ||   '---'       |__/
             \   \           ||           /   /
              \   \____   .------.   ____/   /
               \  ====  /__________\  ====  /
                \  .--------------------.  /
                 \ |\/\/\/\/\/\/\/\/\/\/| /
                  \|/\/\/\/\/\/\/\/\/\/\|/
                   '-.________________.-'
     ______            \____________/            ______
   .'      '-.__    ____|          |____    __.-'      '.
  /             '-./    \__________/    \.-'             \
 |  ===========   |   \              /   |   ===========  |
 |  ===========   |    \  ========  /    |   ===========  |
 |  ===========   |     \__________/     |   ===========  |
 |________________|______________________|________________|
                          EVA - 01
"""

GENDO = r"""
                     _.-''''''''''''-._
                  .'//////////\\\\\\\\\\'.
                 /////////''''''''\\\\\\\\\
                |///''                ''\\\|
                |//    ______________    \\|
                |/   /###//##--##\\###\   \|
               (|   |###//###||###\\###|   |)
                |    '-------''-------'    |
                |                          |
                 \        ,  ||  ,        /
                  \  .----------------.  /
              __.--\(_)(_)(_)||(_)(_)(_)/--.__
          _.-'     |(_)(_)(_)||(_)(_)(_)|     '-._
       .-'     __.-'\__________________/'-.__     '-.
     .'    _.-'  _.-'\  ;;;;;;;;;;;;  /'-._  '-._    '.
    /    .'   .-'     \  ;;;;;;;;;;  /     '-.   '.    \
   /    /   .'         '-.;;;;;;;;.-'         '.   \    \
  /    /   /              '-.  .-'              \   \    \
 /____/___/______________________________________\___\____\
============================================================
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


def _pintar_dibujo(dibujo: str, color: str, resaltados: str, color_resaltado: str) -> str:
    """Pinta el dibujo de un color y algunos de sus caracteres de otro (los ojos, las gafas)."""
    if not _con_color:
        return dibujo
    pintado = ""
    for caracter in dibujo:
        pintado += f"[{color_resaltado if caracter in resaltados else color}m{caracter}"
    return pintado + "[0m"


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
    return "\n".join(Lista((_pintar_dibujo(EVA_01, MORADO, "#=", VERDE), _pintar(mensaje, VERDE), "", *datos, "")))


def fallo(detalle: str, linea: int) -> str:
    alerta = (
        "  ALERTA: sincronización fallida.\n"
        "  Nivel de contaminación mental alto, el EVA no arranca."
    )
    frase = f'  Gendo: "Corrige la línea {linea}, Shinji. O vete."'
    return "\n".join(Lista((_pintar_dibujo(GENDO, NARANJA, "#", ROJO), _pintar(alerta, ROJO), "", detalle, "", frase, "")))
