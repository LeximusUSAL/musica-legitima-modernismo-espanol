#!/usr/bin/env python3
"""
Análisis rápido de adjetivaciones de 'música' usando expresiones regulares
Mucho más rápido que spaCy para corpus grandes
"""

import re
from pathlib import Path
from collections import Counter, defaultdict
import json

# Lista de adjetivos comunes en español (simplificado)
ADJETIVOS_PATTERN = r'\b([a-záéíóúñ]+[ao]s?|clásic[ao]s?|modern[ao]s?|contemporáne[ao]s?|nacional|española?|francés|francesa|alemán|alemana|italiano|italiana|ruso|rusa|inglés|inglesa|popular|populares|sinfónic[ao]s?|religiosa?s?|teatral|dramátic[ao]s?|vocal|instrumental|orquestal|ligera?s?|nueva?s?|antigua?s?|actual|tradicional|folklóric[ao]s?|bailable|selecta?s?|fina?s?|buena?s?|gran|grande|pequeña?s?)\b'

def extraer_adjetivos_musica(texto):
    """Extrae adjetivos cercanos a la palabra 'música' usando regex"""
    adjetivos = []

    # Buscar "música" y capturar contexto cercano
    patron_musica = re.compile(
        r'(?:\b\w+\b\s+){0,3}música(?:\s+\b\w+\b){0,3}',
        re.IGNORECASE
    )

    for match in patron_musica.finditer(texto):
        contexto = match.group()
        # Buscar adjetivos en el contexto
        for adj_match in re.finditer(ADJETIVOS_PATTERN, contexto, re.IGNORECASE):
            adj = adj_match.group(1).lower()
            # Filtrar palabras muy cortas o que no terminan como adjetivos
            if len(adj) >= 4:
                adjetivos.append(adj)

    return adjetivos

def procesar_carpeta(ruta, nombre_publicacion):
    """Procesa todos los archivos .txt de una carpeta"""
    carpeta = Path(ruta)
    archivos = list(carpeta.rglob("*.txt"))

    print(f"\nProcesando {nombre_publicacion}: {len(archivos)} archivos...")

    resultados = []
    todos_adjetivos = Counter()
    temporal_data = defaultdict(lambda: Counter())

    for i, archivo in enumerate(archivos, 1):
        if i % 100 == 0:
            print(f"  Procesados {i}/{len(archivos)} archivos...")

        try:
            texto = archivo.read_text(encoding='utf-8')
        except:
            try:
                texto = archivo.read_text(encoding='latin-1')
            except:
                continue

        # Extraer año del nombre del archivo o contenido
        years = re.findall(r'(19\d{2}|20\d{2})', archivo.stem + texto[:500])
        year = int(years[0]) if years else None

        # Extraer adjetivos
        adjetivos = extraer_adjetivos_musica(texto)

        if adjetivos:
            resultados.append({
                'archivo': archivo.name,
                'year': year,
                'adjetivos': adjetivos,
                'freq': Counter(adjetivos)
            })

            todos_adjetivos.update(adjetivos)

            if year:
                temporal_data[year].update(adjetivos)

    print(f"✅ {nombre_publicacion}: {len(resultados)} archivos con datos, {sum(todos_adjetivos.values())} adjetivos totales")

    return {
        'nombre': nombre_publicacion,
        'archivos_procesados': len(resultados),
        'archivos_totales': len(archivos),
        'adjetivos_totales': dict(todos_adjetivos),
        'top30': todos_adjetivos.most_common(30),
        'temporal': {year: dict(counter) for year, counter in temporal_data.items()},
        'resultados_detallados': resultados
    }

# Procesar las tres publicaciones
print("="*60)
print("ANÁLISIS RÁPIDO DE ADJETIVACIONES DE 'MÚSICA'")
print("="*60)

ondas = procesar_carpeta(
    "/Users/maria/Desktop/ONDAS/ONDAS TXT PRIMERA TRANSCRIPCIÓN",
    "ONDAS"
)

el_sol = procesar_carpeta(
    "/Users/maria/Documents/LEXIMUS/CORPUS/txt- el sol (con vertex)",
    "El Sol"
)

espana = procesar_carpeta(
    "/Users/maria/Documents/LEXIMUS/CORPUS/Música en la revista ESPAÑA/REVISTA ESPAÑA en TXT SOLO MÚSICA",
    "Revista ESPAÑA"
)

# Guardar resultados
resultados_completos = {
    'ONDAS': ondas,
    'El_Sol': el_sol,
    'Revista_ESPAÑA': espana
}

with open('/Users/maria/analisis_completo_musica.json', 'w', encoding='utf-8') as f:
    json.dump(resultados_completos, f, ensure_ascii=False, indent=2)

print("\n" + "="*60)
print("RESUMEN COMPARATIVO")
print("="*60)

for pub_data in [ondas, el_sol, espana]:
    print(f"\n{pub_data['nombre']}:")
    print(f"  Archivos procesados: {pub_data['archivos_procesados']}/{pub_data['archivos_totales']}")
    print(f"  Total adjetivos: {sum(pub_data['adjetivos_totales'].values())}")
    print(f"  Adjetivos únicos: {len(pub_data['adjetivos_totales'])}")
    print(f"\n  Top 10 adjetivos:")
    for adj, freq in pub_data['top30'][:10]:
        print(f"    {adj}: {freq}")

print("\n✅ Análisis completo guardado en: analisis_completo_musica.json")

# Crear visualizaciones rápidas
import plotly.graph_objects as go

# Gráfico comparativo
fig = go.Figure()

adjs_comparar = set()
for pub_data in [ondas, el_sol, espana]:
    adjs_comparar.update([adj for adj, _ in pub_data['top30'][:15]])

adjs_comparar = sorted(adjs_comparar)

for pub_data in [ondas, el_sol, espana]:
    adjs_totales = pub_data['adjetivos_totales']
    freqs = [adjs_totales.get(adj, 0) for adj in adjs_comparar]
    fig.add_trace(go.Bar(name=pub_data['nombre'], x=adjs_comparar, y=freqs))

fig.update_layout(
    title='Comparación de adjetivos asociados a "música"',
    xaxis_title='Adjetivo',
    yaxis_title='Frecuencia absoluta',
    barmode='group',
    height=600
)

fig.write_html('/Users/maria/comparacion_completa_adjetivos.html')
print("✅ Gráfico comparativo guardado en: comparacion_completa_adjetivos.html")

# Análisis temporal
fig2 = go.Figure()

for pub_data in [ondas, el_sol, espana]:
    if pub_data['temporal']:
        years = sorted(pub_data['temporal'].keys())
        totals = [sum(pub_data['temporal'][year].values()) for year in years]
        fig2.add_trace(go.Scatter(
            x=years, y=totals, name=pub_data['nombre'],
            mode='lines+markers'
        ))

fig2.update_layout(
    title='Evolución temporal del uso de adjetivos para "música"',
    xaxis_title='Año',
    yaxis_title='Frecuencia total de adjetivos',
    height=500
)

fig2.write_html('/Users/maria/evolucion_temporal_completa.html')
print("✅ Gráfico temporal guardado en: evolucion_temporal_completa.html")
