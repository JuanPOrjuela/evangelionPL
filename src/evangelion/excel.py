"""Lector de archivos de Excel (.xlsx), hecho a mano y sin librerias.

Un .xlsx es un ZIP con varios archivos XML adentro. Para leerlo hay que:
  1. abrir el ZIP: buscar el directorio del final y sacar cada archivo,
  2. descomprimirlo: los archivos vienen con DEFLATE, asi que aqui esta el
     descompresor (el inverso del compresor que usa lienzo.py para los PNG),
  3. leer el XML: la hoja trae las celdas y los textos repetidos van aparte,
     en sharedStrings.xml.
El resultado son filas de textos, igual que las de un CSV, y tablas.py decide
despues si cada columna es de numeros o de texto.
"""

from .lienzo import _BASE_DISTANCIA, _BASE_LARGO, _EXTRA_DISTANCIA, _EXTRA_LARGO
from .listas import Lista


# --- 1. El ZIP ---------------------------------------------------------------------------

def _entero(datos: bytes, inicio: int, bytes_: int) -> int:
    """Un numero guardado con el byte menos importante primero (little endian)."""
    return int.from_bytes(datos[inicio:inicio + bytes_], "little")


def abrir_zip(datos: bytes) -> dict:
    """{nombre del archivo: contenido ya descomprimido} de todo lo que trae el ZIP."""
    # el "fin del directorio central" esta al final; puede tener un comentario despues
    fin = datos.rfind(b"PK\x05\x06")
    if fin < 0:
        raise ValueError("no es un archivo de Excel .xlsx válido (no se encontró el ZIP por dentro)")
    cantidad = _entero(datos, fin + 10, 2)
    posicion = _entero(datos, fin + 16, 4)
    archivos = {}
    for _ in range(cantidad):
        if datos[posicion:posicion + 4] != b"PK\x01\x02":
            raise ValueError("el ZIP del .xlsx está dañado")
        metodo = _entero(datos, posicion + 10, 2)
        comprimido = _entero(datos, posicion + 20, 4)
        largo_nombre = _entero(datos, posicion + 28, 2)
        largo_extra = _entero(datos, posicion + 30, 2)
        largo_comentario = _entero(datos, posicion + 32, 2)
        local = _entero(datos, posicion + 42, 4)
        nombre = datos[posicion + 46:posicion + 46 + largo_nombre].decode("utf-8", "replace")
        posicion += 46 + largo_nombre + largo_extra + largo_comentario
        # los datos empiezan despues del encabezado local, que tiene su propio nombre y extra
        inicio = local + 30 + _entero(datos, local + 26, 2) + _entero(datos, local + 28, 2)
        contenido = datos[inicio:inicio + comprimido]
        if metodo == 0:
            archivos[nombre] = bytes(contenido)
        elif metodo == 8:
            archivos[nombre] = inflar(contenido)
        else:
            raise ValueError(f"el .xlsx usa una compresión que no conocemos (método {metodo})")
    return archivos


# --- 2. DEFLATE al reves (RFC 1951) --------------------------------------------------------

class _Bits:
    """Lee los bits de a pocos, empezando por el bit menos importante de cada byte."""

    def __init__(self, datos: bytes):
        self.datos, self.posicion, self.reserva, self.cuantos = datos, 0, 0, 0

    def _llenar(self, n: int) -> None:
        while self.cuantos < n:
            byte = self.datos[self.posicion] if self.posicion < len(self.datos) else 0
            self.posicion += 1
            self.reserva |= byte << self.cuantos
            self.cuantos += 8

    def leer(self, n: int) -> int:
        self._llenar(n)
        valor = self.reserva & ((1 << n) - 1)
        self.reserva >>= n
        self.cuantos -= n
        return valor

    def mirar(self, n: int) -> int:
        self._llenar(n)
        return self.reserva & ((1 << n) - 1)

    def soltar(self, n: int) -> None:
        self.reserva >>= n
        self.cuantos -= n

    def al_byte(self) -> None:
        """Descarta los bits que sobran del byte actual."""
        self.soltar(self.cuantos % 8)


def _invertir(codigo: int, bits: int) -> int:
    resultado = 0
    for _ in range(bits):
        resultado = (resultado << 1) | (codigo & 1)
        codigo >>= 1
    return resultado


class _Huffman:
    """Codigo de Huffman canonico armado desde el largo de cada simbolo. Para decodificar
    rapido se arma una tabla: con los proximos `bits` bits se sabe el simbolo y su largo."""

    def __init__(self, largos: bytes):
        self.bits = max(largos) if largos else 0
        if self.bits == 0:
            self.tabla = {}
            return
        cuenta = {}                      # cuantos simbolos hay de cada largo
        for largo in largos:
            if largo:
                cuenta[largo] = cuenta.get(largo, 0) + 1
        siguiente, codigo = {}, 0
        for largo in range(1, 16):
            codigo = (codigo + cuenta.get(largo - 1, 0)) << 1
            siguiente[largo] = codigo
        self.tabla = {}
        for simbolo, largo in enumerate(largos):
            if largo == 0:
                continue
            invertido = _invertir(siguiente[largo], largo)
            siguiente[largo] += 1
            # todos los indices que terminan en este codigo apuntan al simbolo
            for indice in range(invertido, 1 << self.bits, 1 << largo):
                self.tabla[indice] = (simbolo, largo)

    def leer(self, bits: _Bits) -> int:
        simbolo, largo = self.tabla.get(bits.mirar(self.bits), (None, 0))
        if simbolo is None:
            raise ValueError("el .xlsx está dañado (un código de Huffman no existe)")
        bits.soltar(largo)
        return simbolo


