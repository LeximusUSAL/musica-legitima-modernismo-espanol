# Resumen del Proyecto: Construir la Música Legítima

## Información del Repositorio

**URL:** https://github.com/LeximusUSAL/musica-legitima-modernismo-espanol

**Creado:** 11 noviembre 2025

## Contexto Académico

**Proyecto:** LexiMus: Léxico y Ontología de la Música en Español
**Código:** PID2022-139589NB-C33
**Institución:** Universidad de Salamanca

## Contenido del Repositorio

### Estructura de Archivos

```
musica-legitima-modernismo-espanol/
├── README.md (7.7 KB)
├── LICENSE (MIT)
├── .gitignore
├── scripts/ (12 scripts Python)
│   ├── analisis_rapido_musica.py
│   ├── analisis_semanticas_musica.py
│   ├── analisis_temporal_detallado.py
│   ├── analiza_musica.py
│   ├── analizador_valoraciones_critica_mejorado.py
│   ├── analizador_ventana_colocacional.py
│   ├── analizador_ventana_rapido.py
│   ├── detector_genero_musical.py
│   ├── generar_grafico_valoraciones_actualizado.py
│   ├── generar_graficos.py
│   ├── generar_tabla_valoraciones.py
│   └── refinar_analisis_musica.py
├── datos/ (18 archivos de resultados)
│   ├── analisis_completo_musica.json (1.3 MB)
│   ├── analisis_filtrado_musica.json (1.2 MB)
│   ├── resultados_musica_spacy_completo.html (513 KB)
│   ├── LISTA_COMPLETA_ADJETIVOS_VALIDADOS_5607.txt
│   ├── comparacion_metodos_adjetivacion.csv
│   └── [otros archivos CSV/JSON]
└── docs/
    └── articulo_construir_musica_legitima.txt
```

### Total de Archivos Subidos: 31 archivos

## Datos del Corpus

- **Palabras totales:** 2.535.146
- **Archivos analizados:** 1.842 archivos .txt
- **Adjetivos identificados:** 5.607 ocurrencias
- **Adjetivos únicos:** 942

### Publicaciones Analizadas

1. **El Sol** (1918-1932)
   - 1.273 documentos
   - 1.197.469 palabras

2. **Ondas** (1925-1935)
   - 259 números
   - 1.023.495 palabras

3. **España** (1915-1924)
   - 310 artículos
   - 132.182 palabras

## Metodología

### Tecnologías
- Python 3.8+
- spaCy 3.0+ (modelo es_core_news_md)
- Plotly.js 3.2.0
- NLP: análisis morfológico, sintáctico y de dependencias

## Scripts Destacados

### 1. detector_genero_musical.py
Análisis automático de sesgo de género:
- Listas de nombres históricos españoles
- Patrones de tratamiento formal (Don/Doña)
- Ratios de representación masculino/femenino

### 2. analizador_valoraciones_critica_mejorado.py
Análisis multinivel de valoraciones:
- Nivel 1: Adjetivos directos
- Nivel 2: Términos relacionados
- Nivel 3: Ventana expandida (±7 palabras)
- Nivel 4: Análisis contextual (negaciones, intensificadores)

### 3. analizador_ventana_colocacional.py
Análisis de colocaciones y contextos expandidos

### 4. generar_graficos.py
Visualizaciones interactivas con Plotly

## Uso del Repositorio

### Instalación de Dependencias

```bash
pip install spacy
python -m spacy download es_core_news_md
pip install plotly pandas
```

### Ejecución de Scripts

```bash
# Desde la raíz del proyecto
cd musica-legitima-modernismo-espanol

# Análisis básico
python scripts/analisis_rapido_musica.py

# Análisis completo
python scripts/analisis_semanticas_musica.py

# Detección de género
python scripts/detector_genero_musical.py
```

## Licencia

MIT License - Universidad de Salamanca, 2025

