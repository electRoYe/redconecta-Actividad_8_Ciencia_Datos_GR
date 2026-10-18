# Documentación técnica — Proyecto RedConecta Telecom

Documento de apoyo para la **comprensión técnica y la reutilización futura** del
proyecto (Pregunta 3). Describe el flujo de trabajo, la estructura de datos, los
módulos y las decisiones de diseño.

## 1. Flujo de trabajo reproducible

```
dataset_set_D_telecomunicaciones.xlsx
          │
          ▼
  io_salidas.cargar_dataset()  ── Joblib cache ──►  DataFrame limpio
          │
          ├──►  calidad_datos.resumen_calidad()      → evaluación de calidad
          ├──►  estadistica.*                          → descriptivos, IC, correlación, t
          ├──►  visualizacion.generar_todas_las_figuras() → PNG + dashboard.html
          └──►  io_salidas.salida_soporte_tecnico()    → xlsx/csv
               io_salidas.salida_experiencia_clientes()→ xlsx/csv
```

Toda la orquestación está en `main.py`. Cada etapa es independiente y puede
reutilizarse desde el notebook o desde otros scripts.

## 2. Diccionario de datos (dataset de entrada)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `fecha_registro` | fecha | Día del registro operacional |
| `region` | texto | Norte / Centro / Sur |
| `tipo_servicio` | texto | Móvil / Internet Hogar / Empresas |
| `trafico_datos_gb` | float | Tráfico de datos cursado (GB) |
| `latencia_ms` | float | Latencia media de la red (ms) |
| `incidencias_reportadas` | int | Incidencias técnicas del período |
| `tickets_soporte` | int | Tickets de soporte generados |
| `tiempo_resolucion_hr` | float | Tiempo medio de resolución (horas) |
| `clientes_afectados` | int | Clientes impactados |
| `cumplimiento_sla` | texto | Cumple / No cumple |

Dimensiones: **200 registros × 10 columnas**. Período: 01-03-2025 a 16-09-2025.

## 3. Módulos (código modular)

### `src/estadistica.py` (NumPy + SciPy)
Funciones puras y reutilizables:
- `resumen_descriptivo` — n, media, mediana, desviación, IQR, asimetría, curtosis.
- `limites_iqr` / `detectar_atipicos` — detección de valores atípicos.
- `intervalo_confianza_media` — IC de la media con distribución t.
- `correlacion_pearson` — coeficiente r y p-valor.
- `prueba_t_dos_grupos` — prueba t de Welch entre dos grupos.
- `normalizar_min_max` — escalado a [0, 1].

### `src/calidad_datos.py`
Evalúa las dimensiones de calidad: completitud, unicidad, validez de rangos,
categorías esperadas y atípicos. Entrega un **puntaje global 0–100**.

### `src/io_salidas.py` (Joblib)
- `cargar_dataset` — decorada con `@memory.cache`: la limpieza se calcula una vez
  y se reutiliza mientras el archivo no cambie.
- `salida_soporte_tecnico` / `salida_experiencia_clientes` — generan los archivos
  por área (xlsx + csv) con indicadores derivados.
- `persistir_artefacto` — serializa resultados con `joblib.dump`.

### `src/visualizacion.py` (Matplotlib + Seaborn)
Genera cinco figuras y ensambla `dashboard.html` (imágenes embebidas en base64,
archivo autocontenido y portable).

## 4. Buenas prácticas aplicadas

- **Separación de responsabilidades:** datos, cálculo, E/S y visualización en
  módulos distintos.
- **Funciones documentadas** con *docstrings* y *type hints*.
- **Rutas relativas** a la raíz → portabilidad entre equipos.
- **Versiones fijadas** en `requirements.txt` y **semilla** fija.
- **Cache** con Joblib para eficiencia y reproducibilidad.
- **Control de versiones** con Git (commits temáticos).

## 5. Evaluación de calidad de datos (Pregunta 5)

El dataset obtiene **95/100**: completitud total, sin duplicados ni valores fuera
de rango, sin atípicos (regla IQR). Esto es coherente con datos
sintéticos/controlados.

**Consecuencias de usar datos de baja confiabilidad** (si el dataset fuera real y
tuviera problemas):
- *Datos faltantes o erróneos* → KPIs sesgados y mala asignación de recursos.
- *Categorías inconsistentes* (p. ej. "Movil" vs "Móvil ") → conteos partidos.
- *Duplicados* → sobreestimación de incidencias y clientes afectados.
- *Valores fuera de rango* (latencias negativas) → modelos y alertas poco fiables.

Por eso los chequeos quedan **incorporados al flujo**: protegen el análisis ante
futuras cargas de datos reales.

## 6. Extensión y mantenimiento

Para incorporar nuevos datos: reemplazar/añadir el Excel en `data/raw/` y volver a
ejecutar `python main.py`. Para nuevos análisis: agregar funciones en `src/` y
llamarlas desde `main.py` o el notebook, manteniendo el estilo modular.
