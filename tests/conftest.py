import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


@pytest.fixture
def carpeta(tmp_path, monkeypatch):
    """Carpeta temporal con una copia de datos/, para no ensuciar el proyecto."""
    shutil.copytree(RAIZ / "datos", tmp_path / "datos")
    monkeypatch.chdir(tmp_path)
    return tmp_path
