"""
cargar_csv.py
Carga los 6 CSV originales al esquema raw de Supabase SIN modificarlos:
- Todo se guarda como texto (los tipos se convierten luego, en el esquema clean).
- Solo las celdas realmente vacias quedan como NULL. Textos como 'N/A' o 'null' se conservan tal cual, porque forman parte de lo que se audita.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")

URL = os.getenv("DATABASE_URL")
if not URL:
    sys.exit("Falta DATABASE_URL en el archivo .env")

RAW_DIR = RAIZ / "data" / "raw"
TABLAS = [
    "clientes",
    "transacciones",
    "productos",
    "devoluciones",
    "interacciones_crm",
    "campanas_marketing",
]


def leer_csv(ruta: Path) -> pd.DataFrame:
    """Lee el CSV sin interpretar nada: todo texto, sin conversiones."""
    for codificacion in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(
                ruta,
                dtype=str,
                keep_default_na=False,
                na_values=[""],
                encoding=codificacion,
            )
        except UnicodeDecodeError:
            continue
    sys.exit(f"No se pudo leer {ruta.name}: revisa la codificacion del archivo")


# 1. Verificar que estan los 6 archivos
faltan = [t for t in TABLAS if not (RAW_DIR / f"{t}.csv").exists()]
if faltan:
    sys.exit(f"Faltan archivos en data/raw/: {', '.join(t + '.csv' for t in faltan)}")

# 2. Conectar y crear el esquema raw
engine = create_engine(URL, pool_pre_ping=True)
with engine.begin() as con:
    con.execute(text("create schema if not exists raw"))

# 3. Cargar cada CSV y comprobar el conteo
print(f"{'tabla':<22}{'filas CSV':>12}{'filas en BD':>14}   estado")
for tabla in TABLAS:
    df = leer_csv(RAW_DIR / f"{tabla}.csv")

    if df.shape[1] == 1:
        sys.exit(
            f"{tabla}.csv tiene una sola columna: probablemente el separador es ';'. "
            "Agrega sep=';' en pd.read_csv."
        )

    df.to_sql(
        tabla, engine, schema="raw",
        if_exists="replace", index=False,
        chunksize=2000, method="multi",
    )

    with engine.connect() as con:
        en_bd = con.execute(text(f"select count(*) from raw.{tabla}")).scalar()

    estado = "OK" if en_bd == len(df) else "REVISAR"
    print(f"{tabla:<22}{len(df):>12,}{en_bd:>14,}   {estado}")

print("\nCarga terminada. Revisa las tablas en Supabase: esquema raw.")