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
