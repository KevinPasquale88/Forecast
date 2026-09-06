# Appendice C — Formulario

> Tutte le formule numerate del libro, in ordine, con il rimando al capitolo dove ogni simbolo è spiegato per esteso e alla riga di codice che la implementa.

**25.1 — Deviazione di feature (capitolo 25.3, `error_analysis.py:65-75`)**
$$d_{\text{feature}} = \frac{\bar{x}_{\text{errore}} - \bar{x}_{\text{corretto}}}{s_{\text{pooled}}}$$

**32.1 — Regressione logistica (capitolo 32.1, `classification.py:16,28`)**
$$P(y=1 \mid \mathbf{x}) = \sigma(\mathbf{w}^\top \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^\top \mathbf{x} + b)}}$$

**32.2 — Funzione obiettivo regolarizzata (capitolo 32.2, `classification.py:16`, default scikit-learn)**
$$\min_{\mathbf{w}, b} \;\; \frac{1}{2}\mathbf{w}^\top \mathbf{w} + C \sum_{i=1}^{n} \log\Big(1 + e^{-y_i (\mathbf{w}^\top \mathbf{x}_i + b)}\Big)$$

**33.1 — K-fold (capitolo 33.2, `classification.py:15`)**
$$\text{per } i = 1, \dots, k: \quad \text{addestra su } \bigcup_{j \neq i} D_j, \quad \text{valuta su } D_i$$

**34.1 — Accuracy (capitolo 34.1, `classification.py:39`)**
$$\text{Accuracy} = \frac{VP + VN}{VP + VN + FP + FN}$$

**34.2 — F1 (capitolo 34.2, `classification.py:40`)**
$$F1 = 2 \cdot \frac{\text{precisione} \cdot \text{recall}}{\text{precisione} + \text{recall}}, \quad \text{precisione} = \frac{VP}{VP+FP}, \quad \text{recall} = \frac{VP}{VP+FN}$$

**34.3 — TPR/FPR per la curva ROC (capitolo 34.3, `function.py:264`)**
$$\text{TPR}(\tau) = \frac{VP(\tau)}{VP(\tau)+FN(\tau)}, \qquad \text{FPR}(\tau) = \frac{FP(\tau)}{FP(\tau)+VN(\tau)}$$

**35.1 — Soglia F1-ottima (capitolo 35.2, `classification.py:30-35`)**
$$\tau^\star = \operatorname*{arg\,max}_{\tau \in T} \; F1\big(y_{\text{val}},\, \mathbb{1}[y_{\text{score}} \geq \tau]\big)$$

**35.2 — Soglia con calibrazione separata, non implementata (capitolo 35.3)**
$$\tau^\star_{\text{rigoroso}} = \operatorname*{arg\,max}_{\tau \in T} \; F1\big(y_{\text{calib}},\, \mathbb{1}[y_{\text{score,calib}} \geq \tau]\big), \; \text{valutato su } y_{\text{val}} \neq y_{\text{calib}}$$

**36.1 — Ricampionamento bootstrap (capitolo 36.1, `evaluation.py:66`)**
$$I^{(b)} = \{i_1, \dots, i_n\}, \quad i_j \sim \mathcal{U}\{1, \dots, n\} \text{ indipendenti}, \qquad b = 1, \dots, B$$

**36.2 — Stima bootstrap di una metrica (capitolo 36.1, `evaluation.py:68-70`)**
$$\hat{M}^{(b)} = M\big(\{y_{\text{true},i}\}_{i \in I^{(b)}}, \{y_{\text{pred},i}\}_{i \in I^{(b)}}\big)$$

**36.3 — Intervallo di confidenza percentile (capitolo 36.2, `evaluation.py:77-81`)**
$$\text{IC}_{\alpha} = \big[\, \hat{M}_{(0.025)}, \; \hat{M}_{(0.975)} \,\big]$$

**36.4 — Deviazione standard bootstrap (capitolo 36.2, `evaluation.py:37`)**
$$\widehat{SE}_{\text{boot}}(M) = \sqrt{\frac{1}{B-1}\sum_{b=1}^{B}\big(\hat{M}^{(b)} - \bar{M}\big)^2}$$

**37.1 — Wilcoxon signed-rank (capitolo 37.1, `statisticaltest.py:35`)**
$$W = \min(W^+, W^-), \qquad W^+ = \sum_{i:\, d_i > 0} R_i, \quad W^- = \sum_{i:\, d_i < 0} R_i$$

**37.2 — t-test appaiato (capitolo 37.2, `statisticaltest.py:48`)**
$$t = \frac{\bar{d}}{s_d / \sqrt{n}}$$

**37.3 — Test di DeLong (capitolo 37.3, `statisticaltest.py:95`, delegato a `MLstatkit`)**
$$Z = \frac{\widehat{\text{AUC}}_A - \widehat{\text{AUC}}_B}{\sqrt{\widehat{\text{Var}}(\widehat{\text{AUC}}_A) + \widehat{\text{Var}}(\widehat{\text{AUC}}_B) - 2\,\widehat{\text{Cov}}(\widehat{\text{AUC}}_A, \widehat{\text{AUC}}_B)}}$$
