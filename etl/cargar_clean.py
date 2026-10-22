"""
cargar_clean.py
Carga los datasets maestros (salida del notebook de A1) al esquema `clean` de Supabase
con tipos correctos, claves primarias y claves foraneas: el esquema estrella queda
implementado como tablas reales, listo para conectar Power BI.

Tambien carga las tablas de calidad (A1) al esquema `auditoria`.

Requisitos:
- Archivo .env con DATABASE_URL (igual que cargar_csv.py)
- Carpeta data/clean/ con el contenido de datasets_maestros.zip
- data/raw/devoluciones.csv (la tabla de devoluciones no cambia en la limpieza)

El esquema raw NO se toca: queda como evidencia de los datos originales.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Date, create_engine, text

RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")

URL = os.getenv("DATABASE_URL")
if not URL:
    sys.exit("Falta DATABASE_URL en el archivo .env")

CLEAN_DIR = RAIZ / "data" / "clean"
RAW_DIR = RAIZ / "data" / "raw"

# tabla destino -> (archivo origen, columnas de fecha)
# El orden importa: primero dimensiones, luego hechos y eventos (por las claves foraneas)
TABLAS = {
    "dim_fecha":         (CLEAN_DIR / "dim_fecha.csv",             ["fecha"]),
    "clientes":          (CLEAN_DIR / "clientes_maestra.csv",      ["fecha_registro", "primera_compra", "ultima_compra", "fecha_alta_efectiva"]),
    "productos":         (CLEAN_DIR / "productos_limpio.csv",      []),
    "transacciones":     (CLEAN_DIR / "transacciones_maestra.csv", ["fecha", "fecha_devolucion"]),
    "devoluciones":      (RAW_DIR / "devoluciones.csv",            ["fecha_devolucion"]),
    "interacciones_crm": (CLEAN_DIR / "crm_limpio.csv",            ["fecha"]),
    "campanas_marketing":(CLEAN_DIR / "campanas_limpia.csv",       ["fecha_envio", "primera_compra_post"]),
}

AUDITORIA = {
    "metricas_calidad":            CLEAN_DIR / "metricas_calidad.csv",
    "detalle_reglas_consistencia": CLEAN_DIR / "detalle_reglas_consistencia.csv",
    "perfil_campos":               CLEAN_DIR / "perfil_campos.csv",
}

CLAVES_PRIMARIAS = {
    "dim_fecha": "fecha",
    "clientes": "cliente_id",
    "productos": "producto_id",
    "transacciones": "transaccion_id",
    "devoluciones": "devolucion_id",
    "interacciones_crm": "interaccion_id",
    "campanas_marketing": "campana_id",
}

# (tabla, columna, tabla referenciada, columna referenciada)
CLAVES_FORANEAS = [
    ("transacciones", "cliente_id", "clientes", "cliente_id"),
    ("transacciones", "producto_id", "productos", "producto_id"),
    ("transacciones", "fecha", "dim_fecha", "fecha"),
    ("devoluciones", "transaccion_id", "transacciones", "transaccion_id"),
    ("interacciones_crm", "cliente_id", "clientes", "cliente_id"),
    ("campanas_marketing", "cliente_id", "clientes", "cliente_id"),
]

# 1. Verificar que estan todos los archivos
faltan = [str(r.relative_to(RAIZ)) for r, _ in TABLAS.values() if not r.exists()]
faltan += [str(r.relative_to(RAIZ)) for r in AUDITORIA.values() if not r.exists()]
if faltan:
    sys.exit("Faltan archivos:\n  " + "\n  ".join(faltan))

engine = create_engine(URL, pool_pre_ping=True)

# 2. Recrear los esquemas desde cero (raw no se toca)
with engine.begin() as con:
    con.execute(text("drop schema if exists clean cascade"))
    con.execute(text("create schema clean"))
    con.execute(text("drop schema if exists auditoria cascade"))
    con.execute(text("create schema auditoria"))

# 3. Cargar las tablas del modelo con fechas como tipo DATE
print(f"{'tabla':<22}{'filas CSV':>12}{'filas en BD':>14}   estado")
for tabla, (ruta, fechas) in TABLAS.items():
    df = pd.read_csv(ruta)
    for col in fechas:
        fechas_dt = pd.to_datetime(df[col])
        # las fechas vacias (ej. clientes sin compras) deben llegar como NULL, no como NaT
        df[col] = fechas_dt.dt.date.astype(object).where(fechas_dt.notna(), None)
    df.to_sql(
        tabla, engine, schema="clean",
        if_exists="replace", index=False,
        # PostgreSQL admite como maximo 65,535 parametros por consulta (filas x columnas)
        chunksize=min(2000, 65535 // len(df.columns)), method="multi",
        dtype={col: Date() for col in fechas},
    )
    with engine.connect() as con:
        en_bd = con.execute(text(f"select count(*) from clean.{tabla}")).scalar()
    estado = "OK" if en_bd == len(df) else "REVISAR"
    print(f"{tabla:<22}{len(df):>12,}{en_bd:>14,}   {estado}")

# 4. Claves primarias y foraneas: el esquema estrella queda implementado
with engine.begin() as con:
    for tabla, pk in CLAVES_PRIMARIAS.items():
        con.execute(text(f"alter table clean.{tabla} add primary key ({pk})"))
    for tabla, col, ref, ref_col in CLAVES_FORANEAS:
        con.execute(text(
            f"alter table clean.{tabla} add constraint fk_{tabla}_{col} "
            f"foreign key ({col}) references clean.{ref} ({ref_col})"
        ))
print("\nClaves primarias y foraneas creadas.")

# 5. Tablas de calidad de A1
for tabla, ruta in AUDITORIA.items():
    pd.read_csv(ruta).to_sql(tabla, engine, schema="auditoria", if_exists="replace", index=False)
print("Tablas de calidad cargadas en el esquema auditoria.")

# 6. Control: las cifras base deben coincidir con el documento del equipo
with engine.connect() as con:
    ingreso, margen = con.execute(text(
        "select round(sum(monto_neto)::numeric, 2), round(sum(margen_bruto)::numeric, 2) "
        "from clean.transacciones"
    )).fetchone()
print(f"\nIngreso neto total: {ingreso:,}  (esperado 17,392,987.48)")
print(f"Margen bruto total: {margen:,}  (esperado 4,310,329.05)")
print("\nCarga terminada. Revisa en Supabase los esquemas clean y auditoria.")
