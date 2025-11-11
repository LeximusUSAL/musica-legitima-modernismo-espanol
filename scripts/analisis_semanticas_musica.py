#!/usr/bin/env python3
"""
Análisis de las semánticas del concepto "música" en la prensa modernista española
Procesa datos de adjetivaciones de ONDAS, El Sol y Revista España
"""

import json
import re
from collections import Counter, defaultdict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Leer el JSON del archivo HTML
with open('/Users/maria/datos_musica_temp.json', 'r', encoding='utf-8') as f:
    contenido = f.read()
    # Extraer solo el JSON (quitar "const data = " al inicio y ";" al final)
    json_data = contenido.replace('const data = ', '').strip()
    if json_data.endswith(';'):
        json_data = json_data[:-1]
    datos = json.loads(json_data)

# Clasificar archivos por publicación
ondas_data = {}
el_sol_data = {}
espana_data = {}

for archivo, adjetivos in datos.items():
    if 'ONDAS' in archivo.upper():
        ondas_data[archivo] = adjetivos
    elif 'espana' in archivo.lower() or 'españa' in archivo.lower():
        # Archivos de la Revista España
        espana_data[archivo] = adjetivos
    elif 'output' in archivo.lower() or ('19' in archivo and not 'ONDAS' in archivo.upper()):
        # Los archivos con _output o con fechas son de El Sol
        el_sol_data[archivo] = adjetivos

print(f"Archivos ONDAS: {len(ondas_data)}")
print(f"Archivos El Sol: {len(el_sol_data)}")
print(f"Archivos España: {len(espana_data)}")

# Función para consolidar adjetivos de una publicación
def consolidar_adjetivos(data_dict):
    counter = Counter()
    for archivo, adjs in data_dict.items():
        for adj, freq in adjs.items():
            counter[adj] += freq
    return counter

# Consolidar por publicación
ondas_adjs = consolidar_adjetivos(ondas_data)
el_sol_adjs = consolidar_adjetivos(el_sol_data)
espana_adjs = consolidar_adjetivos(espana_data)

print(f"\nTotal adjetivos ONDAS: {sum(ondas_adjs.values())}")
print(f"Total adjetivos El Sol: {sum(el_sol_adjs.values())}")
print(f"Total adjetivos España: {sum(espana_adjs.values())}")

# Top 30 adjetivos por publicación
ondas_top30 = ondas_adjs.most_common(30)
el_sol_top30 = el_sol_adjs.most_common(30)
espana_top30 = espana_adjs.most_common(30)

print("\n=== TOP 30 ADJETIVOS ONDAS ===")
for adj, freq in ondas_top30:
    print(f"{adj}: {freq}")

print("\n=== TOP 30 ADJETIVOS EL SOL ===")
for adj, freq in el_sol_top30:
    print(f"{adj}: {freq}")

print("\n=== TOP 30 ADJETIVOS ESPAÑA ===")
for adj, freq in espana_top30:
    print(f"{adj}: {freq}")

# Categorización semántica de adjetivos
categorias = {
    'Nacionalidad': ['española', 'español', 'francesa', 'francés', 'alemana', 'alemán', 'italiana',
                     'rusa', 'ruso', 'inglesa', 'inglés', 'americana', 'americana', 'cubana',
                     'argentina', 'austríaca', 'checa', 'húngara', 'noruega', 'bohemia', 'andaluza',
                     'catalana', 'vasca', 'vasco', 'nacional', 'nacionales', 'sudamericana', 'centroeuropea'],
    'Género musical': ['sinfónica', 'coral', 'operística', 'instrumental', 'vocal', 'orquestal',
                       'teatral', 'dramática', 'escénica', 'ligera', 'bailable', 'popular', 'populares',
                       'clásica', 'clásicas', 'clásico', 'moderna', 'moderno', 'contemporánea',
                       'antigua', 'tradicional', 'folclórica', 'folclóricas'],
    'Valoración estética': ['buena', 'excelente', 'perfecta', 'soberbia', 'deliciosa', 'hermosa',
                            'bella', 'admirable', 'distinguida', 'fina', 'selecta', 'elegante',
                            'superior', 'gran', 'grande', 'gloriosa', 'ilustre', 'importante',
                            'magistral', 'noble', 'rica', 'sublime'],
    'Valoración negativa': ['inferior', 'pobre', 'mala', 'mediocre', 'ordinaria', 'vulgar'],
    'Cualidades expresivas': ['alegre', 'triste', 'melancólica', 'romántica', 'apasionada',
                              'dramática', 'lírica', 'poética', 'emotiva', 'expresiva', 'suave',
                              'delicada', 'íntima', 'profunda', 'misteriosa', 'sugestiva'],
    'Complejidad': ['sencilla', 'simple', 'fácil', 'complicada', 'compleja', 'difícil',
                    'erudita', 'culta', 'refinada', 'pura'],
    'Novedad/Modernidad': ['nueva', 'nuevo', 'moderna', 'moderno', 'actual', 'contemporánea',
                           'renovadora', 'revolucionaria', 'vieja', 'antigua', 'tradicional',
                           'pasada', 'pasadas', 'arcaica'],
    'Carácter social': ['aristocrática', 'popular', 'populares', 'culta', 'religiosa',
                        'profana', 'sagrada', 'militar', 'seria', 'frívola'],
    'Diversidad cultural': ['negra', 'tzíngara', 'flamenca', 'flamenco', 'oriental', 'exótica',
                            'exóticos', 'indígena', 'arábiga', 'africana', 'tropical'],
    'Tecnología/Radio': ['radiofónica', 'radiogénica', 'microfónica', 'transmitida',
                         'registrada', 'radioyentes']
}

