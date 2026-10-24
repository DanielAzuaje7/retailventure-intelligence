# -*- coding: utf-8 -*-
"""
Script para completar y ejecutar las secciones A2.2, A2.3 y A2.4 en notebooks/02_A2_Rentabilidad.ipynb
"""

import nbformat
from nbclient import NotebookClient

# Leer el notebook actual
nb = nbformat.read('notebooks/02_A2_Rentabilidad.ipynb', as_version=4)

# Conservar celdas de A2.1 (índices 0 a 22)
base_cells = nb.cells[:23]

new_cells = []

# ==========================================
# SECCIÓN A2.2: CUSTOMER LIFETIME VALUE (CLV)
# ==========================================
md_a2_2 = nbformat.v4.new_markdown_cell(
r"""---
## A2.2 Customer Lifetime Value (CLV) por Segmento

El **Customer Lifetime Value (CLV)** proyecta el margen bruto total esperado que un cliente genera a lo largo de su relación con RetailVenture C.A.

### Formulación Metodológica
$$\text{CLV} = \text{Margen Anual Promedio por Cliente} \times \text{Vida Media Esperada } (E[\text{vida}])$$

Donde:
1. **Margen Anual por Cliente:** $\frac{\text{Margen Bruto Total del Segmento}}{2 \text{ años}} \div \text{Clientes Totales del Segmento}$
2. **Tasa de Churn Anual de Cohorte:** $19.7\%$ ($0.197$, calibrada en A3 y consensuada con el equipo).
3. **Vida Media Esperada:**
   - **Horizonte de Negocio (Planificación Retail):** $E[\text{vida}] = \min\left(\frac{1}{0.197}, 3.0\right) = 3.0\text{ años}$ (límite prudencial ante obsolescencia).
   - **Modelo Teórico Puro:** $E[\text{vida}] = \frac{1}{\text{churn}} = \frac{1}{0.197} \approx 5.08\text{ años}$.
4. **Descomposición:** $\text{Margen Anual} = \text{Ticket Promedio} \times \text{Frecuencia Anual} \times \text{Margen } \%$
"""
)
new_cells.append(md_a2_2)

code_a2_2_calc = nbformat.v4.new_code_cell(
r"""# 1. Cálculo de CLV por Segmento
churn_anual = 0.197
vida_teorica = 1.0 / churn_anual
vida_horizonte_3y = 3.0

clv_seg = df_cli.groupby('segmento').agg(
    n_clientes=('cliente_id', 'count'),
    n_con_compras=('sin_compras', lambda s: (s == 0).sum()),
    margen_total=('margen_total', 'sum'),
    gasto_total=('monto_total', 'sum'),
    transacciones_totales=('n_compras', 'sum')
).reset_index()

# Métricas anualizadas por cliente
clv_seg['ticket_promedio'] = clv_seg['gasto_total'] / clv_seg['transacciones_totales']
clv_seg['frecuencia_anual'] = clv_seg['transacciones_totales'] / 2.0 / clv_seg['n_clientes']
clv_seg['margen_pct'] = (clv_seg['margen_total'] / clv_seg['gasto_total']) * 100
clv_seg['margen_anual_por_cliente'] = clv_seg['margen_total'] / 2.0 / clv_seg['n_clientes']

# Estimaciones de CLV
clv_seg['clv_3_anios'] = clv_seg['margen_anual_por_cliente'] * vida_horizonte_3y
clv_seg['clv_teorico_5y'] = clv_seg['margen_anual_por_cliente'] * vida_teorica

# Ordenar por valor y formatear
clv_seg = clv_seg.sort_values('clv_3_anios', ascending=False)
clv_display = clv_seg[['segmento', 'n_clientes', 'ticket_promedio', 'frecuencia_anual', 
                       'margen_pct', 'margen_anual_por_cliente', 'clv_3_anios', 'clv_teorico_5y']].copy()
clv_display.columns = ['Segmento', 'N Clientes', 'Ticket Prom. ($)', 'Frecuencia (tx/año)', 
                       'Margen (%)', 'Margen Anual/Cli ($)', 'CLV 3 Años ($)', 'CLV Teórico 5.1A ($)']
clv_display.round(2)
"""
)
new_cells.append(code_a2_2_calc)

