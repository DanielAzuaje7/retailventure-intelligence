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
