"""Evaluacion de la calidad de los datos (Pregunta 5).

Un dataset poco confiable puede inducir decisiones operativas erroneas:
dimensionar mal el soporte, subestimar clientes afectados o reportar un
cumplimiento de SLA irreal. Este modulo aplica chequeos sistematicos y
reutilizables sobre las dimensiones clasicas de calidad de datos:
completitud, unicidad, validez, consistencia y presencia de atipicos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .estadistica import detectar_atipicos

# Rangos operativos esperados segun el dominio del negocio.
RANGOS_VALIDOS = {
    "trafico_datos_gb": (0, 2000),
    "latencia_ms": (0, 1000),
    "incidencias_reportadas": (0, 500),
    "tickets_soporte": (0, 500),
    "tiempo_resolucion_hr": (0, 240),
    "clientes_afectados": (0, 100000),
}

CATEGORIAS_ESPERADAS = {
    "region": {"Norte", "Centro", "Sur"},
    "tipo_servicio": {"Movil", "Internet Hogar", "Empresas"},
    "cumplimiento_sla": {"Cumple", "No cumple"},
}


def _normaliza_texto(serie: pd.Series) -> pd.Series:
    """Quita espacios sobrantes y normaliza mayusculas de inicio de palabra."""
    return serie.astype(str).str.strip()


def evaluar_completitud(df: pd.DataFrame) -> pd.DataFrame:
    """Porcentaje de valores presentes y faltantes por columna."""
    total = len(df)
    faltantes = df.isnull().sum()
    return pd.DataFrame(
        {
            "faltantes": faltantes,
            "pct_faltantes": (faltantes / total * 100).round(2),
            "pct_completitud": (100 - faltantes / total * 100).round(2),
        }
    )


def evaluar_validez_rangos(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta valores fuera de los rangos operativos esperados."""
    filas = []
    for col, (low, high) in RANGOS_VALIDOS.items():
        if col in df.columns:
            fuera = ((df[col] < low) | (df[col] > high)).sum()
            filas.append(
                {
                    "columna": col,
                    "rango_esperado": f"[{low}, {high}]",
                    "fuera_de_rango": int(fuera),
                }
            )
    return pd.DataFrame(filas)


def evaluar_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta categorias no previstas en las variables cualitativas."""
    filas = []
    for col, validas in CATEGORIAS_ESPERADAS.items():
        if col in df.columns:
            presentes = set(_normaliza_texto(df[col]).unique())
            inesperadas = presentes - validas
            filas.append(
                {
                    "columna": col,
                    "categorias_presentes": ", ".join(sorted(presentes)),
                    "categorias_inesperadas": ", ".join(sorted(inesperadas)) or "-",
                }
            )
    return pd.DataFrame(filas)


def evaluar_atipicos(df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
    """Cantidad y porcentaje de valores atipicos por variable numerica (regla IQR)."""
    filas = []
    numericas = df.select_dtypes(include=[np.number]).columns
    for col in numericas:
        mascara = detectar_atipicos(df[col].to_numpy(), factor)
        n = int(mascara.sum())
        filas.append(
            {
                "columna": col,
                "atipicos": n,
                "pct_atipicos": round(n / len(df) * 100, 2),
            }
        )
    return pd.DataFrame(filas)


def resumen_calidad(df: pd.DataFrame) -> dict:
    """Consolida todos los indicadores de calidad en un solo diccionario.

    Returns:
        dict con DataFrames por dimension y un puntaje global 0-100.
    """
    completitud = evaluar_completitud(df)
    validez = evaluar_validez_rangos(df)
    categorias = evaluar_categorias(df)
    atipicos = evaluar_atipicos(df)
    duplicados = int(df.duplicated().sum())

    # Puntaje simple: penaliza faltantes, fuera de rango, categorias raras y duplicados.
    celdas = df.size
    pen_faltantes = df.isnull().sum().sum() / celdas
    pen_rango = validez["fuera_de_rango"].sum() / len(df) if len(validez) else 0
    pen_cat = sum(1 for c in categorias["categorias_inesperadas"] if c != "-")
    pen_dup = duplicados / len(df)
    puntaje = 100 * (1 - min(1, pen_faltantes + pen_rango + 0.05 * pen_cat + pen_dup))

    return {
        "completitud": completitud,
        "validez_rangos": validez,
        "categorias": categorias,
        "atipicos": atipicos,
        "duplicados": duplicados,
        "puntaje_global": round(float(puntaje), 1),
    }
