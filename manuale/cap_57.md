# Capitolo 57 — Cosa è già pronto e cosa manca ancora

**Obiettivi del capitolo**
- Avere un inventario preciso di ogni figura, tabella e formula numerata già pronta in questo libro.
- Sapere esattamente quali misure richiederebbero un nuovo esperimento, con la procedura per ottenerle.
- Avere l'elenco completo dei riferimenti bibliografici ancora da verificare prima di poterli citare in tesi.

## 57.1 Figure e tabelle riutilizzabili, capitolo per capitolo

**[Fatto]** Elenco delle figure Mermaid numerate: Figura 2.1 (ciclo addestramento/validazione/inferenza), Figura 3.1 (catena tabellare→testo→embedding→classificazione), Figura 12.1 (thread pool e semaforo Ollama), Figura 17.1 (architettura completa), Figura 18.1 (sequenza di un'esecuzione), Figura 54.1 (sequenza di inferenza del chatbot).

**[Fatto]** Elenco delle tabelle principali con dati reali: la tabella di corrispondenza Java→Python (capitolo 13.1), lo schema delle 14 feature di Heart Disease (capitolo 29.2), lo schema delle 19 feature di Diabetes130 (capitolo 30.2), la tabella completa degli iperparametri (capitolo 39.1), le Tabelle 44.1 e 45.1 (risultati completi con IC per entrambi i dataset), la Tabella 46.1 (tassi di errore), la tabella dei limiti con gravità e correggibilità (capitolo 51).

**[Fatto]** Formule numerate: 25.1 (deviazione di feature), 32.1-32.2 (regressione logistica), 33.1 (k-fold), 34.1-34.3 (le tre metriche), 35.1-35.2 (soglia F1-ottima, confronto rigoroso), 36.1-36.4 (bootstrap), 37.1-37.3 (i tre test statistici) — l'elenco completo, con la spiegazione di ogni simbolo, è raccolto in Appendice C.

## 57.2 Misure ancora da produrre, con procedura

**[Fatto]** Tre misure, già proposte nei capitoli precedenti, richiederebbero un nuovo esperimento non condotto in questo libro:

1. **Prestazioni sul test set finale indipendente** (capitolo 55.1). Procedura: modificare `preprocessing_data()` per restituire anche `X_test`/`y_test`; imputare il test set con le statistiche del training set; generare embedding per il test set con i sette modelli; applicare i classificatori già addestrati (senza riaddestrarli) e calcolare le tre metriche.
2. **Confronto con un classificatore non lineare** (capitolo 55.2). Procedura: sostituire `LogisticRegression` con `GradientBoostingClassifier` in una copia di `classification.py`, a parità di ogni altro passaggio; ripetere bootstrap e test statistici sui nuovi risultati; confrontare con le Tabelle 44.1-45.1 esistenti.
3. **Entità precisa dell'ottimismo da soglia** (esercizio del capitolo 35.3). Procedura: per ciascun modello già presente in `datas/`, ricalcolare F1 con $\tau=0.5$ fisso usando i file `{model}_y_true.npy`/`{model}_y_score.npy` già disponibili, e confrontare con l'F1 riportato nelle tabelle esistenti — non richiede nemmeno riaddestrare nulla, solo ricalcolare una metrica su dati già presenti.

> **PROVA TU —** la terza misura è realizzabile in pochi minuti con i dati già nel repository, senza Ollama né Hugging Face. È il modo più rapido di trasformare uno dei limiti metodologici di questo libro (capitolo 35.3, capitolo 51.2) in un numero concreto per la tua tesi.

## 57.3 Riferimenti bibliografici da recuperare e verificare

**[Fatto]** Quattro riferimenti sono già verificati con identificativo concreto (DOI), citati direttamente da `docs/DATASET.md` e già usati nei capitoli 29.1 e 30.1: Janosi et al. (1988, Heart Disease, DOI 10.24432/C52P4W), Detrano et al. (1989, American Journal of Cardiology), Strack et al. (2014, Diabetes130, DOI 10.24432/C5230J), Strack et al. (2014, BioMed Research International).

**[Fatto]** Marcati `[DA VERIFICARE]` in questo libro, da cercare e confermare prima di citarli in tesi (Appendice D ne riporta lo stato dopo la verifica con WebSearch/WebFetch, capitolo di questo libro): il paper originale di E5 (Wang et al., capitolo 5.2), il paper originale di GTE (Li et al., capitolo 5.2), Hastie/Tibshirani/Friedman su bias-variance (capitolo 2.3), DeLong/DeLong/Clarke-Pearson (1988, capitolo 37.3), McInnes/Healy/Melville su UMAP (capitolo 38.2).

## Riepilogo

Questo libro fornisce sei figure Mermaid numerate, oltre dieci tabelle con dati reali, e diciassette formule numerate, tutte pronte per l'uso diretto in tesi. Tre misure aggiuntive richiederebbero un nuovo esperimento, con procedura già delineata per ciascuna — una realizzabile in pochi minuti senza nuovi calcoli pesanti. Cinque riferimenti bibliografici restano da verificare con una fonte esterna prima di poter essere citati con sicurezza.

## Domande di autoverifica

**1. Quale delle tre misure ancora da produrre è realizzabile senza generare nuovi embedding o riaddestrare alcun modello?**
Il ricalcolo dell'F1 con soglia fissa $\tau=0.5$ sui dati di predizione già salvati (`y_true.npy`/`y_score.npy`): richiede solo di ricalcolare una metrica su file già presenti nel repository.

**2. Quanti riferimenti bibliografici sono già verificati con un identificativo concreto in questo libro, e quanti restano da verificare?**
Quattro sono già verificati con DOI (i due dataset e i loro paper originali); cinque restano marcati `[DA VERIFICARE]` e vanno confermati con una ricerca esterna prima di essere citati.

**3. Perché nessuna delle tabelle o figure di questo libro dovrebbe essere incollata nella tesi senza adattamento?**
Perché questo libro è materiale di riferimento, non testo da copiare: ogni tabella o figura va integrata nel contesto specifico della tesi, con la propria numerazione, didascalia e discussione — l'elenco di questo capitolo serve a sapere dove trovarle, non a sostituire la scrittura della tesi stessa.

> **MATERIALE PER LA TESI**
> 1. L'inventario completo di figure, tabelle e formule — riusabile come checklist per assicurarsi di non dimenticare materiale già pronto durante la stesura.
> 2. Le tre misure ancora da produrre con procedura dettagliata — riusabile direttamente come piano di lavoro per un contributo sperimentale originale nella tesi.
> 3. L'elenco dei riferimenti da verificare, con quelli già confermati distinti chiaramente — riusabile come lista di controllo prima della consegna finale della bibliografia.
