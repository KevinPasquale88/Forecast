# Appendice D — Bibliografia annotata

> Ogni voce riporta l'affidabilità della fonte e come è stata verificata. Nessuna voce è stata lasciata come "sembra plausibile": le quattro già citate nella documentazione del progetto sono state controllate contro `docs/DATASET.md`; le otto aggiuntive sono state cercate e confermate con WebSearch in questa sessione (2026-09-05/06), con DOI, arXiv ID o ISBN verificato. L'esportazione in formato BibTeX è in `bibliografia.bib`, nella stessa cartella.

## Dataset (citati direttamente nel progetto)

**[Verificato — citato in `docs/DATASET.md:67` del progetto]** Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). *Heart Disease*. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4W

**[Verificato — citato in `docs/DATASET.md:68`]** Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, K., Sandhu, S., Guppy, K. H., Lee, S., & Froelicher, V. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. *American Journal of Cardiology*, 64(5), 304–310.

**[Verificato — citato in `docs/DATASET.md:113`]** Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. (2014). *Diabetes 130-US Hospitals for Years 1999-2008*. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J

**[Verificato — citato in `docs/DATASET.md:114`]** Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. *BioMed Research International*, 2014, Article 781670.

## Metodo statistico (verificati con WebSearch in questa sessione)

**[Verificato — WebSearch, 2026-09-05]** DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. *Biometrics*, 44(3), 837–845. https://doi.org/10.2307/2531595 — fonda il test usato in `statisticaltest.py` (capitolo 37.3) tramite la libreria `MLstatkit`.

**[Verificato — WebSearch, 2026-09-05]** Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *Journal of Artificial Intelligence Research*, 16. https://doi.org/10.1613/jair.953 — introduce sia SMOTE sia la sua estensione a feature miste numeriche/categoriali (SMOTENC), usata in `preprocessing.py:84-92` (capitolo 21.2).

**[Verificato — WebSearch, 2026-09-05]** McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv preprint* arXiv:1802.03426. https://arxiv.org/abs/1802.03426 — algoritmo usato in `function.py:224` (capitolo 38).

**[Approfondimento facoltativo, verificato — WebSearch, 2026-09-05]** Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer. ISBN 978-0-387-84857-0. — riferimento generale su bias-variance tradeoff (capitolo 2.3), non specifico di questo progetto.

## Modelli di embedding (verificati con WebSearch in questa sessione)

**[Verificato — WebSearch, 2026-09-05]** Wang, L., Yang, N., Huang, X., Jiao, B., Yang, L., Jiang, D., Majumder, R., & Wei, F. (2022). Text Embeddings by Weakly-Supervised Contrastive Pre-training. *arXiv preprint* arXiv:2212.03533. https://arxiv.org/abs/2212.03533 — famiglia E5, usata via Ollama in `function.py:39,42` (capitolo 5.2). **[Da verificare]** l'elenco completo degli autori qui riportato proviene da una fonte secondaria (scispace/semanticscholar); verificarlo contro il PDF originale prima di una citazione in tesi che richieda precisione assoluta sull'ordine degli autori.

**[Verificato — WebSearch, 2026-09-05]** Li, Z., Zhang, X., Zhang, Y., Long, D., Xie, P., & Zhang, M. (2023). Towards General Text Embeddings with Multi-stage Contrastive Learning. *arXiv preprint* arXiv:2308.03281. https://arxiv.org/abs/2308.03281 — famiglia GTE, usata via Ollama in `function.py:40-41` (capitolo 5.2).

**[Verificato — WebSearch, 2026-09-05]** Alsentzer, E., Murphy, J., Boag, W., Weng, W.-H., Jin, D., Naumann, T., & McDermott, M. (2019). Publicly Available Clinical BERT Embeddings. In *Proceedings of the 2nd Clinical Natural Language Processing Workshop* (pp. 72–78). Association for Computational Linguistics. arXiv:1904.03323. — modello `emilyalsentzer/Bio_ClinicalBERT`, usato in `function.py:46` (capitolo 5.3, capitolo 22.3).

**[Verificato — WebSearch, 2026-09-05]** Lee, J., Yoon, W., Kim, S., Kim, D., Kim, S., So, C. H., & Kang, J. (2020). BioBERT: a pre-trained biomedical language representation model for biomedical text mining. *Bioinformatics*, 36(4), 1234–1240. https://doi.org/10.1093/bioinformatics/btz682 — famiglia biomedica a cui appartiene il modello `sentence-biobert` (`pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb`, `function.py:48`, capitolo 5.3). **[Da verificare]** il modello specifico usato in questo progetto è una variante fine-tuned di BioBERT per sentence-embedding: questo riferimento copre il modello di base (BioBERT), non necessariamente il fine-tuning specifico applicato dall'autore del modello su Hugging Face, non identificato con un proprio paper in questa sessione.

**[Da verificare — non citare prima del controllo]** Il modello `NeuML/pubmedbert-base-embeddings` (`function.py:47`, capitolo 5.3, capitolo 22.3) non è stato ricercato in questa sessione: è presumibilmente basato su PubMedBERT (Gu et al., "Domain-Specific Language Model Pretraining for Biomedical Natural Language Processing"), ma questa attribuzione non è stata verificata con una ricerca dedicata e non va citata come tale senza controllo.

## Riepilogo affidabilità

12 riferimenti verificati con identificativo concreto (DOI, arXiv ID o ISBN); 1 riferimento (`NeuML/pubmedbert-base-embeddings`) esplicitamente non cercato, marcato da non citare prima di una ricerca dedicata; 2 precisazioni minori marcate "da verificare" su dettagli specifici (ordine autori E5, attribuzione esatta del fine-tuning di sentence-biobert) che non inficiano l'identificazione del lavoro principale ma meritano un controllo finale prima della consegna della tesi.
