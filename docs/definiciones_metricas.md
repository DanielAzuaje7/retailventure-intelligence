# Definiciones de métricas del negocio

> **Estado: PROPUESTA — pendiente de aprobación del equipo.**
> Una métrica pasa a "aprobada" cuando al menos dos integrantes la revisan.
> Cualquier cambio de fórmula se registra en la tabla de cambios al final.

Objetivo: que A2, A3, A4 y el dashboard calculen **las mismas cifras con las mismas fórmulas**.
Todas las métricas se calculan sobre el esquema `clean` de Supabase.

- **Periodo de los datos:** 2023-01-01 a 2024-12-31 (24 meses).
- **Fecha de corte (`FIN`):** 2024-12-31. Recencia y antigüedad se miden contra esta fecha.
- **Comparación interanual:** 2024 vs. 2023.

---

## 1. Cómo se eligieron: árbol de métricas

Las métricas no se eligen de una lista: salen de descomponer el problema del negocio
hasta llegar a algo calculable con los datos.

```
Margen neto (objetivo de la gerencia)
├── Ingreso neto = Clientes activos × Frecuencia × Ticket promedio
│     ├── Clientes activos  ◄── se pierden por churn                 (A3)
│     ├── Frecuencia
│     └── Ticket = Precio × (1 − Descuento) ◄── dolor 1: ticket −8%   (A2)
├── − Costo → Margen bruto %  ◄── mezcla de categorías y canales     (A2)
├── − Devoluciones            ◄── dolor 2: tasa de devolución 14%    (A3)
└── − Costo comercial         ◄── dolor 3: conversión 22% → 11%      (A4)
```

Cada métrica propuesta pasó este filtro:

1. ¿Qué decisión cambia si sube o baja? (si ninguna, se descarta)
2. ¿Tiene una fórmula exacta, que dos personas calculen igual?
3. ¿Se puede calcular con las columnas disponibles?
4. ¿Tiene contra qué compararse (periodo, segmento, canal)?
5. ¿Puede engañar? → se acompaña de una métrica de control.

Roles:

| Rol | Para qué sirve | Ejemplos |
|---|---|---|
| KPI principal | Lo que la gerencia quiere mover | Margen neto, variación interanual |
| Impulsoras | Las ramas del árbol | Ticket, frecuencia, clientes activos, devolución, conversión |
| Diagnósticas | Explican el porqué | Motivo de devolución, quejas sin resolver, descuento promedio |
| De control | Evitan optimizar mal | Margen % al evaluar descuentos; ROI al evaluar conversión |

---

## 2. Diccionario de métricas

### 2.1 Rentabilidad (`clean.transacciones`)

| Métrica | Fórmula | Columnas | Usa |
|---|---|---|---|
| Ingreso bruto | `Σ ingreso_bruto` (= cantidad × precio_unitario) | `ingreso_bruto` | A2 |
| Ingreso neto | `Σ monto_neto` | `monto_neto` | Todos |
| Monto de descuento | `Σ monto_descuento` | `monto_descuento` | A2, A4 |
| Margen bruto | `Σ margen_bruto` (= monto_neto − cantidad × costo) | `margen_bruto` | A2 |
| Margen bruto % | `Σ margen_bruto / Σ monto_neto` | — | A2 |
| Margen neto de devoluciones | `Σ margen_neto_devol` (margen = 0 si la venta fue devuelta) | `margen_neto_devol` | A2, A3 |
| Ingreso neto final | `Σ monto_neto_final` (= monto_neto − monto_devuelto) | `monto_neto_final` | A3 |
| Ticket promedio | `Σ monto_neto / nº de transacciones` | `monto_neto`, `transaccion_id` | A2, A5 |
| % ventas bajo costo | `mean(venta_bajo_costo)` | `venta_bajo_costo` | A2 |

### 2.2 Clientes (`clean.clientes` + `clean.transacciones`)

| Métrica | Fórmula | Columnas | Usa |
|---|---|---|---|
| Clientes activos (periodo) | Clientes distintos con ≥ 1 compra en el periodo | `cliente_id`, `fecha` | A2, A3 |
| Frecuencia | `nº transacciones / clientes activos` en el periodo (anualizada) | — | A2, A3 |
| Recencia | `recencia_dias` (= FIN − ultima_compra) | `recencia_dias` | A3 |
| Antigüedad | `antiguedad_dias` (desde `fecha_alta_efectiva`, **no** `fecha_registro`) | `antiguedad_dias` | A2 |
| Churn (cliente inactivo) | `recencia_dias > N` | `recencia_dias` | A2, A3 |
| Tasa de churn | clientes en churn / clientes con ≥ 1 compra | — | A2, A3 |
| CLV histórico | `Σ margen_bruto` acumulado del cliente | `margen_total` | A2 |
| CLV estimado | margen promedio por compra × compras por año × vida esperada | ver §3.2 | A2, A3 |
| Ingresos en riesgo a 6 meses | Σ (ingreso mensual promedio histórico × 6) de clientes en churn o en riesgo | `monto_total`, `antiguedad_dias` | A3 |

