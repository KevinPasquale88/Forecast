"""Genera l'Appendice C (tabelle complete) dai file dei risultati.

Chiamato da build_epub.py; si può eseguire da solo dalla radice del progetto:
    env/bin/python manuale_v2/genera_tabelle.py
Le tabelle di un dataset vengono incluse solo se la sua run è della pipeline corretta
(holdout_evaluation.csv con la colonna pr_auc); altrimenti viene scritta un'avvertenza.
"""
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATAS = os.path.join(ROOT, "datas")
ANALISI = os.path.join(ROOT, "manuale_v2", "analisi")
NOMI = {"heart_disease": "Heart Disease", "diabetes130": "Diabetes130"}


def fmt(v):
    if isinstance(v, float):
        return f"{v:.4f}".replace(".", ",")
    return str(v)


def md_table(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(fmt(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def dataset_section(ds):
    res = os.path.join(DATAS, ds, "results")
    out = [f"### C.{1 if ds == 'heart_disease' else 2} {NOMI[ds]}\n"]
    holdout = os.path.join(res, "holdout_evaluation.csv")
    if not os.path.exists(holdout) or "pr_auc" not in pd.read_csv(holdout, nrows=0).columns:
        out.append(
            "> *Attenzione.* I risultati presenti in `datas/" + ds + "/` vengono dalla pipeline "
            "precedente (SMOTENC prima della CV) e non sono validi. Eseguire "
            f"`python main.py --dataset {ds}` e rigenerare il libro.\n"
        )
        return "\n".join(out)

    def add(title, fname, cols=None, note=None):
        path = os.path.join(res, fname)
        if not os.path.exists(path):
            return
        df = pd.read_csv(path)
        if cols:
            df = df[[c for c in cols if c in df.columns]]
        out.append(f"**{title}** (`{fname}`)\n")
        if note:
            out.append(note + "\n")
        out.append(md_table(df) + "\n")

    add("Riepilogo bootstrap (media e IC 95%)", "encoder_comparison_summary.csv",
        ["model", "acc_mean", "acc_ci_low", "acc_ci_high", "f1_mean", "f1_ci_low", "f1_ci_high",
         "auc_mean", "auc_ci_low", "auc_ci_high"])
    perf = pd.read_csv(os.path.join(res, "model_performance.csv")).rename(columns={"Unnamed: 0": "model"})
    out.append("**Medie sui 5 fold** (`model_performance.csv`)\n")
    out.append(md_table(perf) + "\n")
    add("Test set", "holdout_evaluation.csv")
    add("DeLong", "delong_comparison.csv")
    add("Wilcoxon sui bootstrap", "wilcoxon_comparison.csv",
        ["metric", "model_a", "model_b", "mean_a", "mean_b", "p_value", "p_value_bh", "significant_bh"])
    add("t-test appaiato sui bootstrap", "ttest_comparison.csv",
        ["metric", "model_a", "model_b", "mean_a", "mean_b", "statistic", "p_value", "p_value_bh", "significant_bh"])
    add("Errori per modello", "error_summary.csv")
    add("Deviazione delle variabili", "feature_deviation.csv")
    return "\n".join(out)


def extra_section():
    out = ["### C.3 Analisi aggiuntive\n"]
    p = os.path.join(ANALISI, "risultati_aggiuntivi.json")
    if os.path.exists(p):
        r = json.load(open(p, encoding="utf-8"))
        rows = []
        for ds, models in r["baseline"].items():
            for m, v in models.items():
                rows.append({"dataset": NOMI[ds], "modello": m, **v})
        out.append("**Baseline tabellari** (`risultati_aggiuntivi.json`)\n")
        out.append(md_table(pd.DataFrame(rows)) + "\n")
        out.append("**Heart Disease: ROC-AUC out-of-fold per centro**\n")
        out.append(md_table(pd.DataFrame(r["heart_centri"]["per_centro"])) + "\n")
        out.append(
            f"AUC della sola prevalenza del centro: {fmt(r['heart_centri']['auc_solo_prevalenza_centro'])}. "
            f"AUC dei soli indicatori di mancanza: {fmt(r['heart_solo_mancanza']['auc_cv'])}.\n"
        )
    p = os.path.join(ANALISI, "scala_embedding.json")
    if os.path.exists(p):
        r = json.load(open(p, encoding="utf-8"))
        df = pd.DataFrame(r["auc"]).T.reset_index().rename(columns={"index": "model"})
        out.append("**Heart Disease: ROC-AUC con quattro protocolli di scala** (`scala_embedding.json`)\n")
        out.append(md_table(df) + "\n")
        out.append("**DeLong con protocollo equo (standardizzazione + C da CV interna)**\n")
        out.append(md_table(pd.DataFrame(r["delong_equo"])) + "\n")
    return "\n".join(out)


def build():
    parts = ["## Appendice C — Tabelle complete\n",
             "Generata automaticamente dai file dei risultati al momento del build.\n",
             dataset_section("heart_disease"), dataset_section("diabetes130"), extra_section()]
    return "\n".join(parts)


if __name__ == "__main__":
    print(build()[:2000])
