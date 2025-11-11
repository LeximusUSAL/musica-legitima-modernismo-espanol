#!/usr/bin/env python3
"""
Detector Automático de Género en Personas Musicales
Linguistic Gender Detection for Musical Press Analysis

Este script analiza textos musicales (revistas, prensa, corpus) y detecta automáticamente
menciones de hombres y mujeres relacionados con la música mediante:
- Listas de nombres españoles históricos y actuales
- Patrones contextuales de tratamiento formal (Don/Doña, Sr./Sra.)
- Términos profesionales masculinos/femeninos
- Análisis estadístico con ratios de sesgo de género

Proyecto: LexiMus - Universidad de Salamanca
Autor: María [Generado con Claude Code]
Licencia: MIT
"""

import os
import re
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime

class DetectorGeneroMusical:
    def __init__(self, base_directory):
        """
        Inicializa el detector de género

        Args:
            base_directory (str): Ruta al directorio con archivos TXT
        """
        self.base_directory = base_directory
        self.resultados = {}
        self.total_archivos = 0
        self.total_palabras = 0

        # =================================================================
        # LISTAS DE NOMBRES ESPAÑOLES (Expandibles)
        # =================================================================

        # Nombres masculinos históricos y actuales comunes en España
        self.nombres_masculinos = {
            # Clásicos históricos (s. XIX-XX)
            'manuel', 'antonio', 'josé', 'francisco', 'juan', 'pedro', 'luis',
            'carlos', 'miguel', 'rafael', 'fernando', 'jesús', 'ángel', 'diego',
            'pablo', 'andrés', 'ramón', 'tomás', 'enrique', 'alberto', 'joaquín',
            'ricardo', 'felipe', 'ignacio', 'jaime', 'sergio', 'alejandro',

            # Compositores/músicos históricos españoles
            'isaac', 'tomás', 'joaquín', 'manuel', 'ruperto', 'federico',
            'emilio', 'pablo', 'andrés', 'adolfo', 'jesús', 'conrado',

            # Nombres modernos
            'david', 'daniel', 'jorge', 'adrián', 'iván', 'rubén', 'mario',
            'oscar', 'héctor', 'raúl', 'víctor', 'hugo', 'marcos', 'álvaro'
        }

        # Nombres femeninos históricos y actuales
        self.nombres_femeninos = {
            # Clásicos históricos
            'maría', 'carmen', 'josefa', 'dolores', 'pilar', 'teresa',
            'ana', 'francisca', 'isabel', 'rosa', 'antonia', 'mercedes',
            'concepción', 'concha', 'victoria', 'angeles', 'trinidad',
            'encarnación', 'amparo', 'remedios', 'esperanza', 'asunción',

            # Músicas/cantantes históricas
            'consuelo', 'rosario', 'emilia', 'carlota', 'matilde', 'eugenia',
            'margarita', 'carolina', 'elvira', 'adela', 'julia', 'luisa',

            # Nombres modernos
            'laura', 'sara', 'patricia', 'marta', 'elena', 'raquel',
            'cristina', 'paula', 'andrea', 'silvia', 'natalia', 'beatriz',
            'lucía', 'sofía', 'alba', 'claudia', 'sandra', 'mónica'
        }

        # =================================================================
        # TRATAMIENTOS FORMALES
        # =================================================================

        self.tratamientos_masculinos = [
            r'\bdon\s+\w+',           # Don Manuel
            r'\bd\.\s+\w+',           # D. Manuel
            r'\bsr\.\s+\w+',          # Sr. García
            r'\bseñor\s+\w+',         # Señor García
            r'\bmaestro\s+\w+',       # Maestro Albéniz
            r'\bmtro\.\s+\w+',        # Mtro. Albéniz
            r'\bprof\.\s+\w+',        # Prof. García (masculino)
        ]

        self.tratamientos_femeninos = [
            r'\bdoña\s+\w+',          # Doña Carmen
            r'\bdª\.\s+\w+',          # Dª. Carmen
            r'\bdña\.\s+\w+',         # Dña. Carmen
            r'\bsra\.\s+\w+',         # Sra. García
            r'\bseñora\s+\w+',        # Señora García
            r'\bmaestra\s+\w+',       # Maestra Malibran
            r'\bmtra\.\s+\w+',        # Mtra. Malibran
        ]

        # =================================================================
        # TÉRMINOS PROFESIONALES MUSICALES
        # =================================================================

        self.profesiones_masculinas = [
            'compositor', 'pianista', 'violinista', 'director', 'guitarrista',
            'tenor', 'barítono', 'bajo', 'organista', 'concertista',
            'virtuoso', 'solista', 'maestro', 'crítico', 'musicólogo',
            'cantante', 'intérprete', 'ejecutante', 'autor', 'profesor',
            'violonchelista', 'flautista', 'oboísta', 'clarinetista',
            'trompetista', 'violista', 'contrabajista', 'saxofonista'
        ]

        self.profesiones_femeninas = [
            'compositora', 'pianista', 'violinista', 'directora', 'guitarrista',
            'soprano', 'mezzosoprano', 'mezzo-soprano', 'contralto',
            'organista', 'concertista', 'virtuosa', 'solista', 'maestra',
            'crítica', 'musicóloga', 'cantante', 'intérprete', 'ejecutante',
            'autora', 'profesora', 'violonchelista', 'flautista', 'oboísta',
            'clarinetista', 'trompetista', 'violista', 'contrabajista',
            'cantaora', 'bailaora', 'arpista', 'saxofonista'
        ]

        # =================================================================
        # CONTEXTO DIVERSIDAD Y SESGOS
        # =================================================================

        self.terminos_diversidad = [
            'gitano', 'gitana', 'flamenco', 'flamenca', 'afroamericano',
            'afroamericana', 'negro', 'negra', 'judío', 'judía', 'árabe',
            'oriental', 'indígena', 'latinoamericano', 'latinoamericana',
            'hispano', 'hispana', 'mestizo', 'mestiza'
        ]

    # =====================================================================
    # MÉTODOS DE DETECCIÓN
    # =====================================================================

    def detectar_nombres_personas(self, contenido):
        """
        Detecta nombres propios en el texto usando contexto

        Returns:
            dict: {'masculinos': Counter, 'femeninos': Counter,
                   'ejemplos_masculinos': dict, 'ejemplos_femeninos': dict}
        """
        nombres_detectados = {
            'masculinos': Counter(),
            'femeninos': Counter(),
            'ejemplos_masculinos': {},
            'ejemplos_femeninos': {}
        }

        # Normalizar contenido
        contenido_lower = contenido.lower()

        # Buscar nombres masculinos con contexto
        for nombre in self.nombres_masculinos:
            # Patrón: nombre con mayúscula seguido de apellido o contexto
            patron = r'\b' + nombre.capitalize() + r'\b(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?'
            matches = list(re.finditer(patron, contenido, re.IGNORECASE))
            if len(matches) > 0:
                nombres_detectados['masculinos'][nombre] = len(matches)
                # Guardar ejemplos de nombres completos (máximo 3)
                ejemplos = list(set([m.group(0).strip() for m in matches[:5]]))[:3]
                nombres_detectados['ejemplos_masculinos'][nombre] = ejemplos

        # Buscar nombres femeninos con contexto
        for nombre in self.nombres_femeninos:
            patron = r'\b' + nombre.capitalize() + r'\b(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?'
            matches = list(re.finditer(patron, contenido, re.IGNORECASE))
            if len(matches) > 0:
                nombres_detectados['femeninos'][nombre] = len(matches)
                # Guardar ejemplos de nombres completos (máximo 3)
                ejemplos = list(set([m.group(0).strip() for m in matches[:5]]))[:3]
                nombres_detectados['ejemplos_femeninos'][nombre] = ejemplos

        return nombres_detectados

    def detectar_tratamientos_formales(self, contenido):
        """
        Detecta tratamientos formales (Don, Doña, Sr., Sra., etc.)

        Returns:
            dict: {'masculinos': int, 'femeninos': int}
        """
        tratamientos = {
            'masculinos': 0,
            'femeninos': 0
        }

        # Contar tratamientos masculinos
        for patron in self.tratamientos_masculinos:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            tratamientos['masculinos'] += len(matches)

        # Contar tratamientos femeninos
        for patron in self.tratamientos_femeninos:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            tratamientos['femeninos'] += len(matches)

        return tratamientos

    def detectar_profesiones_musicales(self, contenido):
        """
        Detecta menciones de profesiones musicales por género

        Returns:
            dict: {'masculinas': Counter, 'femeninas': Counter}
        """
        profesiones = {
            'masculinas': Counter(),
            'femeninas': Counter()
        }

        contenido_lower = contenido.lower()

        # Profesiones masculinas
        for profesion in self.profesiones_masculinas:
            count = len(re.findall(r'\b' + re.escape(profesion) + r'\b',
                                  contenido_lower))
            if count > 0:
                profesiones['masculinas'][profesion] = count

        # Profesiones femeninas
        for profesion in self.profesiones_femeninas:
            count = len(re.findall(r'\b' + re.escape(profesion) + r'\b',
                                  contenido_lower))
            if count > 0:
                profesiones['femeninas'][profesion] = count

        return profesiones

    def detectar_diversidad_cultural(self, contenido):
        """
        Detecta menciones de diversidad étnica/cultural

        Returns:
            Counter: Conteo de términos de diversidad
        """
        diversidad = Counter()
        contenido_lower = contenido.lower()

        for termino in self.terminos_diversidad:
            count = len(re.findall(r'\b' + re.escape(termino) + r'\b',
                                  contenido_lower))
            if count > 0:
                diversidad[termino] = count

        return diversidad

    # =====================================================================
    # ANÁLISIS ESTADÍSTICO
    # =====================================================================

    def calcular_ratio_genero(self, masculino, femenino):
        """
        Calcula el ratio de sesgo de género

        Returns:
            float: Ratio masculino/femenino (ej: 17.8 significa 17.8:1)
        """
        if femenino == 0:
            return float('inf') if masculino > 0 else 0.0
        return round(masculino / femenino, 2)

    def analizar_archivo(self, filepath):
        """
        Analiza un archivo de texto completo

        Returns:
            dict: Resultados completos del análisis
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()

            # Conteo de palabras
            palabras = len(contenido.split())

            # Detecciones
            nombres = self.detectar_nombres_personas(contenido)
            tratamientos = self.detectar_tratamientos_formales(contenido)
            profesiones = self.detectar_profesiones_musicales(contenido)
            diversidad = self.detectar_diversidad_cultural(contenido)

            # Totales
            total_masculino = (
                sum(nombres['masculinos'].values()) +
                tratamientos['masculinos'] +
                sum(profesiones['masculinas'].values())
            )

            total_femenino = (
                sum(nombres['femeninos'].values()) +
                tratamientos['femeninos'] +
                sum(profesiones['femeninas'].values())
            )

            # Resultados
            resultado = {
                'archivo': os.path.basename(filepath),
                'ruta': filepath,
                'palabras': palabras,
                'detecciones': {
                    'nombres': {
                        'masculinos': dict(nombres['masculinos']),
                        'femeninos': dict(nombres['femeninos']),
                        'ejemplos_masculinos': nombres.get('ejemplos_masculinos', {}),
                        'ejemplos_femeninos': nombres.get('ejemplos_femeninos', {}),
                        'total_masculinos': sum(nombres['masculinos'].values()),
                        'total_femeninos': sum(nombres['femeninos'].values())
                    },
                    'tratamientos': tratamientos,
                    'profesiones': {
                        'masculinas': dict(profesiones['masculinas']),
                        'femeninas': dict(profesiones['femeninas']),
                        'total_masculinas': sum(profesiones['masculinas'].values()),
                        'total_femeninas': sum(profesiones['femeninas'].values())
                    },
                    'diversidad': dict(diversidad),
                    'total_diversidad': sum(diversidad.values())
                },
                'totales': {
                    'menciones_masculinas': total_masculino,
                    'menciones_femeninas': total_femenino,
                    'ratio_sesgo': self.calcular_ratio_genero(
                        total_masculino, total_femenino
                    )
                }
            }

            return resultado

        except Exception as e:
            print(f"❌ Error analizando {filepath}: {e}")
            return None

    def analizar_directorio(self, directorio=None):
        """
        Analiza todos los archivos TXT en un directorio

        Args:
            directorio (str): Ruta al directorio (usa base_directory si None)
        """
        if directorio is None:
            directorio = self.base_directory

        print(f"📂 Analizando directorio: {directorio}")

        archivos_txt = []
        for root, dirs, files in os.walk(directorio):
            for file in files:
                if file.endswith('.txt'):
                    archivos_txt.append(os.path.join(root, file))

        print(f"📄 Encontrados {len(archivos_txt)} archivos TXT")

        # Analizar cada archivo
        resultados_archivos = []
        total_masc = 0
        total_fem = 0
        total_palabras = 0

        for i, filepath in enumerate(archivos_txt, 1):
            print(f"⚙️  Procesando {i}/{len(archivos_txt)}: {os.path.basename(filepath)}")

            resultado = self.analizar_archivo(filepath)
            if resultado:
                resultados_archivos.append(resultado)
                total_masc += resultado['totales']['menciones_masculinas']
                total_fem += resultado['totales']['menciones_femeninas']
                total_palabras += resultado['palabras']

        # Consolidar resultados
        self.resultados = {
            'metadata': {
                'directorio': directorio,
                'total_archivos': len(resultados_archivos),
                'total_palabras': total_palabras,
                'fecha_analisis': datetime.now().isoformat()
            },
            'resumen_general': {
                'menciones_masculinas_total': total_masc,
                'menciones_femeninas_total': total_fem,
                'ratio_sesgo_general': self.calcular_ratio_genero(total_masc, total_fem),
                'porcentaje_masculino': round(
                    (total_masc / (total_masc + total_fem) * 100)
                    if (total_masc + total_fem) > 0 else 0, 2
                ),
                'porcentaje_femenino': round(
                    (total_fem / (total_masc + total_fem) * 100)
                    if (total_masc + total_fem) > 0 else 0, 2
                )
            },
            'archivos': resultados_archivos
        }

        return self.resultados

    def guardar_resultados(self, output_file='resultados_deteccion_genero.json'):
        """
        Guarda los resultados en JSON

        Args:
            output_file (str): Nombre del archivo de salida
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Resultados guardados en: {output_file}")
        return output_file

    def generar_reporte_texto(self, output_file='reporte_genero.txt'):
        """
        Genera un reporte legible en texto plano

        Args:
            output_file (str): Nombre del archivo de salida
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ANÁLISIS DE GÉNERO EN PERSONAS MUSICALES\n")
            f.write("Proyecto LexiMus - Universidad de Salamanca\n")
            f.write("="*80 + "\n\n")

            # Metadata
            meta = self.resultados['metadata']
            f.write(f"📂 Directorio: {meta['directorio']}\n")
            f.write(f"📄 Archivos analizados: {meta['total_archivos']}\n")
            f.write(f"📝 Total palabras: {meta['total_palabras']:,}\n")
            f.write(f"📅 Fecha: {meta['fecha_analisis']}\n\n")

            # Resumen general
            f.write("-"*80 + "\n")
            f.write("RESUMEN GENERAL\n")
            f.write("-"*80 + "\n")
            resumen = self.resultados['resumen_general']
            f.write(f"👨 Menciones masculinas: {resumen['menciones_masculinas_total']:,} "
                   f"({resumen['porcentaje_masculino']}%)\n")
            f.write(f"👩 Menciones femeninas: {resumen['menciones_femeninas_total']:,} "
                   f"({resumen['porcentaje_femenino']}%)\n")

            ratio = resumen['ratio_sesgo_general']
            if ratio == float('inf'):
                f.write(f"⚠️  Ratio de sesgo: ∞:1 (solo menciones masculinas)\n")
            else:
                f.write(f"📊 Ratio de sesgo de género: {ratio}:1 (masculino:femenino)\n")

            f.write("\n")
            f.write("INTERPRETACIÓN:\n")
            if ratio > 10:
                f.write(f"❌ Sesgo extremo detectado ({ratio}:1). Dominancia masculina severa.\n")
            elif ratio > 5:
                f.write(f"⚠️  Sesgo alto detectado ({ratio}:1). Desbalance significativo.\n")
            elif ratio > 2:
                f.write(f"⚠️  Sesgo moderado detectado ({ratio}:1).\n")
            else:
                f.write(f"✅ Representación relativamente equilibrada ({ratio}:1).\n")

            f.write("\n")

            # Top 10 archivos con mayor sesgo
            f.write("-"*80 + "\n")
            f.write("TOP 10 ARCHIVOS CON MAYOR SESGO DE GÉNERO\n")
            f.write("-"*80 + "\n")

            archivos_ordenados = sorted(
                [a for a in self.resultados['archivos']
                 if a['totales']['ratio_sesgo'] != float('inf')],
                key=lambda x: x['totales']['ratio_sesgo'],
                reverse=True
            )[:10]

            for i, archivo in enumerate(archivos_ordenados, 1):
                f.write(f"{i}. {archivo['archivo']}\n")
                f.write(f"   Ratio: {archivo['totales']['ratio_sesgo']}:1 | "
                       f"Masc: {archivo['totales']['menciones_masculinas']} | "
                       f"Fem: {archivo['totales']['menciones_femeninas']}\n\n")

        print(f"✅ Reporte guardado en: {output_file}")
        return output_file

    def generar_web_interactiva(self, output_file='analisis_genero.html'):
        """
        Genera una página web interactiva con gráficos usando Chart.js

        Args:
            output_file (str): Nombre del archivo HTML de salida
        """
        resumen = self.resultados['resumen_general']
        meta = self.resultados['metadata']

        # Consolidar nombres de todos los archivos
        nombres_masculinos_total = Counter()
        nombres_femeninos_total = Counter()
        ejemplos_masculinos = {}
        ejemplos_femeninos = {}

        for archivo in self.resultados['archivos']:
            for nombre, count in archivo['detecciones']['nombres']['masculinos'].items():
                nombres_masculinos_total[nombre] += count
                # Consolidar ejemplos
                if 'ejemplos_masculinos' in archivo['detecciones']['nombres']:
                    if nombre not in ejemplos_masculinos:
                        ejemplos_masculinos[nombre] = []
                    ejemplos_masculinos[nombre].extend(
                        archivo['detecciones']['nombres']['ejemplos_masculinos'].get(nombre, [])
                    )

            for nombre, count in archivo['detecciones']['nombres']['femeninos'].items():
                nombres_femeninos_total[nombre] += count
                # Consolidar ejemplos
                if 'ejemplos_femeninos' in archivo['detecciones']['nombres']:
                    if nombre not in ejemplos_femeninos:
                        ejemplos_femeninos[nombre] = []
                    ejemplos_femeninos[nombre].extend(
                        archivo['detecciones']['nombres']['ejemplos_femeninos'].get(nombre, [])
                    )

        # Limpiar y deduplicar ejemplos
        for nombre in ejemplos_masculinos:
            ejemplos_masculinos[nombre] = list(set(ejemplos_masculinos[nombre]))[:3]
        for nombre in ejemplos_femeninos:
            ejemplos_femeninos[nombre] = list(set(ejemplos_femeninos[nombre]))[:3]

        # Top 10 nombres
        top_masculinos = nombres_masculinos_total.most_common(10)
        top_femeninos = nombres_femeninos_total.most_common(10)

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Género en Personas Musicales</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .chart-container {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        .alert {{
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        .alert-danger {{
            background: #fee;
            border-left: 5px solid #f44;
            color: #c33;
        }}
        .alert-warning {{
            background: #fffbeb;
            border-left: 5px solid #f59e0b;
            color: #92400e;
        }}
        .alert-success {{
            background: #f0fdf4;
            border-left: 5px solid #22c55e;
            color: #166534;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            font-size: 0.9em;
            color: #666;
        }}
        .details-section {{
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
        }}
        .details-section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .top-names {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }}
        .names-column h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .names-column.female h3 {{
            color: #f687b3;
        }}
        .name-item {{
            padding: 12px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .name-item .name {{
            font-weight: 600;
            text-transform: capitalize;
            flex: 1;
        }}
        .name-item .ejemplos {{
            font-size: 0.85em;
            color: #666;
            font-style: italic;
            margin-top: 4px;
        }}
        .name-item .count {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .names-column.female .name-item .count {{
            background: #f687b3;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .ratio-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .ratio-extreme {{
            background: #fee;
            color: #c33;
        }}
        .ratio-high {{
            background: #fffbeb;
            color: #92400e;
        }}
        .ratio-moderate {{
            background: #f0fdf4;
            color: #166534;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Análisis de Género en Personas Musicales</h1>
        <p class="subtitle">Proyecto LexiMus - Universidad de Salamanca</p>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>👨 Menciones Masculinas</h3>
                <div class="number">{resumen['menciones_masculinas_total']:,}</div>
                <div>{resumen['porcentaje_masculino']}% del total</div>
            </div>
            <div class="stat-card">
                <h3>👩 Menciones Femeninas</h3>
                <div class="number">{resumen['menciones_femeninas_total']:,}</div>
                <div>{resumen['porcentaje_femenino']}% del total</div>
            </div>
            <div class="stat-card">
                <h3>📊 Ratio de Sesgo</h3>
                <div class="number">{resumen['ratio_sesgo_general']}:1</div>
                <div>Masculino/Femenino</div>
            </div>
            <div class="stat-card">
                <h3>📄 Archivos Analizados</h3>
                <div class="number">{meta['total_archivos']}</div>
                <div>{meta['total_palabras']:,} palabras</div>
            </div>
        </div>
"""

        # Alerta según el nivel de sesgo
        ratio = resumen['ratio_sesgo_general']
        if ratio > 10:
            html_content += f"""
        <div class="alert alert-danger">
            <strong>❌ Sesgo Extremo Detectado ({ratio}:1)</strong><br>
            Se observa una dominancia masculina severa en el corpus analizado.
            Por cada mención femenina hay {ratio} menciones masculinas.
        </div>
"""
        elif ratio > 5:
            html_content += f"""
        <div class="alert alert-warning">
            <strong>⚠️ Sesgo Alto Detectado ({ratio}:1)</strong><br>
            Existe un desbalance significativo en la representación de género.
        </div>
"""
        elif ratio > 2:
            html_content += f"""
        <div class="alert alert-warning">
            <strong>⚠️ Sesgo Moderado ({ratio}:1)</strong><br>
            Se detecta un desbalance moderado en la representación de género.
        </div>
"""
        else:
            html_content += f"""
        <div class="alert alert-success">
            <strong>✅ Representación Relativamente Equilibrada ({ratio}:1)</strong><br>
            El corpus muestra una representación más balanceada entre géneros.
        </div>
"""

        html_content += f"""
        <div class="chart-container">
            <h2>Distribución por Género</h2>
            <canvas id="genderChart"></canvas>
        </div>

        <div class="chart-container">
            <h2>Comparativa de Menciones</h2>
            <canvas id="comparisonChart"></canvas>
        </div>

        <div class="details-section">
            <h2>🏆 Top 10 Nombres Más Mencionados</h2>
            <div class="top-names">
                <div class="names-column male">
                    <h3>👨 Masculinos</h3>
"""

        # Agregar nombres masculinos
        for nombre, count in top_masculinos:
            ejemplos_str = ""
            if nombre in ejemplos_masculinos and ejemplos_masculinos[nombre]:
                ejemplos_str = f'<div class="ejemplos">ej: {", ".join(ejemplos_masculinos[nombre])}</div>'

            html_content += f"""
                    <div class="name-item">
                        <div class="name">
                            {nombre.capitalize()}
                            {ejemplos_str}
                        </div>
                        <span class="count">{count:,}</span>
                    </div>
"""

        html_content += """
                </div>
                <div class="names-column female">
                    <h3>👩 Femeninos</h3>
"""

        # Agregar nombres femeninos
        for nombre, count in top_femeninos:
            ejemplos_str = ""
            if nombre in ejemplos_femeninos and ejemplos_femeninos[nombre]:
                ejemplos_str = f'<div class="ejemplos">ej: {", ".join(ejemplos_femeninos[nombre])}</div>'

            html_content += f"""
                    <div class="name-item">
                        <div class="name">
                            {nombre.capitalize()}
                            {ejemplos_str}
                        </div>
                        <span class="count">{count:,}</span>
                    </div>
"""

        html_content += """
                </div>
            </div>
        </div>

        <div class="details-section">
            <h2>📊 Archivos con Mayor Sesgo de Género</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Archivo</th>
                        <th>Masculino</th>
                        <th>Femenino</th>
                        <th>Ratio</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Top 15 archivos con mayor sesgo
        archivos_ordenados = sorted(
            [a for a in self.resultados['archivos']
             if a['totales']['ratio_sesgo'] != float('inf') and a['totales']['ratio_sesgo'] > 0],
            key=lambda x: x['totales']['ratio_sesgo'],
            reverse=True
        )[:15]

        for i, archivo in enumerate(archivos_ordenados, 1):
            ratio = archivo['totales']['ratio_sesgo']
            ratio_class = 'ratio-extreme' if ratio > 10 else ('ratio-high' if ratio > 5 else 'ratio-moderate')

            html_content += f"""
                    <tr>
                        <td><strong>{i}</strong></td>
                        <td>{archivo['archivo']}</td>
                        <td>{archivo['totales']['menciones_masculinas']}</td>
                        <td>{archivo['totales']['menciones_femeninas']}</td>
                        <td><span class="ratio-badge {ratio_class}">{ratio}:1</span></td>
                    </tr>
