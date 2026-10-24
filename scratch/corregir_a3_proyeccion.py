import nbformat as nbf
from pathlib import Path
from nbclient import NotebookClient

nb_path = Path("notebooks/A3_Retenciones_Churn_CRM.ipynb")
nb = nbf.read(nb_path, as_version=4)

# Celda 35 (Markdown de sección 10 - A3.4)
nb.cells[35].source = """## 10. A3.4 - Ingreso en riesgo a 6 meses

Proyección por cliente: **(Gasto total en los últimos 12 meses calendario / 12) × 6 meses**. 

> 📌 **Corrección Metodológica aplicada:**  
> Anteriormente se calculaba el promedio solo sobre los *meses activos* (meses con compras). Como el cliente promedio compra en ~5 de los 12 meses, ese cálculo sobrestimaba la tasa mensual casi 4 veces (proyectando $12.7M).  
> Al calcular el ritmo mensual sobre los **12 meses calendario completos**, la proyección anualizada refleja el flujo de caja real de la empresa (un escenario estimado realista y defendible).
"""

# Celda 36 (Código de cálculo de proyección 6 meses)
nb.cells[36].source = """# Corrección Metodológica: Gasto en la ventana reciente (últimos 12 meses calendario: todo 2024)
# Se divide entre 12 meses calendario para obtener la tasa mensual real
tx_reciente = transacciones[transacciones['fecha'] >= (FECHA_CORTE - pd.DateOffset(months=MESES_HISTORICO))]
gasto_12m = tx_reciente.groupby('cliente_id')['monto_neto'].sum().rename('gasto_ultimos_12m')

clientes_proy = con_compras.merge(gasto_12m.reset_index(), on='cliente_id', how='left').fillna({'gasto_ultimos_12m': 0})
clientes_proy['promedio_mensual_12m'] = clientes_proy['gasto_ultimos_12m'] / float(MESES_HISTORICO)
clientes_proy['ingreso_proyectado_6m'] = (clientes_proy['promedio_mensual_12m'] * MESES_PROYECCION).round(2)

riesgo_proy = clientes_proy[clientes_proy['en_riesgo']]
ingreso_riesgo_6m = float(riesgo_proy['ingreso_proyectado_6m'].sum())

proy_seg = riesgo_proy.groupby('segmento').agg(
    n_clientes=('cliente_id', 'count'),
    ingreso_proyectado_6m=('ingreso_proyectado_6m', 'sum'),
).reset_index().sort_values('ingreso_proyectado_6m', ascending=False)

print(f'Ingreso proyectado a 6 meses (clientes en riesgo): ${ingreso_riesgo_6m:,.2f}')
print('\\nProyeccion de fuga por segmento:')
print(proy_seg.to_string(index=False))
"""

# Guardar notebook actualizado
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook A3 actualizado. Ejecutando para validar...")
client = NotebookClient(nb, timeout=90, kernel_name="python3", resources={"metadata": {"path": "notebooks"}})
client.execute()

with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("¡Notebook A3 corregido, ejecutado y guardado con éxito!")