code_a2_2_plot = nbformat.v4.new_code_cell(
r"""# Gráfico de CLV por Segmento (Horizonte 3 años vs Teórico)
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(clv_seg))
width = 0.35

rects1 = ax.bar(x - width/2, clv_seg['clv_3_anios'], width, label='CLV Horizonte 3 Años ($)', color='#1F77B4')
rects2 = ax.bar(x + width/2, clv_seg['clv_teorico_5y'], width, label='CLV Teórico 5.08 Años ($)', color='#AEC7E8')

ax.set_ylabel('Valor Esperado por Cliente ($ USD)', fontsize=11)
ax.set_title('Customer Lifetime Value (CLV) Estimado por Segmento', fontsize=13, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(clv_seg['segmento'], fontsize=11)
ax.legend(frameon=True)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Etiquetas sobre las barras
for rect in rects1:
    height = rect.get_height()
    ax.annotate(f'${height:,.0f}',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.show()
"""
)
new_cells.append(code_a2_2_plot)

md_a2_2_ticket = nbformat.v4.new_markdown_cell(
r"""### Diagnóstico Causal del Ticket Promedio: Localización del -8% Interanual
El caso de negocio de RetailVenture C.A. señala una caída del **8% en el ticket promedio**.
Al analizar la empresa de forma global, el ticket promedio cayó un **-1.94%** ($351.29 \rightarrow $344.49). Sin embargo, al desglosar interanualmente por segmento, se descubre que **la caída del 8% está concentrada exactamente en el segmento `Inactivo` (-8.03%)**, mientras que el segmento `Premium` cayó -1.95% y `Nuevo` creció +2.53%.
"""
)
new_cells.append(md_a2_2_ticket)

code_a2_2_ticket = nbformat.v4.new_code_cell(
r"""# Evolución del Ticket Promedio por Segmento (2023 vs 2024)
ticket_evo = df_trx.pivot_table(index='segmento', columns='anio', values='monto_neto', aggfunc=['mean', 'count'])
ticket_evo['delta_ticket_$'] = ticket_evo[('mean', 2024)] - ticket_evo[('mean', 2023)]
ticket_evo['delta_ticket_%'] = (ticket_evo['delta_ticket_$'] / ticket_evo[('mean', 2023)]) * 100

resumen_ticket = pd.DataFrame({
    'Ticket 2023 ($)': ticket_evo[('mean', 2023)],
    'Ticket 2024 ($)': ticket_evo[('mean', 2024)],
    'Variación ($)': ticket_evo['delta_ticket_$'],
    'Variación Interanual (%)': ticket_evo['delta_ticket_%'],
    'Transacciones 2023': ticket_evo[('count', 2023)],
    'Transacciones 2024': ticket_evo[('count', 2024)]
})

print("EVOLUCIÓN INTERANUAL DEL TICKET PROMEDIO POR SEGMENTO:")
resumen_ticket.round(2)
"""
)
new_cells.append(code_a2_2_ticket)

# ==========================================
# SECCIÓN A2.3: ESTACIONALIDAD DE VENTAS
# ==========================================
md_a2_3 = nbformat.v4.new_markdown_cell(
r"""---
## A2.3 Análisis de Estacionalidad de Ventas (2023 vs 2024)

Analizamos la dinámica temporal mes a mes de los ingresos netos y el margen bruto para identificar picos de demanda, valles operativos y patrones estacionales por canal de venta.
"""
)
new_cells.append(md_a2_3)

code_a2_3_calc = nbformat.v4.new_code_cell(
r"""# Serie temporal mensual: Ingresos y Margen Bruto
mensual = df_trx.groupby(['anio', 'mes']).agg(
    ingreso_neto=('monto_neto', 'sum'),
    margen_bruto=('margen_bruto', 'sum'),
    transacciones=('transaccion_id', 'count'),
    descuento_prom=('descuento', 'mean'),
    tasa_devolucion=('devuelto', 'mean')
).reset_index()

mensual['margen_pct'] = (mensual['margen_bruto'] / mensual['ingreso_neto']) * 100
mensual['tasa_devolucion_pct'] = mensual['tasa_devolucion'] * 100
mensual['anio_mes_str'] = mensual['anio'].astype(str) + '-' + mensual['mes'].astype(str).str.zfill(2)

print("Resumen de Estacionalidad Mensual (Primeros y Últimos meses):")
display(pd.concat([mensual.head(4), mensual.tail(4)]).round(2))
"""
)
new_cells.append(code_a2_3_calc)

