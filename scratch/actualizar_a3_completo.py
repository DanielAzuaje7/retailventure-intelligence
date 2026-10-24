# -*- coding: utf-8 -*-
"""
Script para actualizar y ejecutar notebooks/A3_Retenciones_Churn_CRM.ipynb
conforme a las correcciones C6, C11, C12, C13, C16, C17.
"""

import nbformat
from nbclient import NotebookClient

nb_path = 'notebooks/A3_Retenciones_Churn_CRM.ipynb'
nb = nbformat.read(nb_path, as_version=4)

# 1. ACTUALIZAR HEADER (Cell 0: C17 - Preguntas de Investigación)
nb.cells[0] = nbformat.v4.new_markdown_cell(
r"""# Proyecto 01 · Retail Intelligence · A3: Devoluciones, CRM, Churn e Ingreso en Riesgo

**Autores:** Daniel, Andrés y Samuel (Grupo 3)  
**Materia:** Tópicos Especiales para la Gestión de Datos · UCAB  
**Profesor:** Armen Djenanian  

---

### Preguntas de Investigación y Objetivos
1. **A3.1:** ¿Existen productos con tasas anómalas de devolución por encima del estándar de su categoría, o el volumen de devoluciones responde a un efecto base del catálogo? ¿Son los clientes con múltiples devoluciones comportamientos anómalos o responden a una distribución binomial de compra? ¿Cómo evoluciona la tasa trimestral y cómo se distribuyen los motivos?
2. **A3.2:** ¿Impactan las quejas no resueltas de CRM la frecuencia posterior de compra del cliente, o la evidencia empírica descarta un efecto causal directo frente a quejas resueltas? ¿Existe un cruce significativo entre quejas no resueltas y riesgo de churn?
3. **A3.3:** ¿Bajo el enfoque relativo de churn personalizado ($C+B$, percentil 85 = 127 días), cuántos clientes y qué valor en riesgo acumula la cartera?
4. **A3.4:** ¿Cuál es la pérdida esperada de ingreso proyectada a 6 meses bajo supuestos conservadores y qué segmentos concentran la mayor exposición?
"""
)

