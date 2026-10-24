# Guía Metodológica Integral de Cálculos: A1, A2, A3 y A4

**Proyecto 01: Retail Intelligence (RetailVenture C.A.)**  
*Tópicos Especiales para la Gestión de Datos · Ingeniería Informática*

Este documento detalla **cómo se calcula cada indicador, por qué se calcula de esa manera, qué significa cada número y por qué se escogieron esos parámetros** en las cuatro actividades analíticas del proyecto. Está diseñado como el manual de defensa técnica del equipo ante el jurado evaluador.

---

## 1. Actividad A1: Auditoría de Calidad y Preparación de Datos

### 1.1 Las Cuatro Dimensiones de Calidad (Marco DAMA-DMBOK)
El profesor exige auditar los seis datasets bajo cuatro dimensiones exactas:

1. **Completitud (% de celdas no vacías):**
   * *Cómo se calcula:* Se mide el total de celdas con valores válidos dividido entre el total de celdas esperadas (`filas × columnas`).
   * *Hallazgo clave (Nulos ocultos):* Un nulo no siempre es `NaN`. Se detectaron 433 registros con el texto `'No especificado'` en el campo `genero` de clientes. Si solo se buscan `NaN`, la completitud da 100%, pero la completitud real del campo es **94.59%**.
2. **Unicidad (% de filas no duplicadas):**
   * *Cómo se calcula:* Se valida la unicidad en 3 niveles: duplicados exactos (toda la fila igual), de clave primaria (PK repetida) y duplicados lógicos (mismo cliente, fecha, producto y precio).
   * *Resultado:* 100% de unicidad en claves primarias. En campañas se detectó duplicidad lógica en clientes que recibieron la misma campaña el mismo día con distinto descuento.
3. **Consistencia (% de registros que cumplen reglas lógicas y de negocio):**
   * *Cómo se calcula:* Se diseñó un conjunto de reglas booleanas por dataset (reglas de dominio, integridad referencial FK y consistencia temporal).
   * *¿Por qué Clientes dio 27.46% de consistencia?* Porque **5,803 clientes (72.5%)** compraron por primera vez antes de su supuesta `fecha_registro`. La regla temporal `registro <= primera_compra` falló masivamente.
   * *Decisión técnica de limpieza:* **No se eliminaron los clientes.** Si se eliminaban, se destruía el 72.5% de la facturación histórica. Se demostró que `fecha_registro` medía el alta digital y no la primera compra física. Se creó la columna maestra:
     $$\text{fecha\_alta\_efectiva} = \min(\text{fecha\_registro}, \text{primera\_compra})$$
4. **Oportunidad / Cobertura temporal:**
   * *Cómo se calcula:* % de registros que caen dentro de la ventana oficial de 24 meses (2023-01-01 a 2024-12-31).
   * *Resultado:* 100% de oportunidad. En la tabla `productos` queda vacía/NULL porque es una dimensión estática sin fecha.

---

## 2. Actividad A2: Análisis de Rentabilidad y Comportamiento de Compra

### 2.1 Contribución al Margen Bruto (A2.1)
* **Fórmula de Margen Bruto:**
  $$\text{Margen Bruto (\$) } = \text{monto\_neto} - (\text{cantidad} \times \text{costo})$$
  $$\text{Margen Bruto (\%)} = \frac{\text{Margen Bruto Total}}{\text{Ingreso Neto Total}} = \frac{\$4,310,329.05}{\$17,392,987.48} = 24.78\%$$
* **Por qué Ropa parece una joya pero es un riesgo:**
  * Ropa y Calzado tiene un margen bruto muy atractivo (**39.45%**), pero en A3 se demuestra que devuelve el **21.78%** de lo vendido.
  * Por eso se calcula como métrica de control el **Margen Neto Post-Devolución**, donde la devolución anula el margen ganado.
* **Causalidad en Canales (La trampa de Online):**
  * La Tienda Física rinde **26.02%** de margen, mientras que Online rinde **22.78%** (más de 3 puntos porcentuales menos).
  * *Causa raíz demostrada:* Online otorga el **doble de descuento promedio (7.55%)** que la Tienda Física (3.73%) en todas las categorías, erosionando la ganancia neta.
* **Drill-down a Subcategorías:**
  * En *Hogar y Deco*, las subcategorías **Baño** ($454k) y **Decoración** ($430k) aportan más del 20% del margen total de la empresa.
  * En *Electrónica*, la subcategoría **Computadoras** vende mucho volumen, pero su margen real es de apenas **12.9%** y tiene **17.6%** de devolución.
