#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de ventana colocacional expandida para "música"
Versión mejorada con análisis de dependencias sintácticas y ventana ±3-5 palabras

Proyecto: LexiMus - Análisis de prensa musical española (1915-1935)
Autor: María Palacios Nieto - Universidad de Salamanca
Fecha: Noviembre 2024
"""

import spacy
from collections import Counter, defaultdict
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re

# Configuración
WINDOW_SIZE = 5  # Ventana de ±5 palabras (ajustable a 3)
MIN_FREQ = 3  # Frecuencia mínima para considerar un adjetivo

# Cargar modelo de spaCy (asegúrate de tener instalado: python -m spacy download es_core_news_md)
print("Cargando modelo de spaCy...")
nlp = spacy.load("es_core_news_md")

# Listas de exclusión (sustantivos que pueden aparecer como falsos positivos)
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

class AnalizadorVentanaColocacional:
    """
    Analizador avanzado de adjetivaciones asociadas a 'música' mediante:
    1. Análisis de dependencias sintácticas (relaciones amod, nsubj, acomp, conj)
    2. Ventana colocacional de ±3-5 palabras
    3. Filtrado por POS-tagging (solo adjetivos reales)
    """

    def __init__(self, ventana=5):
        self.ventana = ventana
        self.adjetivos_dependencia = Counter()  # Adjetivos por dependencia sintáctica
        self.adjetivos_ventana = Counter()      # Adjetivos por proximidad
        self.contextos = defaultdict(list)      # Contextos completos para análisis cualitativo
        self.relaciones_sintacticas = defaultdict(list)

        # Estadísticas
        self.total_menciones_musica = 0
        self.docs_procesados = 0

    def es_adjetivo_valido(self, token) -> bool:
        """
        Verifica si un token es un adjetivo válido
        - Debe ser POS=ADJ
        - No estar en lista de exclusiones
        - Tener al menos 3 caracteres
        """
        if token.pos_ != "ADJ":
            return False

        lema = token.lemma_.lower()

        if lema in EXCLUSIONES:
            return False

        if len(lema) < 3:
            return False

        # Filtrar números y símbolos
        if not re.match(r'^[a-záéíóúñü]+$', lema):
            return False

        return True

    def extraer_adjetivos_dependencia(self, token_musica, doc):
        """
        Extrae adjetivos mediante análisis de dependencias sintácticas

        Relaciones analizadas:
        - amod: modificador adjetival directo ("música española")
        - conj: adjetivos coordinados ("música española y moderna")
        - nsubj/nsubjpass: sujeto nominal ("La música es sublime")
        - acomp: complemento adjetival ("la música resultó magnífica")
        - xcomp: complemento predicativo ("consideran la música excelente")
        """
        adjetivos_encontrados = []

        # 1. Modificadores adjetivales directos (amod)
        for child in token_musica.children:
            if child.dep_ == "amod" and self.es_adjetivo_valido(child):
                adjetivos_encontrados.append({
                    'lema': child.lemma_.lower(),
                    'relacion': 'amod',
                    'texto': child.text,
                    'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                })

                # Buscar adjetivos coordinados ("española y moderna")
                for conj_child in child.children:
                    if conj_child.dep_ == "conj" and self.es_adjetivo_valido(conj_child):
                        adjetivos_encontrados.append({
                            'lema': conj_child.lemma_.lower(),
                            'relacion': 'conj',
                            'texto': conj_child.text,
                            'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                        })

        # 2. Construcciones predicativas ("La música es española")
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

        # 3. Música como objeto ("consideran la música excelente")
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
        """
        Extrae adjetivos en ventana de ±N palabras, filtrando por POS
        """
        adjetivos_encontrados = []

        start = max(0, token_musica.i - self.ventana)
        end = min(len(doc), token_musica.i + self.ventana + 1)

        for i in range(start, end):
            if i == token_musica.i:  # Saltar el token "música"
                continue

            token = doc[i]
            if self.es_adjetivo_valido(token):
                # Calcular distancia
                distancia = abs(token.i - token_musica.i)

                adjetivos_encontrados.append({
                    'lema': token.lemma_.lower(),
                    'distancia': distancia,
                    'texto': token.text,
                    'contexto': doc[max(0, token_musica.i-10):min(len(doc), token_musica.i+10)].text
                })

        return adjetivos_encontrados

    def procesar_documento(self, texto: str, nombre_archivo: str = ""):
        """
        Procesa un documento completo
        """
        doc = nlp(texto)

        # Buscar todas las menciones de "música/músicas"
        menciones = 0
        for token in doc:
            if token.lemma_.lower() == "música":
                menciones += 1
                self.total_menciones_musica += 1

                # Extraer adjetivos por dependencia sintáctica
                adj_dep = self.extraer_adjetivos_dependencia(token, doc)
                for adj in adj_dep:
                    self.adjetivos_dependencia[adj['lema']] += 1
                    self.relaciones_sintacticas[adj['relacion']].append({
                        'adjetivo': adj['lema'],
                        'archivo': nombre_archivo,
                        'contexto': adj['contexto']
                    })

                # Extraer adjetivos por ventana colocacional
                adj_vent = self.extraer_adjetivos_ventana(token, doc)
                for adj in adj_vent:
                    self.adjetivos_ventana[adj['lema']] += 1
                    self.contextos[adj['lema']].append({
                        'archivo': nombre_archivo,
                        'contexto': adj['contexto'],
                        'distancia': adj['distancia']
                    })

        self.docs_procesados += 1
        return menciones

    def procesar_corpus(self, directorio_corpus: str, subcorpus: str = ""):
        """
        Procesa todos los archivos .txt de un directorio

        Args:
            directorio_corpus: Ruta base del corpus
            subcorpus: "EL SOL", "ONDAS", "ESPAÑA" o "" para todos
        """
        base_path = Path(directorio_corpus)

        if subcorpus:
            rutas = [base_path / subcorpus]
        else:
            rutas = [base_path / "EL SOL", base_path / "ONDAS", base_path / "ESPAÑA"]

        archivos_procesados = 0

        for ruta in rutas:
            if not ruta.exists():
                print(f"Advertencia: {ruta} no existe")
                continue

            archivos = list(ruta.glob("*.txt"))
            print(f"\nProcesando {len(archivos)} archivos de {ruta.name}...")

            for archivo in archivos:
                try:
                    with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                        texto = f.read()

                    menciones = self.procesar_documento(texto, f"{ruta.name}/{archivo.name}")
                    archivos_procesados += 1

                    if archivos_procesados % 50 == 0:
                        print(f"  Procesados {archivos_procesados} archivos...")

                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")

        print(f"\n✓ Procesados {archivos_procesados} archivos")
        print(f"✓ {self.total_menciones_musica} menciones de 'música' encontradas")

    def generar_informe(self, salida_json: str, salida_csv: str):
        """
        Genera informes en JSON y CSV
        """
        # Preparar datos
        resultados = {
            'estadisticas_generales': {
                'total_menciones_musica': self.total_menciones_musica,
                'documentos_procesados': self.docs_procesados,
                'adjetivos_unicos_dependencia': len(self.adjetivos_dependencia),
                'adjetivos_unicos_ventana': len(self.adjetivos_ventana),
                'ventana_size': self.ventana
            },
            'top_adjetivos_dependencia': dict(self.adjetivos_dependencia.most_common(100)),
            'top_adjetivos_ventana': dict(self.adjetivos_ventana.most_common(100)),
            'relaciones_sintacticas_stats': {
                rel: len(casos) for rel, casos in self.relaciones_sintacticas.items()
            }
        }

        # Guardar JSON
        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Informe JSON guardado en: {salida_json}")

        # Guardar CSV comparativo
        with open(salida_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Adjetivo',
                'Freq_Dependencia',
                'Freq_Ventana',
                'Diferencia_Abs',
                'Ratio_Ventana/Dependencia'
            ])

            todos_adjetivos = set(self.adjetivos_dependencia.keys()) | set(self.adjetivos_ventana.keys())

            for adj in sorted(todos_adjetivos,
                            key=lambda x: self.adjetivos_dependencia[x] + self.adjetivos_ventana[x],
                            reverse=True):
                freq_dep = self.adjetivos_dependencia[adj]
                freq_vent = self.adjetivos_ventana[adj]
                diferencia = freq_vent - freq_dep
                ratio = freq_vent / freq_dep if freq_dep > 0 else float('inf')

                writer.writerow([adj, freq_dep, freq_vent, diferencia, f"{ratio:.2f}"])

        print(f"✓ Informe CSV guardado en: {salida_csv}")

        # Imprimir resumen
        print("\n" + "="*70)
        print("RESUMEN DE RESULTADOS")
        print("="*70)
        print(f"\nMétodo de DEPENDENCIA SINTÁCTICA (más preciso):")
        print("-" * 70)
        for adj, freq in self.adjetivos_dependencia.most_common(20):
            print(f"  {adj:20} {freq:6}")

        print(f"\nMétodo de VENTANA COLOCACIONAL ±{self.ventana} (más exhaustivo):")
        print("-" * 70)
        for adj, freq in self.adjetivos_ventana.most_common(20):
            print(f"  {adj:20} {freq:6}")

        print("\n" + "="*70)


def main():
    """
    Función principal
    """
    print("="*70)
    print("ANALIZADOR DE VENTANA COLOCACIONAL EXPANDIDA")
    print("Corpus: Prensa musical española (1915-1935)")
    print("="*70)

    # Configuración de rutas
    CORPUS_DIR = "/Users/maria/Desktop/Campos_Música/CORPUS"
    SALIDA_JSON = "/Users/maria/Desktop/Campos_Música/resultados_ventana_colocacional.json"
    SALIDA_CSV = "/Users/maria/Desktop/Campos_Música/comparacion_metodos_adjetivacion.csv"

    # Crear analizador
    analizador = AnalizadorVentanaColocacional(ventana=WINDOW_SIZE)

    # Procesar corpus completo
    analizador.procesar_corpus(CORPUS_DIR)

    # Generar informes
    analizador.generar_informe(SALIDA_JSON, SALIDA_CSV)

    print("\n✓ Análisis completado exitosamente")


if __name__ == "__main__":
    main()
