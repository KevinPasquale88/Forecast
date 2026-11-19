# Appendici

## Appendice A — Glossario

| Termine | Significato |
| --- | --- |
| Accuracy | Quota di predizioni corrette sul totale |
| Anisotropia | Tendenza dei vettori di un encoder a occupare una regione stretta dello spazio, così che tutte le frasi sembrano simili |
| AUC (ROC-AUC) | Area sotto la curva ROC; probabilità che un positivo abbia punteggio più alto di un negativo |
| Average precision (PR-AUC) | Area sotto la curva precision-recall; riferimento casuale = prevalenza |
| Baseline | Modello di riferimento con cui confrontare quello proposto |
| Benjamini-Hochberg (BH) | Correzione dei p-value che controlla il false discovery rate |
| Bootstrap | Ricampionamento con reinserimento per stimare la variabilità di una statistica |
| Brier score | Errore quadratico medio tra probabilità predetta ed esito 0/1 |
| Calibrazione | Accordo tra probabilità predette e frequenze osservate |
| Coseno (similarità) | Prodotto scalare di due vettori diviso per il prodotto delle norme |
| Cross-validation (CV) | Divisione in k parti usate a turno come validazione |
| CV annidata | CV interna, dentro ogni fold esterno, per le scelte (soglia, iperparametri) |
| Data leakage | Informazione della valutazione che entra nell'addestramento o nelle scelte |
| DeLong, test di | Test per confrontare due AUC calcolate sugli stessi pazienti |
| Embedding | Vettore numerico che rappresenta un testo (o un token) |
| Encoder | Rete che trasforma un testo in rappresentazioni vettoriali |
| F1 | Media armonica di precision e recall |
| False discovery rate | Quota attesa di falsi positivi tra i risultati dichiarati significativi |
| Fold | Una delle k parti della cross-validation |
| GGUF | Formato dei pesi usato da Ollama e llama.cpp |
| Holdout (test set) | Dati tenuti da parte per una misura finale unica |
| InfoNCE | Perdita contrastiva usata per addestrare encoder di frase |
| Linear probe | Classificatore lineare addestrato su rappresentazioni congelate |
| Macro-F1 | Media degli F1 delle due classi |
| MAR, MCAR, MNAR | Meccanismi di mancanza dei dati (Rubin) |
| Mean pooling | Media dei vettori dei token per ottenere il vettore di frase |
| `max_seq_length` | Numero massimo di token letti dall'encoder; il resto è troncato |
| Out-of-fold (OOF) | Predizione di un record fatta da un modello che non l'ha visto |
| Overfitting | Adattamento eccessivo ai dati di training |
| p-value | Probabilità di una differenza almeno così grande se non ci fosse differenza reale |
| Precision (PPV) | Quota di predetti positivi che sono davvero positivi |
| Prevalenza | Quota di positivi nella popolazione |
| Quantizzazione | Memorizzazione dei pesi con meno bit (es. 8) |
| Recall (sensibilità) | Quota di positivi trovati |
| Regolarizzazione L2 | Penalità sulla somma dei quadrati dei pesi; in scikit-learn controllata da C |
| Self-attention | Meccanismo per cui ogni token combina le rappresentazioni degli altri token |
| Slot filling | Dialogo che raccoglie valori per una lista fissa di campi |
| SMOTE, SMOTENC | Generazione di esempi sintetici della classe rara per interpolazione |
| Soglia (τ) | Probabilità oltre cui il modello predice positivo |
| Specificità | Quota di negativi riconosciuti |
| Standardizzazione | Trasformare ogni variabile in media 0 e deviazione standard 1 |
| Stratificazione | Mantenere la stessa prevalenza nelle parti di una divisione |
| Token, tokenizer | Pezzo di parola; componente che spezza il testo in token |
| t-test appaiato | Test sulla media delle differenze tra misure appaiate |
| UMAP | Metodo di proiezione 2D che conserva la struttura locale |
| Wilcoxon signed-rank | Test non parametrico su differenze appaiate |

## Appendice B — Formulario

