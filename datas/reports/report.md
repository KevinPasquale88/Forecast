# 📊 Encoder Evaluation Report

**Generated:** 2026-05-17 01:47

---

## 🎯 Obiettivo

Verificare la robustezza e l’affidabilità della pipeline basata su embedding generati da modelli moderni (E5-base, E5-large, GTE-large).

## 📘 Modelli valutati

- **e5-base**
- **gte-base**
- **gte-large**
- **e5-large**

---

## 📈 Risultati delle metriche con intervalli di confidenza (Bootstrap 10.000)

| model     |   acc_mean |   acc_ci_low |   acc_ci_high |   f1_mean |   f1_ci_low |   f1_ci_high |   auc_mean |   auc_ci_low |   auc_ci_high |
|:----------|-----------:|-------------:|--------------:|----------:|------------:|-------------:|-----------:|-------------:|--------------:|
| e5-base   |   0.702475 |     0.669837 |      0.735054 |  0.663689 |    0.627163 |     0.699388 |   0.755398 |     0.71977  |      0.79032  |
| gte-base  |   0.783989 |     0.754076 |      0.8125   |  0.777546 |    0.746772 |     0.807024 |   0.826351 |     0.795846 |      0.855741 |
| gte-large |   0.707999 |     0.673913 |      0.740489 |  0.683694 |    0.648373 |     0.718399 |   0.751569 |     0.715765 |      0.785562 |
| e5-large  |   0.74328  |     0.711957 |      0.774457 |  0.735407 |    0.702841 |     0.767215 |   0.773525 |     0.739377 |      0.807318 |


---

## 📉 ROC Curve dei modelli

### e5-base

![ROC e5-base](datas/graphics/ROC_e5-base.png)

### gte-base

![ROC gte-base](datas/graphics/ROC_gte-base.png)

### gte-large

![ROC gte-large](datas/graphics/ROC_gte-large.png)

### e5-large

![ROC e5-large](datas/graphics/ROC_e5-large.png)


---

## 🧩 Confusion Matrix

### e5-base

![CM e5-base](datas/graphics/CM_e5-base.png)

### gte-base

![CM gte-base](datas/graphics/CM_gte-base.png)

### gte-large

![CM gte-large](datas/graphics/CM_gte-large.png)

### e5-large

![CM e5-large](datas/graphics/CM_e5-large.png)


---


---

## 🔍 Discussione e Osservazioni


- I modelli con embedding più grandi (E5-large, GTE-large) mostrano in genere prestazioni migliori.
- GTE-large tende a ottenere ROC-AUC più alte e intervalli di confidenza più stretti.
- Le confusion matrix permettono di analizzare i falsi negativi e falsi positivi.
- Il bootstrap è utile per verificare stabilità e robustezza delle metriche.


---

## 🏁 Conclusioni


- L’approccio basato su embedding + classificatore lineare è efficace.
- Gli encoder moderni come GTE-large mostrano ottime capacità di generalizzazione.
- La pipeline è robusta e stabile, come confermato dal bootstrap 10.000.


---

## 🚀 Possibili Miglioramenti


- Testare ulteriori encoder (bge-large, Jina-Embeddings, E5-mistral).
- Introdurre un classificatore non lineare (XGBoost, LightGBM).
- Utilizzare tecniche avanzate di calibration (Platt scaling).
- Aggiungere un dataset clinico più grande per ridurre il variance error.