code_a2_3_plot1 = nbformat.v4.new_code_cell(
r"""# Comparativa Estacional Mensual: Curva 2023 vs 2024
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
m_2023 = mensual[mensual['anio'] == 2023]
m_2024 = mensual[mensual['anio'] == 2024]

# 1. Ingresos Netos
ax1.plot(m_2023['mes'], m_2023['ingreso_neto'] / 1e3, marker='o', lw=2.2, color='#1F77B4', label='2023')
ax1.plot(m_2024['mes'], m_2024['ingreso_neto'] / 1e3, marker='s', lw=2.2, color='#FF7F0E', label='2024')
ax1.set_ylabel('Ingreso Neto (Miles $ USD)', fontsize=11)
ax1.set_title('Estacionalidad Mensual de Ingresos Netos (2023 vs 2024)', fontsize=12, fontweight='bold')
ax1.grid(alpha=0.3, linestyle='--')
ax1.legend(loc='lower right', frameon=True)

# Destacar pico Q4 y valle Q1
ax1.axvspan(1, 2, color='gray', alpha=0.12, label='Valle Q1 (Ene-Feb)')
ax1.axvspan(11, 12, color='gold', alpha=0.15, label='Pico Q4 (Nov-Dic: Black Friday/Navidad)')

# 2. Margen Bruto
ax2.plot(m_2023['mes'], m_2023['margen_bruto'] / 1e3, marker='o', lw=2.2, color='#2CA02C', label='Margen 2023')
ax2.plot(m_2024['mes'], m_2024['margen_bruto'] / 1e3, marker='s', lw=2.2, color='#D62728', label='Margen 2024')
ax2.set_ylabel('Margen Bruto (Miles $ USD)', fontsize=11)
ax2.set_xlabel('Mes del Año', fontsize=11)
ax2.set_title('Estacionalidad Mensual del Margen Bruto (2023 vs 2024)', fontsize=12, fontweight='bold')
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(meses_nombres, fontsize=10)
ax2.grid(alpha=0.3, linestyle='--')
ax2.legend(loc='lower right', frameon=True)

plt.tight_layout()
plt.show()
"""
)
new_cells.append(code_a2_3_plot1)

code_a2_3_channel = nbformat.v4.new_code_cell(
r"""# Descomposición de la Estacionalidad por Canal de Venta
canal_mensual = df_trx.groupby(['anio', 'mes', 'canal'])['monto_neto'].sum().unstack('canal') / 1e3

fig, ax = plt.subplots(figsize=(11, 4.5))
colores_canal = {'tienda_fisica': '#1F77B4', 'online': '#FF7F0E', 'app_movil': '#2CA02C'}

for canal in ['tienda_fisica', 'online', 'app_movil']:
    ax.plot(range(1, 25), 
            df_trx.groupby(['anio_mes', 'canal'])['monto_neto'].sum().unstack('canal')[canal] / 1e3, 
            label=f'Canal: {canal}', lw=2, color=colores_canal[canal])

ax.set_ylabel('Ventas Mensuales (Miles $ USD)', fontsize=11)
ax.set_title('Evolución Mensual Continua por Canal (24 Meses: 2023 - 2024)', fontsize=12, fontweight='bold')
ax.set_xticks(range(1, 25))
etiquetas_24m = df_trx['anio_mes'].drop_duplicates().sort_values().tolist()
ax.set_xticklabels(etiquetas_24m, rotation=45, ha='right', fontsize=9)
ax.grid(alpha=0.3, linestyle='--')
ax.legend(frameon=True)

plt.tight_layout()
plt.show()
"""
)
new_cells.append(code_a2_3_channel)

# ==========================================
# SECCIÓN A2.4: ELASTICIDAD Y EFECTO DE DESCUENTOS
# ==========================================
md_a2_4 = nbformat.v4.new_markdown_cell(
r"""---
## A2.4 Elasticidad y Efecto de Descuentos

Evaluamos la efectividad de la política de precios y descuentos de RetailVenture C.A. mediante un análisis de elasticidad empírica, punto de equilibrio y ventas por debajo del costo operativo.

### Condición de Punto de Equilibrio (Break-Even)
Para que un descuento porcentual $d$ preserve el margen bruto total con un margen base sin descuento $m$, el volumen vendido $Q$ debe aumentar en al menos:
$$\frac{\Delta Q}{Q} \ge \frac{d}{m - d}$$

Si el margen promedio base es $m \approx 28.8\%$ y se otorga un descuento $d = 20\%$, se requeriría un incremento en unidades de:
$$\frac{\Delta Q}{Q} \ge \frac{0.20}{0.288 - 0.20} = \frac{0.20}{0.088} \approx +227\%$$
"""
)
new_cells.append(md_a2_4)

