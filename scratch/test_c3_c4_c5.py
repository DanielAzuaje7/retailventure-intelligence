# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

DATA_PATH = Path('data/clean')
campanas = pd.read_csv(DATA_PATH / 'campanas_limpia.csv', parse_dates=['fecha_envio'])
clientes = pd.read_csv(DATA_PATH / 'clientes_maestra.csv')
transacciones = pd.read_csv(DATA_PATH / 'transacciones_maestra.csv', parse_dates=['fecha'])

# C3: Chi-squared test on CRM complaints
camp_cli = campanas.groupby('cliente_id').agg(
    impactos_totales=('campana_id', 'count'),
    conversiones_totales=('convertido', 'sum')
).reset_index()

cli_mkt = clientes.merge(camp_cli, on='cliente_id', how='inner')
cli_mkt['convirtio'] = cli_mkt['conversiones_totales'] > 0
cli_mkt['tiene_quejas'] = cli_mkt['n_quejas'] > 0

ct = pd.crosstab(cli_mkt['convirtio'], cli_mkt['tiene_quejas'])
chi2, p_val, dof, ex = stats.chi2_contingency(ct)
print('--- C3: TEST DE CHI-CUADRADO EN QUEJAS CRM ---')
print(ct)
print(f'Chi2: {chi2:.4f}, p-value: {p_val:.4f}')

# C4: Logistic Regression
print('\n--- C4: LOGISTIC REGRESSION ---')
logit_mod = smf.logit('convertido ~ descuento_ofrecido + C(segmento) + C(tipo_campana)', data=campanas).fit(disp=False)
or_df = pd.DataFrame({
    'Odds Ratio': np.exp(logit_mod.params),
    'CI 2.5%': np.exp(logit_mod.conf_int()[0]),
    'CI 97.5%': np.exp(logit_mod.conf_int()[1]),
    'p-value': logit_mod.pvalues
})
print(or_df.round(3).to_string())

# Contrast 25% vs 20%
# Calculate conversion rate and count at 20% and 25% for Esporadico and Overall
c_20 = campanas[campanas['descuento_ofrecido'] == 0.20]
c_25 = campanas[campanas['descuento_ofrecido'] == 0.25]
print(f"\nOverall: 20% conv = {c_20['convertido'].mean()*100:.2f}% (N={len(c_20)}) vs 25% conv = {c_25['convertido'].mean()*100:.2f}% (N={len(c_25)})")

# C5: P(compra 30d | convertido=1) vs P(compra 30d | convertido=0)
print('\n--- C5: CALIDAD DEL FLAG ---')
# Let's see: for each campaign, did client buy in 30d?
camp_elegible = campanas[campanas['fecha_envio'] < '2024-12-01'].copy()
tx_por_cliente = {cli: g['fecha'].values for cli, g in transacciones.groupby('cliente_id')}
post_b = []
for _, r in camp_elegible.iterrows():
    f0 = np.datetime64(r['fecha_envio'])
    f1 = np.datetime64(r['fecha_envio'] + pd.Timedelta(days=30))
    tx = tx_por_cliente.get(r['cliente_id'])
    post_b.append(np.any((tx >= f0) & (tx <= f1)) if tx is not None else False)

camp_elegible['compro_30d'] = post_b
p1 = camp_elegible.loc[camp_elegible['convertido']==1, 'compro_30d'].mean() * 100
p0 = camp_elegible.loc[camp_elegible['convertido']==0, 'compro_30d'].mean() * 100
print(f'P(compra 30d | convertido=1): {p1:.2f}%')
print(f'P(compra 30d | convertido=0): {p0:.2f}%')
