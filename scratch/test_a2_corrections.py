# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

DATA_PATH = Path('data/clean')
transacciones = pd.read_csv(DATA_PATH / 'transacciones_maestra.csv', parse_dates=['fecha'])
clientes = pd.read_csv(DATA_PATH / 'clientes_maestra.csv')

# C7: Ticket Decomposition & Welch Test
transacciones['anio'] = transacciones['fecha'].dt.year
t_2023 = transacciones[transacciones['anio'] == 2023]
t_2024 = transacciones[transacciones['anio'] == 2024]

ticket_2023 = t_2023['monto_neto'].mean()
ticket_2024 = t_2024['monto_neto'].mean()
delta_ticket_pct = ((ticket_2024 - ticket_2023) / ticket_2023) * 100

print(f"--- C7: TICKET PROMEDIO GLOBAL ---")
print(f"Ticket 2023: ${ticket_2023:.2f} (N={len(t_2023):,})")
print(f"Ticket 2024: ${ticket_2024:.2f} (N={len(t_2024):,})")
print(f"Variacion real en microdatos: {delta_ticket_pct:+.2f}% (frente al -8.0% del relato)")

# Welch t-test por segmento
print("\nWelch t-test por segmento:")
for seg in transacciones['segmento'].unique():
    s23 = t_2023.loc[t_2023['segmento'] == seg, 'monto_neto']
    s24 = t_2024.loc[t_2024['segmento'] == seg, 'monto_neto']
    t_stat, p_val = stats.ttest_ind(s24, s23, equal_var=False)
    d_pct = ((s24.mean() - s23.mean()) / s23.mean()) * 100
    print(f"• {seg:10s}: 2023=${s23.mean():.2f} (N={len(s23):,}) -> 2024=${s24.mean():.2f} (N={len(s24):,}) | Delta={d_pct:+.2f}% | p={p_val:.4f}")

# C8: Seasonal Index & Correlation 2023 vs 2024
transacciones['mes'] = transacciones['fecha'].dt.month
m_rev = transacciones.groupby(['anio', 'mes'])['monto_neto'].sum().unstack(level=0)
m_rev['idx_2023'] = m_rev[2023] / m_rev[2023].mean()
m_rev['idx_2024'] = m_rev[2024] / m_rev[2024].mean()
corr_season = m_rev['idx_2023'].corr(m_rev['idx_2024'])
print(f"\n--- C8: ESTACIONALIDAD ---")
print(f"Correlacion del indice estacional entre 2023 y 2024: r = {corr_season:.3f}")

# C10: Counterfactual online margin
onl = transacciones[transacciones['canal'] == 'online']
fis = transacciones[transacciones['canal'] == 'tienda_fisica']
desc_fis_cat = fis.groupby('categoria')['descuento'].mean().to_dict()

onl_curr_rev = onl['monto_neto'].sum()
onl_curr_cost = onl['costo_total'].sum()
onl_curr_margin = onl['margen_bruto'].sum()
onl_curr_pct = onl_curr_margin / onl_curr_rev * 100

onl_cf_desc = onl['categoria'].map(desc_fis_cat)
onl_cf_rev = (onl['precio_unitario'] * onl['cantidad'] * (1 - onl_cf_desc)).sum()
onl_cf_margin = onl_cf_rev - onl_curr_cost
onl_cf_pct = onl_cf_margin / onl_cf_rev * 100
gain_dollars = onl_cf_margin - onl_curr_margin

print(f"\n--- C10: CONTRAFACTUAL ONLINE ---")
print(f"Margen Online actual: {onl_curr_pct:.2f}% (${onl_curr_margin:,.2f})")
print(f"Margen Online contrafactual: {onl_cf_pct:.2f}% (${onl_cf_margin:,.2f})")
print(f"Brecha / Ganancia potencial maxima: +{onl_cf_pct - onl_curr_pct:.2f} pp (${gain_dollars:,.2f})")

# C9: OLS regressions
mod_m = smf.ols('margen_pct_real ~ descuento + C(categoria) + C(canal)', data=transacciones).fit()
mod_u = smf.ols('cantidad ~ descuento + C(categoria) + C(canal)', data=transacciones).fit()

print(f"\n--- C9: REGRESIONES OLS CON CONTROLES ---")
print(f"Efecto de descuento sobre margen %: coef = {mod_m.params['descuento']:.2f} (p = {mod_m.pvalues['descuento']:.4f})")
print(f"Efecto de descuento sobre unidades: coef = {mod_u.params['descuento']:.4f} (p = {mod_u.pvalues['descuento']:.4f})")

# C14: Declining segments 2023 vs 2024
print(f"\n--- C14: SEGMENTOS 2023 vs 2024 ---")
seg_comp = transacciones.groupby(['segmento', 'anio']).agg(
    clientes_activos=('cliente_id', 'nunique'),
    transacciones=('transaccion_id', 'count'),
    margen_total=('margen_bruto', 'sum'),
    ingreso_total=('monto_neto', 'sum')
).reset_index()
seg_comp['frecuencia'] = seg_comp['transacciones'] / seg_comp['clientes_activos']
seg_comp['margen_por_cliente'] = seg_comp['margen_total'] / seg_comp['clientes_activos']
print(seg_comp.round(2).to_string())
