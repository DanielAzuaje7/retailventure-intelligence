# -*- coding: utf-8 -*-
"""
Script para actualizar y reejecutar notebooks/A3_Retenciones_Churn_CRM.ipynb
con las decisiones validadas:
- D2: NO_RESUELTAS = {'sin_resolver', 'escalado'}
- T1 / D1: Churn Relativo C + B (3*W_i con fallback en P85 global = 127 días)
"""

import nbformat
from nbclient import NotebookClient

nb = nbformat.read('notebooks/A3_Retenciones_Churn_CRM.ipynb', as_version=4)

# 1. Modificar Celda 22: Decisión D2 (CRM no resueltas)
cell_22_source = (
    "# ===== CELDA DE DECISIÓN DE EQUIPO (Trazabilidad para Bitácora y Defensa) =====\n"
    "# Decisión acordada por el equipo (Daniel, Andrés y Samuel):\n"
    "# Se adopta {'sin_resolver', 'escalado'} (970 quejas no resueltas analizadas).\n"
    "# Justificación: Una queja escalada que no fue resuelta representa un punto de fricción crítico\n"
    "# no solventado que afecta directamente la retención y recompra del cliente.\n"
    "NO_RESUELTAS = {'sin_resolver', 'escalado'}\n"
    "# ==============================================================================\n"
    "\n"
    "quejas_nr = quejas[quejas['resolucion'].isin(NO_RESUELTAS)].copy()\n"
    "quejas_resueltas = quejas[quejas['resolucion'] == 'resuelto'].copy()\n"
    "print(f'Quejas no resueltas analizadas: {len(quejas_nr)}')\n"
    "print(f'Quejas resueltas (grupo de control): {len(quejas_resueltas)}')\n"
)
nb.cells[22].source = cell_22_source

# 2. Modificar Celda 28: Markdown explicando Churn C + B
cell_28_source = (
    "## 9. A3.3 - Riesgo de churn\n"
    "\n"
    "**Definición operativa consensuada (Decisión de Equipo: Enfoque Relativo C + B):**\n"
    "- **Enfoque Relativo Personalizado (Opción C):** Para clientes con $\\ge 2$ compras, el umbral de churn es individual: "
    "$\\text{Recencia} > 3 \\times W_i$, donde $W_i$ es el intervalo mediano de recompra propio de ese cliente.\n"
    "- **Respaldo Global (Opción B):** Para clientes de una sola compra (donde $W_i$ no está definido), se adopta el "
    "Percentil 85 global ($127\\text{ días}$, ~4 meses) en lugar de la mediana global ($40\\text{ días}$).\n"
    "- **Justificación:** La mediana global clasificaba erróneamente al 72.5% de los clientes en churn (un falso positivo severo). "
    "Con C + B, se identifican con rigor estadístico los clientes que rompieron su patrón habitual de compra (31.6% de los clientes activos con compras).\n"
)
nb.cells[28].source = cell_28_source

