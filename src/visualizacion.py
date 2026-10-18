"""Construccion de graficos y dashboard exploratorio (Pregunta 1).

Genera las figuras del analisis exploratorio y las ensambla en un dashboard
HTML autocontenido (sin dependencias externas de servidor), que puede abrirse
en cualquier navegador para apoyar la interpretacion de los resultados.
"""
from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend no interactivo (reproducible en servidores/CI)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
PALETA = sns.color_palette("deep")


def _guardar_fig(fig, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return ruta


def grafico_latencia_por_servicio(df: pd.DataFrame, dir_fig: str) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.boxplot(data=df, x="tipo_servicio", y="latencia_ms", ax=ax)
    ax.set_title("Distribucion de latencia por tipo de servicio")
    ax.set_xlabel("Tipo de servicio")
    ax.set_ylabel("Latencia (ms)")
    return _guardar_fig(fig, Path(dir_fig) / "fig_latencia_servicio.png")


def grafico_incidencias_region(df: pd.DataFrame, dir_fig: str) -> Path:
    resumen = df.groupby("region")[["incidencias_reportadas", "tickets_soporte"]].sum()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    resumen.plot(kind="bar", ax=ax, color=PALETA[:2])
    ax.set_title("Incidencias y tickets de soporte por region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total acumulado")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(["Incidencias", "Tickets"])
    return _guardar_fig(fig, Path(dir_fig) / "fig_incidencias_region.png")


def grafico_trafico_vs_latencia(df: pd.DataFrame, dir_fig: str) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.scatterplot(
        data=df, x="trafico_datos_gb", y="latencia_ms",
        hue="cumplimiento_sla", ax=ax, alpha=0.8,
    )
    ax.set_title("Trafico de datos vs. latencia segun cumplimiento de SLA")
    ax.set_xlabel("Trafico de datos (GB)")
    ax.set_ylabel("Latencia (ms)")
    return _guardar_fig(fig, Path(dir_fig) / "fig_trafico_latencia.png")


def grafico_sla_por_servicio(df: pd.DataFrame, dir_fig: str) -> Path:
    tabla = pd.crosstab(df["tipo_servicio"], df["cumplimiento_sla"], normalize="index") * 100
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # Orden alfabetico de columnas: "Cumple" (verde), "No cumple" (rojo).
    tabla.plot(kind="barh", stacked=True, ax=ax, color=[PALETA[2], PALETA[3]])
    ax.set_title("Cumplimiento de SLA por tipo de servicio (%)")
    ax.set_xlabel("Porcentaje")
    ax.set_ylabel("Tipo de servicio")
    ax.legend(title="SLA", bbox_to_anchor=(1.02, 1), loc="upper left")
    return _guardar_fig(fig, Path(dir_fig) / "fig_sla_servicio.png")


def grafico_serie_temporal(df: pd.DataFrame, dir_fig: str) -> Path:
    serie = df.set_index("fecha_registro")["clientes_afectados"].resample("W").sum()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(serie.index, serie.values, marker="o", color=PALETA[0])
    ax.set_title("Clientes afectados por semana")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Clientes afectados (suma semanal)")
    fig.autofmt_xdate()
    return _guardar_fig(fig, Path(dir_fig) / "fig_serie_clientes.png")


def _img_base64(ruta: Path) -> str:
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def generar_todas_las_figuras(df: pd.DataFrame, dir_fig: str) -> list[Path]:
    """Genera las cinco figuras del analisis exploratorio."""
    return [
        grafico_latencia_por_servicio(df, dir_fig),
        grafico_incidencias_region(df, dir_fig),
        grafico_trafico_vs_latencia(df, dir_fig),
        grafico_sla_por_servicio(df, dir_fig),
        grafico_serie_temporal(df, dir_fig),
    ]


def construir_dashboard(df: pd.DataFrame, figuras: list[Path], ruta_html: str) -> Path:
    """Ensambla un dashboard HTML exploratorio con KPIs y las figuras.

    Las imagenes se incrustan en base64 para que el archivo sea autocontenido
    y portable (no requiere la carpeta de figuras para visualizarse).
    """
    total_reg = len(df)
    sla_cumple = (df["cumplimiento_sla"] == "Cumple").mean() * 100
    lat_media = df["latencia_ms"].mean()
    clientes = int(df["clientes_afectados"].sum())
    tickets = int(df["tickets_soporte"].sum())

    kpis = [
        ("Registros analizados", f"{total_reg}"),
        ("Cumplimiento de SLA", f"{sla_cumple:.1f}%"),
        ("Latencia media", f"{lat_media:.1f} ms"),
        ("Clientes afectados (total)", f"{clientes:,}"),
        ("Tickets de soporte (total)", f"{tickets:,}"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-val">{v}</div>'
        f'<div class="kpi-lbl">{k}</div></div>'
        for k, v in kpis
    )
    figs_html = "".join(
        f'<div class="card"><img src="data:image/png;base64,{_img_base64(f)}"></div>'
        for f in figuras
    )

    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard RedConecta Telecom</title>
<style>
  :root {{ --azul:#1f4e79; --bg:#f4f6f9; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:Segoe UI,Arial,sans-serif; margin:0; background:var(--bg); color:#222; }}
  header {{ background:var(--azul); color:#fff; padding:24px 32px; }}
  header h1 {{ margin:0; font-size:22px; }}
  header p {{ margin:6px 0 0; opacity:.85; font-size:14px; }}
  .kpis {{ display:flex; flex-wrap:wrap; gap:16px; padding:24px 32px; }}
  .kpi {{ background:#fff; border-radius:10px; padding:18px 22px; flex:1 1 160px;
          box-shadow:0 1px 4px rgba(0,0,0,.08); text-align:center; }}
  .kpi-val {{ font-size:26px; font-weight:700; color:var(--azul); }}
  .kpi-lbl {{ font-size:13px; color:#666; margin-top:4px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(360px,1fr));
           gap:20px; padding:0 32px 32px; }}
  .card {{ background:#fff; border-radius:10px; padding:12px;
           box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  .card img {{ width:100%; height:auto; border-radius:6px; }}
  footer {{ padding:16px 32px; font-size:12px; color:#888; }}
</style></head>
<body>
  <header>
    <h1>Dashboard exploratorio &mdash; RedConecta Telecom S. A.</h1>
    <p>Monitoreo de desempe&ntilde;o del servicio | Periodo: {df.fecha_registro.min():%d-%m-%Y} a {df.fecha_registro.max():%d-%m-%Y}</p>
  </header>
  <section class="kpis">{kpi_html}</section>
  <section class="grid">{figs_html}</section>
  <footer>Generado automaticamente por el flujo reproducible del proyecto (src/visualizacion.py).</footer>
</body></html>"""

    ruta = Path(ruta_html)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(html, encoding="utf-8")
    return ruta