def _fijos() -> tuple:
    literales = bytearray(288)
    for s in range(288):
        literales[s] = 8 if s < 144 else 9 if s < 256 else 7 if s < 280 else 8
    return _Huffman(bytes(literales)), _Huffman(bytes((5,) * 30))


_FIJOS = None
_ORDEN_LARGOS = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)


def _dinamicos(bits: _Bits) -> tuple:
    hlit, hdist, hclen = bits.leer(5) + 257, bits.leer(5) + 1, bits.leer(4) + 4
    largos_de_largos = bytearray(19)
    for i in range(hclen):
        largos_de_largos[_ORDEN_LARGOS[i]] = bits.leer(3)
    codigo_largos = _Huffman(bytes(largos_de_largos))
    largos = bytearray()
    while len(largos) < hlit + hdist:
        simbolo = codigo_largos.leer(bits)
        if simbolo < 16:
            largos.append(simbolo)
        elif simbolo == 16:      # repite el largo anterior de 3 a 6 veces
            if not largos:
                raise ValueError("el .xlsx está dañado (repetición sin largo anterior)")
            largos.extend(bytes((largos[-1],)) * (3 + bits.leer(2)))
        elif simbolo == 17:      # de 3 a 10 ceros
            largos.extend(bytes(3 + bits.leer(3)))
        else:                    # de 11 a 138 ceros
            largos.extend(bytes(11 + bits.leer(7)))
    return _Huffman(bytes(largos[:hlit])), _Huffman(bytes(largos[hlit:hlit + hdist]))


def inflar(datos: bytes) -> bytes:
    """Descomprime datos DEFLATE: bloques guardados tal cual, con Huffman fijo o dinamico."""
    global _FIJOS
    bits, salida = _Bits(datos), bytearray()
    ultimo = False
    while not ultimo:
        ultimo = bits.leer(1) == 1
        tipo = bits.leer(2)
        if tipo == 0:            # guardado sin comprimir
            bits.al_byte()
            largo = bits.leer(16)
            bits.leer(16)        # el complemento del largo
            for _ in range(largo):
                salida.append(bits.leer(8))
            continue
        if tipo == 3:
            raise ValueError("el .xlsx está dañado (tipo de bloque desconocido)")
        if tipo == 1:
            if _FIJOS is None:
                _FIJOS = _fijos()
            literales, distancias = _FIJOS
        else:
            literales, distancias = _dinamicos(bits)
        while True:
            simbolo = literales.leer(bits)
            if simbolo < 256:
                salida.append(simbolo)
                continue
            if simbolo == 256:   # fin del bloque
                break
            n = simbolo - 257
            largo = _BASE_LARGO[n] + bits.leer(_EXTRA_LARGO[n])
            d = distancias.leer(bits)
            distancia = _BASE_DISTANCIA[d] + bits.leer(_EXTRA_DISTANCIA[d])
            if distancia > len(salida):
                raise ValueError("el .xlsx está dañado (una distancia va más atrás del inicio)")
            inicio = len(salida) - distancia
            if distancia >= largo:
                salida.extend(salida[inicio:inicio + largo])
            else:                # se copia algo que se esta escribiendo: byte por byte
                for i in range(largo):
                    salida.append(salida[inicio + i])
    return bytes(salida)


# --- 3. El XML de Excel --------------------------------------------------------------------