| Grandezza | Formula | Capitolo |
| --- | --- | --- |
| Self-attention | softmax(QKᵀ / √d_k) V | 5.3 |
| InfoNCE | −log [exp(sim(q,p⁺)/t) / Σ_j exp(sim(q,p_j)/t)] | 6.3 |
| Regressione logistica | p = 1 / (1 + exp(−(wᵀx + b))) | 22.1 |
| Obiettivo L2 (scikit-learn) | ½‖w‖² + C Σ log(1 + exp(−y±(wᵀx + b))) | 22.2 |
| Soglia F1 | τ* = argmax_τ 2P(τ)R(τ) / (P(τ) + R(τ)) | 7, 26 |
| Sensibilità, specificità | TP/(TP+FN), TN/(TN+FP) | 27.1 |
| Precision, NPV | TP/(TP+FP), TN/(TN+FN) | 27.1 |
| F1 | 2PR / (P + R) | 27.2 |
| AUC | (1 / n₊n₋) Σ_i Σ_j [1(s_i > s_j) + ½·1(s_i = s_j)] | 27.3 |
| Brier | (1/n) Σ (p_i − y_i)²; riferimento costante π(1 − π) | 27.5 |
| SMOTE | x_new = x_i + λ(x_j − x_i), λ ~ U(0,1) | 25.3 |
| t appaiato | t = d̄ / (s_d / √n) | 29.3 |
| Componenti di DeLong | V₁₀(i) = (1/n₋) Σ_j ψ(s_i, s_j), V₀₁(j) = (1/n₊) Σ_i ψ(s_i, s_j) | 29.5 |
| Benjamini-Hochberg | p^BH₍ₖ₎ = min_{j≥k} min(1, m p₍ⱼ₎ / j) | 29.6 |
| Deviazione standardizzata | d = (x̄_errati − x̄_corretti) / s_pooled | 33.2 |

<!-- APPENDICE_C -->

## Appendice D — Comandi e file

### D.1 Comandi

| Scopo | Comando (dalla radice del progetto) |
| --- | --- |
| Attivare l'ambiente | `source env/bin/activate` |
| Test automatici | `python -m pytest -q` |
| Pipeline Heart Disease | `python main.py --dataset heart_disease` |
| Pipeline Diabetes130 | `python main.py --dataset diabetes130` |
| Inferenza su un record | `python inference.py --dataset heart_disease --record '{"age": 63, ...}'` |
| Baseline tabellari e analisi per centro | `PYTHONPATH=. python manuale_v2/analisi/analisi_aggiuntive.py` |
| Effetto della scala degli embedding | `PYTHONPATH=. python manuale_v2/analisi/scala_embedding.py` |
| Figure del libro | `python manuale_v2/analisi/genera_figure.py` |
| Rigenerare l'EPUB | `python manuale_v2/build_epub.py` |

Il build richiede un `pandoc` nativo per Apple Silicon; `build_epub.py` lo cerca nella variabile d'ambiente `PANDOC`, poi nel `PATH`.

### D.2 File di risultato più utili per la tesi

| File | Contenuto |
| --- | --- |
| `datas/<dataset>/results/encoder_comparison_summary.csv` | Medie bootstrap e intervalli al 95% per modello |
| `datas/<dataset>/results/model_performance.csv` | Medie per fold, incluse PR-AUC, Brier, soglia |
| `datas/<dataset>/results/holdout_evaluation.csv` | Misura sul test set |
| `datas/<dataset>/results/delong_comparison.csv` | DeLong per coppia, con BH |
| `datas/<dataset>/results/wilcoxon_comparison.csv`, `ttest_comparison.csv` | Test sui bootstrap |
| `datas/<dataset>/results/error_summary.csv`, `hardest_cases.csv`, `feature_deviation.csv` | Analisi degli errori |
| `datas/<dataset>/reports/report.md` | Report completo della run |
| `manuale_v2/analisi/risultati_aggiuntivi.json` | Baseline, analisi per centro, modello solo mancanza |
| `manuale_v2/analisi/scala_embedding.json` | Varianti di scala e DeLong equo |

## Appendice E — Bibliografia

Le voci marcate † sono state verificate su fonte (DOI, arXiv, PubMed, ACL Anthology, PMLR, JMLR o archivi istituzionali): la maggior parte il 14/11/2026, alcune già per la prima edizione. Le voci senza † sono classici riportati con i dati principali: controllarli su fonte primaria prima di citarli in tesi.

### Dataset

- † Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). *Heart Disease*. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4W
- † Detrano, R., et al. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. *American Journal of Cardiology*, 64(5), 304–310.
- † Strack, B., et al. (2014). *Diabetes 130-US Hospitals for Years 1999-2008*. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
- † Strack, B., et al. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. *BioMed Research International*, 2014, 781670.
- † Johnson, A. E. W., Pollard, T. J., et al. (2016). MIMIC-III, a freely accessible critical care database. *Scientific Data*, 3, 160035.

### Modelli di linguaggio ed embedding