### 2.3 Devoluciones y CRM

| Métrica | Fórmula | Columnas | Usa |
|---|---|---|---|
| Tasa de devolución (transacciones) | `mean(devuelto)` | `devuelto` | A3 |
| Tasa de devolución (monto) | `Σ monto_devuelto / Σ monto_neto` | `monto_devuelto` | A3 |
| Clientes reincidentes en devolución | Clientes con `n_devoluciones ≥ k` (k a definir con la distribución) | `n_devoluciones` | A3 |
| Quejas sin resolver | `n_quejas_sin_resolver` por cliente | `clean.clientes` | A3, A4 |
| Tiempo de respuesta | Mediana de `tiempo_respuesta_hrs` (mediana por los outliers > 168 h) | `clean.interacciones_crm` | A3 |

### 2.4 Marketing (`clean.campanas_marketing`)

| Métrica | Fórmula | Columnas | Usa |
|---|---|---|---|
| Tasa de apertura | `mean(abierto)` | `abierto` | A4 |
| Conversión declarada (oficial) | `mean(convertido)` | `convertido` | A4 |
| Conversión validada 30 días | `mean(convertido_validado_30d)` | `convertido_validado_30d` | A4 |
| Costo implícito del descuento | `descuento_ofrecido × monto_compra_30d` (solo campañas convertidas) | `descuento_ofrecido`, `monto_compra_30d` | A4 |
| ROI de campaña | `(ingreso atribuido − costo del descuento) / costo del descuento` | `monto_compra_30d` | A4 |

---

## 3. Decisiones pendientes (hay que poder defenderlas en la oral)

### 3.1 Umbral de churn (N días)
- **No se fija a ojo:** se obtiene de la distribución de días entre compras consecutivas de cada cliente.
- Referencia: ~50.000 transacciones / ~8.000 clientes ≈ 6 compras en 2 años ≈ una cada ~115 días.
- Regla propuesta: **N = percentil 90 del intervalo entre compras** (se espera entre 120 y 240 días).
- Responsable de proponerlo: A3. Lo usa también A2 (CLV).

### 3.2 Fórmula del CLV estimado
- `CLV = margen promedio por compra × compras por año × vida esperada (años)`
- `vida esperada = 1 / tasa de churn anual`, con **tope de 3 años** para no inflar el valor.
- Se calcula por segmento. Para detectar **segmentos en declive** se compara el CLV (o el margen
  por cliente activo) entre semestres o entre 2023 y 2024.
- Limitación: 24 meses de historia; el CLV es una estimación simple, no un modelo probabilístico.

### 3.3 Qué es un "ticket"
- En los datos, cada `transaccion_id` tiene **un solo producto**: es una línea de venta, no una canasta.
- Opción A: ticket = promedio de `monto_neto` por transacción (simple, es lo que usa el notebook A1).
- Opción B: canasta = `cliente_id + fecha + canal`; ticket = promedio por canasta.
- Hay que elegir una y declararla, porque el enunciado habla de una caída del ticket del 8%.

### 3.4 Devoluciones al final del periodo
- Las ventas de los últimos 30 días todavía no tuvieron tiempo de ser devueltas
  (`ventana_devol_incompleta = 1`).
- Al calcular la tasa del último trimestre, **excluir esas ventas** o declararlo como sesgo.

### 3.5 Conversión oficial
- Decidido en A1: se usa `convertido` (declarada), porque define la cifra del caso (22% → 11%).
- Se reporta también la validada a 30 días como prueba de robustez y como limitación del dato.

---

## 4. Uso en el dashboard

- **Fila superior (KPIs):** ingreso neto, margen bruto %, ticket promedio, tasa de devolución,
  conversión — cada uno con su variación 2024 vs. 2023.
- **Cada sección baja por una rama del árbol** (rentabilidad, fugas, marketing).
- Límite del enunciado: máximo 10 visualizaciones con título en forma de insight.

---

## 5. Registro de cambios

| Fecha | Cambio | Autor | Revisado por |
|---|---|---|---|
| 2026-10-23 | Propuesta inicial | Daniel (con asistencia de IA) | — |