* **Concentración Geográfica (Ciudades):**
  * **Caracas** concentra el **39.05%** del margen ($1.68M). Las 3 principales plazas (Caracas, Maracaibo, Valencia) suman el **72.67%**.
  * El margen % es homogéneo entre ciudades (~30%), demostrando que la rentabilidad regional depende del volumen y no de disparidades de precios.
* **Curva de Lorenz / Pareto 80/20:**
  * El **38.0% de los clientes** genera el **80.0% del margen bruto total**.
  * El 20% superior genera el **56.0%**.

### 2.2 Customer Lifetime Value (CLV) (A2.2)
* **Fórmula estándar elegida:**
  $$\text{CLV} = \text{Margen Promedio Anual por Cliente} \times \text{Vida Útil Esperada (Años)}$$
  $$\text{Vida Útil Esperada} = \min\left(\frac{1}{\text{Tasa de Churn Anual}}, 3\text{ años}\right)$$
* *Por qué se acota a 3 años:* Porque la empresa solo tiene 24 meses de datos históricos. Asumir vidas de 10 años sobreestimaría el valor del cliente de forma irresponsable.
* *Detección de segmentos en declive:* Se compara el margen aportado por cliente activo entre 2023 y 2024.

### 2.3 Estacionalidad (A2.3)
* **Cálculo:** Serie temporal agrupada por `anio_mes` comparando las curvas mensuales de 2023 frente a 2024.
* *Limitación metodológica:* Con 24 meses solo existen 2 ciclos anuales completos. Se reporta como patrón observado de picos (noviembre-diciembre) y valles (primer trimestre), advirtiendo que no constituye una descomposición estacional de largo plazo.

### 2.4 Elasticidad y Efecto de Descuentos (A2.4)
* **Punto de equilibrio del descuento:**
  Para que un descuento $d$ sea rentable vendiendo un producto con margen $m$, el volumen de unidades debe crecer al menos:
  $$\frac{\Delta Q}{Q} \ge \frac{d}{m - d}$$
* *Hallazgo empírico en los datos:* Al pasar de 0% a >15% de descuento, las unidades promedio por compra **no aumentan** (se mantienen en 1.78 unidades), pero el margen real se desploma de **34.3% a 18.0%**. El descuento destruye margen sin generar volumen incremental. Además, se detectaron **711 transacciones vendidas por debajo del costo**.

---

## 3. Actividad A3: Detección de Fugas de Ingresos

### 3.1 Patrón de Devoluciones (A3.1)
* **Tasa de Devolución por Transacción:**
  $$\text{Tasa Trx} = \frac{\text{Transacciones Devueltas (6,724)}}{\text{Transacciones Totales (50,000)}} = 13.45\%$$
* **Tasa de Devolución en Dinero:**
  $$\text{Tasa \$} = \frac{\text{Monto Devuelto Total (\$2,534,466.22)}}{\text{Ingreso Neto Total (\$17,392,987.48)}} = 14.57\%$$
* *El dolor del 14% confirmado:* En el último trimestre (Q4 2024), la tasa se ubicó en **13.46%**, confirmando el nivel crítico reportado por la gerencia.
* *Clientes Reincidentes:* Se identificaron **1,711 clientes con $\ge 2$ devoluciones**.

### 3.2 Impacto de Quejas en CRM vs. Recompra (A3.2)
* **Metodología de Causalidad (Grupo de Control):**
  * Para no asumir que una queja automáticamente reduce compras, se comparó el comportamiento antes y después de la queja en una ventana simétrica de días ($W$), dividiendo a los clientes en:
    1. **Grupo de Tratamiento:** Clientes con quejas NO resueltas (`sin_resolver` + `escalado`).
    2. **Grupo de Control:** Clientes con quejas RESUELTAS (`resuelto`).
* *Hallazgo:* En quejas no resueltas, la frecuencia de compras posteriores cayó **el doble (−0.040 compras)** que en las resueltas (−0.022 compras).

### 3.3 Riesgo de Churn (Inactividad) (A3.3)
* **Por qué NO usar 40 días fijo:**
  * La mediana de recompra es 40 días. Usar 40 días clasifica al **72.5% de los clientes** como perdidos, lo cual es comercialmente absurdo.
* **El Enfoque Híbrido Acordado (C + B):**
  * **Regla Relativa Individual (Opción C):** Un cliente entra en riesgo si su recencia supera **3 veces su propio intervalo mediano de compra** ($\text{Recencia} > 3 \times W_i$).
  * **Regla Global de Respaldo (Opción B):** Para clientes con pocas compras, se usa el **Percentil 85 de la empresa (127 días, ~4 meses)**.

