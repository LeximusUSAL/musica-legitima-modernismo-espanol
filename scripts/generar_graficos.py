#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar gráficos de la sección "Exclusión por omisión"
Artículo: Construir la música legítima
Autor: María Palacios Nieto - Universidad de Salamanca
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Configuración general para todos los gráficos
plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

# ============================================================================
# GRÁFICO 1: Ratio valoraciones positivas/negativas
# ============================================================================

def grafico_ratio_valoraciones():
    """Gráfico de barras comparando valoraciones positivas vs. negativas"""

    fig, ax = plt.subplots(figsize=(10, 6))

    categorias = ['Método\nDependencia\nSintáctica', 'Método\nVentana ±5\npalabras']
    positivas = [156, 312]
    negativas = [8, 14]

    x = np.arange(len(categorias))
    width = 0.35

    bars1 = ax.bar(x - width/2, positivas, width, label='Positivas',
                   color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, negativas, width, label='Negativas',
                   color='#e74c3c', alpha=0.8)

    # Añadir valores sobre las barras
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')

    # Añadir ratios como texto
    ax.text(0, 180, 'Ratio\n19.5:1', ha='center', fontsize=12,
            fontweight='bold', color='#27ae60')
    ax.text(1, 350, 'Ratio\n22.3:1', ha='center', fontsize=12,
            fontweight='bold', color='#27ae60')

    ax.set_xlabel('Método de análisis', fontweight='bold')
    ax.set_ylabel('Número de adjetivaciones', fontweight='bold')
    ax.set_title('Valoración estética positiva vs. negativa en el corpus musical\n(El Sol, ONDAS, España, 1915-1935)',
                 fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('figuras publicación/grafico1_ratio_valoraciones.png',
                dpi=300, bbox_inches='tight')
    plt.savefig('figuras publicación/grafico1_ratio_valoraciones.pdf',
                bbox_inches='tight')
    print("✓ Gráfico 1 generado: grafico1_ratio_valoraciones.png/.pdf")
    plt.close()


# ============================================================================
# GRÁFICO 2: Presencia de géneros en el corpus
# ============================================================================

def grafico_presencia_generos():
    """Gráfico de barras horizontales: presencia de géneros populares"""

    fig, ax = plt.subplots(figsize=(10, 6))

    generos = ['Cuplé', 'Varietés', 'Zarzuela', 'Jazz\n("música negra")',
               'Flamenco']
    menciones = [131, 87, 456, 387, 89]
    porcentajes = [0.005, 0.003, 0.018, 0.015, 0.004]

    y_pos = np.arange(len(generos))

    colors = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#9b59b6']
    bars = ax.barh(y_pos, menciones, color=colors, alpha=0.8)

    # Añadir valores
    for i, (bar, mencion, pct) in enumerate(zip(bars, menciones, porcentajes)):
        width = bar.get_width()
        ax.text(width + 20, bar.get_y() + bar.get_height()/2.,
                f'{mencion} ({pct}%)',
                ha='left', va='center', fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(generos)
    ax.invert_yaxis()
    ax.set_xlabel('Número de menciones en el corpus', fontweight='bold')
    ax.set_title('Presencia de géneros musicales populares en el corpus\n(Total: 2.535.146 palabras)',
                 fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Añadir línea de referencia
    ax.axvline(x=200, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(200, -0.7, 'Umbral\nmarginalidad', ha='center', fontsize=8,
            color='gray')

    plt.tight_layout()
    plt.savefig('figuras publicación/grafico2_presencia_generos.png',
                dpi=300, bbox_inches='tight')
    plt.savefig('figuras publicación/grafico2_presencia_generos.pdf',
                bbox_inches='tight')
    print("✓ Gráfico 2 generado: grafico2_presencia_generos.png/.pdf")
    plt.close()


# ============================================================================
# GRÁFICO 3: Inversión proporcional (escena real vs. discurso)
# ============================================================================

def grafico_inversion_proporcional():
    """Gráfico de barras agrupadas: presencia real vs. presencia discursiva"""

    fig, ax = plt.subplots(figsize=(12, 7))

    categorias = ['Música "ligera"\n(cuplé, varietés,\nzarzuela menor)',
                  'Zarzuela "seria"\nÓpera española',
                  'Música sinfónica\nCámara\nÓpera internacional']

    presencia_real = [62.5, 17.5, 17.5]  # Promedios
    presencia_discurso = [3, 12.5, 75]

    x = np.arange(len(categorias))
    width = 0.35

    bars1 = ax.bar(x - width/2, presencia_real, width,
                   label='Presencia en escena urbana (estimación)',
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, presencia_discurso, width,
                   label='Espacio textual en corpus',
                   color='#e74c3c', alpha=0.8)

    # Añadir valores sobre las barras
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')

    # Añadir flechas de inversión
    ax.annotate('', xy=(0 - width/2, presencia_real[0]),
                xytext=(0 + width/2, presencia_discurso[0]),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(0, 35, 'INVERSIÓN', ha='center', fontsize=10,
            fontweight='bold', color='red', rotation=90)

    ax.annotate('', xy=(2 - width/2, presencia_real[2]),
                xytext=(2 + width/2, presencia_discurso[2]),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(2, 50, 'INVERSIÓN', ha='center', fontsize=10,
            fontweight='bold', color='red', rotation=90)

    ax.set_xlabel('Categoría musical', fontweight='bold')
    ax.set_ylabel('Porcentaje (%)', fontweight='bold')
    ax.set_title('Inversión proporcional: presencia real vs. presencia discursiva\n' +
                 'Programación teatral Madrid 1915-1935 vs. Corpus prensa musical',
                 fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, 85)

    plt.tight_layout()
    plt.savefig('figuras publicación/grafico3_inversion_proporcional.png',
                dpi=300, bbox_inches='tight')
    plt.savefig('figuras publicación/grafico3_inversion_proporcional.pdf',
                bbox_inches='tight')
    print("✓ Gráfico 3 generado: grafico3_inversion_proporcional.png/.pdf")
    plt.close()


# ============================================================================
# GRÁFICO 4: Distribución de "música ligera" por publicación
# ============================================================================

def grafico_musica_ligera_publicacion():
    """Gráfico circular: distribución de 'música ligera' por publicación"""

    fig, ax = plt.subplots(figsize=(10, 8))

    publicaciones = ['ONDAS', 'El Sol', 'España']
    menciones = [109, 11, 3]
    colors = ['#e74c3c', '#3498db', '#f39c12']
    explode = (0.1, 0, 0)  # Destacar ONDAS

    wedges, texts, autotexts = ax.pie(menciones, labels=publicaciones,
                                        autopct='%1.1f%%',
                                        colors=colors, explode=explode,
                                        shadow=True, startangle=90,
                                        textprops={'fontsize': 12, 'fontweight': 'bold'})

    # Añadir números absolutos
    for i, (wedge, mencion) in enumerate(zip(wedges, menciones)):
        ang = (wedge.theta2 - wedge.theta1)/2. + wedge.theta1
        x = np.cos(np.deg2rad(ang)) * 0.7
        y = np.sin(np.deg2rad(ang)) * 0.7
        ax.text(x, y, f'{mencion} menciones', ha='center', va='center',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='white',
                                      alpha=0.8))

    ax.set_title('"Música ligera" por publicación\n(Total: 123 menciones)',
                 fontweight='bold', pad=20, fontsize=14)

    plt.tight_layout()
    plt.savefig('figuras publicación/grafico4_musica_ligera_publicacion.png',
                dpi=300, bbox_inches='tight')
    plt.savefig('figuras publicación/grafico4_musica_ligera_publicacion.pdf',
                bbox_inches='tight')
    print("✓ Gráfico 4 generado: grafico4_musica_ligera_publicacion.png/.pdf")
    plt.close()


# ============================================================================
# GRÁFICO 5: Co-ocurrencias cuplé/varietés con "música"
# ============================================================================

def grafico_coocurrencias():
    """Gráfico comparativo: menciones totales vs. co-ocurrencias con 'música'"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Datos
    generos = ['Cuplé', 'Varietés']
    menciones_totales = [131, 87]
    coocurrencias = [24, 3]

    # Gráfico 1: Menciones totales
    bars1 = ax1.bar(generos, menciones_totales, color=['#e74c3c', '#e67e22'],
                    alpha=0.8)
    ax1.set_ylabel('Número de menciones', fontweight='bold')
    ax1.set_title('Menciones totales en el corpus', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=12)

    # Gráfico 2: Co-ocurrencias con "música"
    bars2 = ax2.bar(generos, coocurrencias, color=['#e74c3c', '#e67e22'],
                    alpha=0.8)
    ax2.set_ylabel('Número de co-ocurrencias', fontweight='bold')
    ax2.set_title('Co-ocurrencias con "música" (ventana ±5)', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=12)

    # Añadir porcentajes de co-ocurrencia
    for i, (total, cooc) in enumerate(zip(menciones_totales, coocurrencias)):
        pct = (cooc / total) * 100
        ax2.text(i, cooc + 1, f'({pct:.1f}% del total)',
                ha='center', fontsize=9, style='italic')

    fig.suptitle('Cuplé y varietés: presencia total vs. asociación con "música"',
                 fontweight='bold', fontsize=14, y=1.02)

    plt.tight_layout()
    plt.savefig('figuras publicación/grafico5_coocurrencias.png',
                dpi=300, bbox_inches='tight')
    plt.savefig('figuras publicación/grafico5_coocurrencias.pdf',
                bbox_inches='tight')
    print("✓ Gráfico 5 generado: grafico5_coocurrencias.png/.pdf")
    plt.close()


# ============================================================================
# EJECUTAR TODOS LOS GRÁFICOS
# ============================================================================

def main():
    """Generar todos los gráficos"""
    print("\n" + "="*70)
    print("GENERANDO GRÁFICOS PARA LA SECCIÓN 'EXCLUSIÓN POR OMISIÓN'")
    print("="*70 + "\n")

    try:
        grafico_ratio_valoraciones()
        grafico_presencia_generos()
        grafico_inversion_proporcional()
        grafico_musica_ligera_publicacion()
        grafico_coocurrencias()

        print("\n" + "="*70)
        print("✅ TODOS LOS GRÁFICOS GENERADOS EXITOSAMENTE")
        print("="*70)
        print("\nArchivos generados en 'figuras publicación/':")
        print("  • grafico1_ratio_valoraciones.png/.pdf")
        print("  • grafico2_presencia_generos.png/.pdf")
        print("  • grafico3_inversion_proporcional.png/.pdf")
        print("  • grafico4_musica_ligera_publicacion.png/.pdf")
        print("  • grafico5_coocurrencias.png/.pdf")
        print("\nFormatos: PNG (para visualización) y PDF (para publicación)")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error al generar gráficos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