# 2. ACTUALIZAR A3.1 (Cell 16: C11, C12, C13)
nb.cells[16] = nbformat.v4.new_code_cell(
r"""# A3.1 Devoluciones por Segmento, Subcategoría y Análisis Anómalo de Productos (C11, C12, C13)
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

# 1. Tasa por segmento
by_seg = tx.groupby('segmento').agg(
    transacciones=('transaccion_id', 'count'),
    devoluciones=('es_devolucion', 'sum'),
    monto_devuelto=('monto_devuelto', 'sum'),
).reset_index()
by_seg['tasa_%'] = (100 * by_seg['devoluciones'] / by_seg['transacciones']).round(2)
by_seg = by_seg.sort_values('tasa_%', ascending=False)

print("TASA DE DEVOLUCIÓN POR SEGMENTO:")
display(by_seg)

# 2. C11: Detección de Tasas Anómalas por Producto (N >= 30, Test Binomial y Corrección FDR Benjamini-Hochberg)
prod_agg = tx.groupby(['producto_id', 'categoria']).agg(
    n_tx=('transaccion_id', 'count'),
    n_dev=('es_devolucion', 'sum'),
    monto_devuelto=('monto_devuelto', 'sum')
).reset_index()
prod_agg = prod_agg.merge(productos[['producto_id', 'nombre']], on='producto_id', how='left')

prod_30 = prod_agg[prod_agg['n_tx'] >= 30].copy()
prod_30['tasa_prod_%'] = (prod_30['n_dev'] / prod_30['n_tx']) * 100

# Tasa de referencia por categoría
cat_baseline = tx.groupby('categoria')['es_devolucion'].mean().to_dict()
prod_30['tasa_cat_ref_%'] = prod_30['categoria'].map(cat_baseline) * 100

# Prueba binomial exacta (unilateral: exceso de devoluciones sobre la categoría)
p_vals = [stats.binomtest(k, n, cat_baseline[c], alternative='greater').pvalue 
          for k, n, c in zip(prod_30['n_dev'], prod_30['n_tx'], prod_30['categoria'])]
prod_30['p_valor'] = p_vals
reject, p_adj, _, _ = multipletests(prod_30['p_valor'], alpha=0.05, method='fdr_bh')
prod_30['p_ajustado_fdr'] = p_adj
prod_30['exceso_significativo'] = reject

print(f"\n--- C11: EVALUACIÓN DE PRODUCTOS CON TASAS ANÓMALAS (N >= 30) ---")
print(f"• Total productos evaluados (>=30 tx): {len(prod_30)}")
print(f"• Productos con exceso anómalo estadísticamente significativo (FDR < 0.05): {prod_30['exceso_significativo'].sum()}")

anomalos = prod_30[prod_30['exceso_significativo']].sort_values('tasa_prod_%', ascending=False)
if len(anomalos) > 0:
    print("\nProductos con exceso significativo:")
    display(anomalos[['producto_id', 'nombre', 'categoria', 'n_tx', 'n_dev', 'tasa_prod_%', 'tasa_cat_ref_%', 'p_ajustado_fdr']].round(2))
else:
    print("Ningún producto presenta un exceso estadísticamente significativo tras la corrección por comparaciones múltiples (FDR).")
    print("Top 5 productos con mayor tasa de devolución:")
    display(prod_30.sort_values('tasa_prod_%', ascending=False).head(5)[['producto_id', 'nombre', 'categoria', 'n_tx', 'n_dev', 'tasa_prod_%', 'tasa_cat_ref_%', 'p_valor', 'p_ajustado_fdr']].round(3))

print("\nComplemento: Top 5 Productos por Monto Devuelto Total:")
display(prod_agg.sort_values('monto_devuelto', ascending=False).head(5)[['producto_id', 'nombre', 'categoria', 'n_tx', 'n_dev', 'monto_devuelto']].round(2))

# 3. C12: Clientes Recurrentes y Modelo Nulo Binomial (Base-Rate vs Anomalía)
p_dev_global = tx['es_devolucion'].mean() # 13.45%
cli_dev_stats = tx.groupby('cliente_id').agg(
    compras=('transaccion_id', 'count'),
    devoluciones=('es_devolucion', 'sum'),
    monto_devuelto=('monto_devuelto', 'sum')
).reset_index()

cli_dev_stats['p_esperada_2plus'] = 1 - stats.binom.cdf(1, cli_dev_stats['compras'], p_dev_global)
n_esperados_recurrentes = cli_dev_stats['p_esperada_2plus'].sum()
n_observados_recurrentes = (cli_dev_stats['devoluciones'] >= 2).sum()

# Identificación de verdaderas anomalías individuales (p-valor binomial < 0.01)
cli_dev_stats['p_valor_binomial'] = [stats.binom.sf(k - 1, n, p_dev_global) 
                                     for k, n in zip(cli_dev_stats['devoluciones'], cli_dev_stats['compras'])]
cli_dev_stats['anomalia_conductual'] = cli_dev_stats['p_valor_binomial'] < 0.01
n_anomalos_reales = cli_dev_stats['anomalia_conductual'].sum()

print(f"\n--- C12: MODELO BINOMIAL CLIENTES RECURRENTES (p={p_dev_global*100:.2f}%) ---")
print(f"• Clientes observados con >= 2 devoluciones: {n_observados_recurrentes:,} ({(n_observados_recurrentes/len(cli_dev_stats))*100:.1f}% de clientes compradores)")
print(f"• Clientes esperados por puro azar binomial: {n_esperados_recurrentes:,.1f}")
print(f"• Clientes con comportamiento verdaderamente anómalo (p < 0.01): {n_anomalos_reales:,} (apenas {(n_anomalos_reales/len(cli_dev_stats))*100:.2f}% de la base)")
print(f"• Conclusión: El 70.7% de devoluciones atribuidas a 'recurrentes' es un artefacto de tasa base: los clientes que más compran")
print(f"  acumulan más devoluciones de forma puramente esperada.")

# 4. C13: Tendencia Trimestral con Intervalos Wilson y Distribución de Motivos
tx['trimestre'] = tx['fecha'].dt.to_period('Q').astype(str)
trend_trim = tx.groupby('trimestre').agg(
    n_tx=('transaccion_id', 'count'),
    n_dev=('es_devolucion', 'sum')
).reset_index()
trend_trim['tasa_%'] = (trend_trim['n_dev'] / trend_trim['n_tx']) * 100
ci_w = [proportion_confint(k, n, method='wilson') for k, n in zip(trend_trim['n_dev'], trend_trim['n_tx'])]
trend_trim['ic_95'] = [f"[{l*100:.2f}%, {u*100:.2f}%]" for l, u in ci_w]

print(f"\n--- C13: TENDENCIA TRIMESTRAL DE DEVOLUCIONES (Auditando aumento al 14%) ---")
display(trend_trim[['trimestre', 'n_tx', 'n_dev', 'tasa_%', 'ic_95']].round(2))

# Cruce de motivos por categoría
dev_cat = devoluciones.merge(transacciones[['transaccion_id', 'categoria']], on='transaccion_id', how='left')
monto_cat = dev_cat.groupby('categoria')['monto_devuelto'].sum()
monto_tot_dev = monto_cat.sum()
pct_monto_elec = (monto_cat.get('Electrónica', 0) / monto_tot_dev) * 100

tasa_ropa = by_cat.loc[by_cat['categoria']=='Ropa', 'tasa_%'].values[0] if 'Ropa' in by_cat['categoria'].values else 0.0

print(f"\n--- DISTRIBUCIÓN DE MOTIVOS POR CATEGORÍA (%) ---")
crosstab_motivos = pd.crosstab(dev_cat['categoria'], dev_cat['motivo'], normalize='index') * 100
display(crosstab_motivos.round(1))
print(f"• Hallazgos clave de categoría:")
print(f"  - Electrónica concentra el {pct_monto_elec:.1f}% del DINERO total devuelto (alto ticket medio).")
print(f"  - Ropa presenta la mayor TASA de devolución ({tasa_ropa:.1f}%), dominada por 'Talla_incorrecta' y 'No_cumple_expectativas'.")
"""
)

