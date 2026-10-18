"""Funciones estadisticas reutilizables para el monitoreo de red.

Este modulo concentra el calculo numerico del proyecto usando NumPy y SciPy.
Al mantener estas funciones en un archivo externo (codigo modular) se habilita
su reutilizacion desde el notebook, los scripts y futuros analisis, evitando
duplicar logica y facilitando las pruebas.

Pregunta de investigacion asociada (P4): el uso de codigo modular con librerias
adicionales (NumPy, SciPy, Joblib) permite estandarizar los calculos, acelerar
el procesamiento y garantizar que cada analisis sea reproducible.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def resumen_descriptivo(valores: np.ndarray) -> dict:
    """Devuelve estadisticos descriptivos robustos de un vector numerico.

    Usa NumPy para los momentos clasicos y SciPy para asimetria y curtosis,
    que ayudan a detectar distribuciones sesgadas (p. ej. latencias extremas).

    Args:
        valores: arreglo 1-D de NumPy o secuencia convertible a arreglo.

    Returns:
        Diccionario con n, media, mediana, desviacion estandar, minimo,
        maximo, rango intercuartilico (IQR), asimetria y curtosis.
    """
    x = np.asarray(valores, dtype=float)
    x = x[~np.isnan(x)]
    if x.size == 0:
        raise ValueError("El vector de valores esta vacio tras eliminar NaN.")

    q1, q3 = np.percentile(x, [25, 75])
    return {
        "n": int(x.size),
        "media": float(np.mean(x)),
        "mediana": float(np.median(x)),
        "desv_std": float(np.std(x, ddof=1)),
        "minimo": float(np.min(x)),
        "maximo": float(np.max(x)),
        "iqr": float(q3 - q1),
        "asimetria": float(stats.skew(x)),
        "curtosis": float(stats.kurtosis(x)),
    }


def limites_iqr(valores: np.ndarray, factor: float = 1.5) -> tuple[float, float]:
    """Calcula los limites inferior y superior segun la regla del IQR.

    Los valores fuera de [Q1 - k*IQR, Q3 + k*IQR] se consideran atipicos.

    Args:
        valores: arreglo numerico.
        factor: multiplicador del IQR (1.5 estandar; 3.0 para atipicos extremos).

    Returns:
        Tupla (limite_inferior, limite_superior).
    """
    x = np.asarray(valores, dtype=float)
    q1, q3 = np.percentile(x[~np.isnan(x)], [25, 75])
    iqr = q3 - q1
    return float(q1 - factor * iqr), float(q3 + factor * iqr)


def detectar_atipicos(valores: np.ndarray, factor: float = 1.5) -> np.ndarray:
    """Devuelve una mascara booleana con los valores atipicos (regla IQR)."""
    x = np.asarray(valores, dtype=float)
    low, high = limites_iqr(x, factor)
    return (x < low) | (x > high)


def intervalo_confianza_media(valores: np.ndarray, confianza: float = 0.95) -> tuple[float, float]:
    """Intervalo de confianza para la media usando la distribucion t de Student.

    Util para reportar la incertidumbre de indicadores como la latencia media.
    """
    x = np.asarray(valores, dtype=float)
    x = x[~np.isnan(x)]
    n = x.size
    media = np.mean(x)
    error = stats.sem(x)
    margen = error * stats.t.ppf((1 + confianza) / 2.0, n - 1)
    return float(media - margen), float(media + margen)


def correlacion_pearson(x: np.ndarray, y: np.ndarray) -> dict:
    """Coeficiente de correlacion de Pearson y su p-valor (SciPy).

    Permite cuantificar relaciones como trafico vs. latencia o
    incidencias vs. tickets de soporte.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mascara = ~(np.isnan(x) | np.isnan(y))
    r, p = stats.pearsonr(x[mascara], y[mascara])
    return {"r": float(r), "p_valor": float(p)}


def prueba_t_dos_grupos(grupo_a: np.ndarray, grupo_b: np.ndarray) -> dict:
    """Prueba t de Welch para comparar la media de dos grupos independientes.

    Ejemplo de uso: comparar el tiempo de resolucion entre registros que
    cumplen y no cumplen el SLA.
    """
    a = np.asarray(grupo_a, dtype=float)
    b = np.asarray(grupo_b, dtype=float)
    t, p = stats.ttest_ind(a[~np.isnan(a)], b[~np.isnan(b)], equal_var=False)
    return {"t": float(t), "p_valor": float(p), "significativo_05": bool(p < 0.05)}


def normalizar_min_max(valores: np.ndarray) -> np.ndarray:
    """Escala un vector al rango [0, 1] con NumPy (util para indicadores)."""
    x = np.asarray(valores, dtype=float)
    rango = np.nanmax(x) - np.nanmin(x)
    if rango == 0:
        return np.zeros_like(x)
    return (x - np.nanmin(x)) / rango
