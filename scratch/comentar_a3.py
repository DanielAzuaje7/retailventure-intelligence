import nbformat as nbf
from pathlib import Path
from nbclient import NotebookClient

nb_path = Path("notebooks/A3_Retenciones_Churn_CRM.ipynb")
nb = nbf.read(nb_path, as_version=4)

# 1. Modificar Celda 22 (Markdown de decisión de quejas)
nb.cells[21].source = """### Decisión de Negocio CRM (Trazabilidad y Calibración Pendiente)

Define qué valores de `resolucion` cuentan como **queja no resuelta**:
- **Opción A (Conservadora / Actual):** `{'sin_resolver'}` (solo quejas con falla confirmada).
- **Opción B (Recomendada por BI):** `{'sin_resolver', 'escalado'}`. Desde la perspectiva del cliente, un ticket escalado a supervisor sin cierre efectivo sigue representando una experiencia insatisfecha y fricción no solucionada.
- **Opción C (Amplia):** `{'sin_resolver', 'escalado', 'parcialmente_resuelto'}`.

> **Nota para la reunión de equipo:** Validar si se adopta la Opción B para reflejar con mayor precisión el impacto de la atención al cliente sobre las recompras.
"""

# 2. Modificar Celda 23 (Código de decisión de quejas)
nb.cells[22].source = """# ===== CELDA DE DECISIÓN DE EQUIPO (Trazabilidad para Bitácora y Defensa) =====
# NOTA DE REVISIÓN: Ajustar según acuerdo con Daniel y el equipo.
# Opción actual: Solo 'sin_resolver' (499 quejas).
# Propuesta recomendada: Incluir 'escalado' si no hubo resolución de segundo nivel.
NO_RESUELTAS = {'sin_resolver'}
# NO_RESUELTAS = {'sin_resolver', 'escalado'}                    # propuesta recomendada
# NO_RESUELTAS = {'sin_resolver', 'escalado', 'parcialmente_resuelto'}  # alternativa amplia
# ==============================================================================

quejas_nr = quejas[quejas['resolucion'].isin(NO_RESUELTAS)].copy()
quejas_resueltas = quejas[quejas['resolucion'] == 'resuelto'].copy()
print(f'Quejas no resueltas analizadas: {len(quejas_nr)}')
print(f'Quejas resueltas (grupo de control): {len(quejas_resueltas)}')
"""

# 3. Modificar Celda 29 (Markdown de definición de Churn)
nb.cells[28].source = r"""## 9. A3.3 - Riesgo de churn

**Definición operativa actual (Borrador):** Un cliente se clasifica en riesgo si su recencia (`recencia_dias` calculada respecto al corte 2024-12-31) supera el intervalo mediano entre compras (`INTERVALO_MEDIANO = 40 días`). Se respeta la etiqueta `segmento` de `clean.clientes`.

---

> ### OBSERVACIÓN TÉCNICA Y CALIBRACIÓN PENDIENTE (REVISIÓN DE EQUIPO):
> 
> 1. **El sesgo de la Mediana (40 días):** Por definición estadística, en una distribución asimétrica de recompras, el 50% de las transacciones habituales tardan *más* de 40 días. Fijar el umbral de churn en 40 días clasifica al **72.5% de los clientes activos como 'perdidos'** e infla la fuga proyectada a **$12.7M a 6 meses** (un escenario irrealmente pesimista para el negocio).
> 
> 2. **Distribución real observada de días entre compras:**
>    - **P50 (Mediana):** 40 días
>    - **P75:** 87 días
>    - **P85:** 127 días (~4 meses)
>    - **P90:** 162 días (~5.4 meses)
> 
> 3. **Propuesta metodológica para acordar en equipo:**
>    - En retail, el abandono real se consolida a partir del **P85 o P90 (120 a 160 días)**, o bien usando un múltiplo representativo de la mediana ($3 \times W = 120\text{ días}$).
>    - Se sugiere adoptar un **Semáforo de Riesgo**:
>      * **En ciclo normal:** Recencia <= 40 días (cliente activo y fidelizado).
>      * **En observación / Riesgo leve:** 41 a 120 días (retraso respecto a su ciclo normal; amerita campaña de reactivación).
>      * **Churn confirmado / Riesgo crítico:** > 120 o 160 días (cliente en abandono real).
> 
> 4. **Conexión con A2.2 (CLV):** La tasa de churn que resulte de este acuerdo alimentará directamente la vida esperada ($1 / \text{churn}$) para el cálculo de Customer Lifetime Value en el notebook `02_A2_Rentabilidad.ipynb`.
"""

