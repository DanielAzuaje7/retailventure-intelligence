# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

DATA_PATH = Path('data/clean')
clientes = pd.read_csv(DATA_PATH / 'clientes_maestra.csv')
crm = pd.read_csv(DATA_PATH / 'crm_limpio.csv', parse_dates=['fecha'])
transacciones = pd.read_csv(DATA_PATH / 'transacciones_maestra.csv', parse_dates=['fecha'])

# Decision D2: NO_RESUELTAS = {'sin_resolver', 'escalado'}
NO_RESUELTAS = {'sin_resolver', 'escalado'}
quejas = crm[crm['tipo'] == 'queja'].copy()
quejas['no_resuelta'] = quejas['resolucion'].isin(NO_RESUELTAS)

# Exclude edge-truncated complaints (first 60 days of 2023 and last 60 days of 2024)
quejas_validas = quejas[(quejas['fecha'] >= '2023-03-01') & (quejas['fecha'] <= '2024-10-31')].copy()
print(f"Quejas totales: {len(quejas)}, Quejas en ventana no truncada: {len(quejas_validas)}")

# Frequency before and after each complaint (60 days)
tx_por_cli = {cli: g['fecha'].values for cli, g in transacciones.groupby('cliente_id')}

pre_freq, post_freq = [], []
for _, r in quejas_validas.iterrows():
    c = r['cliente_id']
    f0 = np.datetime64(r['fecha'])
    f_pre = np.datetime64(r['fecha'] - pd.Timedelta(days=60))
    f_post = np.datetime64(r['fecha'] + pd.Timedelta(days=60))
    tx = tx_por_cli.get(c)
    if tx is not None:
        pre_freq.append(np.sum((tx >= f_pre) & (tx < f0)))
        post_freq.append(np.sum((tx >= f0) & (tx <= f_post)))
    else:
        pre_freq.append(0); post_freq.append(0)

quejas_validas['pre_freq'] = pre_freq
quejas_validas['post_freq'] = post_freq
quejas_validas['delta_freq'] = quejas_validas['post_freq'] - quejas_validas['pre_freq']

did_resumen = quejas_validas.groupby('no_resuelta').agg(
    n_quejas=('interaccion_id', 'count'),
    pre_freq=('pre_freq', 'mean'),
    post_freq=('post_freq', 'mean'),
    delta_freq=('delta_freq', 'mean')
).reset_index()

d_resueltas = did_resumen.loc[did_resumen['no_resuelta']==False, 'delta_freq'].values[0]
d_no_resueltas = did_resumen.loc[did_resumen['no_resuelta']==True, 'delta_freq'].values[0]
did_est = d_no_resueltas - d_resueltas

print("\n--- C6: DID FRECUENCIA PRE/POST QUEJA (VENTANA 60D) ---")
print(did_resumen)
print(f"Delta Resueltas: {d_resueltas:.4f}")
print(f"Delta No Resueltas: {d_no_resueltas:.4f}")
print(f"Estimador DiD (No Resuelta vs Resuelta): {did_est:+.4f}")

# Bootstrap CI for DiD by client
np.random.seed(42)
b_did = []
u_clis = quejas_validas['cliente_id'].unique()
for _ in range(1000):
    idx = np.random.choice(u_clis, size=len(u_clis), replace=True)
    samp = quejas_validas[quejas_validas['cliente_id'].isin(idx)]
    m_nr = samp.loc[samp['no_resuelta']==True, 'delta_freq'].mean()
    m_r = samp.loc[samp['no_resuelta']==False, 'delta_freq'].mean()
    b_did.append(m_nr - m_r)

ic_did = np.percentile(b_did, [2.5, 97.5])
t_stat, p_val = stats.ttest_ind(
    quejas_validas.loc[quejas_validas['no_resuelta']==True, 'delta_freq'],
    quejas_validas.loc[quejas_validas['no_resuelta']==False, 'delta_freq']
)
print(f"IC 95% Bootstrap DiD: [{ic_did[0]:.4f}, {ic_did[1]:.4f}] (Incluye 0: {ic_did[0] <= 0 <= ic_did[1]})")
print(f"t-test p-value: {p_val:.4f}")

# Churn risk crossover (10% of at-risk clients have complaints vs not at-risk)
print("\n--- CHURN RISK CROSSOVER ---")
cli_quejas_count = crm[crm['tipo']=='queja'].groupby('cliente_id').size()
clientes['tiene_queja'] = clientes['cliente_id'].isin(cli_quejas_count.index)
clientes['en_riesgo_churn'] = clientes['recencia_dias'] >= 127

ct_churn = pd.crosstab(clientes['en_riesgo_churn'], clientes['tiene_queja'])
chi2_c, p_val_c, _, _ = stats.chi2_contingency(ct_churn)
prop_en_riesgo = ct_churn.loc[True, True] / ct_churn.loc[True].sum() * 100
prop_no_riesgo = ct_churn.loc[False, True] / ct_churn.loc[False].sum() * 100
print(ct_churn)
print(f"Prop en riesgo (recencia >= 127d) con quejas: {prop_en_riesgo:.2f}%")
print(f"Prop no riesgo (recencia < 127d) con quejas: {prop_no_riesgo:.2f}%")
print(f"Chi2: {chi2_c:.4f}, p-val: {p_val_c:.4f}")
