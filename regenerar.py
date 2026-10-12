"""Regenera el lexer y el parser a partir de grammar/Eva.g4.

Solo hace falta si se cambia la gramatica. Necesita Java 11 o superior;
el .jar de ANTLR se descarga solo la primera vez.

    python regenerar.py
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "src" / "evangelion" / "generado"
VERSION = "4.13.2"  # la misma del runtime en requirements.txt
JAR = RAIZ / "herramientas" / f"antlr-{VERSION}-complete.jar"
URL = f"https://repo1.maven.org/maven2/org/antlr/antlr4/{VERSION}/antlr4-{VERSION}-complete.jar"


def version_java(java: str) -> int:
    try:
        salida = subprocess.run([java, "-version"], capture_output=True, text=True).stderr
    except OSError:
        return 0
    encontrado = re.search(r'version "(\d+)\.(\d+)', salida)
    if not encontrado:
        return 0
    mayor, menor = int(encontrado.group(1)), int(encontrado.group(2))
    return menor if mayor == 1 else mayor  # Java 8 se reporta como 1.8


def buscar_java():
    # En mi laptop el java del PATH es el 8, por eso reviso tambien otras carpetas
    candidatos = [os.environ.get("JAVA_BIN"), shutil.which("java")]
    for patron in ("C:/Program Files/Eclipse Adoptium/*/bin/java.exe",
                   "C:/Program Files/Java/*/bin/java.exe",
                   str(Path.home() / ".jdks" / "*" / "bin" / "java.exe")):
        candidatos += sorted(glob.glob(patron), reverse=True)
    for java in candidatos:
        if java and version_java(java) >= 11:
            return java
    return None


def main() -> int:
    java = buscar_java()
    if java is None:
        print("No encontre Java 11 o superior. Instalalo o apunta JAVA_BIN al java.exe.")
        return 1

    if not JAR.exists():
        print(f"Descargando ANTLR {VERSION}...")
        JAR.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(URL, JAR)

    shutil.rmtree(SALIDA, ignore_errors=True)
    SALIDA.mkdir(parents=True)
    (SALIDA / "__init__.py").write_text("", encoding="utf-8")

    orden = [
        java, "-jar", str(JAR),
        "-Dlanguage=Python3", "-visitor", "-no-listener",
        "-encoding", "utf-8",
        "-o", str(SALIDA), "-Xexact-output-dir",
        "Eva.g4",
    ]
    # se corre dentro de grammar/ para que la ruta no quede escrita en lo generado
    resultado = subprocess.run(orden, cwd=RAIZ / "grammar")
    if resultado.returncode == 0:
        print(f"Listo, lexer y parser regenerados en {SALIDA.relative_to(RAIZ)}")
    return resultado.returncode


if __name__ == "__main__":
    sys.exit(main())