# 3. Modificar Celda 29: Cálculo de Churn C + B
cell_29_source = (
    "con_compras = clientes[clientes['sin_compras'] == 0].copy()\n"
    "sin_compras = clientes[clientes['sin_compras'] == 1]\n"
    "\n"
    "# 1. Calcular intervalo mediano individual (W_i) para clientes con >= 2 compras\n"
    "tx_sorted = transacciones.sort_values(['cliente_id', 'fecha'])\n"
    "tx_sorted['diff_dias'] = tx_sorted.groupby('cliente_id')['fecha'].diff().dt.days\n"
    "w_individual = tx_sorted.groupby('cliente_id')['diff_dias'].median()\n"
    "\n"
    "# 2. Umbral de Respaldo Global: Percentil 85 (127 días)\n"
    "P85_GLOBAL = float(tx_sorted['diff_dias'].quantile(0.85))\n"
    "\n"
    "con_compras['w_i'] = con_compras['cliente_id'].map(w_individual)\n"
    "con_compras['umbral_individual'] = np.where(\n"
    "    con_compras['w_i'].notna() & (con_compras['w_i'] > 0),\n"
    "    3.0 * con_compras['w_i'],\n"
    "    P85_GLOBAL\n"
    ")\n"
    "\n"
    "con_compras['en_riesgo'] = con_compras['recencia_dias'] > con_compras['umbral_individual']\n"
    "riesgo = con_compras[con_compras['en_riesgo']]\n"
    "\n"
    "n_riesgo = int(riesgo['cliente_id'].nunique())\n"
    "monto_riesgo = float(riesgo['monto_total'].sum())\n"
    "margen_riesgo = float(riesgo['margen_total'].sum())\n"
    "\n"
    "print(f'Clientes con compras: {len(con_compras):,}')\n"
    "print(f'Clientes sin compras (excluidos): {len(sin_compras):,}')\n"
    "print(f'Metodología Churn: Relativo Personalizado (3*W_i) con Fallback en P85 ({P85_GLOBAL:.0f} días)')\n"
    "print(f'Clientes en riesgo: {n_riesgo:,} ({100 * n_riesgo / len(con_compras):.1f}% de los activos con compras)')\n"
    "print(f'Monto total en riesgo: ${monto_riesgo:,.2f}')\n"
    "print(f'Margen total en riesgo: ${margen_riesgo:,.2f}')\n"
)
nb.cells[29].source = cell_29_source

# 4. Modificar Celda 34: Tabla de Sensibilidad completa
cell_34_source = (
    "# Sensibilidad del umbral de churn frente a diferentes enfoques metodológicos\n"
    "sens_churn_rows = [\n"
    "    ['Mediana Global (Borrador inicial)', float(INTERVALO_MEDIANO), int((con_compras['recencia_dias'] > INTERVALO_MEDIANO).sum()), float(con_compras.loc[con_compras['recencia_dias'] > INTERVALO_MEDIANO, 'monto_total'].sum())],\n"
    "    ['Percentil 75 Global', float(tx_sorted['diff_dias'].quantile(0.75)), int((con_compras['recencia_dias'] > tx_sorted['diff_dias'].quantile(0.75)).sum()), float(con_compras.loc[con_compras['recencia_dias'] > tx_sorted['diff_dias'].quantile(0.75), 'monto_total'].sum())],\n"
    "    ['Percentil 85 Global (Opción B pura)', P85_GLOBAL, int((con_compras['recencia_dias'] > P85_GLOBAL).sum()), float(con_compras.loc[con_compras['recencia_dias'] > P85_GLOBAL, 'monto_total'].sum())],\n"
    "    ['Percentil 90 Global', float(tx_sorted['diff_dias'].quantile(0.90)), int((con_compras['recencia_dias'] > tx_sorted['diff_dias'].quantile(0.90)).sum()), float(con_compras.loc[con_compras['recencia_dias'] > tx_sorted['diff_dias'].quantile(0.90), 'monto_total'].sum())],\n"
    "    ['Modelo Acordado: C + B (Relativo 3*W_i + P85)', np.nan, n_riesgo, monto_riesgo]\n"
    "]\n"
    "sens_churn = pd.DataFrame(sens_churn_rows, columns=['Metodología / Umbral', 'Umbral (Días)', 'Clientes en Riesgo', 'Monto en Riesgo ($)'])\n"
    "sens_churn['% Clientes Activos'] = (100 * sens_churn['Clientes en Riesgo'] / len(con_compras)).round(1)\n"
    "print('Sensibilidad del churn frente al criterio metodológico:')\n"
    "display(sens_churn.round(2))\n"
)
nb.cells[34].source = cell_34_source

# Guardar notebook modificado
nbformat.write(nb, 'notebooks/A3_Retenciones_Churn_CRM.ipynb')
print("Notebook A3 actualizado. Ejecutando con nbclient...")

client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks'}})
client.execute()

nbformat.write(nb, 'notebooks/A3_Retenciones_Churn_CRM.ipynb')
print("¡Notebook A3_Retenciones_Churn_CRM.ipynb ejecutado exitosamente con todas las salidas renderizadas!")
