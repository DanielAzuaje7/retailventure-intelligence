# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

DATA_PATH = Path('data/clean')
transacciones = pd.read_csv(DATA_PATH / 'transacciones_maestra.csv', parse_dates=['fecha'])
devoluciones_raw = pd.read_csv(DATA_PATH / 'devoluciones_limpia.csv')

# C11: Devoluciones por producto (N >= 30)
transacciones['es_devolucion'] = transacciones['estado'] == 'devuelto'
prod_agg = transacciones.groupby(['producto', 'categoria']).agg(
    n_tx=('transaccion_id', 'count'),
    n_dev=('es_devolucion', 'sum'),
    monto_dev=('monto_neto', lambda s: s[transacciones.loc[s.index, 'es_devolucion']].sum())
).reset_index()

prod_30 = prod_agg[prod_agg['n_tx'] >= 30].copy()
prod_30['tasa_dev'] = prod_30['n_dev'] / prod_30['n_tx']

# Category baseline rates
cat_rates = transacciones.groupby('categoria')['es_devolucion'].mean().to_dict()
prod_30['tasa_cat'] = prod_30['categoria'].map(cat_rates)

# Binomial test against category rate
p_vals = []
for _, r in prod_30.iterrows():
    res = stats.binomtest(r['n_dev'], r['n_tx'], r['tasa_cat'], alternative='greater')
    p_vals.append(res.pvalue)

prod_30['p_valor'] = p_vals
reject, p_adj, _, _ = multipletests(prod_30['p_valor'], alpha=0.05, method='fdr_bh')
prod_30['p_ajustado'] = p_adj
prod_30['es_anomalo'] = reject

print(f"Total productos con >= 30 tx: {len(prod_30)}")
print(f"Productos con exceso anomalos significativos (FDR < 0.05): {prod_30['es_anomalo'].sum()}")
print("Top 5 por tasa de devolucion:")
print(prod_30.sort_values('tasa_dev', ascending=False).head(5)[['producto', 'categoria', 'n_tx', 'n_dev', 'tasa_dev', 'tasa_cat', 'p_valor', 'p_ajustado']].to_string())

# C12: Clientes recurrentes en devoluciones
p_global = transacciones['es_devolucion'].mean() # 13.45%
cli_dev = transacciones.groupby('cliente_id').agg(
    compras=('transaccion_id', 'count'),
    devs=('es_devolucion', 'sum')
).reset_index()

cli_dev['p_binom'] = [stats.binom.sf(k - 1, n, p_global) for k, n in zip(cli_dev['devs'], cli_dev['compras'])]
cli_dev['es_anomalo'] = cli_dev['p_binom'] < 0.01

print(f"\n--- C12: MODELO BINOMIAL CLIENTES RECURRENTES (p={p_global*100:.2f}%) ---")
print(f"Total clientes con compras: {len(cli_dev):,}")
print(f"Clientes con >= 2 devoluciones: {(cli_dev['devs'] >= 2).sum():,} (azar predice aprox 1,700)")
print(f"Clientes verdaderamente anómalos (p < 0.01): {cli_dev['es_anomalo'].sum():,}")

# C13: Tendencia trimestral y motivos por categoría
transacciones['trimestre'] = transacciones['fecha'].dt.to_period('Q').astype(str)
trend_trim = transacciones.groupby('trimestre').agg(
    n_tx=('transaccion_id', 'count'),
    n_dev=('es_devolucion', 'sum')
).reset_index()
trend_trim['tasa'] = (trend_trim['n_dev'] / trend_trim['n_tx']) * 100
ci = [proportion_confint(k, n, method='wilson') for k, n in zip(trend_trim['n_dev'], trend_trim['n_tx'])]
trend_trim['ic_95'] = [f"[{l*100:.2f}%, {u*100:.2f}%]" for l, u in ci]

print("\n--- C13: TENDENCIA TRIMESTRAL DE DEVOLUCIONES ---")
print(trend_trim[['trimestre', 'n_tx', 'n_dev', 'tasa', 'ic_95']].to_string())

# Motivos de devolución por categoría (en devoluciones_limpia)
print("\n--- MOTIVOS DE DEVOLUCIÓN POR CATEGORÍA ---")
if 'motivo' in devoluciones_raw.columns and 'categoria' in devoluciones_raw.columns:
    print(pd.crosstab(devoluciones_raw['categoria'], devoluciones_raw['motivo'], normalize='index').round(3) * 100)
else:
    print("Columnas en devoluciones_raw:", devoluciones_raw.columns.tolist())
