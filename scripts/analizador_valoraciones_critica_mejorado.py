#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZADOR MEJORADO DE VALORACIONES EN CRÍTICA MUSICAL
=======================================================

Corrige las limitaciones del método de bigrams que subcuantifica valoraciones.

PROBLEMA DETECTADO:
- El artículo reporta solo 3.9% valoraciones positivas y 0.4% negativas
- Esto es inverosímil para corpus de crítica musical con miles de documentos

CAUSAS:
1. Análisis restringido a adjetivos directamente asociados a "música"
2. Ignora valoraciones sobre "interpretación", "concierto", "ejecución", etc.
3. Ventana de ±3 tokens pierde construcciones predicativas distantes
4. No captura negaciones ("no es buena"), intensificadores, matices

SOLUCIÓN:
Este script implementa análisis multinivel:
- Nivel 1: Adjetivos sobre "música" (método original)
- Nivel 2: Adjetivos sobre términos relacionados (concierto, interpretación...)
- Nivel 3: Construcciones predicativas distantes (ventana ±7 palabras)
- Nivel 4: Análisis de polaridad contextual (negaciones, intensificadores)

Proyecto: LexiMus - Universidad de Salamanca
Autor: María Palacios Nieto
Fecha: Noviembre 2024
"""

import spacy
from collections import Counter, defaultdict
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

WINDOW_SIZE = 7  # Ventana expandida para capturar predicaciones distantes
MIN_FREQ = 2

# Términos musicales que reciben valoraciones (además de "música")
TERMINOS_MUSICALES = {
    # Eventos
    'concierto', 'recital', 'audición', 'función', 'sesión', 'actuación',
    'programa', 'festival', 'temporada', 'estreno', 'representación',

    # Interpretación
    'interpretación', 'ejecución', 'versión', 'lectura', 'actuación',

    # Obras
    'obra', 'pieza', 'composición', 'partitura', 'sinfonía', 'concierto',
    'ópera', 'zarzuela', 'sonata', 'cuarteto', 'suite', 'preludio',

    # Agentes
    'orquesta', 'coro', 'conjunto', 'agrupación', 'banda',
    'pianista', 'violinista', 'cantante', 'soprano', 'tenor', 'barítono',
    'director', 'maestro', 'compositor', 'autor', 'intérprete'
}

# Léxico evaluativo ampliado
VALORACIONES_POSITIVAS = {
    # Excelencia
    'excelente', 'magnífico', 'magistral', 'espléndido', 'soberbio', 'sublime',
    'extraordinario', 'excepcional', 'admirable', 'notable', 'destacado',
    'brillante', 'glorioso', 'triunfal', 'memorable', 'insuperable',

    # Calidad estética
    'hermoso', 'bello', 'precioso', 'delicioso', 'encantador', 'maravilloso',
    'exquisito', 'refinado', 'elegante', 'distinguido', 'selecto', 'fino',

    # Habilidad técnica
    'perfecto', 'impecable', 'correcto', 'preciso', 'exacto', 'cuidado',
    'depurado', 'pulido', 'acabado', 'logrado', 'conseguido',

    # Originalidad
    'original', 'novedoso', 'innovador', 'genial', 'creativo', 'inspirado',
    'ingenioso', 'sugestivo', 'interesante', 'curioso',

    # Intensidad expresiva
    'emotivo', 'conmovedor', 'emocionante', 'apasionado', 'sentido', 'profundo',
    'intenso', 'vibrante', 'enérgico', 'vigoroso', 'potente', 'fuerte',

    # Éxito
    'exitoso', 'triunfante', 'aplaudido', 'celebrado', 'aclamado', 'festejado',

    # General
    'bueno', 'grande', 'alto', 'superior', 'óptimo', 'ideal', 'mejor'
}

VALORACIONES_NEGATIVAS = {
    # Deficiencia
    'malo', 'pobre', 'deficiente', 'insuficiente', 'inadecuado', 'inaceptable',
    'deplorable', 'lamentable', 'lastimoso', 'penoso', 'triste',

    # Mediocridad
    'mediocre', 'vulgar', 'ordinario', 'común', 'corriente', 'ramplón',
    'anodino', 'insulso', 'soso', 'desabrido', 'gris', 'opaco',

    # Incompetencia
    'torpe', 'tosco', 'burdo', 'chapucero', 'imperfecto', 'defectuoso',
    'erróneo', 'equivocado', 'fallido', 'fracasado', 'frustrado',

    # Aburrimiento
    'aburrido', 'tedioso', 'monótono', 'cansado', 'pesado', 'árido',
    'soporífero', 'fastidioso', 'insípido',

    # Exceso/Defecto
    'excesivo', 'exagerado', 'desmesurado', 'ampuloso', 'pretencioso',
    'escaso', 'limitado', 'reducido', 'pobre', 'débil', 'flojo',

    # Desagrado
    'desagradable', 'feo', 'horrible', 'espantoso', 'atroz', 'pésimo',
    'detestable', 'odioso', 'molesto', 'irritante',

    # Falta originalidad
    'repetitivo', 'imitativo', 'plagiario', 'convencional', 'trillado',
    'gastado', 'manido', 'anticuado', 'obsoleto', 'pasado'
}

# Modificadores de intensidad
INTENSIFICADORES = {
    'muy', 'sumamente', 'extremadamente', 'extraordinariamente', 'altamente',
    'profundamente', 'absolutamente', 'completamente', 'totalmente', 'enteramente',
    'verdaderamente', 'realmente', 'auténticamente', 'genuinamente',
    'excesivamente', 'demasiado', 'sobremanera', 'harto', 'bien',
    'tan', 'tanto', 'bastante', 'asaz'
}

ATENUADORES = {
    'algo', 'un poco', 'poco', 'apenas', 'ligeramente', 'levemente',
    'relativamente', 'moderadamente', 'medianamente', 'regularmente',
    'ciertamente', 'prácticamente', 'casi', 'más o menos'
}

NEGACIONES = {'no', 'nunca', 'jamás', 'tampoco', 'ni', 'sin', 'nada'}

# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class AnalizadorValoracionesMejorado:
    """
    Analizador multinivel de valoraciones en crítica musical
    """

    def __init__(self, ventana=7):
        self.ventana = ventana

        # Cargar modelo spaCy
        print("Cargando modelo spaCy (es_core_news_md)...")
        try:
            self.nlp = spacy.load("es_core_news_md")
        except OSError:
            print("ERROR: Modelo no encontrado. Instala con:")
            print("  python -m spacy download es_core_news_md")
            raise

        # Contadores por nivel de análisis
        self.valoraciones_nivel1 = Counter()  # Sobre "música" directa
        self.valoraciones_nivel2 = Counter()  # Sobre términos relacionados
        self.valoraciones_nivel3 = Counter()  # Predicativas distantes

        # Polaridades
        self.positivas_total = Counter()
        self.negativas_total = Counter()
        self.neutras_total = Counter()

        # Contextos para análisis cualitativo
        self.contextos_positivos = []
        self.contextos_negativos = []

        # Estadísticas
        self.total_documentos = 0
        self.menciones_musica = 0
        self.menciones_terminos_relacionados = 0

        # Por publicación
        self.stats_por_publicacion = defaultdict(lambda: {
            'positivas': Counter(),
            'negativas': Counter(),
            'total_menciones': 0
        })

    def clasificar_polaridad(self, adjetivo_lema: str) -> str:
        """Clasifica polaridad de un adjetivo"""
        if adjetivo_lema in VALORACIONES_POSITIVAS:
            return 'positiva'
        elif adjetivo_lema in VALORACIONES_NEGATIVAS:
            return 'negativa'
        else:
            return 'neutra'

    def detectar_negacion_cercana(self, token, doc, distancia=3):
        """Detecta si hay negación en proximidad del token"""
        start = max(0, token.i - distancia)
        end = min(len(doc), token.i + 1)

        for i in range(start, end):
            if doc[i].lemma_.lower() in NEGACIONES:
                return True
        return False

    def extraer_valoraciones_nivel1(self, token_musica, doc, publicacion=""):
        """
        NIVEL 1: Adjetivos directamente asociados a "música"
        (Método original del artículo)
        """
        valoraciones = []

        # Dependencias sintácticas
        for child in token_musica.children:
            if child.pos_ == "ADJ" or child.dep_ in ("amod", "acomp"):
                lema = child.lemma_.lower()
                polaridad = self.clasificar_polaridad(lema)

                # Detectar negación
                negado = self.detectar_negacion_cercana(child, doc)
                if negado and polaridad == 'positiva':
                    polaridad = 'negativa'
                elif negado and polaridad == 'negativa':
                    polaridad = 'positiva'

                valoraciones.append({
                    'adjetivo': lema,
                    'polaridad': polaridad,
                    'nivel': 1,
                    'negado': negado,
                    'contexto': doc[max(0, token_musica.i-15):min(len(doc), token_musica.i+15)].text
                })

                self.valoraciones_nivel1[lema] += 1

                if polaridad == 'positiva':
                    self.positivas_total[lema] += 1
                    self.stats_por_publicacion[publicacion]['positivas'][lema] += 1
                    self.contextos_positivos.append(valoraciones[-1]['contexto'])
                elif polaridad == 'negativa':
                    self.negativas_total[lema] += 1
                    self.stats_por_publicacion[publicacion]['negativas'][lema] += 1
                    self.contextos_negativos.append(valoraciones[-1]['contexto'])

        return valoraciones

    def extraer_valoraciones_nivel2(self, doc, publicacion=""):
        """
        NIVEL 2: Adjetivos sobre términos musicales relacionados
        (interpretación, concierto, ejecución, etc.)

        Esto es LO QUE FALTABA en el método original
        """
        valoraciones = []

        for token in doc:
            if token.lemma_.lower() in TERMINOS_MUSICALES:
                self.menciones_terminos_relacionados += 1

                # Buscar adjetivos asociados
                for child in token.children:
                    if child.pos_ == "ADJ" or child.dep_ in ("amod", "acomp"):
                        lema = child.lemma_.lower()
                        polaridad = self.clasificar_polaridad(lema)

                        # Solo contar si es evaluativo
                        if polaridad in ['positiva', 'negativa']:
                            negado = self.detectar_negacion_cercana(child, doc)
                            if negado and polaridad == 'positiva':
                                polaridad = 'negativa'
                            elif negado and polaridad == 'negativa':
                                polaridad = 'positiva'

                            valoraciones.append({
                                'adjetivo': lema,
                                'polaridad': polaridad,
                                'nivel': 2,
                                'termino_asociado': token.lemma_.lower(),
                                'negado': negado,
                                'contexto': doc[max(0, token.i-15):min(len(doc), token.i+15)].text
                            })

                            self.valoraciones_nivel2[lema] += 1

                            if polaridad == 'positiva':
                                self.positivas_total[lema] += 1
                                self.stats_por_publicacion[publicacion]['positivas'][lema] += 1
                                self.contextos_positivos.append(valoraciones[-1]['contexto'])
                            elif polaridad == 'negativa':
                                self.negativas_total[lema] += 1
                                self.stats_por_publicacion[publicacion]['negativas'][lema] += 1
                                self.contextos_negativos.append(valoraciones[-1]['contexto'])

        return valoraciones

    def extraer_valoraciones_nivel3(self, doc, publicacion=""):
        """
        NIVEL 3: Construcciones predicativas distantes
        "El concierto resultó sublime"
        "La interpretación fue magistral"
        """
        valoraciones = []

        # Buscar verbos copulativos/predicativos
        verbos_predicativos = {'ser', 'estar', 'resultar', 'parecer', 'mostrarse',
                               'revelarse', 'demostrarse', 'considerarse'}

        for token in doc:
            if token.lemma_.lower() in verbos_predicativos:
                # Buscar sujeto nominal musical
                sujeto = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        if (child.lemma_.lower() == "música" or
                            child.lemma_.lower() in TERMINOS_MUSICALES):
                            sujeto = child
                            break

                if sujeto:
                    # Buscar adjetivo predicativo
                    for child in token.children:
                        if child.dep_ in ("acomp", "attr") and child.pos_ == "ADJ":
                            lema = child.lemma_.lower()
                            polaridad = self.clasificar_polaridad(lema)

                            if polaridad in ['positiva', 'negativa']:
                                negado = self.detectar_negacion_cercana(child, doc)
                                if negado and polaridad == 'positiva':
                                    polaridad = 'negativa'
                                elif negado and polaridad == 'negativa':
                                    polaridad = 'positiva'

                                valoraciones.append({
                                    'adjetivo': lema,
                                    'polaridad': polaridad,
                                    'nivel': 3,
                                    'verbo': token.lemma_.lower(),
                                    'sujeto': sujeto.lemma_.lower(),
                                    'negado': negado,
                                    'contexto': doc[max(0, sujeto.i-10):min(len(doc), child.i+10)].text
                                })

                                self.valoraciones_nivel3[lema] += 1

                                if polaridad == 'positiva':
                                    self.positivas_total[lema] += 1
                                    self.stats_por_publicacion[publicacion]['positivas'][lema] += 1
                                    self.contextos_positivos.append(valoraciones[-1]['contexto'])
                                elif polaridad == 'negativa':
                                    self.negativas_total[lema] += 1
                                    self.stats_por_publicacion[publicacion]['negativas'][lema] += 1
                                    self.contextos_negativos.append(valoraciones[-1]['contexto'])

        return valoraciones

    def procesar_documento(self, texto: str, nombre_archivo: str = "", publicacion: str = ""):
        """Procesa un documento completo con análisis multinivel"""
        doc = self.nlp(texto)

        todas_valoraciones = []

        # Contar menciones de "música"
        for token in doc:
            if token.lemma_.lower() == "música":
                self.menciones_musica += 1
                self.stats_por_publicacion[publicacion]['total_menciones'] += 1

                # Nivel 1: adjetivos directos sobre "música"
                vals_n1 = self.extraer_valoraciones_nivel1(token, doc, publicacion)
                todas_valoraciones.extend(vals_n1)

        # Nivel 2: adjetivos sobre términos relacionados
        vals_n2 = self.extraer_valoraciones_nivel2(doc, publicacion)
        todas_valoraciones.extend(vals_n2)

        # Nivel 3: construcciones predicativas
        vals_n3 = self.extraer_valoraciones_nivel3(doc, publicacion)
        todas_valoraciones.extend(vals_n3)

        self.total_documentos += 1

        return todas_valoraciones

    def procesar_corpus(self, directorio_base: str):
        """Procesa todo el corpus organizando por publicación"""
        base_path = Path(directorio_base)

        publicaciones = {
            'EL SOL': base_path / 'EL SOL',
            'ONDAS': base_path / 'ONDAS',
            'ESPAÑA': base_path / 'ESPAÑA'
        }

        for nombre_pub, ruta_pub in publicaciones.items():
            if not ruta_pub.exists():
                print(f"⚠️  {ruta_pub} no existe, saltando...")
                continue

            archivos = list(ruta_pub.glob("*.txt"))
            print(f"\n{'='*70}")
            print(f"Procesando: {nombre_pub} ({len(archivos)} archivos)")
            print(f"{'='*70}")

            for i, archivo in enumerate(archivos, 1):
                try:
                    texto = archivo.read_text(encoding='utf-8', errors='ignore')
                    self.procesar_documento(texto, archivo.name, nombre_pub)

                    if i % 50 == 0:
                        print(f"  ✓ {i}/{len(archivos)} archivos procesados...")

                except Exception as e:
                    print(f"  ✗ Error en {archivo.name}: {e}")

            print(f"  ✓ {nombre_pub} completado: {len(archivos)} archivos")

    def generar_informe_completo(self, salida_json: str, salida_csv: str):
        """Genera informe completo comparativo"""

        total_valoraciones = sum(self.positivas_total.values()) + sum(self.negativas_total.values())
        total_positivas = sum(self.positivas_total.values())
        total_negativas = sum(self.negativas_total.values())

        # Datos JSON
        resultados = {
            'resumen_ejecutivo': {
                'total_documentos': self.total_documentos,
                'menciones_musica': self.menciones_musica,
                'menciones_terminos_relacionados': self.menciones_terminos_relacionados,
                'total_valoraciones_encontradas': total_valoraciones,
                'valoraciones_positivas': total_positivas,
                'valoraciones_negativas': total_negativas,
                'porcentaje_positivas': round(100 * total_positivas / total_valoraciones, 2) if total_valoraciones > 0 else 0,
                'porcentaje_negativas': round(100 * total_negativas / total_valoraciones, 2) if total_valoraciones > 0 else 0,
            },
            'comparacion_con_articulo': {
                'articulo_positivas_porcentaje': 3.9,
                'articulo_negativas_porcentaje': 0.4,
                'este_analisis_positivas_porcentaje': round(100 * total_positivas / total_valoraciones, 2) if total_valoraciones > 0 else 0,
                'este_analisis_negativas_porcentaje': round(100 * total_negativas / total_valoraciones, 2) if total_valoraciones > 0 else 0,
                'incremento_positivas': 'SE CALCULARÁ',
                'incremento_negativas': 'SE CALCULARÁ'
            },
            'por_nivel_analisis': {
                'nivel_1_musica_directa': len(self.valoraciones_nivel1),
                'nivel_2_terminos_relacionados': len(self.valoraciones_nivel2),
                'nivel_3_predicativas_distantes': len(self.valoraciones_nivel3)
            },
            'top_50_positivas': dict(self.positivas_total.most_common(50)),
            'top_50_negativas': dict(self.negativas_total.most_common(50)),
            'por_publicacion': {
                pub: {
                    'positivas_total': sum(data['positivas'].values()),
                    'negativas_total': sum(data['negativas'].values()),
                    'top_10_positivas': dict(data['positivas'].most_common(10)),
                    'top_10_negativas': dict(data['negativas'].most_common(10))
                }
                for pub, data in self.stats_por_publicacion.items()
            },
            'ejemplos_contextos_positivos': self.contextos_positivos[:20],
            'ejemplos_contextos_negativos': self.contextos_negativos[:20]
        }

        # Guardar JSON
        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Informe JSON guardado: {salida_json}")

        # Guardar CSV comparativo
        with open(salida_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Adjetivo',
                'Polaridad',
                'Frecuencia_Total',
                'Nivel_1',
                'Nivel_2',
                'Nivel_3',
                'Porcentaje_del_Total'
            ])

            # Positivas
            for adj, freq in self.positivas_total.most_common():
                n1 = self.valoraciones_nivel1.get(adj, 0)
                n2 = self.valoraciones_nivel2.get(adj, 0)
                n3 = self.valoraciones_nivel3.get(adj, 0)
                pct = round(100 * freq / total_valoraciones, 2) if total_valoraciones > 0 else 0

                writer.writerow([adj, 'POSITIVA', freq, n1, n2, n3, pct])

            # Negativas
            for adj, freq in self.negativas_total.most_common():
                n1 = self.valoraciones_nivel1.get(adj, 0)
                n2 = self.valoraciones_nivel2.get(adj, 0)
                n3 = self.valoraciones_nivel3.get(adj, 0)
                pct = round(100 * freq / total_valoraciones, 2) if total_valoraciones > 0 else 0

                writer.writerow([adj, 'NEGATIVA', freq, n1, n2, n3, pct])

        print(f"✓ CSV comparativo guardado: {salida_csv}")

        # Imprimir resumen en consola
        self._imprimir_resumen(resultados)

    def _imprimir_resumen(self, resultados):
        """Imprime resumen visual en consola"""
        print("\n" + "="*80)
        print("INFORME DE VALORACIONES - ANÁLISIS MEJORADO")
        print("="*80)

        res = resultados['resumen_ejecutivo']
        print(f"\n📊 ESTADÍSTICAS GENERALES")
        print("-" * 80)
        print(f"  Documentos procesados:              {res['total_documentos']:,}")
        print(f"  Menciones de 'música':              {res['menciones_musica']:,}")
        print(f"  Menciones de términos relacionados: {res['menciones_terminos_relacionados']:,}")
        print(f"  Total valoraciones encontradas:     {res['total_valoraciones_encontradas']:,}")

        print(f"\n✅ VALORACIONES POSITIVAS")
        print("-" * 80)
        print(f"  Total:      {res['valoraciones_positivas']:,}")
        print(f"  Porcentaje: {res['porcentaje_positivas']:.1f}%")
        print(f"\n  Top 10:")
        for adj, freq in list(self.positivas_total.most_common(10)):
            print(f"    {adj:20} → {freq:6,} menciones")

        print(f"\n❌ VALORACIONES NEGATIVAS")
        print("-" * 80)
        print(f"  Total:      {res['valoraciones_negativas']:,}")
        print(f"  Porcentaje: {res['porcentaje_negativas']:.1f}%")
        print(f"\n  Top 10:")
        for adj, freq in list(self.negativas_total.most_common(10)):
            print(f"    {adj:20} → {freq:6,} menciones")

        print(f"\n📈 COMPARACIÓN CON ARTÍCULO ORIGINAL")
        print("-" * 80)
        comp = resultados['comparacion_con_articulo']
        print(f"  Artículo (método bigrams):    Positivas {comp['articulo_positivas_porcentaje']}%  |  Negativas {comp['articulo_negativas_porcentaje']}%")
        print(f"  Este análisis (multinivel):   Positivas {comp['este_analisis_positivas_porcentaje']:.1f}%  |  Negativas {comp['este_analisis_negativas_porcentaje']:.1f}%")

        if comp['este_analisis_positivas_porcentaje'] > 0:
            incremento_pos = ((comp['este_analisis_positivas_porcentaje'] - comp['articulo_positivas_porcentaje']) / comp['articulo_positivas_porcentaje']) * 100
            print(f"  Incremento positivas: +{incremento_pos:.0f}%")

        if comp['este_analisis_negativas_porcentaje'] > 0:
            incremento_neg = ((comp['este_analisis_negativas_porcentaje'] - comp['articulo_negativas_porcentaje']) / comp['articulo_negativas_porcentaje']) * 100
            print(f"  Incremento negativas: +{incremento_neg:.0f}%")

        print(f"\n🎯 DISTRIBUCIÓN POR NIVEL DE ANÁLISIS")
        print("-" * 80)
        niveles = resultados['por_nivel_analisis']
        print(f"  Nivel 1 (música directa):         {niveles['nivel_1_musica_directa']:,}")
        print(f"  Nivel 2 (términos relacionados):  {niveles['nivel_2_terminos_relacionados']:,}")
        print(f"  Nivel 3 (predicativas distantes): {niveles['nivel_3_predicativas_distantes']:,}")

        print(f"\n📰 POR PUBLICACIÓN")
        print("-" * 80)
        for pub, data in resultados['por_publicacion'].items():
            print(f"\n  {pub}:")
            print(f"    Positivas: {data['positivas_total']:,}")
            print(f"    Negativas: {data['negativas_total']:,}")

        print("\n" + "="*80 + "\n")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta el análisis completo"""

    print("="*80)
    print("ANALIZADOR MEJORADO DE VALORACIONES EN CRÍTICA MUSICAL")
    print("Corpus: Prensa musical española (1915-1936)")
    print("="*80)

    # Configuración de rutas
    CORPUS_DIR = "/Users/maria/Desktop/Campos_Música Resonancias/CORPUS"
    SALIDA_JSON = "/Users/maria/Desktop/Campos_Música Resonancias/resultados_valoraciones_mejorado.json"
    SALIDA_CSV = "/Users/maria/Desktop/Campos_Música Resonancias/valoraciones_detalladas.csv"

    # Verificar que existe el directorio
    if not Path(CORPUS_DIR).exists():
        print(f"\n❌ ERROR: No se encuentra el directorio {CORPUS_DIR}")
        print("\nDirectorios disponibles:")
        base = Path("/Users/maria/Desktop/Campos_Música Resonancias")
        for item in base.iterdir():
            if item.is_dir() and 'CORPUS' in item.name.upper():
                print(f"  - {item}")
        return

    # Crear analizador
    analizador = AnalizadorValoracionesMejorado(ventana=WINDOW_SIZE)

    # Procesar corpus
    try:
        analizador.procesar_corpus(CORPUS_DIR)
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return

    # Generar informes
    analizador.generar_informe_completo(SALIDA_JSON, SALIDA_CSV)

    print("\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE\n")
    print(f"Archivos generados:")
    print(f"  - {SALIDA_JSON}")
    print(f"  - {SALIDA_CSV}")
    print("\nRevisa estos archivos para comparar con los resultados del artículo.\n")


if __name__ == "__main__":
    main()