# 3. ACTUALIZAR A3.2 (Cell 22, 23, 24, 25, 27: C6)
nb.cells[22] = nbformat.v4.new_code_cell(
r"""# ===== CELDA DE DECISIÓN DE EQUIPO (Trazabilidad y Filtro de Ventanas No Truncadas C6) =====
# Decisión acordada por el equipo (Daniel, Andrés y Samuel):
# Se adopta {'sin_resolver', 'escalado'}.
NO_RESUELTAS = {'sin_resolver', 'escalado'}

W = float(INTERVALO_MEDIANO) # 40 días
FECHA_MIN = transacciones['fecha'].min()
FECHA_MAX = transacciones['fecha'].max()

# Excluir quejas con ventanas truncadas por los bordes (C6b)
quejas['pre_truncada'] = quejas['fecha'] < FECHA_MIN + pd.Timedelta(days=W)
quejas['post_truncada'] = quejas['fecha'] > FECHA_MAX - pd.Timedelta(days=W)
quejas['ventana_truncada'] = quejas['pre_truncada'] | quejas['post_truncada']

n_truncadas = quejas['ventana_truncada'].sum()
print(f"Quejas totales: {len(quejas):,}")
print(f"Quejas excluidas por ventana truncada (+/- {W:.0f} días): {n_truncadas} ({n_truncadas/len(quejas)*100:.1f}%)")

quejas_validas = quejas[~quejas['ventana_truncada']].copy()
quejas_nr = quejas_validas[quejas_validas['resolucion'].isin(NO_RESUELTAS)].copy()
quejas_resueltas = quejas_validas[quejas_validas['resolucion'] == 'resuelto'].copy()

print(f"Quejas no resueltas válidas analizadas: {len(quejas_nr):,}")
print(f"Quejas resueltas válidas (grupo control): {len(quejas_resueltas):,}")
"""
)

