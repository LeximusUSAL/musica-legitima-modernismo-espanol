#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar tabla de valoraciones estéticas como imagen JPG
Artículo: Construir la música legítima
Autor: María Palacios Nieto - Universidad de Salamanca
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

# Configuración
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

def crear_tabla_valoraciones():
    """Crea tabla de valoraciones como imagen JPG de alta calidad"""

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')

    # Datos de la tabla
    headers = ['Categoría', 'Adjetivos representativos', 'Freq.\nDepend.', 'Freq.\nVentana±5', 'Ratio\nV/D']

    row_positiva = [
        'POSITIVA',
        'buen/buena, admirable, bello/bella,\ndelicioso/a, excelente, magnífico/a,\nsublime, perfecto/a, espléndido/a, hermoso/a',
        '156',
        '312',
        '2.0x'
    ]

    row_negativa = [
        'NEGATIVA',
        'malo/mala, mediocre, pobre,\ninferior, vulgar',
        '8',
        '14',
        '1.75x'
    ]

    row_ratio = [
        'Ratio Pos./Neg.',
        '—',
        '19.5:1',
        '22.3:1',
        '—'
    ]

    # Crear tabla con matplotlib
    table_data = [row_positiva, row_negativa, row_ratio]

    # Colores
    color_header = '#34495e'
    color_positiva = '#e8f8f5'
    color_negativa = '#fdecea'
    color_ratio = '#f8f9f9'

    # Crear tabla
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc='left',
        loc='center',
        colWidths=[0.15, 0.45, 0.12, 0.13, 0.10]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 3)

    # Estilizar celdas
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Headers
            cell.set_facecolor(color_header)
            cell.set_text_props(weight='bold', color='white', fontsize=11)
            cell.set_height(0.15)
        else:
            # Colorear filas
            if i == 1:  # POSITIVA
                cell.set_facecolor(color_positiva)
            elif i == 2:  # NEGATIVA
                cell.set_facecolor(color_negativa)
            elif i == 3:  # Ratio
                cell.set_facecolor(color_ratio)
                cell.set_text_props(weight='bold')

            # Columna 1 (categoría) en negrita
            if j == 0:
                cell.set_text_props(weight='bold', fontsize=10)

            # Columnas numéricas centradas
            if j in [2, 3, 4]:
                cell.set_text_props(ha='center')
                cell._loc = 'center'
                if i == 3:  # Ratio en negrita
                    cell.set_text_props(weight='bold', ha='center', fontsize=11)

        # Bordes
        cell.set_edgecolor('#bdc3c7')
        cell.set_linewidth(1.5)

    # Título
    plt.title('Tabla 1. Valoración estética positiva vs. negativa en el corpus musical\n(El Sol, ONDAS, España, 1915-1935)',
              fontweight='bold', fontsize=13, pad=20, loc='left')

    # Notas al pie
    nota = ('Nota: Freq. Depend. = frecuencia mediante análisis de dependencias sintácticas; '
            'Freq. Ventana±5 = frecuencia mediante ventana colocacional de ±5 palabras; '
            'Ratio V/D = proporción ventana/dependencia, indicador de complejidad sintáctica.')

    plt.figtext(0.1, 0.08, nota, wrap=True, horizontalalignment='left',
                fontsize=9, style='italic', color='#34495e')

    plt.tight_layout(rect=[0, 0.12, 1, 0.96])

    # Guardar como JPG de alta calidad
    plt.savefig('figuras publicación/tabla1_valoraciones_esteticas.jpg',
                dpi=300, bbox_inches='tight', format='jpg',
                facecolor='white', edgecolor='none', pil_kwargs={'quality': 95})

    # También como PNG (mejor calidad para tablas)
    plt.savefig('figuras publicación/tabla1_valoraciones_esteticas.png',
                dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')

    print("✓ Tabla generada exitosamente:")
    print("  • tabla1_valoraciones_esteticas.jpg (alta calidad, 95%)")
    print("  • tabla1_valoraciones_esteticas.png (calidad máxima)")

    plt.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("GENERANDO TABLA DE VALORACIONES ESTÉTICAS")
    print("="*70 + "\n")

    crear_tabla_valoraciones()

    print("\n" + "="*70)
    print("✅ TABLA GENERADA")
    print("="*70 + "\n")
