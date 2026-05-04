# Análisis de opiniones — Samsung Galaxy S24 Ultra

Scripts en Python que acompañan al trabajo académico de la asignatura
**Técnicas de Extracción y Almacenamiento de Datos Masivos** de la
Fundación Universitaria Compensar.

El pipeline corresponde a la **etapa de contextualización** del
proyecto: extracción de comentarios, análisis estadístico de una
encuesta, análisis de sentimiento con BERT y análisis de frecuencia
de palabras.

## Estructura del proyecto

```
.
├── main.py
├── pyproject.toml
├── README.md
└── src/
    └── contextualization/
        ├── __init__.py
        ├── cli.py
        ├── extraction_scraping.py
        ├── statistical_analysis.py
        ├── sentiment_analysis.py
        └── word_frequency.py
```

## Instalación

1. Asegúrate de tener **Python 3.10 o superior** instalado.
2. Crea y activa un entorno virtual:

   ```bash
   python -m venv env
   source env/bin/activate     # Linux / macOS
   env\Scripts\activate        # Windows
   ```

3. Instala el proyecto en modo editable (esto instala el paquete
   `contextualization` y todas sus dependencias declaradas en
   `pyproject.toml`):

   ```bash
   pip install -e .
   ```

Tras la instalación quedan disponibles tres formas equivalentes de
ejecutar el pipeline:

```bash
contextualization <paso>             # comando global (recomendado)
python -m contextualization.cli <paso>
python main.py <paso>
```

donde `<paso>` es uno de: `extraction`, `statistics`, `sentiment`,
`frequency` o `all`.

## Orden de ejecución

Ejecuta los pasos **en orden**, ya que cada etapa consume las
salidas de la anterior.

### 1. Extracción de comentarios (`extraction`)

Antes de correr este paso:

1. Crea una cuenta de desarrollador en <https://developer.x.com>.
2. Genera un **Bearer Token**.
3. Expónlo como variable de entorno:

   ```bash
   export X_BEARER_TOKEN="tu_token_aqui"     # Linux / macOS
   set X_BEARER_TOKEN=tu_token_aqui          # Windows CMD
   ```

4. Ejecuta:

   ```bash
   contextualization extraction
   ```

**Salida**: `s24_comments.db` (SQLite) con los tweets extraídos.

### 2. Análisis estadístico (`statistics`)

Procesa los datos de la encuesta y genera estadísticas resumidas:

```bash
contextualization statistics
```

**Salidas**:

- `survey_statistics.csv` — tabla de estadísticas.
- `likert_distribution.png` — gráfico de distribución Likert.
- `averages.png` — gráfico de medias / medianas.

### 3. Análisis de sentimiento (`sentiment`)

Clasifica cada comentario como positivo, neutral o negativo:

```bash
contextualization sentiment
```

> **Nota**: la primera ejecución descarga el modelo BERT (~700 MB).
> Requiere **mínimo 4 GB de RAM** disponibles.

**Salidas**:

- `classified_comments.csv` — comentarios con su sentimiento.
- `sentiment_by_aspect.csv` — análisis por aspecto del producto.
- `sentiment_distribution.png` — gráficos de distribución.

### 4. Análisis de frecuencia de palabras (`frequency`)

Identifica las palabras más mencionadas en los comentarios:

```bash
contextualization frequency
```

**Salidas**:

- `word_frequency.csv` — tabla de frecuencias.
- `word_frequency.png` — gráfico de barras.

### Pipeline completo

Para correr las cuatro etapas seguidas:

```bash
contextualization all
```

## Notas de privacidad

Todos los scripts cumplen con la **Ley 1581 de 2012** (Régimen General
de Protección de Datos Personales en Colombia) mediante:

- **Anonimización** de los IDs de usuario con hash SHA-256.
- **Minimización de datos**: solo se recolectan los campos necesarios.
- **Cifrado en tránsito** vía HTTPS.
- **Tokens de acceso** gestionados a través de variables de entorno
  (nunca en el código fuente).

## Solución de problemas

| Problema | Solución |
|---|---|
| `ImportError: No module named 'tweepy'` | Ejecuta `pip install -e .` con el entorno virtual activado. |
| `ValueError: Token not found` | Define la variable de entorno `X_BEARER_TOKEN`. |
| `Out of memory` en el paso 3 | BERT requiere ≥ 4 GB de RAM. Cierra otras aplicaciones. |
| `LookupError` con NLTK | El script descarga los stopwords automáticamente en la primera ejecución; verifica conexión a internet. |

## Autor

**Fabian Rodríguez**
Técnicas de Extracción y Almacenamiento de Datos Masivos
Fundación Universitaria Compensar — 2026