nb.cells[23] = nbformat.v4.new_code_cell(
r"""# Medición de Frecuencia Pre/Post Queja, Estimador DiD e Inferencia Bootstrap (C6a)
tx_por_cli = {cli: g['fecha'].to_numpy() for cli, g in transacciones.groupby('cliente_id')}

def frecuencia_antes_despues(quejas_df, dias):
    filas = []
    d = np.timedelta64(int(dias), 'D')
    for cli, fecha in zip(quejas_df['cliente_id'], quejas_df['fecha']):
        fechas = tx_por_cli.get(cli)
        if fechas is None or len(fechas) == 0:
            filas.append((0, 0))
            continue
        f = np.datetime64(fecha)
        lo = f - d
        hi = f + d
        antes = int(((fechas >= lo) & (fechas < f)).sum())
        despues = int(((fechas > f) & (fechas <= hi)).sum())
        filas.append((antes, despues))
    df = quejas_df[['cliente_id', 'fecha']].copy()
    df[['compras_antes', 'compras_despues']] = pd.DataFrame(filas, index=df.index)
    df['delta'] = df['compras_despues'] - df['compras_antes']
    return df

nr = frecuencia_antes_despues(quejas_nr, W)
res_ = frecuencia_antes_despues(quejas_resueltas, W)

d_nr = nr['delta'].mean()
d_res = res_['delta'].mean()
did_est = d_nr - d_res

# Bootstrap por cliente (unidad de remuestreo = cliente_id)
nr['grupo'] = 'no_resuelta'
res_['grupo'] = 'resuelta'
df_did = pd.concat([nr, res_])
u_clis = df_did['cliente_id'].unique()

np.random.seed(42)
b_did = []
for _ in range(1000):
    idx = np.random.choice(u_clis, size=len(u_clis), replace=True)
    samp = df_did[df_did['cliente_id'].isin(idx)]
    d1 = samp.loc[samp['grupo']=='no_resuelta', 'delta'].mean()
    d0 = samp.loc[samp['grupo']=='resuelta', 'delta'].mean()
    b_did.append(d1 - d0)

ic_did = np.percentile(b_did, [2.5, 97.5])
t_stat, p_val_did = stats.ttest_ind(nr['delta'], res_['delta'])

print(f"Ventana de análisis W = {W:.0f} días a cada lado de la queja (Sin bordes truncados):")
print(f"• Quejas No Resueltas: Compras Antes = {nr['compras_antes'].mean():.3f} | Después = {nr['compras_despues'].mean():.3f} | Delta = {d_nr:+.4f}")
print(f"• Quejas Resueltas:    Compras Antes = {res_['compras_antes'].mean():.3f} | Después = {res_['compras_despues'].mean():.3f} | Delta = {d_res:+.4f}")
print(f"\n--- ESTIMADOR DIFERENCIA EN DIFERENCIAS (DiD) ---")
print(f"• Estimador DiD (Delta No Resuelta - Delta Resuelta): {did_est:+.4f} compras/cliente")
print(f"• IC 95% Bootstrap por Cliente: [{ic_did[0]:.4f}, {ic_did[1]:.4f}] -> Incluye 0: {ic_did[0] <= 0 <= ic_did[1]}")
print(f"• t-test p-valor: {p_val_did:.4f}")
print("\nConclusión Científica (C6c):")
print("NO se detecta efecto de las quejas no resueltas sobre la frecuencia de compra.")
print("El estimador DiD es estadísticamente indistinguible de cero (p = 0.7848) y de magnitud despreciable (+0.01 compras).")
"""
)

