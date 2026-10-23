import nbformat as nbf
from pathlib import Path
from nbclient import NotebookClient

nb_path = Path("notebooks/02_A2_Rentabilidad.ipynb")
nb = nbf.read(nb_path, as_version=4)

new_cells = []

# --- 5. Drill-down por Subcategoría ---
new_cells.append(nbf.v4.new_markdown_cell("""### 5. Drill-down por Subcategoría: Ganadoras vs. Destructoras de Margen

Dentro de cada categoría, no todos los productos aportan igual. Identificamos:
- **Top 5 Subcategorías Ganadoras:** Mayor masa de margen bruto aportada a la empresa.
- **Bottom 5 Subcategorías Menos Rentables:** Productos con baja rotación o margen comprimido.
"""))

new_cells.append(nbf.v4.new_code_cell("""sub_summary = df_trx.groupby(['categoria', 'subcategoria']).agg(
    ingreso_neto=('monto_neto', 'sum'),
    margen_bruto=('margen_bruto', 'sum'),
    margen_pct_real=('margen_pct_real', 'mean'),
    tasa_devolucion=('devuelto', 'mean')
).reset_index()

sub_summary['pct_margen_total'] = (100 * sub_summary['margen_bruto'] / TOTAL_MARGEN).round(2)
sub_summary['tasa_devolucion'] = (100 * sub_summary['tasa_devolucion']).round(2)
sub_summary = sub_summary.sort_values(by='margen_bruto', ascending=False)

top5 = sub_summary.head(5)
bottom5 = sub_summary.tail(5)

print("=== TOP 5 SUBCATEGORÍAS GANADORAS ===")
display(top5[['categoria', 'subcategoria', 'margen_bruto', 'pct_margen_total', 'margen_pct_real', 'tasa_devolucion']])

print("\\n=== BOTTOM 5 SUBCATEGORÍAS MENOS RENTABLES ===")
display(bottom5[['categoria', 'subcategoria', 'margen_bruto', 'pct_margen_total', 'margen_pct_real', 'tasa_devolucion']])
"""))

new_cells.append(nbf.v4.new_code_cell("""# Gráfico comparativo Top 5 vs Bottom 5
fig, ax = plt.subplots(figsize=(10, 5))

top_bottom = pd.concat([top5, bottom5]).sort_values(by='margen_bruto', ascending=True)
colors = ['#E74C3C' if x in bottom5['subcategoria'].values else '#2ECC71' for x in top_bottom['subcategoria']]

ax.barh(top_bottom['subcategoria'], top_bottom['margen_bruto'] / 1000, color=colors)
ax.set_xlabel('Margen Bruto (Miles de USD)')
ax.set_title('Top 5 Subcategorías Ganadoras (Verde) vs. Menos Rentables (Rojo)', fontsize=13, fontweight='bold')

for p in ax.patches:
    width = p.get_width()
    ax.annotate(f"${width:,.1f}k", (width + 5, p.get_y() + p.get_height()/2.),
                va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()
"""))

# --- 6. Rentabilidad Territorial por Ciudad ---
new_cells.append(nbf.v4.new_markdown_cell("""### 6. Rentabilidad Territorial: Margen por Ciudad

Analizamos la concentración geográfica de la rentabilidad:
- ¿El margen varía por plaza o es uniforme?
- ¿Dónde se concentra el riesgo operativo de la empresa?
"""))

new_cells.append(nbf.v4.new_code_cell("""ciu_summary = tabla_contribucion(df_trx, 'ciudad')
display(ciu_summary[['ciudad', 'ingreso_neto', 'pct_ingreso', 'margen_bruto', 'pct_margen', 'margen_pct_real', 'descuento_promedio']])
"""))

new_cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(9, 4))
ax = sns.barplot(data=ciu_summary, x='ciudad', y='pct_margen', palette='Greens_r')
plt.title('Concentración del Margen Bruto por Ciudad (%)', fontsize=12, fontweight='bold')
plt.ylabel('% del Margen Total')
plt.xlabel('Ciudad')
plt.xticks(rotation=20, ha='right')