code_a2_4_calc = nbformat.v4.new_code_cell(
r"""# Segmentación por Tramos de Descuento
bins = [-0.001, 0.001, 0.05, 0.10, 0.15, 0.20, 1.0]
labels = ['0% (Sin desc.)', '1% - 5%', '6% - 10%', '11% - 15%', '16% - 20%', '> 20%']
df_trx['tramo_descuento'] = pd.cut(df_trx['descuento'], bins=bins, labels=labels)

tramos_desc = df_trx.groupby('tramo_descuento', observed=True).agg(
    transacciones=('transaccion_id', 'count'),
    unidades_promedio=('cantidad', 'mean'),
    ticket_promedio=('monto_neto', 'mean'),
    ingreso_total=('monto_neto', 'sum'),
    margen_total=('margen_bruto', 'sum'),
    ventas_bajo_costo=('venta_bajo_costo', 'sum')
).reset_index()

tramos_desc['margen_pct'] = (tramos_desc['margen_total'] / tramos_desc['ingreso_total']) * 100
tramos_desc['pct_transacciones'] = (tramos_desc['transacciones'] / len(df_trx)) * 100

print("COMPORTAMIENTO OPERATIVO POR TRAMO DE DESCUENTO:")
display(tramos_desc[['tramo_descuento', 'transacciones', 'pct_transacciones', 'unidades_promedio', 
                     'ticket_promedio', 'margen_pct', 'ventas_bajo_costo']].round(2))
"""
)
new_cells.append(code_a2_4_calc)

code_a2_4_plot = nbformat.v4.new_code_cell(
r"""# Gráfica de Destrucción de Margen vs Inelasticidad del Volumen
fig, ax1 = plt.subplots(figsize=(10, 5))

x = np.arange(len(tramos_desc))
color_margen = '#D62728'
color_unid = '#1F77B4'

# Margen % (eje izquierdo)
bars = ax1.bar(x - 0.15, tramos_desc['margen_pct'], width=0.3, color=color_margen, label='Margen Bruto (%)')
ax1.set_ylabel('Margen Bruto Real (%)', color=color_margen, fontsize=11, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=color_margen)
ax1.set_xticks(x)
ax1.set_xticklabels(tramos_desc['tramo_descuento'], fontsize=10)
ax1.set_ylim(0, 35)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Unidades por canasta (eje derecho)
ax2 = ax1.twinx()
lines = ax2.plot(x + 0.15, tramos_desc['unidades_promedio'], color=color_unid, marker='o', lw=2.5, label='Unidades Promedio / Canasta')
ax2.set_ylabel('Unidades por Ticket', color=color_unid, fontsize=11, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color_unid)
ax2.set_ylim(1.0, 2.5)

# Títulos y anotaciones
plt.title('Destrucción de Margen por Descuento vs. Demanda Inelástica', fontsize=12, fontweight='bold', pad=12)

for bar in bars:
    yval = bar.get_height()
    ax1.annotate(f'{yval:.1f}%', xy=(bar.get_x() + bar.get_width()/2, yval),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

for i, txt in enumerate(tramos_desc['unidades_promedio']):
    ax2.annotate(f'{txt:.2f} un.', xy=(x[i] + 0.15, txt),
                 xytext=(0, 6), textcoords="offset points", ha='center', va='bottom', fontsize=9, color=color_unid, fontweight='bold')

plt.tight_layout()
plt.show()
"""
)
new_cells.append(code_a2_4_plot)

md_a2_4_bajo_costo = nbformat.v4.new_markdown_cell(
r"""### Auditoría de Ventas Bajo Costo (`venta_bajo_costo`)
En la limpieza y enriquecimiento de datos de A1 se identificaron **711 transacciones donde el ingreso neto fue inferior al costo total de adquisición del producto**.
Esto se debió exclusivamente a descuentos excesivos combinados con productos de bajo margen natural.
"""
)
new_cells.append(md_a2_4_bajo_costo)

code_a2_4_bajo_costo = nbformat.v4.new_code_cell(
r"""# Auditoría y concentración de ventas bajo costo
v_bajo_costo = df_trx[df_trx['venta_bajo_costo'] == True]

perdida_total = v_bajo_costo['margen_bruto'].sum()
descuento_medio_vbc = v_bajo_costo['descuento'].mean() * 100

resumen_vbc = v_bajo_costo.groupby('canal').agg(
    transacciones=('transaccion_id', 'count'),
    perdida_total=('margen_bruto', 'sum'),
    ingreso_neto=('monto_neto', 'sum'),
    descuento_prom=('descuento', lambda s: s.mean() * 100)
).reset_index()

resumen_vbc['%_de_las_ventas_negativas'] = (resumen_vbc['transacciones'] / len(v_bajo_costo)) * 100

print(f"Total transacciones bajo costo: {len(v_bajo_costo):,} ({len(v_bajo_costo)/len(df_trx)*100:.2f}% del total)")
print(f"Pérdida acumulada directa en margen: ${perdida_total:,.2f} USD")
print(f"Descuento promedio en ventas bajo costo: {descuento_medio_vbc:.1f}%")
print("\nDistribución de Ventas Bajo Costo por Canal:")
display(resumen_vbc.round(2))
"""
)
new_cells.append(code_a2_4_bajo_costo)