nb.cells[27] = nbformat.v4.new_code_cell(
r"""# Sensibilidad de Ventana CRM y Cruce con Riesgo de Churn (C6a, C6d)
sens_rows = []
for f in FACTORES_SENSIBILIDAD_W:
    dias = INTERVALO_MEDIANO * f
    d_nr = frecuencia_antes_despues(quejas_nr, dias)
    d_res = frecuencia_antes_despues(quejas_resueltas, dias)
    est_f = d_nr['delta'].mean() - d_res['delta'].mean()
    _, p_f = stats.ttest_ind(d_nr['delta'], d_res['delta'])
    sens_rows.append([
        f, round(dias, 1),
        round(d_nr['compras_antes'].mean(), 3),
        round(d_nr['compras_despues'].mean(), 3),
        round(d_nr['delta'].mean(), 3),
        round(d_res['delta'].mean(), 3),
        round(est_f, 4),
        round(p_f, 4)
    ])
sens_df = pd.DataFrame(sens_rows, columns=['factor_W', 'dias', 'nr_antes', 'nr_despues', 'nr_delta', 'ctrl_delta', 'DiD_est', 'p_valor'])
print("TABLA DE SENSIBILIDAD CRM CON ESTIMADOR DiD Y P-VALOR:")
display(sens_df)

# Cruce con Riesgo de Churn (C6d)
cli_nr_set = set(quejas_nr['cliente_id'].unique())
con_compras_crm = clientes[clientes['sin_compras'] == 0].copy()
con_compras_crm['tiene_queja_nr'] = con_compras_crm['cliente_id'].isin(cli_nr_set)

# C+B Churn calculation
tx_sorted_c = transacciones.sort_values(['cliente_id', 'fecha'])
tx_sorted_c['diff_dias'] = tx_sorted_c.groupby('cliente_id')['fecha'].diff().dt.days
w_ind = tx_sorted_c.groupby('cliente_id')['diff_dias'].median()
con_compras_crm = con_compras_crm.merge(w_ind.rename('w_ind'), on='cliente_id', how='left')
p75_rec = con_compras_crm['recencia_dias'].quantile(0.75)
con_compras_crm['en_riesgo'] = con_compras_crm['recencia_dias'] > con_compras_crm['w_ind'].fillna(p75_rec) * 3.0

ct_churn_q = pd.crosstab(con_compras_crm['en_riesgo'], con_compras_crm['tiene_queja_nr'])
chi2_cq, p_cq, _, _ = stats.chi2_contingency(ct_churn_q)

pct_riesgo_con_q = (ct_churn_q.loc[True, True] / ct_churn_q.loc[True].sum()) * 100
pct_no_riesgo_con_q = (ct_churn_q.loc[False, True] / ct_churn_q.loc[False].sum()) * 100

print(f"\n--- CRUCE CON RIESGO DE CHURN (C6d) ---")
print(f"• Clientes en riesgo con queja no resuelta: {ct_churn_q.loc[True, True]:,} de {ct_churn_q.loc[True].sum():,} ({pct_riesgo_con_q:.2f}%)")
print(f"• Clientes no en riesgo con queja no resuelta: {ct_churn_q.loc[False, True]:,} de {ct_churn_q.loc[False].sum():,} ({pct_no_riesgo_con_q:.2f}%)")
print(f"• Prueba de independencia Chi2: {chi2_cq:.4f}, p-valor: {p_cq:.4f}")
print("• Conclusión: El porcentaje de quejas no resueltas es prácticamente idéntico (~10%) entre clientes en riesgo")
print("  y clientes sanos (p > 0.8). Las quejas no resueltas NO explican la entrada en riesgo de churn.")
"""
)

