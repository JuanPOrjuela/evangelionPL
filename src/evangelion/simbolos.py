"""Tabla de simbolos: que variables existen, de que clase son y donde se definieron."""

from dataclasses import dataclass


@dataclass
class Simbolo:
    nombre: str
    clase: str     # tabla, numero, texto, booleano o nulo
    valor: object
    linea: int

    def detalle(self) -> str:
        if self.clase == "tabla":
            return f"{len(self.valor)} filas x {len(self.valor.columnas)} columnas"
        if self.clase == "booleano":
            return "verdadero" if self.valor else "falso"
        if self.clase == "nulo":
            return "nulo"
        return str(self.valor)


class TablaSimbolos:
    def __init__(self):
        self._simbolos: dict[str, Simbolo] = {}

    def definir(self, nombre: str, clase: str, valor, linea: int) -> None:
        self._simbolos[nombre] = Simbolo(nombre, clase, valor, linea)

    def buscar(self, nombre: str):
        return self._simbolos.get(nombre)

    def nombres(self) -> list:
        return list(self._simbolos)

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
