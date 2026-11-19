# Capitolo 43 — Protocollo sperimentale

**Obiettivi del capitolo**

- Sapere con precisione quali numeri, in questa parte del libro, provengono da un'esecuzione già presente nel repository e quali da un calcolo eseguito appositamente per questo libro.
- Avere i comandi esatti per riprodurre ogni cifra citata nei capitoli 44-47.
- Conoscere i limiti del protocollo sperimentale prima di leggerne i risultati, non dopo.

## 43.1 Cosa è stato eseguito da chi, e quando

**[Fatto]** Le tabelle riassuntive dei capitoli 44 e 45 provengono da `datas/heart_disease/reports/report.md` e `datas/diabetes130/reports/report.md`, tracciati nel repository e generati — secondo la data riportata in cima a ciascun file — il 2026-09-06 (alle 12:53 Heart Disease, alle 19:48 Diabetes130), da esecuzioni complete della pipeline **corretta**: quella successiva ai fix di qualità documentati in `docs/CHANGES.md` (test set usato, soglia calibrata, indicatori di mancanza, report data-driven, correzione Benjamini-Hochberg). I commit corrispondenti ("run pipeline heart disease", "run pipeline diabetes139") tracciano l'intero albero di output di ciascuna esecuzione. **[Decisione dichiarata]** Il libro usa questi risultati tracciati, senza rilanciare `python main.py` durante la stesura: rieseguire l'intera pipeline sovrascriverebbe file già tracciati da git senza garanzia di produrre numeri identici, data la non completa determinismo di alcune componenti (per esempio l'inferenza dei modelli via Ollama, capitolo 39.3 sulla mappa dei semi casuali, che copre i semi del progetto ma non necessariamente ogni sorgente di variabilità del server Ollama stesso). Una prima stesura di questa parte usava i numeri di un'esecuzione precedente ai fix (datata 2026-08-02); tutte le tabelle sono state aggiornate ai risultati della pipeline corretta.

## 43.2 Comandi eseguiti in questa sessione (con output reale) vs. comandi da eseguire tu

**[Fatto]** Non tutti i numeri di questa parte provengono dal 2026-08-02: alcuni sono stati calcolati appositamente durante la scrittura di questo libro, con comandi eseguiti realmente e il cui output è riportato per intero dove compaiono. Per trasparenza, l'elenco completo:

| Calcolo | Comando (sintetizzato) | Dove compare |
|---|---|---|
| Sbilanciamento reale delle classi (entrambi i dataset) | Script Python su file grezzi, `pandas` | Capitolo 4.2 |
| Dimensioni per file sorgente dei valori mancanti (Heart Disease) | Script Python su 4 file `.data` | Capitolo 29.2, 29.3 |
| Missingness di `max_glu_serum`/`A1Cresult` (Diabetes130) | Script Python su `diabetic_data.csv` | Capitolo 30.2 |
| Dimensioni degli embedding per tutti e 7 i modelli | `np.load(...).shape` su file già presenti | Capitolo 32.3, 39.1 |
| Rapporto dimensione-embedding/dimensione-training-set | Calcolo aritmetico su dimensioni verificate | Capitolo 32.3 |
| Verifica esistenza `e5_large`/`gte_large` per Diabetes130 | `os.path.exists(...)` | Capitolo 32.3 |
| Baseline a maggioranza e casuale stratificato | `sklearn.dummy.DummyClassifier` su `y_true.npy` già presenti | Capitolo 47 |

**[Fatto]** Ogni altro numero — le tabelle di accuratezza/F1/AUC dei capitoli 44-45, le metriche holdout, i tassi di errore del capitolo 46, i valori dei tre test statistici — proviene direttamente dai due `report.md` e dai CSV già presenti in `datas/`, non da un calcolo di questa sessione. **[Fatto]** L'elenco completo dei file consultati per questa parte: `datas/{heart_disease,diabetes130}/reports/report.md`, `.../results/encoder_comparison_summary.csv`, `.../results/holdout_evaluation.csv`, `.../results/error_summary.csv`, `.../results/hardest_cases.csv`, `.../results/{wilcoxon,ttest,delong}_comparison.csv`.

> **PROVA TU —** rigenera tu stesso questi risultati sul tuo ambiente, seguendo l'installazione della Parte III, con:
> ```bash
> source env/bin/activate
> python main.py --dataset heart_disease
> python main.py --dataset diabetes130
> ```
> Confronta le tue tabelle con quelle dei capitoli 44-45. Se differiscono di più di qualche millesimo, è materiale diretto per una sezione della tesi sulla riproducibilità: i semi casuali del capitolo 39.3 dovrebbero garantire risultati identici per tutte le componenti seedate, ma non è garantito che coprano ogni sorgente di variabilità (per esempio versioni diverse dei modelli scaricati da Ollama nel frattempo).

## 43.3 Limiti dichiarati del protocollo

**[Fatto]** Questo protocollo sperimentale eredita, senza eccezione, tutti i limiti metodologici già individuati nei capitoli precedenti — è bene elencarli qui in un solo posto, prima di leggere i risultati:

- Le metriche di cross-validation (le tabelle principali dei capitoli 44-45) sono misurate sul pool bilanciato da SMOTE, non sulla distribuzione di classe reale: la stima su quella distribuzione è fornita solo dalla valutazione holdout, che consiste in una singola misura su 184 (Heart Disease) o 4.000 (Diabetes130) casi, senza intervallo di confidenza bootstrap.
- Il test set holdout è stato usato una sola volta e dopo ogni decisione di sviluppo, come deve essere — ma resta un solo split (seed 42), non una stima su split ripetuti.
- Il rapporto dimensione-embedding/dimensione-training-set è sfavorevole per due modelli su Heart Disease (capitolo 32.3).
- Diabetes130 usa un campione di 20.000 righe su 101.766 disponibili (capitolo 30.1).
- I due file di embedding a 1024 dimensioni del training di Diabetes130 sono esclusi da git per dimensione (`.gitignore`): esistono su disco dopo la riesecuzione, ma chi clona il repository deve rigenerarli (capitolo 32.3).

**[Fatto]** Tre limiti presenti in una prima versione di questo elenco non esistono più nel codice attuale, e la loro storia è documentata in `docs/CHANGES.md`: l'assenza di un test set finale indipendente (oggi c'è, fase 7), la soglia ottimizzata sullo stesso fold misurato (oggi calibrata su una fetta separata), e l'assenza di correzione per confronti multipli (oggi Benjamini-Hochberg accanto ai p-value grezzi).