def categorizar_adjetivo(adj):
    """Retorna las categorías a las que pertenece un adjetivo"""
    cats = []
    for cat, adjs in categorias.items():
        if adj in adjs:
            cats.append(cat)
    return cats if cats else ['Otros']

# Análisis por categorías para cada publicación
def analizar_categorias(adjs_counter, nombre_pub):
    cat_counts = defaultdict(int)
    for adj, freq in adjs_counter.items():
        cats = categorizar_adjetivo(adj)
        for cat in cats:
            cat_counts[cat] += freq

    print(f"\n=== CATEGORÍAS SEMÁNTICAS: {nombre_pub} ===")
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / sum(cat_counts.values())) * 100
        print(f"{cat}: {count} ({porcentaje:.1f}%)")

    return dict(cat_counts)

ondas_cats = analizar_categorias(ondas_adjs, "ONDAS")
el_sol_cats = analizar_categorias(el_sol_adjs, "EL SOL")
espana_cats = analizar_categorias(espana_adjs, "ESPAÑA")

# Crear DataFrame comparativo
df_comparativo = pd.DataFrame({
    'ONDAS': ondas_cats,
    'El Sol': el_sol_cats,
    'España': espana_cats
}).fillna(0)

# Normalizar por totales (porcentajes)
df_porcentajes = df_comparativo.div(df_comparativo.sum(axis=0), axis=1) * 100

print("\n=== COMPARATIVA PORCENTUAL ===")
print(df_porcentajes.to_string())

# Generar visualizaciones

# 1. Gráfico de barras agrupadas - Top 20 adjetivos por publicación
fig1 = go.Figure()

# Obtener top 20 de cada publicación y unir
todos_tops = set([x[0] for x in ondas_top30[:20]] +
                 [x[0] for x in el_sol_top30[:20]] +
                 [x[0] for x in espana_top30[:20]])

adjs_orden = sorted(todos_tops,
                    key=lambda x: ondas_adjs.get(x, 0) + el_sol_adjs.get(x, 0) + espana_adjs.get(x, 0),
                    reverse=True)[:25]

fig1.add_trace(go.Bar(name='ONDAS',
                      x=adjs_orden,
                      y=[ondas_adjs.get(adj, 0) for adj in adjs_orden]))
fig1.add_trace(go.Bar(name='El Sol',
                      x=adjs_orden,
                      y=[el_sol_adjs.get(adj, 0) for adj in adjs_orden]))
fig1.add_trace(go.Bar(name='España',
                      x=adjs_orden,
                      y=[espana_adjs.get(adj, 0) for adj in adjs_orden]))

fig1.update_layout(
    title='Adjetivos más frecuentes asociados a "música" por publicación',
    xaxis_title='Adjetivo',
    yaxis_title='Frecuencia',
    barmode='group',
    height=600,
    font=dict(size=12)
)

fig1.write_html('/Users/maria/grafico_comparativo_adjetivos.html')
print("\n✅ Gráfico comparativo guardado en grafico_comparativo_adjetivos.html")

# 2. Gráfico de categorías semánticas
fig2 = go.Figure()

categorias_orden = sorted(df_porcentajes.index,
                         key=lambda x: df_porcentajes.loc[x].sum(),
                         reverse=True)

