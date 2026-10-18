"""Lectura de datos y generacion de archivos de salida por area (Joblib).

Aqui se usa Joblib con dos propositos de buenas practicas:
  1. Cachear la carga/limpieza del dataset (memory.cache) para no repetir
     trabajo costoso al re-ejecutar el analisis.
  2. Persistir artefactos del analisis (dump/load) de forma reproducible.

Ademas se generan los archivos de salida solicitados para dos areas:
  - Soporte Tecnico
  - Experiencia de Clientes
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Memory, dump

# Cache en disco para operaciones costosas (reproducibilidad y velocidad).
_CACHE_DIR = Path(__file__).resolve().parent.parent / "cache_joblib"
memory = Memory(location=str(_CACHE_DIR), verbose=0)


@memory.cache
def cargar_dataset(ruta: str) -> pd.DataFrame:
    """Carga el dataset desde Excel y aplica limpieza basica reproducible.

    El resultado queda cacheado por Joblib: la segunda ejecucion con la misma
    ruta y contenido no vuelve a leer ni limpiar el archivo.
    """
    df = pd.read_excel(ruta)
    # Normalizacion de texto para evitar categorias duplicadas por espacios.
    for col in ("region", "tipo_servicio", "cumplimiento_sla"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    return df.sort_values("fecha_registro").reset_index(drop=True)


def _guardar(df: pd.DataFrame, destino: Path) -> None:
    """Guarda un DataFrame en Excel y CSV (UTF-8) en la ruta indicada."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(destino.with_suffix(".xlsx"), index=False)
    df.to_csv(destino.with_suffix(".csv"), index=False, encoding="utf-8-sig")


def salida_soporte_tecnico(df: pd.DataFrame, dir_salida: str) -> pd.DataFrame:
    """Archivo para el area de Soporte Tecnico.

    Incluye fecha, region, tipo de servicio, incidencias, tickets y tiempos de
    resolucion para evaluar la carga operativa y oportunidades de mejora.
    """
    cols = [
        "fecha_registro",
        "region",
        "tipo_servicio",
        "incidencias_reportadas",
        "tickets_soporte",
        "tiempo_resolucion_hr",
    ]
    salida = df[cols].copy()
    # Indicador derivado: tickets por incidencia (eficiencia de canalizacion).
    denom = salida["incidencias_reportadas"].replace(0, np.nan)
    salida["tickets_por_incidencia"] = (salida["tickets_soporte"] / denom).round(2)
    _guardar(salida, Path(dir_salida) / "salida_soporte_tecnico")
    return salida


def salida_experiencia_clientes(df: pd.DataFrame, dir_salida: str) -> pd.DataFrame:
    """Archivo para el area de Experiencia de Clientes.

    Incluye fecha, tipo de servicio, clientes afectados, latencia y estado de
    cumplimiento de SLA para analizar el impacto en la percepcion del servicio.
    """
    cols = [
        "fecha_registro",
        "tipo_servicio",
        "clientes_afectados",
        "latencia_ms",
        "cumplimiento_sla",
    ]
    salida = df[cols].copy()
    # Clasificacion de latencia en niveles interpretables para el negocio.
    salida["nivel_latencia"] = pd.cut(
        salida["latencia_ms"],
        bins=[0, 40, 80, float("inf")],
        labels=["Buena", "Aceptable", "Critica"],
    )
    _guardar(salida, Path(dir_salida) / "salida_experiencia_clientes")
    return salida


def persistir_artefacto(objeto, ruta: str) -> None:
    """Serializa cualquier objeto (modelo, resumen, etc.) con Joblib."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    dump(objeto, ruta)
