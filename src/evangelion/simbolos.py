"""Tabla de simbolos: que variables existen, de que clase son y donde se definieron."""

from .listas import Lista


class Simbolo:
    def __init__(self, nombre: str, clase: str, valor, linea: int):
        self.nombre = nombre
        self.clase = clase     # tabla, numero, texto, booleano, lista, diccionario, funcion o nulo
        self.valor = valor
        self.linea = linea

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
        self._locales: Lista[dict[str, Simbolo]] = Lista()

    def entrar(self) -> None:
        self._locales.agregar({})

    def salir(self) -> None:
        self._locales.sacar()

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

    def nombres(self) -> Lista:
        locales = Lista(self._locales[-1]) if self._locales else Lista()
        return locales + Lista(n for n in self._simbolos if n not in locales)

    def __len__(self) -> int:
        return len(self._simbolos)

    def como_texto(self) -> str:
        if not self._simbolos:
            return "  (vacía)"
        ancho = max(len(n) for n in self._simbolos)
        ancho = max(ancho, len("NOMBRE"))
        filas = Lista((f"  {'NOMBRE':<{ancho}}  {'CLASE':<9} {'LÍNEA':<6} VALOR",))
        for s in self._simbolos.values():
            filas.agregar(f"  {s.nombre:<{ancho}}  {s.clase:<9} {s.linea:<6} {s.detalle()}")
        return "\n".join(filas)
