#!/usr/bin/env python3
"""
Refina el análisis eliminando palabras que no son adjetivos reales
"""

import json
from collections import Counter, defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Cargar datos
with open('/Users/maria/analisis_completo_musica.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

# Lista de palabras a excluir (no son adjetivos reales asociados a música)
EXCLUIR = {
    'música', 'musica', 'para', 'como', 'esta', 'está', 'pero', 'entre', 'donde',
    'desde', 'hasta', 'sobre', 'toda', 'todo', 'todos', 'todas', 'otra', 'otro',
    'otros', 'otras', 'mismo', 'misma', 'mismos', 'mismas', 'cámara', 'camara',
    'maestro', 'maestros', 'maestra', 'maestras', 'palacio', 'palacios',
    'ópera', 'opera', 'teatro', 'teatros', 'piano', 'pianos', 'orquesta',
    'orquestas', 'arte', 'artes', 'obra', 'obras', 'historia', 'historias',
    'público', 'publico', 'públicos', 'publicos', 'referencia', 'referencias',
    'éxito', 'exito', 'nota', 'notas', 'sala', 'salas', 'años', 'anos',
    'siglo', 'siglos', 'época', 'epoca', 'épocas', 'epocas', 'parte', 'partes',
    'forma', 'formas', 'género', 'genero', 'géneros', 'generos', 'autor',
    'autores', 'compositores', 'compositor', 'programa', 'programas',
    'ciudad', 'ciudades', 'país', 'pais', 'países', 'paises', 'mundo',
    'vida', 'vidas', 'nombre', 'nombres', 'estilo', 'estilos', 'momento',
    'momentos', 'tiempo', 'tiempos', 'lugar', 'lugares', 'cosa', 'cosas',
    'medio', 'medios', 'manera', 'maneras', 'modo', 'modos', 'caso', 'casos',
    'ejemplo', 'ejemplos', 'aspecto', 'aspectos', 'carácter', 'caracter',
    'caracteres', 'gente', 'personas', 'persona', 'artista', 'artistas',
    'crítica', 'critica', 'críticas', 'criticas'
}

# Lista de adjetivos válidos conocidos (expandida)
ADJETIVOS_VALIDOS = {
    # Nacionalidad
    'española', 'español', 'españolas', 'españoles',
    'francesa', 'francés', 'francesas', 'franceses',
    'alemana', 'alemán', 'alemanas', 'alemanes',
    'italiana', 'italiano', 'italianas', 'italianos',
    'rusa', 'ruso', 'rusas', 'rusos',
    'inglesa', 'inglés', 'inglesas', 'ingleses',
    'americana', 'americano', 'americanas', 'americanos',
    'argentina', 'argentino', 'argentinas', 'argentinos',
    'cubana', 'cubano', 'cubanas', 'cubanos',
    'mexicana', 'mexicano', 'mexicanas', 'mexicanos',
    'austríaca', 'austriaco', 'austríacas', 'austriacos',
    'checa', 'checo', 'checas', 'checos',
    'húngara', 'húngaro', 'húngaras', 'húngaros',
    'noruega', 'noruego', 'noruegas', 'noruegos',
    'bohemia', 'bohemio', 'bohemias', 'bohemios',
    'andaluza', 'andaluz', 'andaluzas', 'andaluces',
    'catalana', 'catalán', 'catalanas', 'catalanes',
    'vasca', 'vasco', 'vascas', 'vascos',
    'asturiana', 'asturiano', 'asturianas', 'asturianos',
    'gallega', 'gallego', 'gallegas', 'gallegos',
    'nacional', 'nacionales',

    # Género musical
    'sinfónica', 'sinfónico', 'sinfónicas', 'sinfónicos',
    'coral', 'corales',
    'operística', 'operístico', 'operísticas', 'operísticos',
    'instrumental', 'instrumentales',
    'vocal', 'vocales',
    'orquestal', 'orquestales',
    'teatral', 'teatrales',
    'dramática', 'dramático', 'dramáticas', 'dramáticos',
    'escénica', 'escénico', 'escénicas', 'escénicos',
    'ligera', 'ligero', 'ligeras', 'ligeros',
    'bailable', 'bailables',
    'popular', 'populares',
    'clásica', 'clásico', 'clásicas', 'clásicos',
    'moderna', 'moderno', 'modernas', 'modernos',
    'contemporánea', 'contemporáneo', 'contemporáneas', 'contemporáneos',
    'antigua', 'antiguo', 'antiguas', 'antiguos',
    'tradicional', 'tradicionales',
    'folclórica', 'folclórico', 'folclóricas', 'folclóricos',
    'folklórica', 'folklórico', 'folklóricas', 'folklóricos',

    # Valoración estética
    'buena', 'bueno', 'buenas', 'buenos',
    'excelente', 'excelentes',
    'magnífica', 'magnífico', 'magníficas', 'magníficos',
    'perfecta', 'perfecto', 'perfectas', 'perfectos',
    'soberbia', 'soberbio', 'soberbias', 'soberbios',
    'deliciosa', 'delicioso', 'deliciosas', 'deliciosos',
    'hermosa', 'hermoso', 'hermosas', 'hermosos',
    'bella', 'bello', 'bellas', 'bellos',
    'admirable', 'admirables',
    'distinguida', 'distinguido', 'distinguidas', 'distinguidos',
    'fina', 'fino', 'finas', 'finos',
    'selecta', 'selecto', 'selectas', 'selectos',
    'elegante', 'elegantes',
    'superior', 'superiores',
    'gran', 'grande', 'grandes',
    'gloriosa', 'glorioso', 'gloriosas', 'gloriosos',
    'ilustre', 'ilustres',
    'importante', 'importantes',
    'magistral', 'magistrales',
    'noble', 'nobles',
    'rica', 'rico', 'ricas', 'ricos',
    'sublime', 'sublimes',

    # Valoración negativa
    'inferior', 'inferiores',
    'pobre', 'pobres',
    'mala', 'malo', 'malas', 'malos',
    'mediocre', 'mediocres',
    'ordinaria', 'ordinario', 'ordinarias', 'ordinarios',
    'vulgar', 'vulgares',

    # Cualidades expresivas
    'alegre', 'alegres',
    'triste', 'tristes',
    'melancólica', 'melancólico', 'melancólicas', 'melancólicos',
    'romántica', 'romántico', 'románticas', 'románticos',
    'apasionada', 'apasionado', 'apasionadas', 'apasionados',
    'lírica', 'lírico', 'líricas', 'líricos',
    'poética', 'poético', 'poéticas', 'poéticos',
    'emotiva', 'emotivo', 'emotivas', 'emotivos',
    'expresiva', 'expresivo', 'expresivas', 'expresivos',
    'suave', 'suaves',
    'delicada', 'delicado', 'delicadas', 'delicados',
    'íntima', 'íntimo', 'íntimas', 'íntimos',
    'profunda', 'profundo', 'profundas', 'profundos',
    'misteriosa', 'misterioso', 'misteriosas', 'misteriosos',
    'sugestiva', 'sugestivo', 'sugestivas', 'sugestivos',

    # Complejidad
    'sencilla', 'sencillo', 'sencillas', 'sencillos',
    'simple', 'simples',
    'fácil', 'fáciles',
    'complicada', 'complicado', 'complicadas', 'complicados',
    'compleja', 'complejo', 'complejas', 'complejos',
    'difícil', 'difíciles',
    'erudita', 'erudito', 'eruditas', 'eruditos',
    'culta', 'culto', 'cultas', 'cultos',
    'refinada', 'refinado', 'refinadas', 'refinados',
    'pura', 'puro', 'puras', 'puros',

    # Novedad
    'nueva', 'nuevo', 'nuevas', 'nuevos',
    'actual', 'actuales',
    'renovadora', 'renovador', 'renovadoras', 'renovadores',
    'revolucionaria', 'revolucionario', 'revolucionarias', 'revolucionarios',
    'vieja', 'viejo', 'viejas', 'viejos',
    'arcaica', 'arcaico', 'arcaicas', 'arcaicos',

    # Carácter social
    'aristocrática', 'aristocrático', 'aristocráticas', 'aristocráticos',
    'religiosa', 'religioso', 'religiosas', 'religiosos',
    'profana', 'profano', 'profanas', 'profanos',
    'sagrada', 'sagrado', 'sagradas', 'sagrados',
    'militar', 'militares',
    'seria', 'serio', 'serias', 'serios',
    'frívola', 'frívolo', 'frívolas', 'frívolos',

    # Diversidad cultural
    'negra', 'negro', 'negras', 'negros',
    'tzíngara', 'tzíngaro', 'tzíngaras', 'tzíngaros',
    'gitana', 'gitano', 'gitanas', 'gitanos',
    'flamenca', 'flamenco', 'flamencas', 'flamencos',
    'oriental', 'orientales',
    'exótica', 'exótico', 'exóticas', 'exóticos',
    'indígena', 'indígenas',
    'arábiga', 'arábigo', 'arábig', 'arábigos',
    'africana', 'africano', 'africanas', 'africanos',
    'tropical', 'tropicales',

    # Tecnología/Radio
    'radiofónica', 'radiofónico', 'radiofónicas', 'radiofónicos',
    'radiogénica', 'radiogénico', 'radiogénicas', 'radiogénicos',
    'microfónica', 'microfónico', 'microfónicas', 'microfónicos',
    'transmitida', 'transmitido', 'transmitidas', 'transmitidos',
    'registrada', 'registrado', 'registradas', 'registrados',

    # Otros adjetivos musicales
    'variada', 'variado', 'variadas', 'variados',
    'llena', 'lleno', 'llenas', 'llenos',
    'mozartiana', 'mozartiano', 'mozartianas', 'mozartianos',
    'wagneriana', 'wagneriano', 'wagnerianas', 'wagnerianos',
    'beethoveniana', 'beethoveniano', 'beethovenianas', 'beethovenianos',
    'evocativa', 'evocativo', 'evocativas', 'evocativos',
    'heredada', 'heredado', 'heredadas', 'heredados',
    'escrita', 'escrito', 'escritas', 'escritos',
    'compuesta', 'compuesto', 'compuestas', 'compuestos',
    'interpretada', 'interpretado', 'interpretadas', 'interpretados',
    'ejecutada', 'ejecutado', 'ejecutadas', 'ejecutados',
    'trascendental', 'trascendentales',
    'característica', 'característico', 'características', 'característicos',
    'típica', 'típico', 'típicas', 'típicos',
    'propia', 'propio', 'propias', 'propios',
    'nuestra', 'nuestro', 'nuestras', 'nuestros',
    'diversa', 'diverso', 'diversas', 'diversos',
    'amplia', 'amplio', 'amplias', 'amplios',
    'extensa', 'extenso', 'extensas', 'extensos',
    'breve', 'breves',
    'larga', 'largo', 'largas', 'largos',
    'corta', 'corto', 'cortas', 'cortos',
    'única', 'único', 'únicas', 'únicos',
    'especial', 'especiales',
    'particular', 'particulares',
    'general', 'generales',
    'universal', 'universales',
    'internacional', 'internacionales'
}

def filtrar_adjetivos(adjs_dict):
    """Filtra el diccionario de adjetivos quitando palabras no válidas"""
    filtrado = {}
    for adj, freq in adjs_dict.items():
        adj_lower = adj.lower()
        # Incluir si está en la lista de válidos o si termina en -a/-o/-os/-as y no está en excluir
        if adj_lower in ADJETIVOS_VALIDOS:
            filtrado[adj] = freq
        elif adj_lower not in EXCLUIR and len(adj) >= 4:
            # Verificar terminaciones típicas de adjetivos
            if any(adj_lower.endswith(term) for term in ['ada', 'ado', 'adas', 'ados',
                                                           'osa', 'oso', 'osas', 'osos',
                                                           'ica', 'ico', 'icas', 'icos',
                                                           'ana', 'ano', 'anas', 'anos',
                                                           'esa', 'és', 'esas', 'eses',
                                                           'enta', 'ento', 'entas', 'entos',
                                                           'iva', 'ivo', 'ivas', 'ivos',
                                                           'ble', 'bles', 'al', 'ales']):
                filtrado[adj] = freq

    return filtrado

# Filtrar datos de cada publicación
print("Filtrando adjetivos...")

for pub_key in ['ONDAS', 'El_Sol', 'Revista_ESPAÑA']:
    pub_data = datos[pub_key]
    print(f"\n{pub_key}:")
    print(f"  Antes del filtrado: {len(pub_data['adjetivos_totales'])} adjetivos únicos")

    # Filtrar adjetivos totales
    pub_data['adjetivos_totales'] = filtrar_adjetivos(pub_data['adjetivos_totales'])

    # Recalcular top30
    counter = Counter(pub_data['adjetivos_totales'])
    pub_data['top30'] = counter.most_common(30)

    # Filtrar datos temporales
    for year in pub_data['temporal']:
        pub_data['temporal'][year] = filtrar_adjetivos(pub_data['temporal'][year])

    print(f"  Después del filtrado: {len(pub_data['adjetivos_totales'])} adjetivos únicos")
    print(f"  Total adjetivos: {sum(pub_data['adjetivos_totales'].values())}")
    print(f"\n  Nuevo Top 15:")
    for i, (adj, freq) in enumerate(pub_data['top30'][:15], 1):
        print(f"    {i}. {adj}: {freq}")

# Guardar datos filtrados
with open('/Users/maria/analisis_filtrado_musica.json', 'w', encoding='utf-8') as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

print("\n✅ Datos filtrados guardados en: analisis_filtrado_musica.json")

# Crear visualizaciones mejoradas
print("\nGenerando visualizaciones...")

# Gráfico comparativo mejorado
fig1 = go.Figure()

adjs_top = set()
for pub_key in ['ONDAS', 'El_Sol', 'Revista_ESPAÑA']:
    adjs_top.update([adj for adj, _ in datos[pub_key]['top30'][:20]])

adjs_top = sorted(adjs_top, key=lambda x: sum(datos[pub]['adjetivos_totales'].get(x, 0)
                                                for pub in ['ONDAS', 'El_Sol', 'Revista_ESPAÑA']),
                  reverse=True)[:30]

for pub_key, pub_name in [('ONDAS', 'ONDAS'), ('El_Sol', 'El Sol'), ('Revista_ESPAÑA', 'Revista ESPAÑA')]:
    adjs_dict = datos[pub_key]['adjetivos_totales']
    freqs = [adjs_dict.get(adj, 0) for adj in adjs_top]
    fig1.add_trace(go.Bar(name=pub_name, x=adjs_top, y=freqs))

fig1.update_layout(
    title='Adjetivos más frecuentes asociados a "música" (datos filtrados)',
    xaxis_title='Adjetivo',
    yaxis_title='Frecuencia absoluta',
    barmode='group',
    height=700,
    xaxis={'tickangle': -45}
)

fig1.write_html('/Users/maria/comparacion_filtrada_adjetivos.html')
print("✅ Gráfico comparativo filtrado guardado")

# Análisis temporal mejorado
fig2 = make_subplots(
    rows=3, cols=1,
    subplot_titles=('ONDAS', 'El Sol', 'Revista ESPAÑA'),
    vertical_spacing=0.1
)

adjetivos_seguir = ['española', 'popular', 'moderna', 'ligera', 'contemporánea',
                    'clásica', 'francesa', 'nueva', 'nacional', 'rusa']

row_num = 1
for pub_key, pub_name in [('ONDAS', 'ONDAS'), ('El_Sol', 'El Sol'), ('Revista_ESPAÑA', 'Revista ESPAÑA')]:
    temporal = datos[pub_key]['temporal']

    for adj in adjetivos_seguir:
        years = []
        freqs = []
        for year in sorted(temporal.keys()):
            if temporal[year].get(adj, 0) > 0:
                years.append(year)
                freqs.append(temporal[year][adj])

        if years:
            fig2.add_trace(
                go.Scatter(x=years, y=freqs, name=adj, mode='lines+markers',
                          showlegend=(row_num == 1)),
                row=row_num, col=1
            )

    row_num += 1

fig2.update_xaxes(title_text="Año")
fig2.update_yaxes(title_text="Frecuencia")
fig2.update_layout(height=1200, title_text="Evolución temporal de adjetivos clave")

fig2.write_html('/Users/maria/evolucion_temporal_filtrada.html')
print("✅ Gráfico temporal filtrado guardado")

print("\n✅ Análisis refinado completado")
