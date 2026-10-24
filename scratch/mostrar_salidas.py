"""
mostrar_salidas.py
Imprime el codigo y/o la salida de texto de celdas de un notebook ya ejecutado.

Uso:
    python scratch/mostrar_salidas.py <notebook> [celdas] [--codigo] [--buscar texto]
    celdas: "16" o "16,17" o "16-19" (por defecto, todas)
"""
import json
import re
import sys


def texto_salidas(celda):
    partes = []
    for o in celda.get("outputs", []):
        if o.get("output_type") == "stream":
            partes.append("".join(o["text"]))
        elif o.get("output_type") in ("execute_result", "display_data"):
            datos = o.get("data", {})
            if "text/plain" in datos:
                partes.append("".join(datos["text/plain"]))
            elif "image/png" in datos:
                partes.append("[imagen]")
        elif o.get("output_type") == "error":
            partes.append(f"ERROR {o.get('ename')}: {o.get('evalue')}")
    return "\n".join(partes)


args = sys.argv[1:]
ruta = args.pop(0)
ver_codigo = "--codigo" in args
buscar = None
if "--buscar" in args:
    buscar = args[args.index("--buscar") + 1]
seleccion = None
if args and re.fullmatch(r"[\d,\-]+", args[0]):
    seleccion = set()
    for tramo in args[0].split(","):
        a, _, b = tramo.partition("-")
        seleccion.update(range(int(a), int(b or a) + 1))

nb = json.load(open(ruta, encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    if seleccion is not None and i not in seleccion:
        continue
    fuente = "".join(c["source"])
    salida = texto_salidas(c) if c["cell_type"] == "code" else ""
    if buscar and buscar.lower() not in (fuente + salida).lower():
        continue
    print(f"\n===== celda {i} ({c['cell_type']}) =====")
    if ver_codigo or c["cell_type"] == "markdown":
        print(fuente)
        if salida:
            print("----- salida -----")
    print(salida)