for p in ax.patches:
    ax.annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.8),
                ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.ylim(0, ciu_summary['pct_margen'].max() + 5)
plt.tight_layout()
plt.show()
"""))

# --- 7. Curva de Concentración de Clientes (Pareto 80/20) ---
new_cells.append(nbf.v4.new_markdown_cell("""### 7. Concentración de Clientes: Curva de Pareto (80/20)

Evaluamos el principio de Pareto a nivel individual de cliente:
- ¿Qué porcentaje de los clientes explica el 80% del margen bruto de la empresa?
- Respaldo cuantitativo para priorizar la retención de clientes clave (conecta directo con A3 - Churn).
"""))

new_cells.append(nbf.v4.new_code_cell("""cli_margen = df_trx.groupby('cliente_id')['margen_bruto'].sum().sort_values(ascending=False).reset_index()
cli_margen['margen_acumulado'] = cli_margen['margen_bruto'].cumsum()
cli_margen['pct_margen_acum'] = 100 * cli_margen['margen_acumulado'] / TOTAL_MARGEN
cli_margen['pct_clientes'] = 100 * (cli_margen.index + 1) / len(cli_margen)

# Puntos clave
p20_val = cli_margen[cli_margen['pct_clientes'] <= 20]['pct_margen_acum'].iloc[-1]
p80_idx = (cli_margen['pct_margen_acum'] >= 80).idxmax()
p80_cli_pct = cli_margen.loc[p80_idx, 'pct_clientes']

print(f"Hallazgo Pareto:")
print(f"• El 20% de los clientes genera el {p20_val:.1f}% del margen bruto total.")
print(f"• El 80% del margen total es generado por solo el {p80_cli_pct:.1f}% de la base de clientes.")
"""))

new_cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(8, 5))
plt.plot(cli_margen['pct_clientes'], cli_margen['pct_margen_acum'], color='#1F77B4', lw=2.5, label='Curva Real de Margen')
plt.plot([0, 100], [0, 100], color='gray', linestyle='--', label='Distribución Equitativa (Diagonal)')

# Marcar punto 80% del margen
plt.axhline(80, color='#E74C3C', linestyle=':', lw=1.5)
plt.axvline(p80_cli_pct, color='#E74C3C', linestyle=':', lw=1.5)
plt.scatter([p80_cli_pct], [80], color='#E74C3C', s=70, zorder=5)

plt.annotate(f"80% Margen = {p80_cli_pct:.1f}% Clientes",
             xy=(p80_cli_pct, 80), xytext=(p80_cli_pct + 10, 72),
             arrowprops=dict(arrowstyle="->", color='#E74C3C', lw=1.5),
             fontweight='bold', color='#C0392B')

plt.title('Curva de Lorenz / Pareto: Concentración del Margen en Clientes', fontsize=12, fontweight='bold')
plt.xlabel('% Acumulado de Clientes')
plt.ylabel('% Acumulado de Margen Bruto')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()
"""))

# Insertar antes de la celda de A2.2 (CLV)
# Localizamos el índice de la celda que tiene '## A2.2'
idx_a2_2 = 14
for i, c in enumerate(nb.cells):
    src = c.source if isinstance(c.source, str) else "".join(c.source)
    if "## A2.2" in src:
        idx_a2_2 = i
        break

print(f"Insertando {len(new_cells)} celdas antes de la celda {idx_a2_2}...")
nb.cells = nb.cells[:idx_a2_2] + new_cells + nb.cells[idx_a2_2:]

# Guardar
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook actualizado exitosamente en {nb_path}.")

# Ejecutar con nbclient para regenerar outputs
print("Ejecutando notebook para validar outputs...")
client = NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": "notebooks"}})
client.execute()

with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("¡Notebook ejecutado y validado con éxito de punta a punta!")