**[Interpretazione]** Nessuno dei limiti rimasti, singolarmente, invalida i risultati: sono tutti limiti di grado, non di natura — il campionamento di Diabetes130 è motivato da vincoli di tempo reali, non arbitrario; un singolo split holdout è comunque una stima onesta, solo meno stabile di split ripetuti. Ma vanno tenuti presenti leggendo ogni tabella dei capitoli 44-47, non solo alla fine nella Parte XI.

## Riepilogo

I risultati di questa parte combinano numeri già tracciati nel repository (le tabelle principali di accuratezza/F1/AUC, le metriche holdout, i tassi di errore, i test statistici, provenienti dalle esecuzioni del 2026-09-06 con la pipeline corretta) e numeri calcolati appositamente durante la scrittura di questo libro (sbilanciamento reale delle classi, missingness per centro clinico, dimensioni degli embedding, baseline banale) — con la provenienza di ciascuno dichiarata esplicitamente. Il protocollo eredita i limiti metodologici residui elencati qui come promemoria; tre limiti storici (test set inutilizzato, soglia sul fold misurato, assenza di correzione per confronti multipli) sono stati corretti nel codice prima di queste esecuzioni.

## Domande di autoverifica

**1. Le tabelle di accuratezza/F1/AUC dei capitoli 44-45 provengono da un'esecuzione fatta durante la scrittura di questo libro?**
No: provengono da `datas/{heart_disease,diabetes130}/reports/report.md`, tracciati nel repository e generati il 2026-09-06 dalle esecuzioni complete della pipeline corretta (commit "run pipeline heart disease" e "run pipeline diabetes139") — una scelta dichiarata esplicitamente, non un'omissione.

**2. Quali numeri di questa parte, invece, sono stati calcolati appositamente per questo libro?**
Lo sbilanciamento reale delle classi, la scomposizione della missingness per centro clinico e per feature, le dimensioni degli embedding e il rapporto parametri/campioni, e il calcolo del modello di riferimento banale (capitolo 47) — tutti con il comando usato dichiarato esplicitamente dove compaiono.

**3. Perché nessuno dei limiti elencati al paragrafo 43.3 invalida da solo i risultati, pur meritando attenzione?**
Perché sono limiti di grado — pratiche meno rigorose della migliore prassi possibile, ma comunque comuni e ragionevoli nel settore — non errori che rendono i numeri privi di significato. Vanno interpretati con la giusta cautela, non ignorati né considerati fatali.

> **MATERIALE PER LA TESI**
> 1. La tabella di provenienza dei calcoli (§43.2), con il comando sintetizzato per ciascuno — riusabile integralmente come dichiarazione di trasparenza metodologica in "Materiali e metodi".
> 2. L'elenco dei limiti dichiarati, raccolto in un solo punto prima dei risultati — riusabile come premessa esplicita alla sezione "Risultati" della tesi, per calibrare correttamente le aspettative del lettore.
> 3. Il comando di riproduzione completo (§43.2, riquadro Prova tu) — riusabile in un'appendice sulla riproducibilità sperimentale.
