#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script ACTUALIZADO para generar gráfico de valoraciones con TRES métodos
Incluye los nuevos datos del análisis multinivel mejorado

Artículo: Construir la música legítima
Autor: María Palacios Nieto - Universidad de Salamanca
Actualizado: 10 Noviembre 2024
"""

import matplotlib.pyplot as plt
import numpy as np

# Configuración general
plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['figure.dpi'] = 300

def grafico_ratio_valoraciones_actualizado():
    """
    Gráfico de barras comparando valoraciones positivas vs. negativas
    con TRES métodos:
    1. Método Dependencia Sintáctica (original)
    2. Método Ventana ±5 palabras (original)
    3. Método Multinivel Mejorado (NUEVO - incluye términos relacionados)
    """

    fig, ax = plt.subplots(figsize=(14, 7))

    # DATOS
    categorias = [
        'Método\nDependencia\nSintáctica',
        'Método\nVentana ±5\npalabras',
        'Método\nMultinivel\nMejorado'
    ]

    # Valoraciones positivas
    positivas = [156, 312, 2318]

    # Valoraciones negativas
    negativas = [8, 14, 138]

    # Calcular ratios
    ratios = [
        f"{positivas[0]/negativas[0]:.1f}:1",
        f"{positivas[1]/negativas[1]:.1f}:1",
        f"{positivas[2]/negativas[2]:.1f}:1"
    ]

    # Posiciones en el eje X
    x = np.arange(len(categorias))
    width = 0.35

    # Crear barras
    bars1 = ax.bar(x - width/2, positivas, width, label='Positivas',
                   color='#2ecc71', alpha=0.85, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + width/2, negativas, width, label='Negativas',
                   color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1.2)

    # Añadir valores sobre las barras POSITIVAS
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=12)

    # Añadir valores sobre las barras NEGATIVAS
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Añadir RATIOS como texto destacado
    ax.text(0, 200, f'Ratio\n{ratios[0]}', ha='center', fontsize=13,
            fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                     edgecolor='#27ae60', linewidth=2))

    ax.text(1, 370, f'Ratio\n{ratios[1]}', ha='center', fontsize=13,
            fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                     edgecolor='#27ae60', linewidth=2))

    ax.text(2, 1350, f'Ratio\n{ratios[2]}', ha='center', fontsize=13,
            fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                     edgecolor='#27ae60', linewidth=2))

    # Etiquetas y título
    ax.set_xlabel('Método de análisis', fontweight='bold', fontsize=13)
    ax.set_ylabel('Número de adjetivaciones', fontweight='bold', fontsize=13)
    ax.set_title('Valoración estética positiva vs. negativa en el corpus musical\n' +
                 '(El Sol, ONDAS, España, 1915-1935)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=11)

    # Leyenda
    ax.legend(loc='upper left', framealpha=0.95, fontsize=12,
              edgecolor='black', shadow=True)

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)

    # Ajustar límites del eje Y
    ax.set_ylim(0, 2500)

    # Añadir nota explicativa
    nota = ('Nota: El Método Multinivel Mejorado incluye valoraciones sobre "música" + términos relacionados\n' +
            '(concierto, interpretación, ejecución, obra, programa, etc.) + construcciones predicativas distantes.')

    plt.figtext(0.5, 0.02, nota, wrap=True, horizontalalignment='center',
                fontsize=9, style='italic', color='#34495e',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout(rect=[0, 0.06, 1, 0.98])

    # Guardar gráfico
    plt.savefig('grafico1_ratio_valoraciones_ACTUALIZADO.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig('grafico1_ratio_valoraciones_ACTUALIZADO.pdf',
                bbox_inches='tight')
    plt.savefig('grafico1_ratio_valoraciones_ACTUALIZADO.jpg',
                dpi=300, bbox_inches='tight', facecolor='white',
                pil_kwargs={'quality': 95})

    print("✓ Gráfico actualizado generado:")
    print("  • grafico1_ratio_valoraciones_ACTUALIZADO.png")
    print("  • grafico1_ratio_valoraciones_ACTUALIZADO.pdf")
    print("  • grafico1_ratio_valoraciones_ACTUALIZADO.jpg")

    plt.show()


def tabla_comparativa_metodos():
    """
    Tabla comparativa de los tres métodos
    """

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('off')

    # Headers
    headers = ['Método', 'Positivas', 'Negativas', 'Total', 'Ratio P/N', '% Positivas', '% Negativas']

    # Datos
    row1 = [
        'Dependencia Sintáctica',
        '156',
        '8',
        '164',
        '19.5:1',
        '95.1%',
        '4.9%'
    ]

    row2 = [
        'Ventana ±5 palabras',
        '312',
        '14',
        '326',
        '22.3:1',
        '95.7%',
        '4.3%'
    ]

    row3 = [
        'Multinivel Mejorado',
        '2,318',
        '138',
        '2,456',
        '16.8:1',
        '94.4%',
        '5.6%'
    ]

    row_incremento = [
        'Incremento vs. Dependencia',
        '+1,385%',
        '+1,625%',
        '+1,398%',
        '—',
        '—',
        '—'
    ]

    table_data = [row1, row2, row3, row_incremento]

    # Colores
    color_header = '#2c3e50'
    color_metodo1 = '#ecf0f1'
    color_metodo2 = '#d5dbdb'
    color_metodo3 = '#aed6f1'  # Destacar el nuevo
    color_incremento = '#fcf3cf'

    # Crear tabla
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        colWidths=[0.25, 0.12, 0.12, 0.12, 0.12, 0.13, 0.13]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 3.5)

    # Estilizar celdas
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Headers
            cell.set_facecolor(color_header)
            cell.set_text_props(weight='bold', color='white', fontsize=12)
        else:
            # Colorear filas
            if i == 1:
                cell.set_facecolor(color_metodo1)
            elif i == 2:
                cell.set_facecolor(color_metodo2)
            elif i == 3:
                cell.set_facecolor(color_metodo3)
                cell.set_text_props(weight='bold')  # Destacar el nuevo método
            elif i == 4:
                cell.set_facecolor(color_incremento)
                cell.set_text_props(weight='bold', color='#196f3d')

            # Primera columna en negrita
            if j == 0:
                cell.set_text_props(weight='bold', ha='left')
                cell._loc = 'left'
            else:
                cell.set_text_props(ha='center')

        # Bordes
        cell.set_edgecolor('#7f8c8d')
        cell.set_linewidth(1.5)

    # Título
    plt.title('Tabla Comparativa: Tres métodos de análisis de valoraciones estéticas\n' +
              '(El Sol, ONDAS, España, 1915-1935)',
              fontweight='bold', fontsize=14, pad=30)

    # Nota al pie
    nota = ('El Método Multinivel Mejorado captura: (1) adjetivos directos sobre "música", ' +
            '(2) adjetivos sobre términos relacionados (concierto, interpretación, ejecución, etc.), ' +
            '(3) construcciones predicativas distantes.')

    plt.figtext(0.5, 0.08, nota, wrap=True, horizontalalignment='center',
                fontsize=9, style='italic', color='#2c3e50')

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])

    # Guardar
    plt.savefig('tabla_comparativa_metodos_ACTUALIZADO.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig('tabla_comparativa_metodos_ACTUALIZADO.pdf',
                bbox_inches='tight')

    print("✓ Tabla comparativa generada:")
    print("  • tabla_comparativa_metodos_ACTUALIZADO.png")
    print("  • tabla_comparativa_metodos_ACTUALIZADO.pdf")

    plt.show()


def main():
    """Generar ambos gráficos actualizados"""
    print("\n" + "="*80)
    print("GENERANDO GRÁFICOS ACTUALIZADOS CON NUEVOS DATOS")
    print("="*80 + "\n")

    try:
        grafico_ratio_valoraciones_actualizado()
        print()
        tabla_comparativa_metodos()

        print("\n" + "="*80)
        print("✅ GRÁFICOS ACTUALIZADOS GENERADOS EXITOSAMENTE")
        print("="*80)
        print("\nArchivos generados en 'figuras publicación/':")
        print("  1. grafico1_ratio_valoraciones_ACTUALIZADO.png/.pdf/.jpg")
        print("  2. tabla_comparativa_metodos_ACTUALIZADO.png/.pdf")
        print("\nFormatos: PNG (web), PDF (publicación), JPG (alta calidad)")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error al generar gráficos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
