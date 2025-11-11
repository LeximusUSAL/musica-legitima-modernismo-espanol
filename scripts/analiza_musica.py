#!/usr/bin/env python3
# analiza_musica_v3_fixed.py

"""Analiza adjetivaciones asociadas a la palabra 'música' en archivos .txt (acepta carpetas)
y genera un archivo HTML interactivo (resultados_musica.html) que puedes abrir directamente en el navegador.

Uso:
    python3 analiza_musica_v3_fixed.py ruta_a_archivo_o_carpeta [otra_ruta ...]

Requisitos:
    pip install spacy pandas plotly
    python -m spacy download es_core_news_md
"""

import sys
import re
from pathlib import Path
from collections import Counter
import json

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

try:
    import spacy
    nlp = spacy.load("es_core_news_md")
except Exception as e:
    print("⚠️ Error: asegúrate de tener spaCy y el modelo español instalados:")
    print("   pip install spacy pandas plotly")
    print("   python -m spacy download es_core_news_md")
    raise


def extraer_adjetivos_asociados(texto):
    doc = nlp(texto)
    adjs = []
    for token in doc:
        if token.lemma_.lower() == "música":
            for hijo in token.children:
                if hijo.pos_ == "ADJ" or hijo.dep_ in ("amod", "acomp"):
                    adjs.append(hijo.text.lower())
            prev = token.nbor(-1) if token.i - 1 >= 0 else None
            if prev is not None and prev.pos_ == "ADJ":
                adjs.append(prev.text.lower())
            if token.head is not None and token.head.pos_ == "ADJ":
                adjs.append(token.head.text.lower())
            for neighbor in doc[max(0, token.i - 3): token.i + 4]:
                if neighbor.pos_ == "ADJ":
                    adjs.append(neighbor.text.lower())
    cleaned = [re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ-]", "", a).strip() for a in adjs if a.strip()]
    return [c for c in cleaned if c]


def procesar_archivo(path):
    path = Path(path)
    nombre_periodico = path.stem
    try:
        texto = path.read_text(encoding="utf-8")
    except Exception:
        texto = path.read_text(encoding="latin-1")

    years = re.findall(r"(19\d{2}|20\d{2})", texto)
    dates = re.findall(r"(\d{1,2}[\/\-]\d{1,2}[\/\-](?:19|20)\d{2})", texto)

    if years:
        rango_tiempo = f"{min(years)} - {max(years)}"
    elif dates:
        rango_tiempo = f"{min(dates)} - {max(dates)}"
    else:
        rango_tiempo = "No disponible"

    adjetivos = extraer_adjetivos_asociados(texto)
    return {
        "ruta": str(path),
        "Periódico": nombre_periodico,
        "Rango temporal": rango_tiempo,
        "Adjetivos": adjetivos
    }


def obtener_txt_de_ruta(ruta):
    ruta_path = Path(ruta)
    if ruta_path.is_file() and ruta_path.suffix.lower() == ".txt":
        return [ruta_path]
    elif ruta_path.is_dir():
        return list(ruta_path.rglob("*.txt"))
    else:
        return []


def generar_html(resultados, output_path="resultados_musica.html"):
    rows = []
    total_adjs = []
    per_periodico_counts = {}

    for r in resultados:
        adjs = r["Adjetivos"]
        rows.append({
            "Periódico": r["Periódico"],
            "Archivo": Path(r["ruta"]).name,
            "Rango temporal": r["Rango temporal"],
            "Adjetivos (lista)": ", ".join(sorted(set(adjs))) if adjs else ""
        })
        total_adjs.extend(adjs)
        per_periodico_counts[r["Periódico"]] = per_periodico_counts.get(r["Periódico"], []) + adjs

    df = pd.DataFrame(rows)
    counter = Counter([a for a in total_adjs if a])
    top_items = counter.most_common(50)
    words, counts = zip(*top_items) if top_items else ([], [])

    if words:
        fig = go.Figure(data=[go.Bar(x=list(words), y=list(counts))])
        fig.update_layout(title="Frecuencia de adjetivos asociados a 'música'",
                          xaxis_title="Adjetivos", yaxis_title="Frecuencia")
        plot_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    else:
        plot_html = "<p>No se encontraron adjetivos asociados a 'música'.</p>"

    table_html = df.to_html(index=False, classes="tabla-resultados", escape=False)
    js_data = json.dumps({k: dict(Counter(v)) for k, v in per_periodico_counts.items()})

    html = f'''
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Adjetivaciones de 'música'</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
.tabla-resultados {{ border-collapse: collapse; width: 100%; }}
.tabla-resultados th, .tabla-resultados td {{ border: 1px solid #ddd; padding: 8px; }}
.tabla-resultados th {{ background-color: #f2f2f2; }}
</style>
</head>
<body>
<h1>Adjetivaciones asociadas a la palabra "música"</h1>
<p><strong>Archivos analizados:</strong> {len(resultados)}</p>

<h2>Frecuencia global</h2>
{plot_html}

<h2>Resultados por archivo</h2>
{table_html}

<h2>Top adjetivos por periódico</h2>
<div id="detalles"></div>

<script>
const data = {js_data};
let html = "";
for (const [periodico, adj] of Object.entries(data)) {{
  html += `<h3>${{periodico}}</h3><ul>`;
  const sorted = Object.entries(adj).sort((a,b)=>b[1]-a[1]);
  for (const [word,count] of sorted.slice(0,30)) {{
    html += `<li>${{word}} — ${{count}}</li>`;
  }}
  html += "</ul>";
}}
document.getElementById("detalles").innerHTML = html;
</script>

</body>
</html>
'''
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analiza_musica_v3_fixed.py ruta_a_archivo_o_carpeta [otra_ruta ...]")
        sys.exit(1)

    rutas = sys.argv[1:]
    archivos = []
    for r in rutas:
        archivos.extend(obtener_txt_de_ruta(r))
    if not archivos:
        print("❌ No se encontraron archivos .txt en las rutas proporcionadas.")
        sys.exit(1)

    resultados = []
    for archivo in archivos:
        print(f"Analizando {archivo}...")
        try:
            resultados.append(procesar_archivo(archivo))
        except Exception as e:
            print(f"⚠️ Error procesando {archivo}: {e}")

    out = generar_html(resultados)
    print(f"\n✅ He creado: {out} — ábrelo en tu navegador.")
    

if __name__ == "__main__":
    main()
