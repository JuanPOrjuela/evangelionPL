@echo off
rem Lanzador para Windows: eva ejemplos\01_primera_prueba.eva
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run.py" %*
) else (
    python "%~dp0run.py" %*
)
