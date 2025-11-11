#!/usr/bin/env python3
"""
Análisis temporal detallado de las semánticas de "música"
en la prensa modernista española (1915-1936)
"""

import json
from collections import Counter, defaultdict
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Cargar datos filtrados
with open('/Users/maria/analisis_filtrado_musica.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

print("="*70)
print("ANÁLISIS TEMPORAL DETALLADO - SEMÁNTICAS DE 'MÚSICA'")
print("="*70)

# Función para analizar tendencias temporales
def analizar_evolucion_temporal(temporal_data, nombre_pub):
    """Analiza la evolución temporal de adjetivos"""
    if not temporal_data:
        print(f"\n{nombre_pub}: Sin datos temporales suficientes")
        return None

    years = sorted(temporal_data.keys())
    if len(years) < 3:
        print(f"\n{nombre_pub}: Rango temporal insuficiente ({len(years)} años)")
        return None

    print(f"\n{'='*70}")
    print(f"{nombre_pub.upper()}")
    print(f"{'='*70}")
    print(f"Rango temporal: {min(years)}-{max(years)} ({len(years)} años con datos)")

    # Calcular totales por año
    totales_anuales = {year: sum(temporal_data[year].values()) for year in years}
    print(f"\nEstadísticas generales:")
    print(f"  Total de adjetivos: {sum(totales_anuales.values())}")
    print(f"  Promedio anual: {np.mean(list(totales_anuales.values())):.1f}")
    print(f"  Año con más adjetivos: {max(totales_anuales, key=totales_anuales.get)} ({totales_anuales[max(totales_anuales, key=totales_anuales.get)]})")

    # Dividir en periodos
    tercio = len(years) // 3
    periodo1 = years[:tercio]
    periodo2 = years[tercio:2*tercio]
    periodo3 = years[2*tercio:]

    # Agregar por periodos
    periodo1_adjs = Counter()
    periodo2_adjs = Counter()
    periodo3_adjs = Counter()

    for y in periodo1:
        periodo1_adjs.update(temporal_data[y])
    for y in periodo2:
        periodo2_adjs.update(temporal_data[y])
    for y in periodo3:
        periodo3_adjs.update(temporal_data[y])

    print(f"\nPeriodo 1 ({periodo1[0]}-{periodo1[-1]}): {sum(periodo1_adjs.values())} adjetivos")
    print(f"Periodo 2 ({periodo2[0]}-{periodo2[-1]}): {sum(periodo2_adjs.values())} adjetivos")
    print(f"Periodo 3 ({periodo3[0]}-{periodo3[-1]}): {sum(periodo3_adjs.values())} adjetivos")

    # Top 10 por periodo
    print(f"\nTop 10 adjetivos por periodo:")
    print(f"\nPeriodo 1 ({periodo1[0]}-{periodo1[-1]}):")
    for adj, freq in periodo1_adjs.most_common(10):
        print(f"  {adj}: {freq}")

    print(f"\nPeriodo 2 ({periodo2[0]}-{periodo2[-1]}):")
    for adj, freq in periodo2_adjs.most_common(10):
        print(f"  {adj}: {freq}")

    print(f"\nPeriodo 3 ({periodo3[0]}-{periodo3[-1]}):")
    for adj, freq in periodo3_adjs.most_common(10):
        print(f"  {adj}: {freq}")

    # Adjetivos emergentes y declinantes
    todos_adjs = set(periodo1_adjs.keys()) | set(periodo2_adjs.keys()) | set(periodo3_adjs.keys())

    emergentes = []
    declinantes = []

    for adj in todos_adjs:
        freq1 = periodo1_adjs.get(adj, 0) / len(periodo1) if len(periodo1) > 0 else 0
        freq3 = periodo3_adjs.get(adj, 0) / len(periodo3) if len(periodo3) > 0 else 0

        if freq1 > 0:
            cambio = ((freq3 - freq1) / freq1) * 100
        elif freq3 > 0:
            cambio = 100
        else:
            continue

        if cambio > 100 and freq3 >= 1:
            emergentes.append((adj, cambio, freq1, freq3))
        elif cambio < -50 and freq1 >= 1:
            declinantes.append((adj, cambio, freq1, freq3))

    emergentes.sort(key=lambda x: x[1], reverse=True)
    declinantes.sort(key=lambda x: x[1])

    print(f"\nAdjetivos EMERGENTES (top 10):")
    for adj, cambio, f1, f3 in emergentes[:10]:
        print(f"  {adj}: {f1:.1f}→{f3:.1f} ({cambio:+.0f}%)")

    print(f"\nAdjetivos DECLINANTES (top 10):")
    for adj, cambio, f1, f3 in declinantes[:10]:
        print(f"  {adj}: {f1:.1f}→{f3:.1f} ({cambio:+.0f}%)")

    return {
        'years': years,
        'totales_anuales': totales_anuales,
        'periodo1': (periodo1, periodo1_adjs),
        'periodo2': (periodo2, periodo2_adjs),
        'periodo3': (periodo3, periodo3_adjs),
        'emergentes': emergentes[:15],
        'declinantes': declinantes[:15]
    }

# Analizar cada publicación
ondas_temporal = analizar_evolucion_temporal(datos['ONDAS']['temporal'], "ONDAS")
el_sol_temporal = analizar_evolucion_temporal(datos['El_Sol']['temporal'], "El Sol")
espana_temporal = analizar_evolucion_temporal(datos['Revista_ESPAÑA']['temporal'], "Revista ESPAÑA")

# Análisis comparativo por categorías semánticas
categorias = {
    'Nacionalidad': ['española', 'español', 'francesa', 'francés', 'alemana', 'alemán', 'italiana',
                     'rusa', 'ruso', 'inglesa', 'inglés', 'nacional', 'nacionales', 'andaluza',
                     'catalana', 'vasca', 'asturiana'],
    'Modernidad': ['moderna', 'moderno', 'contemporánea', 'contemporáneo', 'nueva', 'nuevo',
                   'actual', 'actuales', 'renovadora'],
    'Tradición': ['antigua', 'antiguo', 'tradicional', 'clásica', 'clásico', 'vieja', 'viejo'],
    'Género musical': ['sinfónica', 'ligera', 'popular', 'instrumental', 'vocal', 'teatral',
                       'dramática', 'coral', 'operística', 'orquestal'],
    'Valoración': ['buena', 'bueno', 'excelente', 'perfecta', 'hermosa', 'bella', 'gran', 'grande',
                   'sublime', 'gloriosa', 'fina', 'elegante'],
    'Diversidad': ['negra', 'flamenca', 'flamenco', 'oriental', 'exótica', 'indígena', 'tropical']
}

def clasificar_por_categorias(adjs_dict):
    """Clasifica adjetivos por categorías semánticas"""
    cat_counts = defaultdict(int)
    for adj, freq in adjs_dict.items():
        clasificado = False
        for cat, adjs_cat in categorias.items():
            if any(adj.lower().startswith(a.lower()[:4]) for a in adjs_cat):
                cat_counts[cat] += freq
                clasificado = True
                break
        if not clasificado:
            cat_counts['Otros'] += freq
    return dict(cat_counts)

print(f"\n{'='*70}")
print("ANÁLISIS POR CATEGORÍAS SEMÁNTICAS")
print(f"{'='*70}")

for pub_key, pub_name in [('ONDAS', 'ONDAS'), ('El_Sol', 'El Sol'), ('Revista_ESPAÑA', 'Revista ESPAÑA')]:
    print(f"\n{pub_name}:")
    cat_counts = clasificar_por_categorias(datos[pub_key]['adjetivos_totales'])
    total = sum(cat_counts.values())
    for cat in sorted(cat_counts.keys(), key=lambda x: cat_counts[x], reverse=True):
        pct = (cat_counts[cat] / total) * 100
        print(f"  {cat}: {cat_counts[cat]} ({pct:.1f}%)")

# Crear visualizaciones
print("\n" + "="*70)
print("GENERANDO VISUALIZACIONES")
print("="*70)

# 1. Evolución temporal de categorías semánticas por publicación
fig1 = make_subplots(
    rows=2, cols=1,
    subplot_titles=('ONDAS (1925-1935)', 'El Sol (1918-1936)'),
    vertical_spacing=0.15
)

# ONDAS
if ondas_temporal:
    for cat in ['Modernidad', 'Tradición', 'Nacionalidad']:
        years = []
        freqs = []
        for year in ondas_temporal['years']:
            adjs_year = datos['ONDAS']['temporal'][year]
            cat_freq = sum(freq for adj, freq in adjs_year.items()
                          if any(adj.lower().startswith(a.lower()[:4]) for a in categorias.get(cat, [])))
            if cat_freq > 0:
                years.append(year)
                freqs.append(cat_freq)
        if years:
            fig1.add_trace(go.Scatter(x=years, y=freqs, name=cat, mode='lines+markers'), row=1, col=1)

# El Sol
if el_sol_temporal:
    for cat in ['Modernidad', 'Tradición', 'Nacionalidad']:
        years = []
        freqs = []
        for year in el_sol_temporal['years']:
            adjs_year = datos['El_Sol']['temporal'][year]
            cat_freq = sum(freq for adj, freq in adjs_year.items()
                          if any(adj.lower().startswith(a.lower()[:4]) for a in categorias.get(cat, [])))
            if cat_freq > 0:
                years.append(year)
                freqs.append(cat_freq)
        if years:
            fig1.add_trace(go.Scatter(x=years, y=freqs, name=cat, mode='lines+markers',
                                     showlegend=False), row=2, col=1)

fig1.update_xaxes(title_text="Año")
fig1.update_yaxes(title_text="Frecuencia")
fig1.update_layout(height=900, title_text="Evolución de categorías semánticas clave")
fig1.write_html('/Users/maria/evolucion_categorias_semanticas.html')
print("✅ Gráfico de categorías temporales guardado")

# 2. Comparación de emergentes vs declinantes
fig2 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('ONDAS', 'El Sol'),
    specs=[[{"type": "bar"}, {"type": "bar"}]]
)

