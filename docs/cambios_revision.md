# Cambios de la revisión externa (A2, A3, A4)

Rama: `revision-externa-a2-a4`.

**Qué es "antes" y "después":**
- **Valor antes:** salida de la versión previa a la revisión externa (commit `066777b`, "Primera versión con métricas definidas"), o la cifra citada por la revisión cuando ese commit no la imprime.
- **Valor después:** salida de esta rama, con el notebook ejecutado de principio a fin.
- Parte de las correcciones ya estaba aplicada en `main` (commits `710413e` y `a1b8c63`). En esos casos la columna "después" coincide con `main`. La revisión de esta rama verificó el cálculo y corrigió lo que faltaba (por ejemplo, cifras de "antes" escritas a mano en el código).

| Corrección | Métrica | Valor antes | Valor después | Notebook |
|---|---|---|---|---|
| C2 | Asignaciones compra-campaña atribuidas | 2,176 | 2,122 | A4 |
| C2 | Transacciones atribuidas a más de una campaña | 54 (no se reportaba) | 0 | A4 |
| C2 | Monto atribuido (USD) | 733,832.74 | 716,645.40 | A4 |
| C2 | Costo estimado en descuentos (USD) | 92,794.78 | 90,682.05 | A4 |
| C2 | Compras atribuidas: push_reactivacion / email_descuento / sms_oferta_flash / email_fidelizacion / social_ads | 445 / 753 / 332 / 446 / 200 | 436 / 738 / 323 / 430 / 195 | A4 |
| C2 | Retorno bruto de ingreso por tipo (mismo orden) | 8.11 / 7.92 / 7.89 / 7.99 / 7.35 | 8.12 / 7.93 / 7.86 / 8.01 / 7.26 | A4 |
| C2 | Retorno bruto de margen por tipo (mismo orden) | 2.07 / 2.00 / 1.97 / 1.94 / 1.88 | 2.06 / 1.99 / 1.97 / 1.93 / 1.88 | A4 |
| C1 | Retorno bruto global de ingreso | 7.91 | 7.90 (= 1 / 12.654%, verificado en la celda de identidad) | A4 |
| C1 | Retorno bruto global de margen | no se imprimía | 1.98 (= margen % / descuento medio) | A4 |
| C1 | Tasa de compra de referencia | no existía en 066777b; en `main`: 20.40% (30 días previos al envío) | 21.17% (mismo cliente, bloques de 31 días sin campaña) | A4 |
| C1 | Tasa de compra post-envío | en `main`: 20.18% (solo compras last-touch del envío) | 20.85% (cualquier compra, envíos con referencia) | A4 |
| C1 | Lift incremental global | en `main`: −0.22 p.p., IC [−1.23, +0.87] | −0.32 p.p., IC [−1.25, +0.59] (incluye 0) | A4 |
| C1 | Lift por tipo: email_descuento / email_fidelizacion / push_reactivacion / sms_oferta_flash / social_ads | en `main`: −0.13 / +0.35 / −1.37 / +0.23 / −0.12 p.p. | −1.03 / +0.14 / −0.02 / +0.24 / −0.19 p.p. (todos los IC incluyen 0) | A4 |
| C1 | Margen incremental | en `main`: −11,953.66 (margen post − margen pre) | −2,282.24, IC [−8,929.52, +4,367.54] (lift × envíos × margen por compra) | A4 |
| C1 | ROI incremental global | en `main`: −1.13, IC [−1.35, −0.94] | −1.03, IC [−1.10, −0.95] (no incluye 0; incluye −1) | A4 |
| C1 | ROI incremental por tipo (mismo orden) | en `main`: −1.09 / −0.96 / −1.29 / −1.11 / −1.33 | −1.08 / −0.99 / −1.00 / −0.98 / −1.02 | A4 |
| C1 | IC 95% del lift frente a nunca contactados | [−1.86, +0.33] (1,000 réplicas) | [−1.91, +0.27] (2,000 réplicas) | A4 |
| C3 | Quejas: diferencia sí − nunca convirtieron | 17.50% vs 17.75%, sin prueba en 066777b | +0.25 p.p., IC 95% [−2.75, +3.24], p (z) = 0.871 | A4 |
| C3 | Quejas no resueltas: diferencia | 5.71% vs 5.15%, sin prueba | −0.56 p.p., IC 95% [−2.31, +1.18], p (z) = 0.542 | A4 |
| C3 | Devoluciones: diferencia | 44.95% vs 44.58%, sin prueba | −0.37 p.p., IC 95% [−4.27, +3.53], p (z) = 0.851 | A4 |
| C3 | Conclusión de A4.3 | "la causa raíz es post-venta" | sin diferencia significativa en ningún indicador | A4 |
| C3 | Segmento × conversión (nueva) | no existía | Chi2 = 46.83, p = 1.65e-09 | A4 |
| C3 | Devoluciones con conversión validada (nueva) | no existía | 44.01% vs 69.46% (p = 8.2e-11); por cada 100 compras 13.41 vs 12.44 | A4 |
| C4 | Modelo de conversión vs descuento | en `main`: logit con descuento continuo, OR = 26.711 por unidad de descuento | logit con descuento categórico: OR vs 0% = 1.36 / 1.78 / 2.20 / 2.38 / 2.36 (5% a 25%) | A4 |
| C4 | Contraste 25% vs 20% | bruto 11.42% vs 11.39%, chi-cuadrado p = 1.000 | ajustado por segmento y tipo: OR = 0.993, IC 95% [0.789, 1.249], p = 0.952 | A4 |
| C4 | Contraste 25% vs 20% con conversión validada (nuevo) | no existía | OR = 1.240, IC 95% [0.779, 1.975], p = 0.364 | A4 |
| C4 | Conclusión de A4.2 | 066777b: "punto de saturación en >20%"; `main`: "rendimientos decrecientes y estancamiento" | rendimientos decrecientes posibles, no concluyente | A4 |
| C5 | P(compra 30d \| convertido = 1) vs (= 0) | 22.81% vs 20.45%, sin prueba | +2.36 p.p., IC 95% [−0.72, +5.45], p = 0.121 (no difieren) | A4 |
| C5 | Variación relativa de la conversión validada (2023-S1 a 2024-S2) | no se imprimía (revisión: −56%) | −55.5%; −50.4% con ventana completa (1.44% en 2024-S2) | A4 |
| C5 | Descomposición declarada por segmento (nueva) | no existía | −5.43 p.p. = mezcla −0.21 + dentro −5.22 | A4 |
| C5 | Descomposición declarada por tipo (nueva) | no existía | −5.43 p.p. = mezcla −0.01 + dentro −5.42 | A4 |
| C5 | Descomposición validada por segmento / tipo (nueva) | no existía | −1.46 p.p. = mezcla −0.22 + dentro −1.24 / mezcla 0.00 + dentro −1.47 | A4 |
| C5 | Frase frente al enunciado | "confirma de manera precisa una contracción de ~50%" | los niveles difieren (11.8% vs 22%), caída relativa de magnitud similar (−46.0% vs −50%) | A4 |
| C6 | DiD frecuencia (no resueltas − resueltas), W = 40 días | 066777b: −0.010 vs −0.022 sin prueba; `main`: +0.0125, IC [−0.0549, +0.0846] (bootstrap sin reemplazo), t-test p = 0.7848 | +0.0125, IC 95% [−0.0770, +0.1011], p bootstrap = 0.755 | A3 |
| C6 | Quejas excluidas por ventana truncada (W = 40 días) | no se excluían en 066777b | 221 | A3 |
| C6 | DiD con ventana 1.5W (60 días) | `main`: +0.0035 (exclusión de 40 días) | −0.0189, IC [−0.1349, +0.1002], p = 0.752 (343 quejas excluidas) | A3 |
| C6 | Clientes en riesgo con queja no resuelta | `main`: 100 de 1,016 (9.84%) vs 9.03%, p = 0.434 (churn con respaldo P75) | 246 de 2,407 (10.22%) vs 514 de 5,201 (9.88%), p = 0.648 (churn C+B del equipo) | A3 |
| C7 | Afirmación sobre el −8% del ticket | 066777b: "concentrada exactamente en el segmento Inactivo" | los datos no reproducen el −8%; ticket global −1.94% (Welch p = 0.132, nuevo) | A2 |
| C7 | Descomposición del ticket por segmento (nueva) | no existía | −$6.80 = mezcla −$0.02 + precio −$6.78 | A2 |
| C7 | Descomposición del ticket por categoría (nueva) | no existía | −$6.80 = mezcla −$0.93 + precio −$5.87 | A2 |
| C7 | Descomposición del ticket por canal (nueva) | no existía | −$6.80 = mezcla +$0.18 + precio −$6.97 | A2 |
| C7 | Aporte de Inactivo al ticket global | `main`: −0.14 p.p. (variación % × peso, escrito a mano) | −0.15 puntos (efecto precio / ticket 2023) | A2 |
| C8 | Picos y valles estacionales | 066777b: "Pico Q4 (Black Friday/Navidad)" y "Valle Q1" sombreados | picos en ambos años: ninguno; valle: febrero, que desaparece con ingreso por día | A2 |
| C8 | Correlación del índice estacional 2023 vs 2024 | `main`: r = 0.275 sin p-valor | r = 0.275, p = 0.387 | A2 |
| C8 | Correlación por categoría y canal (nueva para canal) | solo matrices por categoría, sin correlación | 0 de 9 grupos con correlación significativa entre años | A2 |
| C8 | Eje Y de las gráficas de estacionalidad | 650 a 800 mil (066777b) | desde 0 | A2 |
| C9 | Nombre de la métrica | "unidades por ticket" / "demanda inelástica" | tamaño de canasta | A2 |
| C9 | Canasta ~ descuento (OLS con controles) | coef +0.0377, p = 0.6408 (errores clásicos) | coef +0.0377, IC 95% [−0.1218, +0.1972], p = 0.643 (HC1) | A2 |
| C9 | Margen % ~ descuento (OLS con controles) | coef −82.47, p < 0.001 | coef −82.47, IC 95% [−83.36, −81.59], p < 0.001 (HC1) | A2 |
| C9 | Punto de equilibrio | 066777b: +227% para 20% (markdown, m ≈ 28.8% a mano); `main`: no existía | 5% → +21.0%, 10% → +53.1%, 15% → +108.6%, 20% → +226.9%, 25% → +655.2% (m = 28.82%, calculado) | A2 |
| C10 | Nombre del cruce canal × categoría | "Cruce Causal" | "Cruce descriptivo" (introducción y sección 4) | A2 |
| C10 | Margen de tienda física en el resumen | `main`: 31.51% (promedio simple de categorías) | 26.02% (margen ponderado del canal) | A2 |
| C10 | Brecha actual de margen tienda − online (nueva) | no se imprimía | 3.25 p.p. (≈ $212,647.56) | A2 |
| C10 | Contrafactual online con descuento de tienda | +3.14 p.p. (+$277,632.43) | sin cambio; se agrega que explica el 97% de la brecha y se presenta como tope | A2 |
| C11 | Referencia de cada producto | tasa de la categoría completa (incluye al producto) | tasa del resto de la categoría | A3 |
| C11 | Productos con p < 0.05 sin corregir (nuevo) | no se reportaba | 9 de 318 (≈ 16 esperados por azar) | A3 |
| C11 | Productos con exceso significativo tras BH | 0 | 0 (menor q = 0.580, PRD0095) | A3 |
| C11 | Ranking de productos | 066777b: por monto devuelto | tasa vs. resto de categoría con IC de Wilson; ranking por monto como complemento | A3 |
| C12 | Clientes con ≥ 2 devoluciones: observados vs esperados | 1,711 vs 1,707.6 | sin cambio; se agrega la distribución completa (0, 1, 2, 3, 4+) | A3 |
| C12 | Recurrentes anómalos | 20 (solo p < 0.01) | 54 (20 por p < 0.01, 47 por ≥ 3 dev. con tasa ≥ 40% y ≥ 4 compras, 13 ambos) | A3 |
| C12 | Esperados por azar con cada criterio (nuevo) | no se reportaba | 22.2 (p < 0.01) y 57.9 (criterio de tasa): sin exceso sobre el azar | A3 |
| C13 | Tendencia de la tasa de devolución (nueva) | no se probaba | OR por 12 meses = 1.008, IC [0.964, 1.054], p = 0.727 (sin tendencia) | A3 |
| C13 | Último trimestre vs anteriores (nueva) | no se probaba | 13.45% vs 13.45%, p = 0.994 (no se reproduce el 14%) | A3 |
| C13 | Tasa con ventana de devolución incompleta | 13.45% igual a la global, sin explicación | 13.43% vs 13.45%; 158 de 276 devoluciones fechadas el 2024-12-31 (fechas recortadas en origen) | A3 |
| C13 | Texto de Ropa | "mayor TASA (0.0%), dominada por Talla_incorrecta y No_cumple_expectativas" | 21.78%; motivos principales Producto_defectuoso 28.3% y No_cumple_expectativas 22.7% | A3 |
| C13 | Motivo × categoría sin Talla_incorrecta (nueva) | no existía | Chi2 = 84.66, p < 0.001 | A3 |
| C14 | Tasa de churn usada en el CLV | fijada a mano: 10% / 15% / 28% / 35% / 85% (Premium / Frecuente / Esporádico / Nuevo / Inactivo), origen no trazable | retención observada 2023 → 2024: 100.0% / 99.29% / 77.68% / 32.03% / 0.0% | A2 |
| C14 | CLV Premium | 4,178.77 (perpetuidad con churn 10%) | 2,052.59 (margen 2023) → 2,104.20 (margen 2024), 3 años | A2 |
| C14 | CLV Frecuente | 1,760.50 | 1,100.04 → 1,089.03 | A2 |
| C14 | CLV Esporádico | 318.79 | 297.05 → 299.21 | A2 |
| C14 | CLV Nuevo | 125.06 | 113.25 → 124.40 | A2 |
| C14 | CLV Inactivo | 46.42 | 82.14 → 78.17 | A2 |
| C14 | Segmentos en declive (nuevo) | no se identificaban | Frecuente (clientes −0.08%, margen/cliente −1.00%) e Inactivo (−2.47%, −4.83%) | A2 |
| C15 | Conversión por canal de envío (nueva) | no existía | validada: email 2.34%, push_app 2.03%, sms 1.63%, redes_sociales 1.58% | A4 |
| C15 | Combinaciones analizadas | tipo × canal × segmento (24 de 25 con ≥ 100 envíos) | tipo × segmento (24 de 25) y canal × segmento (19 de 20); cada tipo usa un único canal | A4 |
| C15 | Conversión validada por segmento | calculada con todos los envíos: Nuevo 0.43%, Inactivo 0.16% | con ventana completa: Nuevo 0.45%, Inactivo 0.17% | A4 |
| C15 | Segmentos que reciben campañas y no convierten | Nuevo e Inactivo, 24.6% de los envíos, sin datos de respaldo para la hipótesis | Nuevo e Inactivo, 24.6%; compran en 30 días 5.80% y 3.30%; mismo descuento (12.30% vs 12.47%); declarada 24× y 32× la validada | A4 |
| C16 | Ventana del gasto para ingreso en riesgo (texto) | "12 meses activos" | "12 meses calendario" (parámetro y comentario) | A3 |
| C16 | Indicador principal del resumen ejecutivo | intervalo mediano entre compras (40 días) | 2,407 clientes en riesgo (31.6%) e ingreso en riesgo a 6 meses $635,911.35 | A3 |
| C16 | Ingreso en riesgo con el método anterior (meses con compras) | "$12.7M" escrito a mano | $3,118,914.07 (calculado; 2.3 meses con compra de 12 en promedio) | A3 |
| C16 | Clientes en riesgo con queja no resuelta (solape en A3.4) | 222 (solo quejas con ventana completa) | 246 (todas las quejas no resueltas, igual que el cruce de C6) | A3 |
| C16 | Decisión de quejas no resueltas | "pendiente de validar" en el markdown | opción B adoptada (`sin_resolver` + `escalado`) | A3 |
| C17 | Explicación de las ventas bajo costo | "711 transacciones"; "se debió exclusivamente a descuentos excesivos" (afirmado) | calculado: descuento 19.6% vs 5.0%; margen natural 15.0% vs 34.6%; 100% con descuento mayor que el margen natural | A2 |
| C17 | Títulos con conclusión anticipada | "Ganadoras vs. Destructoras de Margen"; A4.2 "(5% a 25%)" afirmativo | "mayor y menor margen"; A4.2 formulada como pregunta | A2, A4 |
| C18 | Margen en `cruce_margen` y `sub_summary` | ya ponderado en `main` (066777b: promedio de margen_pct_real por transacción) | Σmargen/Σingreso, sin cambios en esta rama | A2 |
| C18 | Margen por canal: promedio simple vs ponderado (referencia) | simple: 31.52% / 28.51% / 31.58% (app / online / tienda) | ponderado: 25.91% / 22.78% / 26.02% | A2 |
| C19 | Fuente de datos de A2 y A4 | CSV locales de data/clean | esquema `clean` de Supabase en solo lectura (CSV como alternativa comentada) | A2, A4 |
| C19 | Lectura de A3 | Supabase sin orden fijo ni bloqueo de escritura | Supabase en solo lectura, ordenado por clave primaria | A3 |
| C19 | Cifras de control impresas | A2 y A3 (A4 no las imprimía) | A2, A3 y A4: ingreso 17,392,987.48 y margen 4,310,329.05 (assert en A2 y A4) | A2, A3, A4 |
| C20 | Margen del top 20% de clientes | 56.1% (leía la fila del cliente 1,522) | 56.0% (1,521 clientes) | A2 |
| C20 | Clientes que concentran el 80% del margen | 2,893 (índice, no conteo) | 2,894 = 38.0% de los 7,608 con compras (36.2% sobre los 8,000) | A2 |
| C20 | Aclaración del denominador | markdown con 7,608 / 8,000 / 392 escritos a mano | markdown sin cifras; conteos impresos y en el eje X | A2 |
