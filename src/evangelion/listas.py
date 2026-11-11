"""Nuestra libreria de listas: el arreglo del lenguaje, sin usar las listas de Python.

Una Lista es una cadena de nodos doblemente enlazada: cada nodo guarda un valor y sabe
quien va antes y quien va despues. Agregar al final no recorre nada. Para llegar a una
posicion se camina desde el extremo mas cercano o desde el ultimo nodo visitado (el
cursor), asi recorrer la lista con un indice no vuelve a empezar en cada paso.
"""


class _Nodo:
    __slots__ = ("valor", "anterior", "siguiente")

    def __init__(self, valor, anterior=None, siguiente=None):
        self.valor = valor
        self.anterior = anterior
        self.siguiente = siguiente


class Lista:
    __slots__ = ("_primero", "_ultimo", "_largo", "_cursor", "_posicion")
    __hash__ = None   # como cambia por dentro, no sirve de clave de un diccionario

    def __init__(self, elementos=()):
        self._primero = self._ultimo = self._cursor = None
        self._largo = self._posicion = 0
        for elemento in elementos:
            self.agregar(elemento)

    # --- Agregar y sacar -------------------------------------------------------------

    def agregar(self, valor) -> None:
        nodo = _Nodo(valor, self._ultimo)
        if self._ultimo is None:
            self._primero = nodo
        else:
            self._ultimo.siguiente = nodo
        self._ultimo = nodo
        self._largo += 1

    def insertar(self, posicion: int, valor) -> None:
        """Mete el valor antes de esa posicion; con posicion = largo queda de ultimo."""
        if posicion == self._largo:
            self.agregar(valor)
            return
        siguiente = self._nodo(posicion)
        nodo = _Nodo(valor, siguiente.anterior, siguiente)
        if siguiente.anterior is None:
            self._primero = nodo
        else:
            siguiente.anterior.siguiente = nodo
        siguiente.anterior = nodo
        self._largo += 1
        self._cursor = None    # las posiciones se corrieron

    def extender(self, elementos) -> None:
        for elemento in elementos:
            self.agregar(elemento)

    def sacar(self, posicion: int = -1):
        """Quita el elemento de esa posicion y lo devuelve; sin posicion, el ultimo."""
        nodo = self._nodo(posicion)
        if nodo.anterior is None:
            self._primero = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self._ultimo = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        self._largo -= 1
        self._cursor = None    # el cursor podia estar en el nodo que se fue
        return nodo.valor

    # --- Llegar a una posicion ---------------------------------------------------------

    def _nodo(self, posicion: int) -> _Nodo:
        if posicion.__class__ is not int and not isinstance(posicion, int):
            raise TypeError("la posición de una lista va con un número entero")
        if posicion < 0:
            posicion += self._largo
        if not 0 <= posicion < self._largo:
            raise IndexError("la posición no existe en la lista")
        # lo mas comun al recorrer: la misma posicion o la siguiente
        if self._cursor is not None:
            if posicion == self._posicion:
                return self._cursor
            if posicion == self._posicion + 1:
                self._cursor, self._posicion = self._cursor.siguiente, posicion
                return self._cursor
        # si no, se arranca desde lo que quede mas cerca: el primero, el ultimo o el cursor
        nodo, actual = self._primero, 0
        if self._largo - 1 - posicion < posicion:
            nodo, actual = self._ultimo, self._largo - 1
        if self._cursor is not None and abs(self._posicion - posicion) < abs(actual - posicion):
            nodo, actual = self._cursor, self._posicion
        while actual < posicion:
            nodo, actual = nodo.siguiente, actual + 1
        while actual > posicion:
            nodo, actual = nodo.anterior, actual - 1
        self._cursor, self._posicion = nodo, posicion
        return nodo

    def __getitem__(self, posicion):
        if posicion.__class__ is slice:
            inicio, fin, paso = posicion.indices(self._largo)
            return Lista(self._nodo(i).valor for i in range(inicio, fin, paso))
        return self._nodo(posicion).valor

    def __setitem__(self, posicion: int, valor) -> None:
        self._nodo(posicion).valor = valor

    # --- Lo que permite usarla como cualquier coleccion -----------------------------------

    def __len__(self) -> int:
        return self._largo

    def __iter__(self):
        nodo = self._primero
        while nodo is not None:
            yield nodo.valor
            nodo = nodo.siguiente

    def __reversed__(self):
        nodo = self._ultimo
        while nodo is not None:
            yield nodo.valor
            nodo = nodo.anterior

    def __contains__(self, buscado) -> bool:
        return any(valor == buscado for valor in self)

    def __eq__(self, otra):
        """Es igual a otra coleccion con los mismos valores en el mismo orden."""
        if isinstance(otra, (str, bytes, dict, set)) or not hasattr(otra, "__iter__") or not hasattr(otra, "__len__"):
            return NotImplemented
        if len(self) != len(otra):
            return False
        return all(a == b for a, b in zip(self, otra))

    def __lt__(self, otra) -> bool:
        """Se comparan elemento por elemento; manda la primera diferencia."""
        if not isinstance(otra, Lista):
            return NotImplemented
        for a, b in zip(self, otra):
            if a != b:
                return a < b
        return len(self) < len(otra)

    def __add__(self, otra) -> "Lista":
        nueva = Lista(self)
        nueva.extender(otra)
        return nueva

    def __mul__(self, veces: int) -> "Lista":
        nueva = Lista()
        for _ in range(veces):
            nueva.extender(self)
        return nueva

    __rmul__ = __mul__

    def __repr__(self) -> str:
        return "[" + ", ".join(repr(valor) for valor in self) + "]"

    def contar(self, buscado) -> int:
        return sum(1 for valor in self if valor == buscado)

    def indice(self, buscado) -> int:
        """La primera posicion donde esta; si no esta, ValueError."""
        for i, valor in enumerate(self):
            if valor == buscado:
                return i
        raise ValueError("el valor no está en la lista")

    # --- Operaciones que devuelven otra lista -----------------------------------------------

    def invertida(self) -> "Lista":
        return Lista(reversed(self))