"""

        html_content += """
                </tbody>
            </table>
        </div>

        <div class="metadata">
            <strong>📂 Directorio analizado:</strong> """ + meta['directorio'] + """<br>
            <strong>📅 Fecha de análisis:</strong> """ + meta['fecha_analisis'] + """<br>
            <strong>📝 Total palabras procesadas:</strong> """ + f"{meta['total_palabras']:,}" + """
        </div>

        <footer>
            <p><strong>LexiMus: Léxico y ontología de la música en español</strong></p>
            <p>Universidad de Salamanca | Instituto Complutense de Ciencias Musicales | Universidad de La Rioja</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                🤖 Generado con <a href="https://claude.com/claude-code" target="_blank">Claude Code</a>
            </p>
        </footer>
    </div>

    <script>
        // Gráfico de Pastel
        const ctx1 = document.getElementById('genderChart').getContext('2d');
        new Chart(ctx1, {
            type: 'pie',
            data: {
                labels: ['Masculino', 'Femenino'],
                datasets: [{
                    data: [""" + str(resumen['menciones_masculinas_total']) + """, """ + str(resumen['menciones_femeninas_total']) + """],
                    backgroundColor: ['#667eea', '#f687b3'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 14 },
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                let value = context.parsed || 0;
                                let total = """ + str(resumen['menciones_masculinas_total'] + resumen['menciones_femeninas_total']) + """;
                                let percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value.toLocaleString() + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });

        // Gráfico de Barras
        const ctx2 = document.getElementById('comparisonChart').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['Menciones Totales'],
                datasets: [
                    {
                        label: 'Masculino',
                        data: [""" + str(resumen['menciones_masculinas_total']) + """],
                        backgroundColor: '#667eea',
                        borderRadius: 10
                    },
                    {
                        label: 'Femenino',
                        data: [""" + str(resumen['menciones_femeninas_total']) + """],
                        backgroundColor: '#f687b3',
                        borderRadius: 10
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 14 },
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Web interactiva generada: {output_file}")
        return output_file


# ==========================================================================
# FUNCIÓN PRINCIPAL
# ==========================================================================

def main():
    """
    Ejecuta el análisis completo

    Uso:
        python3 detector_genero_musical.py /ruta/a/tus/archivos/txt
    """
    # Verificar argumentos de línea de comandos
    if len(sys.argv) < 2:
        print("❌ ERROR: Debes especificar la ruta al directorio con archivos TXT")
        print("\nUso:")
        print("  python3 detector_genero_musical.py /ruta/a/tus/archivos/txt")
        print("\nEjemplo:")
        print("  python3 detector_genero_musical.py ~/Desktop/MisRevistas")
        sys.exit(1)

    directorio_base = sys.argv[1]

    # Verificar que el directorio existe
    if not os.path.exists(directorio_base):
        print(f"❌ ERROR: El directorio no existe: {directorio_base}")
        sys.exit(1)

    if not os.path.isdir(directorio_base):
        print(f"❌ ERROR: La ruta no es un directorio: {directorio_base}")
        sys.exit(1)

    print("🎵 DETECTOR AUTOMÁTICO DE GÉNERO EN PERSONAS MUSICALES")
    print("="*80)
    print(f"📂 Directorio: {directorio_base}\n")

    # Inicializar detector
    detector = DetectorGeneroMusical(directorio_base)

    # Ejecutar análisis
    resultados = detector.analizar_directorio()

    # Guardar resultados
    detector.guardar_resultados('resultados_deteccion_genero.json')
    detector.generar_reporte_texto('reporte_genero.txt')
    detector.generar_web_interactiva('analisis_genero.html')

    # Imprimir resumen
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
    resumen = resultados['resumen_general']
    print(f"👨 Menciones masculinas: {resumen['menciones_masculinas_total']:,}")
    print(f"👩 Menciones femeninas: {resumen['menciones_femeninas_total']:,}")
    print(f"📊 Ratio de sesgo: {resumen['ratio_sesgo_general']}:1")
    print(f"\n📁 Archivos generados:")
    print(f"   - analisis_genero.html (🌐 página web interactiva)")
    print(f"   - resultados_deteccion_genero.json (datos completos)")
    print(f"   - reporte_genero.txt (resumen legible)")


if __name__ == "__main__":
    main()
