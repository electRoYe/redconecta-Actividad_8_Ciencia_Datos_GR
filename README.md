# RedConecta Telecom S. A. — Análisis operacional reproducible

Proyecto de ciencia de datos para analizar el desempeño del servicio de
telecomunicaciones de **RedConecta Telecom S. A.** y respaldar decisiones de
mejora de la calidad del servicio, mediante un flujo de trabajo reproducible,
código modular y control de versiones.

> Asignatura: Ciencia de Datos — Semana 8 (Unidad 3) · IACC

---

## 1. Objetivos

**General:** analizar la información operacional (tráfico, latencia, incidencias,
tickets de soporte, cumplimiento de SLA) para respaldar decisiones orientadas a
mejorar la calidad del servicio.

**Específicos:**
- Construir un flujo reproducible y documentado (scripts, librerías, versiones).
- Evaluar la calidad del dataset e identificar limitaciones.
- Implementar funciones reutilizables con **NumPy, SciPy y Joblib**.
- Generar un **dashboard exploratorio** y archivos de salida para dos áreas.

## 2. Preguntas de investigación

1. ¿Cómo se relacionan el tráfico, las incidencias y la carga de soporte con la
   calidad del servicio?
2. ¿Qué diferencias de desempeño existen entre regiones y tipos de servicio?
3. ¿Qué tan confiable es el dataset para sustentar decisiones operativas?

## 3. Estructura del repositorio

```
proyecto/
├── data/
│   ├── raw/              # Dataset oficial (entrada, no se modifica)
│   └── processed/        # Salidas por área (Soporte Técnico, Experiencia Clientes)
├── src/                  # Código modular reutilizable
│   ├── estadistica.py    # Funciones NumPy / SciPy (descriptivos, IC, correlación, t)
│   ├── calidad_datos.py  # Evaluación de calidad del dataset
│   ├── io_salidas.py     # Carga (Joblib cache) y archivos de salida
│   └── visualizacion.py  # Figuras y dashboard HTML
├── notebooks/
│   └── analisis_redconecta.ipynb   # Análisis guiado paso a paso
├── outputs/
│   ├── figures/          # Gráficos PNG del análisis exploratorio
│   └── dashboard.html    # Dashboard exploratorio autocontenido
├── docs/
│   └── documentacion_tecnica.md    # Documentación técnica detallada
├── main.py               # Orquesta el flujo completo de principio a fin
├── requirements.txt      # Dependencias con versiones fijadas
├── .gitignore
└── README.md
```

## 4. Instalación y ejecución

Requisitos: **Python 3.10+**.

```bash
# 1. (Opcional) crear entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el flujo completo
python main.py
```

El script `main.py` carga los datos, evalúa su calidad, ejecuta el análisis
estadístico, genera las figuras y el dashboard, y escribe los archivos de salida.

Para el análisis guiado:

```bash
jupyter notebook notebooks/analisis_redconecta.ipynb
```

## 5. Etapas del análisis

1. **Carga y limpieza** — lectura del Excel, normalización de texto y orden por
   fecha. Cacheada con Joblib para acelerar re-ejecuciones.
2. **Evaluación de calidad** — completitud, duplicados, validez de rangos,
   categorías esperadas y atípicos (regla IQR). Entrega un puntaje global.
3. **Análisis estadístico** — descriptivos, intervalos de confianza,
   correlaciones de Pearson y prueba t de Welch (NumPy + SciPy).
4. **Visualización** — cinco gráficos exploratorios y un dashboard HTML con KPIs.
5. **Salidas por área** — archivos para Soporte Técnico y Experiencia de Clientes.

## 6. Principales resultados

- **Calidad del dataset: 95/100.** 100% de completitud, sin duplicados ni valores
  fuera de rango; sin atípicos según la regla IQR (consistente con datos
  controlados/sintéticos).
- **Latencia media:** ≈ 64.9 ms (IC 95%: 60.3–69.5 ms).
- **Correlaciones débiles y no significativas** entre tráfico y latencia, e
  incidencias y tickets: el análisis permite *descartar* relaciones aparentes.
- Las diferencias relevantes aparecen por **región y tipo de servicio**, insumo
  para priorizar recursos de soporte y mejorar la experiencia del cliente.

## 7. Archivos de salida

| Área | Archivo | Variables |
|------|---------|-----------|
| Soporte Técnico | `data/processed/salida_soporte_tecnico.{xlsx,csv}` | fecha, región, tipo de servicio, incidencias, tickets, tiempo de resolución, tickets/incidencia |
| Experiencia de Clientes | `data/processed/salida_experiencia_clientes.{xlsx,csv}` | fecha, tipo de servicio, clientes afectados, latencia, cumplimiento SLA, nivel de latencia |

## 8. Tecnologías

`pandas` · `numpy` · `scipy` · `joblib` · `matplotlib` · `seaborn` · `jupyter`

## 9. Reproducibilidad y control de versiones

- Dependencias fijadas en `requirements.txt`.
- Semilla aleatoria fija (`np.random.seed(42)`).
- Rutas relativas a la raíz del proyecto.
- Historial de cambios versionado con Git (ver `git log`).

---

*Equipo de Ciencia de Datos — RedConecta Telecom S. A.*
