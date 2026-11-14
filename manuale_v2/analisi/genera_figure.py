"""Figure aggiuntive del manuale v2 (eseguire dalla radice del progetto):

    env/bin/python manuale_v2/analisi/genera_figure.py

Legge i risultati della pipeline (datas/heart_disease/results) e risultati_aggiuntivi.json e
scrive PNG a 200 DPI in manuale_v2/figure/.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

FIG = os.path.join("manuale_v2", "figure")
BLUE, GREY, INK, LIGHT = "#2a78d6", "#9a9a9a", "#222222", "#e8f0fb"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
extra = json.load(open(os.path.join("manuale_v2", "analisi", "risultati_aggiuntivi.json")))


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, title, sub="", hi=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=LIGHT if hi else "white", ec=BLUE if hi else GREY, lw=1.6 if hi else 1.1))
    ax.text(x, y + (0.12 if sub else 0), title, ha="center", va="center", fontsize=10, fontweight="bold", color=INK)
    if sub:
        ax.text(x, y - 0.17, sub, ha="center", va="center", fontsize=8.2, color="#555555")


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))


def fig_pipeline():
    fig, ax = plt.subplots(figsize=(8.5, 9.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 11); ax.axis("off")
    box(ax, 5, 10.2, 8.6, 0.8, "1 · Preprocessing", "carica · binarizza il target · split 80/20 stratificato · nessuna imputazione né oversampling")
    L, R, W = 2.9, 7.6, 4.0
    ax.text(L + 0.2, 9.35, "training 80% (736 / 16.000)", fontsize=8.2, color="#555555")
    ax.text(R + 0.2, 9.35, "test 20% (184 / 4.000)", fontsize=8.2, color="#555555")
    arrow(ax, L, 9.8, L, 8.95); arrow(ax, R, 9.8, R, 8.95)
    box(ax, L, 8.55, W, 0.8, "2 · Embedding training", "record → frase → 7 encoder")
    box(ax, R, 8.55, 4.0, 0.8, "2 · Embedding test", "stessi encoder, file *_test.npy", hi=True)
    steps = [("3 · Classificazione", "CV 5 fold · soglia out-of-fold"), ("4 · Valutazione", "bootstrap 10.000 · grafici"),
             ("5 · Analisi degli errori", "FP, FN, casi difficili"), ("6 · Test statistici", "Wilcoxon · t-test · DeLong · BH")]
    y = 7.15
    prev = 8.15
    for t, s in steps:
        arrow(ax, L, prev, L, y + 0.4)
        box(ax, L, y, W, 0.8, t, s)
        prev = y - 0.4
        y -= 1.4
    box(ax, R, 5.75, 4.0, 0.8, "7 · Holdout", "classificatore finale · misura unica", hi=True)
    arrow(ax, R, 8.15, R, 6.15)
    ax.annotate("", xy=(R - 2.0, 5.75), xytext=(L + 2.0, 8.4),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1, connectionstyle="angle,angleA=0,angleB=90,rad=0"))
    box(ax, 5, 1.0, 8.6, 0.8, "8 · Report", "reports/report.md: tabelle, grafici, test, holdout")
    arrow(ax, L, prev, L, 1.4); arrow(ax, R, 5.35, R, 1.4)
    ax.set_title("Le otto fasi di main.py: il test set segue una strada separata", loc="left", fontsize=12, fontweight="bold")
    save(fig, "schema_pipeline.png")


def fig_cv():
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Un fold esterno: la soglia nasce da una CV interna sul solo training del fold", loc="left",
                 fontsize=11.5, fontweight="bold")
    for i in range(5):
        x = 0.4 + i * 1.9
        ax.add_patch(FancyBboxPatch((x, 4.5), 1.7, 0.6, boxstyle="round,pad=0.01", fc=LIGHT if i == 4 else "white",
                                    ec=BLUE if i == 4 else GREY))
        ax.text(x + 0.85, 4.8, "validazione" if i == 4 else f"training {i + 1}", ha="center", va="center", fontsize=8.5)
    ax.text(0.4, 5.35, "CV esterna (5 fold): il fold di validazione serve solo a misurare", fontsize=8.5, color="#555555")
    for i in range(5):
        x = 0.4 + i * 1.25
        ax.add_patch(FancyBboxPatch((x, 2.6), 1.1, 0.55, boxstyle="round,pad=0.01", fc="#f3f3f3" if i == 2 else "white", ec=GREY))
        ax.text(x + 0.55, 2.875, "OOF" if i == 2 else "fit", ha="center", va="center", fontsize=8)
    ax.text(0.4, 2.25, "CV interna sui 4 fold di training: punteggi out-of-fold per ogni record",
            fontsize=8.5, color="#555555")
    ax.annotate("", xy=(3.15, 3.2), xytext=(3.15, 4.45), arrowprops=dict(arrowstyle="-|>", color=GREY))
    box(ax, 8.4, 2.9, 2.6, 0.75, "τ = argmax F1", "sui punteggi out-of-fold")
    ax.annotate("", xy=(7.05, 2.9), xytext=(6.6, 2.9), arrowprops=dict(arrowstyle="-|>", color=GREY))
    box(ax, 2.6, 0.9, 4.4, 0.75, "Regressione logistica", "addestrata su tutti i 4 fold di training")
    box(ax, 7.9, 0.9, 3.8, 0.75, "Predizione sul fold di validazione", "positivo se p ≥ τ", hi=True)
    ax.annotate("", xy=(6.3, 0.9), xytext=(4.8, 0.9), arrowprops=dict(arrowstyle="-|>", color=GREY))
    ax.annotate("", xy=(8.2, 1.3), xytext=(8.4, 2.5), arrowprops=dict(arrowstyle="-|>", color=GREY))
    save(fig, "schema_cv_soglia.png")


def fig_chatbot():
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    ax.set_title("Chatbot: interfacce sottili, una sola logica, lo stesso modello misurato sul test set", loc="left",
                 fontsize=11.5, fontweight="bold")
    box(ax, 1.6, 4.0, 2.6, 0.75, "Streamlit", "app_streamlit.py")
    box(ax, 1.6, 2.7, 2.6, 0.75, "Telegram", "bot_telegram.py")
    box(ax, 5.0, 3.35, 3.0, 0.9, "chatbot_core.py", "domande · parser · sessione", hi=True)
    box(ax, 8.6, 4.15, 2.5, 0.75, "record_to_text()", "stessa frase del training")
    box(ax, 8.6, 2.95, 2.5, 0.75, "sentence-biobert", "512 token")
    box(ax, 8.6, 1.75, 2.5, 0.75, "deployed_bundle", "classificatore + τ")
    box(ax, 5.0, 0.8, 5.2, 0.75, "main.py: ricostruisce tutto a ogni avvio", "preprocessing → embedding → classificazione")
    for y in (4.0, 2.7):
        ax.annotate("", xy=(3.5, 3.35), xytext=(2.9, y), arrowprops=dict(arrowstyle="-|>", color=GREY))
    for y in (4.15, 2.95, 1.75):
        ax.annotate("", xy=(7.35, y), xytext=(6.5, 3.35), arrowprops=dict(arrowstyle="-|>", color=GREY))
    ax.annotate("", xy=(8.6, 1.35), xytext=(7.3, 0.8), arrowprops=dict(arrowstyle="-|>", color=GREY))
    save(fig, "schema_chatbot.png")


def fig_baseline():
    s = pd.read_csv("datas/heart_disease/results/encoder_comparison_summary.csv")
    h = pd.read_csv("datas/heart_disease/results/holdout_evaluation.csv")
    b = extra["baseline"]["heart_disease"]
    rows = [(m, s.loc[s.model == m, "auc_mean"].item(), h.loc[h.model == m, "auc"].item(), "enc") for m in s.model]
    rows += [("tabellare: reg. logistica", b["regressione_logistica"]["cv_auc"], b["regressione_logistica"]["test_auc"], "tab"),
             ("tabellare: gradient boosting", b["gradient_boosting"]["cv_auc"], b["gradient_boosting"]["test_auc"], "tab")]
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for i, (m, cv, te, k) in enumerate(rows):
        c = INK if k == "tab" else (BLUE if m in ("bioclinicalbert", "pubmedbert", "sentence-biobert") else GREY)
        ax.plot([cv], [i], "o", color=c, ms=8)
        ax.plot([te], [i], "o", mfc="none", mec=c, ms=8)
        ax.text(0.795, i, f"{cv:.3f}".replace(".", ","), va="center", ha="right", fontsize=8.5, color="#555555")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_xlim(0.76, 0.94)
    ax.set_xlabel("ROC-AUC (pieno: cross-validation · vuoto: test set)")
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_title("Heart Disease: la regressione logistica sulle colonne originali vale quanto il miglior encoder",
                 loc="left", fontsize=11, fontweight="bold")
    save(fig, "baseline_heart.png")


def fig_centri():
    rows = extra["heart_centri"]["per_centro"]
    models = ["e5-base", "gte-base", "gte-large", "e5-large", "bioclinicalbert", "pubmedbert", "sentence-biobert"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for j, r in enumerate(rows):
        for k, m in enumerate(models):
            c = BLUE if k >= 4 else GREY
            ax.plot(r[m], j + (k - 3) * 0.07, "o", color=c, ms=6, alpha=0.9)
    ax.set_yticks(range(len(rows)), [f"{r['centro']} (n={r['n_train']}, prev. {r['prevalenza_train']:.0%})" for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel("ROC-AUC out-of-fold calcolata dentro il singolo centro (blu: biomedici · grigio: generalisti)")
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_title("Dentro un solo centro l'AUC scende: parte del segnale aggregato è il centro stesso", loc="left",
                 fontsize=11, fontweight="bold")
    save(fig, "auc_per_centro.png")


if __name__ == "__main__":
    fig_pipeline(); fig_cv(); fig_chatbot(); fig_baseline(); fig_centri()
    print("figure scritte in", FIG)
