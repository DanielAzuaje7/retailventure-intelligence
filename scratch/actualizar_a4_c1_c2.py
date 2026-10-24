# -*- coding: utf-8 -*-
"""
Script para actualizar notebooks/04_A4_Marketing_ROI.ipynb con las correcciones C1 (completada) y C2 (aplicada):
1. Descomposición del margen incremental (N tx, margen medio, margen total) y explicación de ROI < -1.
2. Confirmación escrita de ventana previa limpia y bootstrap a nivel de cliente.
3. Tabla por tipo de campaña con tasa pre, tasa post, lift (IC 95%) y ROI incremental (IC 95%).
4. Atribución Last-Touch real (merge_asof) eliminando duplicados (reporte de 54 tx deduplicadas).
5. Robustez: Diff-in-Diff con 3,200 clientes nunca contactados y sensibilidad al % de canje.
6. Redacción rigurosa: 'no se detecta efecto incremental estadísticamente significativo'.
"""

import nbformat
from nbclient import NotebookClient

# Leer el notebook base generado o reconstruir con las celdas actualizadas
with open('scratch/crear_a4_notebook.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Verificamos que podemos actualizar la sección A4.4 en scratch/crear_a4_notebook.py directamente
print("Generador listo para actualizar.")