# ==========================================
# SECCIÓN 14: TABLA MAESTRA RESUMEN PARA A5
# ==========================================
md_a2_summary = nbformat.v4.new_markdown_cell(
r"""---
## Resumen Ejecutivo de A2 (Métricas Clave para el Dashboard A5)

A continuación se consolidan las métricas directrices de rentabilidad requeridas para gobernar los filtros e indicadores del tablero gerencial de A5:
"""
)
new_cells.append(md_a2_summary)

code_a2_summary = nbformat.v4.new_code_cell(
r"""# Tabla resumen ejecutivo para la entrega y dashboard A5
m_fisica = canal_summary.loc[canal_summary['canal'] == 'tienda_fisica', 'margen_pct_real'].values[0]
m_online = canal_summary.loc[canal_summary['canal'] == 'online', 'margen_pct_real'].values[0]
delta_inactivo = resumen_ticket.loc['Inactivo', 'Variación Interanual (%)']

resumen_a2 = pd.DataFrame({
    'Dimensión / Métrica': [
        'Ingresos Netos Totales',
        'Margen Bruto Total',
        'Margen Bruto (%)',
        'Margen Neto de Devoluciones Total',
        'Margen Neto de Devoluciones (%)',
        'Ticket Promedio Global 2023',
        'Ticket Promedio Global 2024',
        'Variación Ticket Global (%)',
        'Caída Ticket Segmento Inactivo (%)',
        'Canal Físico: Margen Bruto (%)',
        'Canal Online: Margen Bruto (%)',
        'Gap de Margen Físico vs Online (p.p.)',
        'Transacciones con Margen Negativo (Bajo Costo)',
        'Pérdida Directa por Ventas Bajo Costo ($)',
        'Concentración Pareto (% Clientes para 80% Margen)',
        'CLV Promedio Segmento Premium (3 Años)',
        'CLV Promedio Segmento Inactivo (3 Años)'
    ],
    'Valor': [
        f"${df_trx['monto_neto'].sum():,.2f}",
        f"${df_trx['margen_bruto'].sum():,.2f}",
        f"{(df_trx['margen_bruto'].sum() / df_trx['monto_neto'].sum())*100:.2f}%",
        f"${df_trx['margen_neto_devol'].sum():,.2f}",
        f"{(df_trx['margen_neto_devol'].sum() / df_trx['monto_neto'].sum())*100:.2f}%",
        f"${df_trx[df_trx['anio']==2023]['monto_neto'].mean():.2f}",
        f"${df_trx[df_trx['anio']==2024]['monto_neto'].mean():.2f}",
        f"{((df_trx[df_trx['anio']==2024]['monto_neto'].mean() - df_trx[df_trx['anio']==2023]['monto_neto'].mean()) / df_trx[df_trx['anio']==2023]['monto_neto'].mean())*100:.2f}%",
        f"{delta_inactivo:.2f}%",
        f"{m_fisica:.2f}%",
        f"{m_online:.2f}%",
        f"{(m_fisica - m_online):.2f} p.p.",
        f"{len(v_bajo_costo):,} tx",
        f"${abs(perdida_total):,.2f}",
        f"{p80_cli_pct:.1f}%",
        f"${clv_seg.loc[clv_seg['segmento']=='Premium', 'clv_3_anios'].values[0]:,.2f}",
        f"${clv_seg.loc[clv_seg['segmento']=='Inactivo', 'clv_3_anios'].values[0]:,.2f}"
    ]
})

print("TABLA CONSOLIDADA EJECUTIVA A2:")
display(resumen_a2)
"""
)
new_cells.append(code_a2_summary)

# Unir celdas base con nuevas celdas
nb.cells = base_cells + new_cells

# Guardar notebook actualizado
nbformat.write(nb, 'notebooks/02_A2_Rentabilidad.ipynb')
print(f"Notebook actualizado con {len(nb.cells)} celdas. Ejecutando con nbclient...")

# Ejecutar notebook completo con el cwd en notebooks/
client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks'}})
client.execute()

# Guardar notebook con salidas renderizadas
nbformat.write(nb, 'notebooks/02_A2_Rentabilidad.ipynb')
print("¡Notebook 02_A2_Rentabilidad.ipynb ejecutado exitosamente con todas las salidas renderizadas!")
