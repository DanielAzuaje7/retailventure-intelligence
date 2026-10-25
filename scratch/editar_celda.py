"""
editar_celda.py
Reemplaza, inserta o borra una celda de un notebook identificada por su id.
El texto de la celda se escribe a mano en un archivo aparte; este script solo lo coloca.

Uso:
    python scratch/editar_celda.py <notebook> replace <cell_id> <archivo_fuente>
    python scratch/editar_celda.py <notebook> insert-after <cell_id> <archivo_fuente> <code|markdown>
    python scratch/editar_celda.py <notebook> delete <cell_id>
"""
import sys
import uuid

import nbformat

ruta, modo, cell_id = sys.argv[1:4]
nb = nbformat.read(ruta, as_version=4)
idx = next(i for i, c in enumerate(nb.cells) if c.get("id") == cell_id)

if modo == "delete":
    nb.cells.pop(idx)
else:
    fuente = open(sys.argv[4], encoding="utf-8").read().rstrip("\n")
    if modo == "replace":
        nb.cells[idx].source = fuente
        if nb.cells[idx].cell_type == "code":
            nb.cells[idx].outputs = []
            nb.cells[idx].execution_count = None
    elif modo == "insert-after":
        tipo = sys.argv[5]
        nueva = nbformat.v4.new_code_cell(fuente) if tipo == "code" else nbformat.v4.new_markdown_cell(fuente)
        nueva["id"] = uuid.uuid4().hex[:8]
        nb.cells.insert(idx + 1, nueva)
        print("nueva celda:", nueva["id"])
    else:
        sys.exit(f"modo desconocido: {modo}")

nbformat.write(nb, ruta)
print(f"{modo} {cell_id} OK ({len(nb.cells)} celdas)")
