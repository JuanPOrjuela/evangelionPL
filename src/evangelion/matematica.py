"""Nuestra libreria de matematicas, hecha a mano para no usar el modulo math.

Las funciones con decimales se calculan con series (Taylor) o con el metodo de
Newton, y se paran cuando el siguiente termino ya no cambia el resultado.
Varias tienen un segundo metodo y se elige desde el lenguaje con metodo():
    metodo("sen", "duplicacion")   # desde aqui sen() ya no usa Taylor
    metodo("sen")                  # dice cual metodo esta activo
"""

from .listas import Lista

PI = 3.141592653589793
LN2 = 0.6931471805599453
PRECISION = 1e-15

# El primer metodo de cada funcion es el que se usa si no se cambia
METODOS = {"exp": ("taylor", "newton"), "ln": ("serie", "newton"),
           "sen": ("taylor", "duplicacion"), "cos": ("taylor", "duplicacion"),
           "raiz": ("newton", "biseccion")}
_activo = {}


def reiniciar_metodos() -> None:
    """Vuelve todas las funciones a su metodo por defecto (al empezar cada programa)."""
    for funcion, opciones in METODOS.items():
        _activo[funcion] = opciones[0]


def metodo(funcion, nombre=None):
    """metodo("sen") dice que metodo usa sen(); metodo("sen", "duplicacion") lo cambia."""
    if funcion not in METODOS:
        raise ValueError(f"'{funcion}' no tiene métodos para escoger; se pueden cambiar: "
                         + ", ".join(METODOS))
    if nombre is None:
        return _activo[funcion]
    if nombre not in METODOS[funcion]:
        raise ValueError(f"'{nombre}' no es un método de {funcion}(); los que hay son: "
                         + ", ".join(METODOS[funcion]))
    _activo[funcion] = nombre
    return nombre


reiniciar_metodos()


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
    if _activo["raiz"] == "biseccion":
        return _raiz_biseccion(x, indice)
    # el primer intento sale de los logaritmos y Newton lo pule
    aproximacion = exp(ln(x) / indice)
    for _ in range(100):
        siguiente = ((indice - 1) * aproximacion + x / aproximacion ** (indice - 1)) / indice
        if absoluto(siguiente - aproximacion) <= PRECISION * siguiente:
            return siguiente
        aproximacion = siguiente
    return aproximacion


def _raiz_biseccion(x, indice):
    """La raiz y cumple y^indice = x. Esta entre 0 y max(1, x): se parte ese intervalo
    a la mitad y se queda la mitad donde y^indice pasa de menos a mas que x."""
    bajo, alto = 0.0, x if x > 1 else 1.0
    for _ in range(2000):
        medio = (bajo + alto) / 2
        if medio == bajo or medio == alto:   # ya no caben mas decimales
            return medio
        if medio ** indice < x:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


def exp(x):
    """e^x con el metodo activo: "taylor" (la serie) o "newton" (resuelve ln(y) = x)."""
    if x > 709:
        raise OverflowError("el resultado de exp() es demasiado grande")
    if x < -745:
        return 0.0
    if _activo["exp"] == "newton" and x > -700:
        return _exp_newton(x)
    return _exp_taylor(x)


def _exp_newton(x):
    """Newton sobre f(y) = ln(y) - x: y = y - f(y)/f'(y) = y * (1 + x - ln(y)).
    El primer intento es una potencia de 2 cercana: e^x = 2^(x / ln 2)."""
    y = 2.0 ** int(x / LN2)
    for _ in range(100):
        siguiente = y * (1 + x - _ln_serie(y))
        if absoluto(siguiente - y) <= PRECISION * siguiente:
            return siguiente
        y = siguiente
    return y


def _exp_taylor(x):
    """Serie de Taylor e^x = 1 + x + x^2/2! + ... Se parte x a la mitad varias veces para
    que la serie converja rapido, y al final se eleva al cuadrado: e^x = (e^(x/2^k))^(2^k)."""
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
    """Logaritmo natural con el metodo activo: "serie" o "newton" (resuelve e^y = x)."""
    if x <= 0:
        raise ValueError("el logaritmo solo existe para números mayores que cero")
    if _activo["ln"] == "newton":
        return _ln_newton(x)
    return _ln_serie(x)


def _partir_en_potencia_de_2(x) -> tuple:
    """x = m * 2^k con m entre 1 y 2."""
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    while x < 1:
        x *= 2
        k -= 1
    return x, k


def _ln_newton(x):
    """ln(x) = k*ln(2) + ln(m), y ln(m) con Newton sobre f(y) = e^y - m:
    y = y - (e^y - m) / e^y = y - 1 + m / e^y. Como m esta entre 1 y 2, y esta entre 0 y 0.7."""
    m, k = _partir_en_potencia_de_2(x)
    y = m - 1
    for _ in range(100):
        siguiente = y - 1 + m / _exp_taylor(y)
        if absoluto(siguiente - y) <= PRECISION:
            y = siguiente
            break
        y = siguiente
    return k * LN2 + y


def _ln_serie(x):
    """x = m * 2^k con m entre 1 y 2, asi ln(x) = k*ln(2) + ln(m),
    y ln(m) sale de la serie ln(m) = 2 * (z + z^3/3 + z^5/5 + ...) con z = (m-1)/(m+1)."""
    x, k = _partir_en_potencia_de_2(x)
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


def _duplicar_angulo(x) -> tuple:
    """Seno y coseno sin series: se parte el angulo a la mitad hasta que es casi 0, donde
    sen(a) = a y 1 - cos(a) = a^2/2, y se vuelve a doblar con
    sen(2a) = 2 sen(a) cos(a) y 1 - cos(2a) = 2 sen(a)^2. Devuelve (seno, coseno)."""
    a, mitades = _reducir_angulo(x), 0
    while absoluto(a) > 1e-8:
        a /= 2
        mitades += 1
    seno, uno_menos_coseno = a, a * a / 2
    for _ in range(mitades):
        seno, uno_menos_coseno = 2 * seno * (1 - uno_menos_coseno), 2 * seno * seno
    return seno, 1 - uno_menos_coseno


def sen(x):
    """Seno con el metodo activo: "taylor" (x - x^3/3! + x^5/5! - ...) o "duplicacion"."""
    if _activo["sen"] == "duplicacion":
        return _duplicar_angulo(x)[0]
    x = _reducir_angulo(x)
    termino, suma, n = x, x, 1
    while absoluto(termino) > PRECISION:
        termino *= -x * x / ((n + 1) * (n + 2))
        suma += termino
        n += 2
    return suma


def cos(x):
    """Coseno con el metodo activo: "taylor" (1 - x^2/2! + x^4/4! - ...) o "duplicacion"."""
    if _activo["cos"] == "duplicacion":
        return _duplicar_angulo(x)[1]
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


def tanh(x):
    """Tangente hiperbolica: (e^2x - 1) / (e^2x + 1). Va de -1 a 1.
    Desde |x| > 20 ya es 1 o -1 con todos los decimales que caben."""
    if x > 20:
        return 1.0
    if x < -20:
        return -1.0
    e2x = exp(2 * x)
    return (e2x - 1) / (e2x + 1)


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

    def barajar(self, lista: Lista) -> Lista:
        """Fisher-Yates: recorre la lista de atras hacia adelante intercambiando al azar."""
        lista = Lista(lista)
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