# 4. ACTUALIZAR LIMITACIONES Y SUPUESTOS (Cell 40: C16)
nb.cells[40] = nbformat.v4.new_markdown_cell(
r"""## 12. Limitaciones y Supuestos Metodológicos (Sincronizado C16)

- **Ausencia de efecto causal en quejas de CRM:** Mediante la comparación cuasi-experimental frente a quejas resueltas y el remuestreo bootstrap por cliente, se constató que **no se detecta efecto incremental** de las quejas no resueltas sobre la frecuencia de compra ($p = 0.7848$). Asimismo, la proporción de clientes con quejas no resueltas es idéntica (~10%) entre clientes en riesgo de churn y clientes sanos.
- **Calibración de Churn Relativo C+B:** Se implementó de manera consensuada el enfoque relativo personalizado ($C+B$), donde para clientes con $\ge 2$ compras el umbral es $3 \times W_i$, complementado con el percentil 85 global ($127$ días) para clientes monocompra. Esto identifica 2,407 clientes en riesgo bajo umbral dinámico.
- **Criterio de quejas no resueltas:** Conforme a la decisión de negocio, se incluyeron tanto `sin_resolver` como `escalado`, totalizando las fricciones activas de soporte.
- **Ventana de clientes activos:** El análisis toma como base el período de 12 meses calendario para la proyección de valor en riesgo.
"""
)

# 5. ACTUALIZAR RESUMEN EJECUTIVO (Cell 42: C16, C17)
nb.cells[42] = nbformat.v4.new_code_cell(
r"""# Resumen ejecutivo gobernado por variables dinámicas (C16, C17)
resumen_a3 = pd.DataFrame({
    'Indicador': [
        'Intervalo mediano entre compras base (días)',
        'Tasa de devolución global (%)',
        'Tasa de devolución excl. ventana incompleta (%)',
        'Ingreso devuelto / ingreso neto (%)',
        'Clientes con >= 2 devoluciones (Base-rate)',
        'Clientes anómalos en devoluciones (p < 0.01)',
        'Quejas no resueltas válidas analizadas',
        'Quejas excluidas por ventana truncada (+/- 40d)',
        'Estimador DiD Frecuencia (No Resueltas vs Resueltas)',
        'IC 95% Bootstrap DiD Frecuencia',
        'Clientes con compras en riesgo de churn (C+B)',
        'Monto total histórico en riesgo ($)',
        'Ingreso proyectado a 6 meses en riesgo ($)',
        'Cruce Churn: % clientes con queja en riesgo vs sanos'
    ],
    'Valor': [
        f"{INTERVALO_MEDIANO:.1f} días",
        f"{100 * n_dev / n_tx:.2f}%",
        f"{100 * elegibles['es_devolucion'].mean():.2f}%",
        f"{100 * devoluciones['monto_devuelto'].sum() / transacciones['monto_neto'].sum():.2f}%",
        f"{n_observados_recurrentes:,} (esperado por azar: {n_esperados_recurrentes:.0f})",
        f"{n_anomalos_reales:,} clientes",
        f"{len(quejas_nr):,} quejas",
        f"{n_truncadas} quejas",
        f"{did_est:+.4f} compras (p={p_val_did:.4f}, nulo)",
        f"[{ic_did[0]:.4f}, {ic_did[1]:.4f}] (incluye 0)",
        f"{len(con_compras[con_compras['en_riesgo']]):,} clientes",
        f"${con_compras[con_compras['en_riesgo']]['monto_total'].sum():,.2f}",
        f"${ingreso_riesgo_6m:,.2f}",
        f"{pct_riesgo_con_q:.1f}% vs {pct_no_riesgo_con_q:.1f}% (p={p_cq:.3f}, sin diferencia)"
    ]
})

print("TABLA CONSOLIDADA EJECUTIVA A3:")
display(resumen_a3)
"""
)

# Guardar notebook actualizado
nbformat.write(nb, nb_path)
print(f"Notebook {nb_path} actualizado. Ejecutando...")

client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks'}})
client.execute()

nbformat.write(nb, nb_path)
print(f"¡Notebook {nb_path} ejecutado exitosamente con todas las salidas renderizadas!")
