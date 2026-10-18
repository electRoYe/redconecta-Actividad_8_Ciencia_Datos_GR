"""Flujo de trabajo reproducible - Proyecto RedConecta Telecom S. A.

Ejecuta de principio a fin el analisis operacional:
    1. Carga y limpieza del dataset (cacheada con Joblib).
    2. Evaluacion de la calidad de los datos.
    3. Analisis estadistico (NumPy / SciPy).
    4. Generacion de figuras y dashboard exploratorio.
    5. Archivos de salida para Soporte Tecnico y Experiencia de Clientes.

Uso:
    python main.py

Todas las rutas son relativas a la raiz del proyecto, por lo que el script
es reproducible en cualquier equipo que instale requirements.txt.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src import calidad_datos, io_salidas, visualizacion
from src.estadistica import (
    correlacion_pearson,
    intervalo_confianza_media,
    prueba_t_dos_grupos,
    resumen_descriptivo,
)

RAIZ = Path(__file__).resolve().parent
RUTA_DATOS = RAIZ / "data" / "raw" / "dataset_set_D_telecomunicaciones.xlsx"
DIR_PROCESADO = RAIZ / "data" / "processed"
DIR_FIGURAS = RAIZ / "outputs" / "figures"
DIR_OUTPUTS = RAIZ / "outputs"


def separador(titulo: str) -> None:
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def main() -> None:
    separador("1. CARGA Y LIMPIEZA DEL DATASET (Joblib cache)")
    df = io_salidas.cargar_dataset(str(RUTA_DATOS))
    print(f"Registros: {len(df)} | Columnas: {len(df.columns)}")
    print(f"Periodo: {df.fecha_registro.min():%d-%m-%Y} a {df.fecha_registro.max():%d-%m-%Y}")

    separador("2. EVALUACION DE CALIDAD DE DATOS (Pregunta 5)")
    calidad = calidad_datos.resumen_calidad(df)
    print("Completitud por columna (%):")
    print(calidad["completitud"]["pct_completitud"].to_string())
    print(f"\nRegistros duplicados: {calidad['duplicados']}")
    print("\nValores fuera de rango operativo:")
    print(calidad["validez_rangos"].to_string(index=False))
    print("\nValores atipicos (regla IQR):")
    print(calidad["atipicos"].to_string(index=False))
    print(f"\nPuntaje global de calidad: {calidad['puntaje_global']} / 100")

    separador("3. ANALISIS ESTADISTICO (NumPy / SciPy)")
    print("Resumen descriptivo de la latencia (ms):")
    desc = resumen_descriptivo(df["latencia_ms"].to_numpy())
    for k, v in desc.items():
        print(f"  {k:12s}: {v:.3f}" if isinstance(v, float) else f"  {k:12s}: {v}")

    ic = intervalo_confianza_media(df["latencia_ms"].to_numpy())
    print(f"\nIC 95% para la latencia media: [{ic[0]:.2f}, {ic[1]:.2f}] ms")

    corr = correlacion_pearson(
        df["trafico_datos_gb"].to_numpy(), df["latencia_ms"].to_numpy()
    )
    print(f"\nCorrelacion trafico vs. latencia: r={corr['r']:.3f} (p={corr['p_valor']:.3f})")

    corr2 = correlacion_pearson(
        df["incidencias_reportadas"].to_numpy(), df["tickets_soporte"].to_numpy()
    )
    print(f"Correlacion incidencias vs. tickets: r={corr2['r']:.3f} (p={corr2['p_valor']:.3f})")

    cumple = df.loc[df["cumplimiento_sla"] == "Cumple", "tiempo_resolucion_hr"].to_numpy()
    no_cumple = df.loc[df["cumplimiento_sla"] == "No cumple", "tiempo_resolucion_hr"].to_numpy()
    tt = prueba_t_dos_grupos(cumple, no_cumple)
    print(
        f"\nPrueba t (tiempo resolucion, Cumple vs No cumple): "
        f"t={tt['t']:.3f}, p={tt['p_valor']:.3f}, "
        f"significativo={tt['significativo_05']}"
    )

    separador("4. FIGURAS Y DASHBOARD EXPLORATORIO (Pregunta 1)")
    figuras = visualizacion.generar_todas_las_figuras(df, str(DIR_FIGURAS))
    for f in figuras:
        print(f"  Figura generada: {f.relative_to(RAIZ)}")
    dashboard = visualizacion.construir_dashboard(
        df, figuras, str(DIR_OUTPUTS / "dashboard.html")
    )
    print(f"  Dashboard: {dashboard.relative_to(RAIZ)}")

    separador("5. ARCHIVOS DE SALIDA POR AREA")
    sop = io_salidas.salida_soporte_tecnico(df, str(DIR_PROCESADO))
    exp = io_salidas.salida_experiencia_clientes(df, str(DIR_PROCESADO))
    print(f"  Soporte Tecnico       -> {len(sop)} filas (xlsx + csv)")
    print(f"  Experiencia Clientes  -> {len(exp)} filas (xlsx + csv)")

    # Persistencia del resumen de calidad como artefacto reproducible (Joblib).
    io_salidas.persistir_artefacto(
        {"descriptivo_latencia": desc, "ic_latencia": ic, "calidad_global": calidad["puntaje_global"]},
        str(DIR_OUTPUTS / "artefacto_analisis.joblib"),
    )
    print("\nFlujo completado correctamente.")


if __name__ == "__main__":
    np.random.seed(42)  # reproducibilidad
    main()
