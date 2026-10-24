# Definiciones de Métricas del Negocio (v2.0)

> **Estado: CONSENSO TÉCNICO Y CONTRATO DE MÉTRICAS (A2, A3, A4)**  
> Documento unificado a partir de la propuesta inicial de Daniel y las observaciones metodológicas de A3.  
> Garantiza que los tres análisis y el dashboard hablen el mismo idioma sin duplicaciones ni contradicciones.

---

## 1. El Marco Conceptual: Árbol de Métricas

Para evitar métricas aisladas o de vanidad, todo el análisis se articula bajo la descomposición del Margen Neto:

```
Margen Neto (Objetivo Gerencial)
├── (+) Ingreso Neto = Clientes Activos × Frecuencia × Ticket Promedio
│     ├── Clientes Activos  ◄── Se erosionan por CHURN (A3)
│     ├── Frecuencia        ◄── Impactada por quejas no resueltas de CRM (A3)
│     └── Ticket Promedio   ◄── Precio × (1 − Descuento aplicado) (A2)
├── (−) Costo de Mercancía  ◄── Define el Margen Bruto % según categoría y canal (A2)
├── (−) Devoluciones        ◄── Fuga directa de ingresos y margen (A3)
└── (−) Costo Comercial     ◄── Descuentos promocionales y ROI de Campañas (A4)
```

---

## 2. Diccionario Oficial de Métricas

### 2.1 Rentabilidad y Ventas (`clean.transacciones`)

| Métrica | Definición / Fórmula | Columna(s) | Áreas que la usan |
|---|---|---|---|
| **Ingreso Bruto** | `Σ (cantidad × precio_unitario)` | `ingreso_bruto` | A2 |
| **Ingreso Neto** | `Σ monto_neto` (Venta real facturada tras aplicar descuento) | `monto_neto` | **Todos** (Métrica canónica de facturación) |
| **Descuento Aplicado** | Porcentaje de descuento efectivo en la transacción | `descuento` | A2 |
| **Monto Descuento** | `Σ (ingreso_bruto − monto_neto)` | `monto_descuento` | A2, A4 |
| **Margen Bruto ($)** | `Σ margen_bruto` (= `monto_neto − (cantidad × costo)`) | `margen_bruto` | A2, A3 |
| **Margen Bruto (%)** | `Σ margen_bruto / Σ monto_neto` (Global de la empresa: 24.78%) | — | A2, A5 |
| **Margen Neto Post-Devol.** | Margen bruto anulado si hubo devolución (`0` si `devuelto=1`) | `margen_neto_devol` | A2 (Control), A3 |
| **Ingreso Neto Final** | `monto_neto − monto_devuelto` | `monto_neto_final` | A3 |
| **Ticket Promedio** | `Σ monto_neto / COUNT(transaccion_id)` | `monto_neto` | A2, A5 |

> ⚠️ **Regla de oro:** No confundir `transacciones.descuento` (descuento que realmente se cobró) con `campanas_marketing.descuento_ofrecido` (descuento que prometía la promoción publicitaria).

---

### 2.2 Clientes, Churn y CLV (`clean.clientes` + `clean.transacciones`)

| Métrica | Definición / Fórmula | Columna(s) | Áreas que la usan |
|---|---|---|---|
| **Clientes Activos** | Clientes con al menos 1 transacción en el periodo evaluado | `cliente_id` | A2, A3 |
| **Antigüedad Real** | Días desde `fecha_alta_efectiva` hasta el corte 2024-12-31 | `antiguedad_dias` | A2 |
| **Recencia** | Días transcurridos desde la última compra hasta 2024-12-31 | `recencia_dias` | A3 |
| **Cadencia de Recompra** | Distribución de días entre compras consecutivas del mismo cliente | — | P50=40d, P75=87d, P85=127d, P90=162d |
| **Cliente en Churn** | Cliente activo con `recencia_dias > N días` (Umbral calibrado) | `recencia_dias` | A2 (CLV), A3 (Fugas) |
| **Tasa de Churn Anual** | Clientes en churn / Total clientes con historial de compra | — | A2, A3 |
| **CLV Histórico** | Margen bruto total acumulado que el cliente ya dejó | `margen_total` | A2, A3 |
| **CLV Estimado (Futuro)** | `Margen Anual Promedio × Vida Esperada (1 / Churn Anual)` | — | A2 (Tope de vida: 3 años) |
| **Fuga Proyectada (6m)** | `(Gasto del cliente en los últimos 12 meses calendario / 12) × 6` | `monto_neto` | A3 (Solo clientes en Churn) |

> 📌 **Regla de Proyección a 6 meses:** Debe dividirse entre los 12 meses calendario completos (no solo los meses con compras), evitando inflar artificialmente la proyección. Para no duplicar fugas, se cruza por `cliente_id` entre Churn y quejas de CRM.

---

### 2.3 Devoluciones y CRM (`clean.devoluciones` + `clean.interacciones_crm`)