### 3.4 Cuantificación Económica a 6 Meses (A3.4)
* **Fórmula Corregida:**
  $$\text{Ingreso Proyectado a 6m} = \left(\frac{\text{Gasto Real del Cliente en 2024}}{12\text{ meses calendario}}\right) \times 6\text{ meses}$$
* *Por qué se corrigió:* La versión preliminar dividía entre los meses con compras (meses activos). Como un cliente suele comprar solo 4 o 5 meses al año, eso cuadruplicaba artificialmente su flujo mensual, inflando la pérdida proyectada a $12.7M. Con la fórmula calendario, la fuga estimada se sitúa en un rango realista y creíble de **$440k a $700k** bajo umbrales P85-P90.

---

## 4. Actividad A4: Evaluación de la Efectividad del Marketing

### 4.1 ¿Qué es la Conversión y por qué la pide el proyecto?
* **Concepto de Negocio:** La conversión mide la efectividad de una campaña publicitaria: qué porcentaje de los clientes que recibieron un estímulo comercial (email, push, SMS) terminaron comprando.
* **Dónde se pide en el proyecto:**
  1. *En la Problemática:* *"la efectividad de las campañas de marketing ha disminuido de un 22% a un 11% de conversión en 18 meses"*.
  2. *En A4.1 a A4.4:* El profesor pide calcular la conversión por campaña, canal y segmento, evaluar el impacto del descuento ofrecido, diagnosticar qué clientes no convierten y calcular el ROI.
* **El contraste en los datos:**
  * **Conversión Declarada (`convertido`):** Pasó de **11.3% (Q1 2023) a 5.6% (Q4 2024)**. Se redujo exactamente a la mitad (50% de caída, el mismo patrón que el 22% ➔ 11% del caso).
  * **Conversión Validada (`convertido_validado_30d`):** Al cruzar con transacciones reales en los 30 días posteriores, apenas el **2.0%** de los clientes compró.
* *Decisión metodológica:* Se usa la conversión declarada como métrica principal para responder al problema del negocio, pero se expone la validada como hallazgo de auditoría técnica.

### 4.2 Reglas de Atribución y ROI de Campañas (A4.4)
* **Atribución al Último Contacto (Last-Touch):** Si un cliente recibió un email el lunes y un SMS el jueves antes de comprar el viernes, el 100% del ingreso se le atribuye al SMS. Esto evita duplicar ventas entre campañas concurrentes.
* **Exclusión de Cola:** Se excluyen las campañas enviadas en diciembre de 2024 por no disponer de los 30 días completos de observación antes del corte.
* **Fórmula de ROI:**
  $$\text{Costo Implícito del Descuento} = \text{descuento\_ofrecido} \times \text{monto\_compra\_atribuido}$$
  $$\text{ROI} = \frac{\text{Ingreso Atribuido Deduplicado} - \text{Costo del Descuento}}{\text{Costo del Descuento}}$$
  *(Las campañas con 0% de descuento ofrecido tienen costo financiero nulo; se evalúan por ingreso neto por envío en lugar de ROI).*

---

## 5. Resumen del Storytelling para A5

El conjunto de estas cuatro actividades conforma el relato ejecutivo exigido por la Gerencia General:

1. **Inicio (Qué está pasando):** El ticket cayó −8.03% en los clientes que se van a la inactividad, las devoluciones se mantienen en un crítico 13.5% (Q4) y la conversión publicitaria cayó a la mitad (11.3% a 5.6%).
2. **Nudo (Por qué ocurre):** 
   * Fuga 1: El canal Online quema margen otorgando el doble de descuento (7.5% vs 3.7%).
   * Fuga 2: Ropa y Calzado sufre 21.8% de devoluciones y las quejas sin resolver deprimen la recompra a la mitad.
   * Fuga 3: Campañas masivas desconectadas de compras reales con atribución inflada.
3. **Desenlace (Recomendaciones Cuantificadas):**
   * *Recomendación 1 (Pricing/Online):* Topar los descuentos del canal digital al 4%, recuperando 3 puntos de margen bruto equivalente a ~$200k anuales.
   * *Recomendación 2 (Calidad/Devoluciones):* Auditoría de tallas y calidad en Ropa y Calzado para bajar la devolución del 21.8% al promedio de la empresa (13.5%), rescatando ~$120k en margen neto.
   * *Recomendación 3 (CRM/Retención):* Protocolo de resolución en 24h para quejas escaladas en clientes Premium y Frecuentes, evitando una fuga proyectada de ~$400k a 6 meses.
