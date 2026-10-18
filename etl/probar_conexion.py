"""Comprueba que Python puede conectarse a Supabase."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

engine = create_engine(os.environ["DATABASE_URL"])

with engine.connect() as con:
    fila = con.execute(
        text("select current_database(), current_user, now()")
    ).fetchone()

print("Base de datos:", fila[0])
print("Usuario:      ", fila[1])
print("Hora servidor:", fila[2])
print("\nConexión exitosa")