| Métrica | Definición / Fórmula | Columna(s) | Áreas que la usan |
|---|---|---|---|
| **Tasa Devolución (Trx)** | `COUNT(devoluciones) / COUNT(transacciones elegibles)` | `devuelto` | A3 (Global: 13.45%) |
| **Tasa Devolución ($)** | `Σ monto_devuelto / Σ monto_neto` | `monto_devuelto` | A3 (Global: 14.57%) |
| **Ventana Incompleta** | Compras con `fecha > 2024-12-01` (aún en plazo legal de 30d) | `ventana_devol_incompleta` | A3 (Excluir o reportar) |
| **Cliente Reincidente** | Cliente con $\ge 2$ devoluciones en su historial | `n_devoluciones` | A3 (1,711 clientes) |
| **Queja No Resuelta** | Interacción tipo queja con `resolucion IN ('sin_resolver', 'escalado')` | `resolucion` | A3 |
| **Impacto de Quejas** | Comparación de compras pre y post queja en ventana simétrica $W$ | `fecha` | A3 (Comparando vs Quejas Resueltas) |

---

### 2.4 Marketing y ROI (`clean.campanas_marketing`)

| Métrica | Definición / Fórmula | Columna(s) | Áreas que la usan |
|---|---|---|---|
| **Conversión Declarada** | % de campañas marcadas `convertido = 1` por la plataforma | `convertido` | A4 (Métrica oficial del caso) |
| **Conversión Validada** | % con compra real trazable del cliente en los 30 días posteriores | `convertido_validado_30d` | A4 (Prueba de robustez ~2%) |
| **Atribución Única (Deduplicada)** | Si un cliente tuvo varias campañas antes de comprar, se atribuye solo a la última | — | A4 (Evita duplicar ingresos) |
| **Exclusión de Cola** | Campañas enviadas después de 2024-12-01 (no tienen 30 días de observación) | `fecha_envio` | A4 (358 campañas fuera) |
| **Costo Implícito Descuento** | `descuento_ofrecido × monto_compra_30d` (en campañas convertidas) | — | A4 |
| **ROI Estimado de Campaña** | `(Ingreso Atribuido Deduplicado − Costo Descuento) / Costo Descuento` | — | A4 (Reportar como asociación atribuida) |

---

## 3. Contraste Empírico: Datos Reales vs. Enunciado del Caso

Al explorar los datos reales de `clean`, encontramos las siguientes correspondencias exactas con la problemática planteada por la Gerencia:

| Indicador del Problema | Lo que dice el Enunciado | Lo que demuestran los Datos Reales | Hallazgo para el Storytelling (A5) |
|---|---|---|---|
| **Caída del Ticket Promedio** | "Caída del 8% interanual" | **$351.29 (2023) ➔ $344.49 (2024)** (Caída de −1.9% por línea de venta) | La caída por producto es leve (−1.9%), pero la caída del margen neto es mayor por el exceso de descuentos online. |
| **Tasa de Devoluciones** | "Subió al 14% en el último trimestre" | **13.45% global / 13.46% en Q4-2024** | La tasa se mantiene en niveles críticos (~13.5%), concentrada fuertemente en Ropa (21.8%) y Electrónica (17.6%). |
| **Deterioro del Marketing** | "Efectividad cayó de 22% a 11% en 18 meses" | **11.3% (Q1-2023) ➔ 5.6% (Q4-2024)** | La efectividad **se redujo exactamente a la mitad** en los datos. La tendencia del dolor se cumple de forma idéntica. |

---

## 4. Las 4 Decisiones Exactas para Completar A2, A3 y A4

Para tener el 100% de los notebooks cerrados sin duplicaciones, el equipo solo debe acordar estos 4 parámetros:

### 1. Umbral de Churn ($N$ días de inactividad) ➔ *Afecta A2 (CLV) y A3 (Fugas)*
* **Situación:** La mediana es 40 días, pero el P85 es 127 días y el P90 es 162 días.
* **Propuesta recomendada:** Fijar el corte en **120 o 160 días** (o adoptar el semáforo: 40d atención, 120d riesgo, 160d crítico). 
* **Impacto en A2:** La tasa de abandono anual resultante define la vida útil esperada ($1 / \text{churn}$) para el CLV.

### 2. Criterio de Quejas No Resueltas en CRM ➔ *Afecta A3 (Fugas)*
* **Situación:** En el borrador solo se tomó `sin_resolver` (499 quejas).
* **Propuesta recomendada:** Incluir también `escalado` (`{'sin_resolver', 'escalado'}`), ya que una queja escalada sin cierre representa insatisfacción no resuelta para el cliente.

### 3. Métrica Oficial de Conversión de Campañas ➔ *Afecta A4 (Marketing)*
* **Situación:** La conversión declarada por la plataforma es 9.0% (baja de 11.3% a 5.6%), mientras que la conversión validada con compras es 2.0%.
* **Propuesta recomendada:** Usar la **conversión declarada como métrica principal** (es la que mide el dolor del caso) y reportar la **validada a 30 días como auditoría técnica de calidad**.

### 4. Regla de Atribución y Ventana para ROI ➔ *Afecta A4 (Marketing)*
* **Situación:** Varios envíos de campañas coinciden con la misma compra de un cliente en 30 días.
* **Propuesta recomendada:** Aplicar regla de **atribución al último contacto (Last-Touch)** para no duplicar ventas, y **excluir los envíos de diciembre 2024** por tener ventana de observación incompleta.

---

## 5. Historial de Versiones
* **v1.0 (2026-10-23):** Propuesta inicial de árbol de métricas y diccionario de campos.
* **v2.0 (2026-10-23):** Incorporación de corrección de meses calendario para proyección a 6m, reglas de deduplicación de campañas, separación de descuentos aplicados vs ofrecidos y alineación de los 4 acuerdos de equipo.