ENTIDADES = (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"))


def _texto_xml(texto: str) -> str:
    """Cambia las marcas del XML (&amp;, &#233;...) por el caracter que representan."""
    if "&" not in texto:
        return texto
    partes, i = Lista(), 0
    while True:
        j = texto.find("&#", i)
        if j < 0:
            break
        fin = texto.find(";", j)
        if fin < 0:
            break
        numero = texto[j + 2:fin]
        partes.agregar(texto[i:j])
        partes.agregar(chr(int(numero[1:], 16) if numero[:1] in ("x", "X") else int(numero)))
        i = fin + 1
    partes.agregar(texto[i:])
    texto = "".join(partes)
    for entidad, caracter in ENTIDADES:
        texto = texto.replace(entidad, caracter)
    return texto.replace("&amp;", "&")


def _atributo(etiqueta: str, nombre: str):
    """El valor de nombre="..." dentro de una etiqueta, o None si no lo trae."""
    for comilla in ('"', "'"):
        marca = f" {nombre}={comilla}"
        i = etiqueta.find(marca)
        if i >= 0:
            inicio = i + len(marca)
            return etiqueta[inicio:etiqueta.find(comilla, inicio)]
    return None


def _elementos(xml: str, nombre: str):
    """Recorre cada <nombre ...>...</nombre> (o <nombre .../>) y entrega (etiqueta, contenido)."""
    i = 0
    while True:
        i = xml.find(f"<{nombre}", i)
        if i < 0:
            return
        siguiente = xml[i + len(nombre) + 1:i + len(nombre) + 2]
        if siguiente not in (" ", ">", "/"):    # <c> no debe confundirse con <cols>
            i += 1
            continue
        cierre = xml.find(">", i)
        etiqueta = xml[i:cierre + 1]
        if etiqueta.endswith("/>"):
            yield etiqueta, ""
            i = cierre + 1
            continue
        fin = xml.find(f"</{nombre}>", cierre)
        yield etiqueta, xml[cierre + 1:fin]
        i = fin + len(nombre) + 3


def _textos_de(contenido: str) -> str:
    """Junta todos los <t>...</t> (un texto con formato viene partido en varios)."""
    return "".join(_texto_xml(texto) for _, texto in _elementos(contenido, "t"))


def _columna(referencia: str) -> int:
    """B7 -> 1 (las columnas empiezan en 0): las letras son un numero en base 26."""
    numero = 0
    for letra in referencia:
        if not letra.isalpha():
            break
        numero = numero * 26 + (ord(letra.upper()) - ord("A") + 1)
    return numero - 1


def _ruta_de_hoja(archivos: dict, hoja) -> str:
    """El archivo XML de la hoja pedida (por nombre o por numero, 1 es la primera)."""
    libro = archivos.get("xl/workbook.xml", b"").decode("utf-8", "replace")
    relaciones = archivos.get("xl/_rels/workbook.xml.rels", b"").decode("utf-8", "replace")
    destinos = {}
    for etiqueta, _ in _elementos(relaciones, "Relationship"):
        destino = _atributo(etiqueta, "Target") or ""
        destino = destino[1:] if destino.startswith("/") else "xl/" + destino
        destinos[_atributo(etiqueta, "Id")] = destino
    hojas = Lista()
    for etiqueta, _ in _elementos(libro, "sheet"):
        hojas.agregar((_texto_xml(_atributo(etiqueta, "name") or ""), destinos.get(_atributo(etiqueta, "r:id"))))
    if not hojas:
        if "xl/worksheets/sheet1.xml" in archivos:
            return "xl/worksheets/sheet1.xml"
        raise ValueError("el .xlsx no tiene hojas")
    nombres = ", ".join(nombre for nombre, _ in hojas)
    if hoja is None:
        elegida = hojas[0]
    elif isinstance(hoja, int) and not isinstance(hoja, bool):
        if not 1 <= hoja <= len(hojas):
            raise ValueError(f"el libro tiene {len(hojas)} hojas ({nombres}); la hoja {hoja} no existe")
        elegida = hojas[hoja - 1]
    elif isinstance(hoja, str):
        encontradas = Lista(h for h in hojas if h[0] == hoja)
        if not encontradas:
            raise ValueError(f"no hay una hoja llamada '{hoja}'; las hojas son: {nombres}")
        elegida = encontradas[0]
    else:
        raise ValueError('la hoja va con su nombre ("Sheet1") o con su número (1 es la primera)')
    if elegida[1] not in archivos:
        raise ValueError(f"no se encontró la hoja '{elegida[0]}' dentro del .xlsx")
    return elegida[1]


def leer_xlsx(ruta, hoja=None) -> Lista:
    """Las filas de la hoja como listas de textos, con "" en las celdas vacias."""
    with open(ruta, "rb") as archivo:
        archivos = abrir_zip(archivo.read())
    compartidos = Lista()
    if "xl/sharedStrings.xml" in archivos:
        xml = archivos["xl/sharedStrings.xml"].decode("utf-8", "replace")
        for _, contenido in _elementos(xml, "si"):
            compartidos.agregar(_textos_de(contenido))
    compartidos = tuple(compartidos)    # se consultan por numero muchas veces

    xml = archivos[_ruta_de_hoja(archivos, hoja)].decode("utf-8", "replace")
    filas, ancho = Lista(), 0
    for _, contenido in _elementos(xml, "row"):
        celdas, siguiente = {}, 0
        for etiqueta, dentro in _elementos(contenido, "c"):
            referencia = _atributo(etiqueta, "r")
            columna = _columna(referencia) if referencia else siguiente
            siguiente = columna + 1
            tipo = _atributo(etiqueta, "t")
            valores = Lista(v for _, v in _elementos(dentro, "v"))
            valor = _texto_xml(valores[0]) if valores else ""
            if tipo == "s" and valor != "":
                valor = compartidos[int(valor)]
            elif tipo == "inlineStr":
                valor = _textos_de(dentro)
            elif tipo == "b":
                valor = "verdadero" if valor == "1" else "falso"
            if valor != "":
                celdas[columna] = valor
        if celdas:                       # las filas vacias no cuentan, igual que en un CSV
            ancho = max(ancho, max(celdas) + 1)
            filas.agregar(celdas)
    return Lista(Lista(celdas.get(c, "") for c in range(ancho)) for celdas in filas)
