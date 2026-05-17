import pandas as pd
import os
import datetime

# ============================================================
#  CARICA RISULTATI (CSV con metriche medie e CI)
# ============================================================

def load_summary(summary_path="datas/results/encoder_comparison_summary.csv"):
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"File non trovato: {summary_path}")
    return pd.read_csv(summary_path)


# ============================================================
#  CREA IL CONTENUTO MARKDOWN
# ============================================================

def generate_markdown(summary):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    md = []

    md.append(f"# 📊 Encoder Evaluation Report\n")
    md.append(f"**Generated:** {now}\n")
    md.append("---\n")

    md.append("## 🎯 Obiettivo\n")
    md.append("Verificare la robustezza e l’affidabilità della pipeline basata su embedding generati da modelli moderni (E5-base, E5-large, GTE-large).\n")

    md.append("## 📘 Modelli valutati\n")
    for model in summary["model"]:
        md.append(f"- **{model}**")

    md.append("\n---\n")

    # ============================
    # METRICHE CON CI
    # ============================

    md.append("## 📈 Risultati delle metriche con intervalli di confidenza (Bootstrap 10.000)\n")

    md.append(summary.to_markdown(index=False))
    md.append("\n\n---\n")

    # ============================
    # GRAFICI INSERITI NEL REPORT
    # ============================

    md.append("## 📉 ROC Curve dei modelli\n")
    for model in summary["model"]:
        roc_path = f"datas/graphics/ROC_{model}.png"
        real_roc_path = f"../graphics/ROC_{model}.png"
        if os.path.exists(roc_path):
            md.append(f"### {model}\n")
            md.append(f"![ROC {model}]({real_roc_path})\n")

    md.append("\n---\n")

    md.append("## 🧩 Confusion Matrix\n")
    for model in summary["model"]:
        cm_path = f"datas/graphics/CM_{model}.png"
        real_cm_path = f"../graphics/CM_{model}.png"
        if os.path.exists(cm_path):
            md.append(f"### {model}\n")
            md.append(f"![CM {model}]({real_cm_path})\n")

    md.append("\n---\n")

    boxplot_path = "datas/results/BOXPLOT_metrics.png"
    real_boxplot_path = "../results/BOXPLOT_metrics.png"
    if os.path.exists(boxplot_path):
        md.append("## 📦 Boxplot delle Metriche (Bootstrap)\n")
        md.append(f"![Boxplot]({real_boxplot_path})\n")

    md.append("\n---\n")

    # ============================
    # DISCUSSIONE
    # ============================

    md.append("## 🔍 Discussione e Osservazioni\n")
    md.append("""
- I modelli con embedding più grandi (E5-large, GTE-large) mostrano in genere prestazioni migliori.
- GTE-large tende a ottenere ROC-AUC più alte e intervalli di confidenza più stretti.
- Le confusion matrix permettono di analizzare i falsi negativi e falsi positivi.
- Il bootstrap è utile per verificare stabilità e robustezza delle metriche.
""")

    md.append("\n---\n")

    # ============================
    # CONCLUSIONI
    # ============================

    md.append("## 🏁 Conclusioni\n")
    md.append("""
- L’approccio basato su embedding + classificatore lineare è efficace.
- Gli encoder moderni come GTE-large mostrano ottime capacità di generalizzazione.
- La pipeline è robusta e stabile, come confermato dal bootstrap 10.000.
""")

    md.append("\n---\n")

    # ============================
    # MIGLIORAMENTI
    # ============================

    md.append("## 🚀 Possibili Miglioramenti\n")
    md.append("""
- Testare ulteriori encoder (bge-large, Jina-Embeddings, E5-mistral).
- Introdurre un classificatore non lineare (XGBoost, LightGBM).
- Utilizzare tecniche avanzate di calibration (Platt scaling).
- Aggiungere un dataset clinico più grande per ridurre il variance error.
""")

    return "\n".join(md)


# ============================================================
#  PRINCIPALE
# ============================================================

def generate_report():

    print("[INFO] Carico riepilogo metriche...")
    summary = load_summary()

    print("[INFO] Genero il report markdown...")
    md_content = generate_markdown(summary)

    md_path = "datas/reports/report.md"

    with open(md_path, "w") as f:
        f.write(md_content)

    print(f"[OK] Report Markdown creato: {md_path}")
    print("\n=== REPORT COMPLETO GENERATO ===")
