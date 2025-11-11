# Repositorio para investigación sobre estrategias Léxicas y poder simbólico en la Prensa del Modernismo Español

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/spaCy-3.0+-green.svg)](https://spacy.io/)

## Descripción del Proyecto

Este repositorio contiene el código, datos y documentación de la investigación **"Construir la música legítima: estrategias léxicas y poder simbólico en la prensa del modernismo español (El Sol, España y Ondas, 1915-1935)"**.

La investigación analiza la adjetivación del concepto "música" como estrategia discursiva para legitimar jerarquías culturales en tres publicaciones paradigmáticas del modernismo español. Mediante metodologías mixtas que combinan análisis cualitativo tradicional con procesamiento de lenguaje natural (NLP), se identificaron **5.607 adjetivos asociados al término "música"** en un corpus de **2.535.146 palabras** distribuidas en **1.842 archivos**.

### Publicaciones Analizadas

1. **El Sol** (1918-1932) - 1.273 documentos, 1.197.469 palabras
2. **Ondas** (1925-1935) - 259 números, 1.023.495 palabras
3. **España** (1915-1924) - 310 artículos, 132.182 palabras

### Acceso al Corpus

Puede consultarse el corpus utilizado en esta investigación, en formato **carrel de Distant Reader** (Eric Lease Morgan):

- **El Sol**: https://leximususal.github.io/el-sol-spanish-filtered/index.txt
- **Ondas**: https://leximususal.github.io/ondas-carrel/index.txt
- **Semanario España**: https://leximususal.github.io/revista-espana-carrel/index.txt

## Contexto Académico

**Investigación realizada dentro del Proyecto LexiMus:**

**LexiMus: Léxico y Ontología de la Música en Español**
PID2022-139589NB-C33
Universidad de Salamanca

**Autora:** María Palacios Nieto
**Institución:** Universidad de Salamanca
**Área:** Musicología Digital, Humanidades Digitales

## Marco Teórico

El análisis se fundamenta en tres ejes teóricos:

- **Análisis Crítico del Discurso** (Van Dijk, Fairclough)
- **Campos de Poder Simbólico** (Bourdieu)
- **Historia Conceptual** (Koselleck, De Bolla)

## Hallazgos Principales

### Categorías Semánticas Identificadas

| Categoría | % del Corpus | Ejemplos |
|-----------|--------------|----------|
| Nacionalidad | 17.6% | española, francesa, alemana, rusa |
| Tipo de música | 14.7% | sinfónica, coral, operística, ligera |
| Modernidad/Novedad | 10.9% | moderna, contemporánea, nueva, actual |
| Valoración positiva | 3.9% | excelente, hermosa, sublime, admirable |
| Carácter social | 6.2% | aristocrática, popular, culta, seria |
| Valoración negativa | 0.4% | inferior, mediocre, vulgar |

### Patrones Discursivos Clave

1. **Paradigma Nacionalista**: El Sol lidera con "música española" (10.7% del discurso)
2. **Discurso de Modernidad**: 13.9% de adjetivos relacionados con lo nuevo/contemporáneo
3. **Jerarquización Estética**: Clara dicotomía "música seria" vs. "música ligera"
4. **Hegemonía Francesa**: "Música francesa" supera ampliamente a otras geografías

## Estructura del Repositorio

```
musica-legitima-modernismo-espanol/
├── README.md                    # Este archivo
├── RESUMEN_PROYECTO.md          # Guía completa del proyecto
├── LICENSE                      # Licencia MIT
├── scripts/                     # Scripts de análisis Python
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
└── datos/                       # Datos de análisis
    ├── analisis_completo_musica.json
    ├── analisis_filtrado_musica.json
    ├── comparacion_metodos_adjetivacion.csv
    ├── resultados_musica_spacy_completo.html
    ├── resultados_valoraciones_mejorado.json
    ├── LISTA_COMPLETA_ADJETIVOS_VALIDADOS_5607.txt
    └── [otros archivos de datos]
```

## Metodología

### Tecnologías Utilizadas

- **Python 3.8+**
- **spaCy 3.0+** con modelo `es_core_news_md`
- **Plotly.js 3.2.0** para visualizaciones
- **NLP**: Análisis morfológico, sintáctico y de dependencias

### Pipeline de Análisis

```
Textos históricos → Extracción OCR → Limpieza →
spaCy NLP → Extracción adjetivos → Categorización semántica →
Análisis estadístico → Visualización
```

### Scripts Principales

#### 1. `analiza_musica.py`
Identifica lemas de "música" y adjetivos mediante análisis de dependencias sintácticas.

#### 2. `detector_genero_musical.py`
Detecta automáticamente menciones de género (masculino/femenino) en personas musicales mediante:
- Listas de nombres históricos españoles
- Patrones de tratamiento formal
- Análisis estadístico de sesgo de género

#### 3. `analizador_valoraciones_critica_mejorado.py`
Análisis multinivel de valoraciones críticas:
- Nivel 1: Adjetivos directos sobre "música"
- Nivel 2: Términos relacionados (concierto, interpretación)
- Nivel 3: Construcciones predicativas (ventana ±7 palabras)
- Nivel 4: Análisis contextual (negaciones, intensificadores)

#### 4. `analizador_ventana_colocacional.py`
Análisis de colocaciones y contextos expandidos para capturar construcciones complejas.

#### 5. `generar_graficos.py`
Generación de visualizaciones interactivas con Plotly.

## Uso de los Scripts

### Requisitos

```bash
pip install spacy
python -m spacy download es_core_news_md
pip install plotly pandas
```

### Ejecución Básica

```bash
# Análisis rápido
python scripts/analisis_rapido_musica.py

# Análisis semántico completo
python scripts/analisis_semanticas_musica.py

# Detector de género
python scripts/detector_genero_musical.py

# Análisis de valoraciones
python scripts/analizador_valoraciones_critica_mejorado.py
```

## Datos

### Corpus Originales

Los textos originales fueron extraídos de:
- Hemeroteca Digital de la Biblioteca Nacional de España
- Hemeroteca Municipal de Madrid

El corpus completo está disponible en formato **Distant Reader (carrel)** creado por Eric Lease Morgan. Ver enlaces en la sección [Acceso al Corpus](#acceso-al-corpus).

### Datos Procesados

Los archivos JSON contienen:
- Frecuencias de adjetivos por publicación y período
- Categorías semánticas asignadas
- Estadísticas temporales y comparativas
- Colocaciones y contextos

## Resultados y Visualizaciones

Los scripts generan:
- **Gráficos interactivos HTML** (Plotly)
- **Tablas CSV** para análisis estadístico
- **Archivos JSON** con datos estructurados
- **Reportes de texto** con hallazgos principales

## Citar este Trabajo

```bibtex
@article{palacios2025construir,
  title={Construir la música legítima: estrategias léxicas y poder simbólico en la prensa del modernismo español (El Sol, España y Ondas, 1915-1935)},
  author={Palacios Nieto, María},
  journal={[Revista]},
  year={2025},
  institution={Universidad de Salamanca},
  note={Proyecto LexiMus (PID2022-139589NB-C33)}
}
```

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

**María Palacios Nieto**
Universidad de Salamanca
Proyecto LexiMus: Léxico y Ontología de la Música en Español

## Agradecimientos

Este proyecto ha sido financiado por:
- **Proyecto LexiMus** (PID2022-139589NB-C33)
- Universidad de Salamanca
- Instituto Complutense de Ciencias Musicales
- Universidad de La Rioja

Agradecimiento especial a **Eric Lease Morgan** por el desarrollo de Distant Reader.

## Referencias Bibliográficas

- Bourdieu, P. (1979). *La Distinction*. Minuit.
- De Bolla, P. (2013). *The Architecture of Concepts*. Fordham University Press.
- Fairclough, N. (2010). *Critical Discourse Analysis*. Routledge.
- Koselleck, R. (2004). *Futures Past*. Columbia University Press.
- Van Dijk, T. (2001). *Critical Discourse Analysis*. Handbook of Discourse Analysis.

---

**Generado:** Noviembre 2024
**Versión:** 1.0