def ordenada(elementos, key=None, reverse: bool = False) -> Lista:
    """Devuelve una Lista ordenada con merge sort: se parte en dos, se ordena cada mitad
    y se mezclan. Es estable: los iguales conservan el orden en que venian."""
    lista = Lista(elementos)
    if len(lista) < 2:
        return lista
    clave = key if key is not None else (lambda valor: valor)
    izquierda, derecha = Lista(), Lista()
    for i, valor in enumerate(lista):
        (izquierda if i < len(lista) // 2 else derecha).agregar(valor)
    izquierda = ordenada(izquierda, key, reverse)
    derecha = ordenada(derecha, key, reverse)

    mezcla, a, b = Lista(), iter(izquierda), iter(derecha)
    va, vb = next(a), next(b)
    while True:
        # el de la derecha solo pasa primero si de verdad va antes
        derecha_primero = clave(va) < clave(vb) if reverse else clave(vb) < clave(va)
        if derecha_primero:
            mezcla.agregar(vb)
            vb = next(b, _FIN)
            if vb is _FIN:
                mezcla.agregar(va)
                mezcla.extender(a)
                return mezcla
        else:
            mezcla.agregar(va)
            va = next(a, _FIN)
            if va is _FIN:
                mezcla.agregar(vb)
                mezcla.extender(b)
                return mezcla


_FIN = object()


def partir(texto: str, separador: str = None) -> Lista:
    """Parte un texto en pedazos. Sin separador, por espacios y saltos de linea."""
    pedazos, actual = Lista(), ""
    if separador is None:
        for letra in texto:
            if letra.isspace():
                if actual:
                    pedazos.agregar(actual)
                actual = ""
            else:
                actual += letra
        if actual:
            pedazos.agregar(actual)
        return pedazos
    resto = texto
    while True:
        pedazo, encontrado, resto = resto.partition(separador)
        pedazos.agregar(pedazo)
        if not encontrado:
            return pedazos


def lineas_de(texto: str) -> Lista:
    """Las lineas de un texto, sin el salto de linea, como splitlines."""
    lineas = partir(texto.replace("\r\n", "\n").replace("\r", "\n"), "\n")
    if len(lineas) > 0 and lineas[-1] == "":
        lineas.sacar()
    return lineas