if ondas_temporal and ondas_temporal['emergentes']:
    emerg_adjs = [x[0] for x in ondas_temporal['emergentes'][:8]]
    emerg_vals = [x[1] for x in ondas_temporal['emergentes'][:8]]
    fig2.add_trace(go.Bar(x=emerg_adjs, y=emerg_vals, name='Emergentes',
                          marker_color='green'), row=1, col=1)

if el_sol_temporal and el_sol_temporal['emergentes']:
    emerg_adjs = [x[0] for x in el_sol_temporal['emergentes'][:8]]
    emerg_vals = [x[1] for x in el_sol_temporal['emergentes'][:8]]
    fig2.add_trace(go.Bar(x=emerg_adjs, y=emerg_vals, name='Emergentes',
                          marker_color='green', showlegend=False), row=1, col=2)

fig2.update_layout(height=600, title_text="Adjetivos emergentes (% de cambio)")
fig2.write_html('/Users/maria/adjetivos_emergentes.html')
print("✅ Gráfico de emergentes guardado")

# Exportar tablas detalladas
if ondas_temporal:
    df_ondas = pd.DataFrame({
        'Periodo_1': [f"{x[0]}: {x[1]}" for x in ondas_temporal['periodo1'][1].most_common(20)],
        'Periodo_2': [f"{x[0]}: {x[1]}" for x in ondas_temporal['periodo2'][1].most_common(20)],
        'Periodo_3': [f"{x[0]}: {x[1]}" for x in ondas_temporal['periodo3'][1].most_common(20)]
    })
    df_ondas.to_csv('/Users/maria/ondas_evolucion_periodos.csv', index=False)

if el_sol_temporal:
    df_sol = pd.DataFrame({
        'Periodo_1': [f"{x[0]}: {x[1]}" for x in el_sol_temporal['periodo1'][1].most_common(20)],
        'Periodo_2': [f"{x[0]}: {x[1]}" for x in el_sol_temporal['periodo2'][1].most_common(20)],
        'Periodo_3': [f"{x[0]}: {x[1]}" for x in el_sol_temporal['periodo3'][1].most_common(20)]
    })
    df_sol.to_csv('/Users/maria/el_sol_evolucion_periodos.csv', index=False)

print("✅ Tablas de periodos exportadas")

print("\n✅ Análisis temporal detallado completado")
print("\nArchivos generados:")
print("  - evolucion_categorias_semanticas.html")
print("  - adjetivos_emergentes.html")
print("  - ondas_evolucion_periodos.csv")
print("  - el_sol_evolucion_periodos.csv")
