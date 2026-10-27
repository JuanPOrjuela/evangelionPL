"""Tabla de simbolos: que variables existen, de que clase son y donde se definieron."""

from dataclasses import dataclass


@dataclass
class Simbolo:
    nombre: str
    clase: str     # tabla, numero, texto, booleano, lista, diccionario, funcion o nulo
    valor: object
    linea: int

    def detalle(self) -> str:
        if self.clase == "tabla":
            return f"{len(self.valor)} filas x {len(self.valor.columnas)} columnas"
        if self.clase == "booleano":
            return "verdadero" if self.valor else "falso"
        if self.clase == "nulo":
            return "nulo"
        if self.clase == "lista":
            return f"{len(self.valor)} elementos"
        if self.clase == "diccionario":
            return f"{len(self.valor)} claves"
        if self.clase == "funcion":
            return f"{self.valor.nombre}({', '.join(self.valor.parametros)})"
        return str(self.valor)


class TablaSimbolos:
    """El ambito global y, encima, uno por cada llamada a funcion que este corriendo.
    Una variable se busca primero en el ambito de la funcion y despues en el global."""

    def __init__(self):
        self._simbolos: dict[str, Simbolo] = {}
        self._locales: list[dict[str, Simbolo]] = []

    def entrar(self) -> None:
        self._locales.append({})

    def salir(self) -> None:
        self._locales.pop()

    @property
    def profundidad(self) -> int:
        return len(self._locales)

    def definir(self, nombre: str, clase: str, valor, linea: int) -> None:
        ambito = self._locales[-1] if self._locales else self._simbolos
        ambito[nombre] = Simbolo(nombre, clase, valor, linea)

    def buscar(self, nombre: str):
        if self._locales and nombre in self._locales[-1]:
            return self._locales[-1][nombre]
        return self._simbolos.get(nombre)

    def nombres(self) -> list:
        locales = list(self._locales[-1]) if self._locales else []
        return locales + [n for n in self._simbolos if n not in locales]

    def __len__(self) -> int:
        return len(self._simbolos)

    def como_texto(self) -> str:
        if not self._simbolos:
            return "  (vacía)"
        ancho = max(len(n) for n in self._simbolos)
        ancho = max(ancho, len("NOMBRE"))
        filas = [f"  {'NOMBRE':<{ancho}}  {'CLASE':<9} {'LÍNEA':<6} VALOR"]
        for s in self._simbolos.values():
            filas.append(f"  {s.nombre:<{ancho}}  {s.clase:<9} {s.linea:<6} {s.detalle()}")
        return "\n".join(filas)