fig2.add_trace(go.Bar(name='ONDAS',
                      x=categorias_orden,
                      y=[df_porcentajes.loc[cat, 'ONDAS'] for cat in categorias_orden]))
fig2.add_trace(go.Bar(name='El Sol',
                      x=categorias_orden,
                      y=[df_porcentajes.loc[cat, 'El Sol'] for cat in categorias_orden]))
fig2.add_trace(go.Bar(name='España',
                      x=categorias_orden,
                      y=[df_porcentajes.loc[cat, 'España'] for cat in categorias_orden]))

fig2.update_layout(
    title='Distribución porcentual de categorías semánticas',
    xaxis_title='Categoría semántica',
    yaxis_title='Porcentaje (%)',
    barmode='group',
    height=600,
    font=dict(size=12)
)

fig2.write_html('/Users/maria/grafico_categorias_semanticas.html')
print("✅ Gráfico de categorías guardado en grafico_categorias_semanticas.html")

# 3. Heatmap comparativo
fig3 = go.Figure(data=go.Heatmap(
    z=df_porcentajes.values,
    x=df_porcentajes.columns,
    y=df_porcentajes.index,
    colorscale='Blues',
    text=df_porcentajes.round(1).values,
    texttemplate='%{text}%',
    textfont={"size": 10}
))

fig3.update_layout(
    title='Mapa de calor: Distribución de categorías semánticas (%)',
    height=700,
    font=dict(size=12)
)

fig3.write_html('/Users/maria/heatmap_categorias.html')
print("✅ Heatmap guardado en heatmap_categorias.html")

# Exportar datos a CSV para referencia
df_comparativo.to_csv('/Users/maria/datos_comparativos_musica.csv')
df_porcentajes.to_csv('/Users/maria/datos_porcentajes_musica.csv')

# Crear tabla de top adjetivos
df_tops = pd.DataFrame({
    'ONDAS_adj': [x[0] for x in ondas_top30],
    'ONDAS_freq': [x[1] for x in ondas_top30],
    'ElSol_adj': [x[0] for x in el_sol_top30],
    'ElSol_freq': [x[1] for x in el_sol_top30],
    'España_adj': [x[0] for x in espana_top30] if espana_top30 else [''] * 30,
    'España_freq': [x[1] for x in espana_top30] if espana_top30 else [0] * 30
})

df_tops.to_csv('/Users/maria/top30_adjetivos_por_publicacion.csv', index=False)
print("✅ Datos exportados a CSV")

# Análisis de adjetivos exclusivos y compartidos
ondas_set = set(ondas_adjs.keys())
el_sol_set = set(el_sol_adjs.keys())
espana_set = set(espana_adjs.keys())

print("\n=== ANÁLISIS DE VOCABULARIOS ===")
print(f"Adjetivos únicos ONDAS: {len(ondas_set)}")
print(f"Adjetivos únicos El Sol: {len(el_sol_set)}")
print(f"Adjetivos únicos España: {len(espana_set)}")

print(f"\nAdjetivos compartidos ONDAS y El Sol: {len(ondas_set & el_sol_set)}")
print(f"Adjetivos exclusivos de ONDAS: {len(ondas_set - el_sol_set - espana_set)}")
print(f"Adjetivos exclusivos de El Sol: {len(el_sol_set - ondas_set - espana_set)}")

# Adjetivos exclusivos más frecuentes
ondas_exclusivos = [(adj, freq) for adj, freq in ondas_adjs.items()
                    if adj in (ondas_set - el_sol_set - espana_set)]
el_sol_exclusivos = [(adj, freq) for adj, freq in el_sol_adjs.items()
                     if adj in (el_sol_set - ondas_set - espana_set)]

print("\n=== TOP 10 ADJETIVOS EXCLUSIVOS DE ONDAS ===")
for adj, freq in sorted(ondas_exclusivos, key=lambda x: x[1], reverse=True)[:10]:
    print(f"{adj}: {freq}")

print("\n=== TOP 10 ADJETIVOS EXCLUSIVOS DE EL SOL ===")
for adj, freq in sorted(el_sol_exclusivos, key=lambda x: x[1], reverse=True)[:10]:
    print(f"{adj}: {freq}")

print("\n✅ Análisis completado. Archivos generados:")
print("   - grafico_comparativo_adjetivos.html")
print("   - grafico_categorias_semanticas.html")
print("   - heatmap_categorias.html")
print("   - datos_comparativos_musica.csv")
print("   - datos_porcentajes_musica.csv")
print("   - top30_adjetivos_por_publicacion.csv")