# 4. Modificar Celda 30 (Código de umbral de churn)
nb.cells[29].source = """con_compras = clientes[clientes['sin_compras'] == 0].copy()
sin_compras = clientes[clientes['sin_compras'] == 1]

# UMBRAL ACTUAL (Borrador exploratorio): Mediana de recompra (40 días).
# NOTA DE REVISIÓN: El equipo debe decidir si mantiene este umbral base o adopta
# el percentil 85-90 (120 - 160 días) para evitar sobreestimar el churn (ver tabla de sensibilidad abajo).
UMBRAL_BASE = float(INTERVALO_MEDIANO)

con_compras['en_riesgo'] = con_compras['recencia_dias'] > UMBRAL_BASE
riesgo = con_compras[con_compras['en_riesgo']]

n_riesgo = int(riesgo['cliente_id'].nunique())
monto_riesgo = float(riesgo['monto_total'].sum())
margen_riesgo = float(riesgo['margen_total'].sum())

print(f'Clientes con compras: {len(con_compras):,}')
print(f'Clientes sin compras (excluidos): {len(sin_compras):,}')
print(f'Umbral de inactividad: recencia > {UMBRAL_BASE:.0f} dias (exploratorio, pendiente de calibracion)')
print(f'Clientes en riesgo: {n_riesgo:,} ({100 * n_riesgo / len(con_compras):.1f}% de los que compran)')
print(f'Monto total en riesgo: ${monto_riesgo:,.2f}')
print(f'Margen total en riesgo: ${margen_riesgo:,.2f}')
"""

# 5. Modificar Celda 41 (Markdown de Limitaciones y Supuestos)
nb.cells[40].source = """## 12. Limitaciones y supuestos

- **No se demuestra causalidad** entre quejas del CRM y caída de compras; se reporta una asociación temporal robustecida con un grupo de control (quejas resueltas).
- **Umbral de churn en revisión:** El umbral base actual (40 días) es exploratorio. La calibración formal entre 120 y 160 días (percentil 85-90) está pendiente de validación con Daniel y el equipo para el entregable definitivo y para alimentar el CLV de A2.
- **Criterio de quejas no resueltas:** Actualmente solo contempla `sin_resolver`; la inclusión de `escalado` está sujeta a decisión de equipo para evitar subregistro de fricciones de clientes.
- **La proyección a 6 meses es un escenario estimado** a partir del ritmo de compra reciente, no una pérdida confirmada.
- `margen_neto_devol` de A1 supone que una devolución anula toda la venta y su margen; las devoluciones parciales pueden requerir ajuste.
- `fecha_alta_efectiva` corrige el problema de `fecha_registro`; todos los análisis temporales deben usarla (o `recencia_dias`, ya calculada contra el corte).
- El flag `convertido` de campañas es atribución declarada; no se usa en A3 (corresponde a A4).
- La etiqueta `segmento` se respeta tal como viene en `clean.clientes`; la definición analítica de churn vive aparte.
"""

# Guardar notebook actualizado
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook A3 actualizado limpiamente.")
Client = NotebookClient(nb, timeout=90, kernel_name="python3", resources={"metadata": {"path": "notebooks"}})
Client.execute()

with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("¡Notebook A3 validado y guardado con éxito!")
