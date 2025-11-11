#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versión optimizada del analizador con barra de progreso
"""

import spacy
from collections import Counter, defaultdict
import json
import csv
from pathlib import Path
import re
import sys

# Configuración
WINDOW_SIZE = 5
MIN_FREQ = 3

EXCLUSIONES = {
    'cámara', 'palacio', 'teatro', 'conservatorio', 'salón', 'academia',
    'sociedad', 'círculo', 'club', 'historia', 'escuela', 'maestro',
    'director', 'compositor', 'orquesta', 'programa', 'concierto',
    'ópera', 'zarzuela', 'sinfonía', 'obra', 'pieza', 'festival',
    'temporada', 'sesión', 'audición', 'función', 'estreno', 'interpretación',
    'crítica', 'revista', 'periódico', 'artículo', 'sección', 'página',
    'número', 'edición', 'serie', 'colección', 'mundo', 'vida', 'arte',
    'cultura', 'época', 'siglo', 'tiempo', 'momento', 'día', 'noche',
    'tarde', 'mañana', 'semana', 'mes', 'año', 'década', 'periodo',
    'casa', 'sala', 'local', 'edificio', 'ciudad', 'país', 'capital',
    'centro', 'instituto', 'universidad', 'ministerio', 'gobierno'
}

print("Cargando modelo de spaCy...", flush=True)
nlp = spacy.load("es_core_news_md")
print("✓ Modelo cargado", flush=True)

class AnalizadorVentanaColocacional:
    def __init__(self, ventana=5):
        self.ventana = ventana
        self.adjetivos_dependencia = Counter()
        self.adjetivos_ventana = Counter()
        self.contextos = defaultdict(list)
        self.relaciones_sintacticas = defaultdict(list)
        self.total_menciones_musica = 0
        self.docs_procesados = 0

        # Estadísticas por fuente
        self.stats_por_fuente = defaultdict(lambda: {
            'menciones_musica': 0,
            'adjetivos_dep': Counter(),
            'adjetivos_vent': Counter()
        })

    def es_adjetivo_valido(self, token) -> bool:
        if token.pos_ != "ADJ":
            return False
        lema = token.lemma_.lower()
        if lema in EXCLUSIONES:
            return False
        if len(lema) < 3:
            return False
        if not re.match(r'^[a-záéíóúñü]+$', lema):
            return False
        return True

    def extraer_adjetivos_dependencia(self, token_musica, doc):
        adjetivos_encontrados = []

        # Modificadores directos
        for child in token_musica.children:
            if child.dep_ == "amod" and self.es_adjetivo_valido(child):
                adjetivos_encontrados.append({
                    'lema': child.lemma_.lower(),
                    'relacion': 'amod',
                    'texto': child.text,
                    'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                })

                # Coordinación
                for conj_child in child.children:
                    if conj_child.dep_ == "conj" and self.es_adjetivo_valido(conj_child):
                        adjetivos_encontrados.append({
                            'lema': conj_child.lemma_.lower(),
                            'relacion': 'conj',
                            'texto': conj_child.text,
                            'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                        })

        # Construcciones predicativas
        if token_musica.dep_ in ["nsubj", "nsubjpass"]:
            head = token_musica.head
            for child in head.children:
                if child.dep_ in ["acomp", "attr"] and self.es_adjetivo_valido(child):
                    adjetivos_encontrados.append({
                        'lema': child.lemma_.lower(),
                        'relacion': child.dep_,
                        'texto': child.text,
                        'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                    })

        if token_musica.dep_ in ["dobj", "obj"]:
            head = token_musica.head
            for child in head.children:
                if child.dep_ == "xcomp" and self.es_adjetivo_valido(child):
                    adjetivos_encontrados.append({
                        'lema': child.lemma_.lower(),
                        'relacion': 'xcomp',
                        'texto': child.text,
                        'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                    })

        return adjetivos_encontrados

    def extraer_adjetivos_ventana(self, token_musica, doc):
        adjetivos_encontrados = []
        start = max(0, token_musica.i - self.ventana)
        end = min(len(doc), token_musica.i + self.ventana + 1)

        for i in range(start, end):
            if i == token_musica.i:
                continue
            token = doc[i]
            if self.es_adjetivo_valido(token):
                distancia = abs(token.i - token_musica.i)
                adjetivos_encontrados.append({
                    'lema': token.lemma_.lower(),
                    'distancia': distancia,
                    'texto': token.text,
                    'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                })

        return adjetivos_encontrados

    def procesar_documento(self, texto: str, nombre_archivo: str = "", fuente: str = ""):
        doc = nlp(texto)
        menciones = 0

        for token in doc:
            if token.lemma_.lower() == "música":
                menciones += 1
                self.total_menciones_musica += 1

                if fuente:
                    self.stats_por_fuente[fuente]['menciones_musica'] += 1

                # Dependencias
                adj_dep = self.extraer_adjetivos_dependencia(token, doc)
                for adj in adj_dep:
                    self.adjetivos_dependencia[adj['lema']] += 1
                    if fuente:
                        self.stats_por_fuente[fuente]['adjetivos_dep'][adj['lema']] += 1
                    self.relaciones_sintacticas[adj['relacion']].append({
                        'adjetivo': adj['lema'],
                        'archivo': nombre_archivo,
                        'contexto': adj['contexto']
                    })

                # Ventana
                adj_vent = self.extraer_adjetivos_ventana(token, doc)
                for adj in adj_vent:
                    self.adjetivos_ventana[adj['lema']] += 1
                    if fuente:
                        self.stats_por_fuente[fuente]['adjetivos_vent'][adj['lema']] += 1
                    self.contextos[adj['lema']].append({
                        'archivo': nombre_archivo,
                        'contexto': adj['contexto'],
                        'distancia': adj['distancia']
                    })

        self.docs_procesados += 1
        return menciones

    def procesar_corpus(self, directorio_corpus: str):
        base_path = Path(directorio_corpus)
        rutas = [
            (base_path / "EL SOL", "EL SOL"),
            (base_path / "ONDAS", "ONDAS"),
            (base_path / "ESPAÑA", "ESPAÑA")
        ]

        total_archivos = 0
        for ruta, _ in rutas:
            if ruta.exists():
                total_archivos += len(list(ruta.glob("*.txt")))

        print(f"\n{'='*70}")
        print(f"Total de archivos a procesar: {total_archivos}")
        print(f"{'='*70}\n", flush=True)

        archivos_procesados = 0

        for ruta, fuente in rutas:
            if not ruta.exists():
                print(f"⚠ Advertencia: {ruta} no existe", flush=True)
                continue

            archivos = list(ruta.glob("*.txt"))
            print(f"\n📁 Procesando {len(archivos)} archivos de {fuente}...", flush=True)

            for i, archivo in enumerate(archivos, 1):
                try:
                    with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                        texto = f.read()

                    menciones = self.procesar_documento(texto, f"{fuente}/{archivo.name}", fuente)
                    archivos_procesados += 1

                    if i % 50 == 0:
                        progreso = (archivos_procesados / total_archivos) * 100
                        print(f"  ✓ {i}/{len(archivos)} archivos de {fuente} procesados ({progreso:.1f}% total)", flush=True)

                except Exception as e:
                    print(f"  ✗ Error en {archivo.name}: {e}", flush=True)

            print(f"✓ {fuente} completado: {len(archivos)} archivos procesados", flush=True)

        print(f"\n{'='*70}")
        print(f"✓ PROCESAMIENTO COMPLETADO")
        print(f"{'='*70}")
        print(f"Total archivos procesados: {archivos_procesados}")
        print(f"Total menciones 'música': {self.total_menciones_musica}")
        print(f"{'='*70}\n", flush=True)

    def generar_informe(self, salida_json: str, salida_csv: str):
        # Preparar datos
        resultados = {
            'estadisticas_generales': {
                'total_menciones_musica': self.total_menciones_musica,
                'documentos_procesados': self.docs_procesados,
                'adjetivos_unicos_dependencia': len(self.adjetivos_dependencia),
                'adjetivos_unicos_ventana': len(self.adjetivos_ventana),
                'ventana_size': self.ventana
            },
            'estadisticas_por_fuente': {
                fuente: {
                    'menciones_musica': stats['menciones_musica'],
                    'top_20_dependencia': dict(stats['adjetivos_dep'].most_common(20)),
                    'top_20_ventana': dict(stats['adjetivos_vent'].most_common(20))
                }
                for fuente, stats in self.stats_por_fuente.items()
            },
            'top_adjetivos_dependencia': dict(self.adjetivos_dependencia.most_common(100)),
            'top_adjetivos_ventana': dict(self.adjetivos_ventana.most_common(100)),
            'relaciones_sintacticas_stats': {
                rel: len(casos) for rel, casos in self.relaciones_sintacticas.items()
            }
        }

        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print(f"✓ Informe JSON guardado: {salida_json}", flush=True)

        # CSV comparativo
        with open(salida_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Adjetivo',
                'Freq_Dependencia',
                'Freq_Ventana',
                'Diferencia_Abs',
                'Ratio_Ventana/Dependencia',
                'Porcentaje_Dependencia',
                'Porcentaje_Ventana'
            ])

            todos_adjetivos = set(self.adjetivos_dependencia.keys()) | set(self.adjetivos_ventana.keys())
            total_dep = sum(self.adjetivos_dependencia.values())
            total_vent = sum(self.adjetivos_ventana.values())

            for adj in sorted(todos_adjetivos,
                            key=lambda x: self.adjetivos_dependencia[x] + self.adjetivos_ventana[x],
                            reverse=True):
                freq_dep = self.adjetivos_dependencia[adj]
                freq_vent = self.adjetivos_ventana[adj]
                diferencia = freq_vent - freq_dep
                ratio = freq_vent / freq_dep if freq_dep > 0 else float('inf')
                pct_dep = (freq_dep / total_dep * 100) if total_dep > 0 else 0
                pct_vent = (freq_vent / total_vent * 100) if total_vent > 0 else 0

                writer.writerow([adj, freq_dep, freq_vent, diferencia, f"{ratio:.2f}",
                               f"{pct_dep:.2f}", f"{pct_vent:.2f}"])

        print(f"✓ Informe CSV guardado: {salida_csv}", flush=True)

        # Resumen por pantalla
        print(f"\n{'='*70}")
        print("RESUMEN DE RESULTADOS")
        print(f"{'='*70}\n")

        print("📊 ESTADÍSTICAS GENERALES:")
        print(f"  • Documentos procesados: {self.docs_procesados}")
        print(f"  • Menciones 'música': {self.total_menciones_musica}")
        print(f"  • Adjetivos únicos (Dependencia): {len(self.adjetivos_dependencia)}")
        print(f"  • Adjetivos únicos (Ventana ±{self.ventana}): {len(self.adjetivos_ventana)}")

        print(f"\n📈 POR FUENTE:")
        for fuente in ["EL SOL", "ONDAS", "ESPAÑA"]:
            if fuente in self.stats_por_fuente:
                stats = self.stats_por_fuente[fuente]
                print(f"\n  {fuente}:")
                print(f"    • Menciones 'música': {stats['menciones_musica']}")
                print(f"    • Top 5 (Dependencia):")
                for adj, freq in stats['adjetivos_dep'].most_common(5):
                    print(f"      - {adj}: {freq}")

        print(f"\n🔝 TOP 20 ADJETIVOS (Método DEPENDENCIA):")
        print(f"{'-'*70}")
        for i, (adj, freq) in enumerate(self.adjetivos_dependencia.most_common(20), 1):
            pct = (freq / sum(self.adjetivos_dependencia.values()) * 100)
            print(f"  {i:2}. {adj:20} {freq:6} ({pct:5.2f}%)")

        print(f"\n🔝 TOP 20 ADJETIVOS (Método VENTANA ±{self.ventana}):")
        print(f"{'-'*70}")
        for i, (adj, freq) in enumerate(self.adjetivos_ventana.most_common(20), 1):
            pct = (freq / sum(self.adjetivos_ventana.values()) * 100)
            print(f"  {i:2}. {adj:20} {freq:6} ({pct:5.2f}%)")

        print(f"\n{'='*70}\n", flush=True)


def main():
    print(f"{'='*70}")
    print("ANALIZADOR DE VENTANA COLOCACIONAL EXPANDIDA")
    print("Corpus: Prensa musical española (1915-1935)")
    print(f"{'='*70}\n", flush=True)

    CORPUS_DIR = "/Users/maria/Desktop/Campos_Música/CORPUS"
    SALIDA_JSON = "/Users/maria/Desktop/Campos_Música/resultados_ventana_colocacional.json"
    SALIDA_CSV = "/Users/maria/Desktop/Campos_Música/comparacion_metodos_adjetivacion.csv"

    analizador = AnalizadorVentanaColocacional(ventana=WINDOW_SIZE)
    analizador.procesar_corpus(CORPUS_DIR)
    analizador.generar_informe(SALIDA_JSON, SALIDA_CSV)

    print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE\n", flush=True)


if __name__ == "__main__":
    main()
