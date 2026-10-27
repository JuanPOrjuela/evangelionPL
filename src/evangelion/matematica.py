"""Nuestra libreria de matematicas, hecha a mano para no usar el modulo math.

Las funciones con decimales se calculan con series (Taylor) o con el metodo de
Newton, y se paran cuando el siguiente termino ya no cambia el resultado.
"""

PI = 3.141592653589793
LN2 = 0.6931471805599453
PRECISION = 1e-15


def es_entero(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def piso(x):
    """El entero mas grande que no pasa de x: piso(2.7) = 2, piso(-2.3) = -3."""
    entero = int(x)  # int() corta hacia el cero
    return entero - 1 if x < entero else entero


def techo(x):
    """El entero mas pequeno que no es menor que x: techo(2.1) = 3."""
    entero = int(x)
    return entero + 1 if x > entero else entero


def absoluto(x):
    return -x if x < 0 else x


def raiz(x, indice=2):
    """Raiz con el metodo de Newton: se mejora una aproximacion hasta que no cambia."""
    if indice == 0:
        raise ValueError("el índice de la raíz no puede ser 0")
    if indice < 0:
        # raiz(x, -n) = 1 / raiz(x, n)
        if x == 0:
            raise ValueError("cero no tiene raíz con índice negativo (sería dividir por cero)")
        return 1 / raiz(x, -indice)
    if x < 0:
        if es_entero(indice) and indice % 2 == 1:
            return -raiz(-x, indice)
        raise ValueError("no hay raíz real de un número negativo")
    if x == 0:
        return 0.0
    # el primer intento sale de los logaritmos y Newton lo pule
    aproximacion = exp(ln(x) / indice)
    for _ in range(100):
        siguiente = ((indice - 1) * aproximacion + x / aproximacion ** (indice - 1)) / indice
        if absoluto(siguiente - aproximacion) <= PRECISION * siguiente:
            return siguiente
        aproximacion = siguiente
    return aproximacion


def exp(x):
    """e^x. Se parte x a la mitad varias veces para que la serie converja rapido,
    y al final se eleva al cuadrado las mismas veces: e^x = (e^(x/2^k))^(2^k)."""
    if x > 709:
        raise OverflowError("el resultado de exp() es demasiado grande")
    if x < -745:
        return 0.0
    mitades = 0
    while absoluto(x) > 0.5:
        x /= 2
        mitades += 1
    termino, suma, n = 1.0, 1.0, 1
    while absoluto(termino) > PRECISION * suma:
        termino *= x / n
        suma += termino
        n += 1
    for _ in range(mitades):
        suma *= suma
    return suma


def ln(x):
    """Logaritmo natural. x = m * 2^k con m entre 1 y 2, asi ln(x) = k*ln(2) + ln(m),
    y ln(m) sale de la serie ln(m) = 2 * (z + z^3/3 + z^5/5 + ...) con z = (m-1)/(m+1)."""
    if x <= 0:
        raise ValueError("el logaritmo solo existe para números mayores que cero")
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    while x < 1:
        x *= 2
        k -= 1
    z = (x - 1) / (x + 1)
    z2, termino, suma, n = z * z, z, 0.0, 1
    while True:
        sumando = termino / n
        suma += sumando
        if absoluto(sumando) <= PRECISION:
            break
        termino *= z2
        n += 2
    return k * LN2 + 2 * suma


def log(x, base=10):
    if base <= 0 or base == 1:
        raise ValueError("la base del logaritmo tiene que ser positiva y distinta de 1")
    return ln(x) / ln(base)


def piso_log10(x) -> int:
    """El exponente de la potencia de 10 que queda justo debajo de x.
    Se corrige al final porque log() puede dar 2.9999999 en vez de 3."""
    p = piso(log(x, 10))
    while 10.0 ** (p + 1) <= x:
        p += 1
    while 10.0 ** p > x:
        p -= 1
    return p


def techo_log2(n: int) -> int:
    """Cuantas veces hay que doblar 1 para llegar a n (sin decimales)."""
    k, potencia = 0, 1
    while potencia < n:
        potencia *= 2
        k += 1
    return k


def _reducir_angulo(x):
    """Lleva el angulo al rango [-pi, pi], donde la serie converge rapido."""
    vueltas = piso((x + PI) / (2 * PI))
    return x - vueltas * 2 * PI


def sen(x):
    x = _reducir_angulo(x)
    termino, suma, n = x, x, 1
    while absoluto(termino) > PRECISION:
        termino *= -x * x / ((n + 1) * (n + 2))
        suma += termino
        n += 2
    return suma


def cos(x):
    x = _reducir_angulo(x)
    termino, suma, n = 1.0, 1.0, 0
    while absoluto(termino) > PRECISION:
        termino *= -x * x / ((n + 1) * (n + 2))
        suma += termino
        n += 2
    return suma


def tan(x):
    coseno = cos(x)
    if absoluto(coseno) < 1e-15:
        raise ValueError("la tangente no existe en ese ángulo")
    return sen(x) / coseno


def factorial(n):
    if not es_entero(n) or n < 0:
        raise ValueError("factorial() solo recibe enteros desde 0")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


E = exp(1)


class Aleatorio:
    """Generador congruencial lineal (los mismos numeros que usa glibc).
    Con la misma semilla siempre salen los mismos numeros, asi los resultados se pueden repetir."""

    def __init__(self, semilla: int = 42):
        self.estado = semilla % 2 ** 31

    def siguiente(self) -> float:
        """Un numero entre 0 (incluido) y 1 (sin incluir)."""
        self.estado = (1103515245 * self.estado + 12345) % 2 ** 31
        return self.estado / 2 ** 31

    def entero(self, desde: int, hasta: int) -> int:
        """Un entero entre desde y hasta, los dos incluidos."""
        return desde + int(self.siguiente() * (hasta - desde + 1))

    def barajar(self, lista: list) -> list:
        """Fisher-Yates: recorre la lista de atras hacia adelante intercambiando al azar."""
        lista = list(lista)
        for i in range(len(lista) - 1, 0, -1):
            j = self.entero(0, i)
            lista[i], lista[j] = lista[j], lista[i]
        return lista


# --- Metodos numericos: reciben una funcion f(x) que escribe el usuario ----------------

def derivada(f, x, h=1e-6):
    """Derivada con diferencia centrada: (f(x + h) - f(x - h)) / 2h."""
    return (f(x + h) - f(x - h)) / (2 * h)


def biseccion(f, a, b, tolerancia=1e-12):
    """Raiz de f entre a y b: se parte el intervalo a la mitad y se queda la mitad
    donde f cambia de signo, hasta que el intervalo es mas pequeno que la tolerancia."""
    fa, fb = f(a), f(b)
    if fa == 0:
        return a
    if fb == 0:
        return b
    if (fa < 0) == (fb < 0):
        raise ValueError("f(a) y f(b) tienen el mismo signo, así que no se sabe si hay una raíz en medio")
    for _ in range(200):
        medio = (a + b) / 2
        fm = f(medio)
        if fm == 0 or (b - a) / 2 < tolerancia:
            return medio
        if (fm < 0) == (fa < 0):
            a, fa = medio, fm
        else:
            b = medio
    return (a + b) / 2


def newton(f, x, tolerancia=1e-12):
    """Metodo de Newton-Raphson: x = x - f(x) / f'(x), con la derivada numerica."""
    for _ in range(100):
        pendiente = derivada(f, x)
        if pendiente == 0:
            raise ValueError("la derivada se hizo 0 y Newton no puede seguir; prueba otro punto de inicio")
        siguiente = x - f(x) / pendiente
        if absoluto(siguiente - x) <= tolerancia * (1 + absoluto(siguiente)):
            return siguiente
        x = siguiente
    raise ValueError("Newton no convergió en 100 pasos; prueba otro punto de inicio o usa biseccion()")