- Vaswani, A., et al. (2017). Attention is all you need. *Advances in Neural Information Processing Systems 30*.
- † Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *Proceedings of NAACL-HLT 2019*, 4171–4186. (Pagine confermate da una sola fonte secondaria: verificarle sull'ACL Anthology.)
- † Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992. https://doi.org/10.18653/v1/D19-1410
- van den Oord, A., Li, Y., & Vinyals, O. (2018). Representation learning with contrastive predictive coding. arXiv:1807.03748.
- † Wang, L., et al. (2022). Text embeddings by weakly-supervised contrastive pre-training. arXiv:2212.03533.
- † Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Multilingual E5 text embeddings: a technical report. arXiv:2402.05672.
- † Li, Z., et al. (2023). Towards general text embeddings with multi-stage contrastive learning. arXiv:2308.03281.
- † Lee, J., et al. (2020). BioBERT: a pre-trained biomedical language representation model for biomedical text mining. *Bioinformatics*, 36(4), 1234–1240. https://doi.org/10.1093/bioinformatics/btz682
- † Gu, Y., Tinn, R., Cheng, H., et al. (2021). Domain-specific language model pretraining for biomedical natural language processing. *ACM Transactions on Computing for Healthcare*, 3(1), Article 2. https://doi.org/10.1145/3458754
- † Alsentzer, E., et al. (2019). Publicly available clinical BERT embeddings. *Proceedings of the 2nd Clinical NLP Workshop*, 72–78. arXiv:1904.03323.
- † Romanov, A., & Shivade, C. (2018). Lessons from natural language inference in the clinical domain. *Proceedings of EMNLP 2018*, 1586–1596.
- † Alain, G., & Bengio, Y. (2016). Understanding intermediate layers using linear classifier probes. arXiv:1610.01644.
- Model card (Hugging Face), da citare con data di consultazione: `NeuML/pubmedbert-base-embeddings`, `pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb`, `moka-ai/m3e-base`, `thenlper/gte-large-zh`, `intfloat/e5-base-v2`, `intfloat/multilingual-e5-large-instruct`.

### Dati tabellari e testo

- † Hegselmann, S., Buendia, A., Lang, H., Agrawal, M., Jiang, X., & Sontag, D. (2023). TabLLM: Few-shot classification of tabular data with large language models. *Proceedings of AISTATS 2023*, PMLR 206, 5549–5581.
- † Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? *NeurIPS 2022, Datasets and Benchmarks Track*. arXiv:2207.08815.

### Metodo e statistica

- † Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research*, 16, 321–357. https://doi.org/10.1613/jair.953
- † DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. *Biometrics*, 44(3), 837–845. https://doi.org/10.2307/2531595
- † Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology*, 143(1), 29–36.
- † Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE*, 10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432
- † Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. (Il titolo compare in due varianti nelle fonti secondarie: controllarlo sul PDF originale.)
- † Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: the Achilles heel of predictive analytics. *BMC Medicine*, 17, 230. https://doi.org/10.1186/s12916-019-1466-7
- Efron, B. (1979). Bootstrap methods: another look at the jackknife. *The Annals of Statistics*, 7(1), 1–26.
- Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.
- † Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society, Series B*, 57(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
- † Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. *Machine Learning*, 52, 239–281. https://doi.org/10.1023/A:1024068626366
- † Dietterich, T. G. (1998). Approximate statistical tests for comparing supervised classification learning algorithms. *Neural Computation*, 10(7), 1895–1923. https://doi.org/10.1162/089976698300017197
- † Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics*, 7, 91.
- † Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research*, 11, 2079–2107.
- † Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data*, 6(4), Article 15. (Versione precedente: KDD 2011, 556–563.)
- † Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*, 4(9), 100804. https://doi.org/10.1016/j.patter.2023.100804
- Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3), 581–592.
- † McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform manifold approximation and projection for dimension reduction. arXiv:1802.03426.
- † Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

### Clinica, reporting e regolamentazione

- † Collins, G. S., et al. (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*, 385, e078378. https://doi.org/10.1136/bmj-2023-078378 (correzione: BMJ 2024;385:q902).
- Regolamento (UE) 2016/679 (GDPR), articolo 9. EUR-Lex.
- Regolamento (UE) 2017/745 relativo ai dispositivi medici (MDR), allegato VIII, regola 11. EUR-Lex.
- Regolamento (UE) 2024/1689 (AI Act). EUR-Lex.
- Hospital Readmissions Reduction Program, Patient Protection and Affordable Care Act (2010), sezione 3025.
