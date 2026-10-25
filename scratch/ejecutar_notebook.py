"""
ejecutar_notebook.py
Ejecuta uno o varios notebooks de principio a fin con nbclient y guarda las salidas
en el mismo archivo (equivalente a `jupyter nbconvert --execute --inplace`).

Uso (desde la raiz del repo, con el .venv):
    .venv/Scripts/python.exe scratch/ejecutar_notebook.py notebooks/04_A4_Marketing_ROI.ipynb
"""
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

RAIZ = Path(__file__).resolve().parents[1]

codigo_salida = 0
for ruta in sys.argv[1:]:
    ruta = Path(ruta).resolve()
    nb = nbformat.read(ruta, as_version=4)
    inicio = time.time()
    # cwd = carpeta del notebook, igual que al abrirlo en Jupyter/VS Code
    cliente = NotebookClient(nb, timeout=1800, kernel_name="python3",
                             resources={"metadata": {"path": str(ruta.parent)}})
    try:
        cliente.execute()
        estado = "OK"
    except CellExecutionError as e:
        estado = "ERROR"
        codigo_salida = 1
        print(str(e)[-3000:])
    nbformat.write(nb, ruta)
    print(f"{estado}  {ruta.relative_to(RAIZ)}  ({time.time() - inicio:.0f} s)")

sys.exit(codigo_salida)
