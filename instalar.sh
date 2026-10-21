#!/usr/bin/env bash
# Instalacion en Linux (o en una VM con Ubuntu): crea el entorno virtual,
# instala el runtime de ANTLR y pytest, y corre las pruebas
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null; then
    echo "No encontre python3. En Ubuntu: sudo apt install python3"
    exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo "Hace falta Python 3.10 o superior y este es $(python3 --version)"
    exit 1
fi

# En Ubuntu el modulo venv viene aparte (paquete python3-venv)
if ! python3 -m venv .venv >/dev/null 2>&1 || [ ! -x .venv/bin/pip ]; then
    rm -rf .venv
    echo "Falta el paquete python3-venv, lo instalo (pide la contrasena de sudo)"
    sudo apt-get update -qq
    sudo apt-get install -y python3-venv
    python3 -m venv .venv
fi

.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q "antlr4-python3-runtime==4.13.2" "pytest>=8.0"
.venv/bin/python -m pytest

chmod +x eva.sh
echo
echo "Listo. Prueba con: ./eva.sh ejemplos/01_primera_prueba.eva"
