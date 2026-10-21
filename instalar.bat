@echo off
rem Crea el entorno virtual, instala las dependencias y corre las pruebas
cd /d "%~dp0"
python -m venv .venv
".venv\Scripts\python.exe" -m pip install "antlr4-python3-runtime==4.13.2" "pytest>=8.0"
".venv\Scripts\python.exe" -m pytest
echo.
echo Listo. Prueba con: eva ejemplos\01_primera_prueba.eva
