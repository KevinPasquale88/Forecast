# Capitolo 55 — Direzioni di sviluppo difendibili in sede di discussione

**Obiettivi del capitolo**
- Avere tre proposte di estensione concrete, ciascuna motivata da un limite già documentato in questo libro, non generiche.
- Sapere, per ciascuna, quale sforzo di implementazione richiederebbe e cosa dimostrerebbe se realizzata.
- Poter rispondere con sicurezza se un membro della commissione chiede "cosa faresti dopo?".

Ogni proposta di questo capitolo risponde a un limite specifico già identificato nel libro, con un rimando esatto — non è un elenco generico di "possibili miglioramenti futuri".

## 55.1 Il test set finale indipendente: la proposta che è già stata realizzata — e cosa apre

**[Fatto]** La prima proposta di questo capitolo, nella sua stesura originale, rispondeva al limite più grave individuato al capitolo 51.1: `X_test`/`y_test`, calcolati e mai usati. È stata realizzata, punto per punto, dai fix di revisione (`docs/CHANGES.md` §1): `preprocessing_data()` salva il test set imputato con le sole statistiche del training (esattamente l'attenzione anti-contaminazione che la proposta richiedeva, capitolo 33.3), `main.py` ne genera gli embedding, e la fase 7 (`holdout_evaluation.py`) riporta le metriche finali su dati mai toccati durante lo sviluppo. **[Fatto]** L'esito ha realizzato entrambi gli scenari che la proposta prospettava, uno per dataset: su Heart Disease le metriche holdout sono vicine (anzi leggermente superiori) a quelle di cross-validation — fiducia rafforzata; su Diabetes130 sono crollate al livello del caso (capitolo 45, Tabella 45.1bis) — il risultato negativo "altrettanto interessante, e più onesto di non verificarlo affatto".

**[Interpretazione]** Le direzioni che questa realizzazione apre, e che restano da fare: (1) trasformare la misura holdout singola in una stima con incertezza — bootstrap sui 184/4.000 casi di test, o split ripetuti con semi diversi (capitolo 43.3); (2) indagare *perché* il segnale di Diabetes130 non si trasferisce — per esempio confrontando la distribuzione degli score fra pool bilanciato e test reale, o provando feature aggiuntive (diagnosi ICD-9, farmaci) escluse dalla selezione del capitolo 30.2.

## 55.2 Un classificatore non lineare come confronto

**[Fatto]** Risponde al suggerimento tuttora presente nella sezione "Potential Improvements" del report (`generatereport.py:228`, "Introduce a non-linear classifier") e al posizionamento metodologico del capitolo 53.1 (linear probing come scelta specifica, non necessariamente ottimale in assoluto) — una scelta che i fix di revisione hanno deliberatamente lasciato invariata (`docs/CHANGES.md`, "What this branch deliberately does not change"). **Implementazione concreta**: sostituire, in una copia di `classification.py`, `LogisticRegression` con un `GradientBoostingClassifier` o `RandomForestClassifier` di scikit-learn (nessuna nuova dipendenza da aggiungere a `requirements.txt`, già presente nella stessa libreria) — a parità di ogni altro passaggio della pipeline (stessi embedding, stessa `StratifiedKFold`, stesso protocollo di soglia).

**[Interpretazione]** Cosa dimostrerebbe: se un classificatore non lineare non migliorasse sostanzialmente le prestazioni rispetto alla regressione logistica, sarebbe una prova indiretta che il segnale utile negli embedding è già ben rappresentabile linearmente — coerente con l'idea di linear probing del capitolo 53.1, e un argomento a favore della scelta del progetto originale. Se lo migliorasse sostanzialmente, indicherebbe che il progetto ha lasciato del segnale non sfruttato sul tavolo, particolarmente rilevante per Heart Disease dove il capitolo 32.3 ha già mostrato un regime `p > n` sfavorevole a un modello semplice quanto a uno complesso, in modi diversi.

> **ATTENZIONE —** questo confronto avrebbe senso solo se accompagnato dallo stesso rigore statistico già applicato in questo libro (bootstrap, test di significatività, capitolo 36-37): una singola cifra di accuratezza più alta per il classificatore non lineare, senza un intervallo di confidenza o un test di significatività, ripeterebbe esattamente l'errore di lettura "solo descrittiva" già criticato ai capitoli 44.3-45.2.

## 55.3 Calibrazione delle probabilità e reportistica generata dai dati

**[Fatto]** La stesura originale di questa proposta rispondeva a due limiti: la soglia F1-ottima ottimisticamente scelta (nel frattempo corretta con la fetta di calibrazione, capitolo 23.2 — "calibrazione" in un senso diverso da quello di questo paragrafo) e il testo statico del report (nel frattempo reso data-driven, capitolo 52.3). Restano due tasselli. **Implementazione concreta, parte 1 (calibrazione delle probabilità)**: `sklearn.calibration.CalibratedClassifierCV` avvolgerebbe il classificatore esistente per produrre probabilità meglio calibrate (nel senso tecnico: una probabilità stimata dello 0.7 dovrebbe corrispondere, su molti casi, a una frequenza osservata di positivi vicina al 70%) — una proprietà distinta dall'accuratezza o dall'AUC, tuttora mai verificata in questo progetto, e suggerita anche dal report stesso ("Apply probability calibration", `generatereport.py:229`). **Implementazione concreta, parte 2 (report)**: il test di coerenza automatico proposto al capitolo 52.3 — l'unico dei tre livelli di prevenzione non ancora implementato — che verifichi che ogni nome di modello citato da `_build_discussion()` corrisponda davvero alla sua posizione in classifica.

**[Interpretazione]** Cosa dimostrerebbe: la calibrazione risponde a una domanda diversa da quella già misurata (discriminazione fra classi) — se le probabilità stimate sono utilizzabili direttamente come stime di rischio (rilevante per un contesto clinico, capitolo 1.2), non solo come un punteggio da sogliare; sui dati holdout di Diabetes130, dove la discriminazione è quasi nulla, un'analisi di calibrazione renderebbe ancora più chiaro cosa il sistema può e non può offrire. Il test di coerenza completerebbe la prevenzione del difetto meglio documentato della storia del progetto (capitolo 52).

## Riepilogo

Tre direzioni di sviluppo, ciascuna ancorata a un limite specifico documentato. La prima — il test set finale indipendente — è stata realizzata dai fix di revisione, con esiti che validano Heart Disease e ridimensionano Diabetes130, e apre a sua volta due seguiti concreti (incertezza sulla misura holdout, indagine sul segnale di Diabetes130). Le altre due restano da fare: un classificatore non lineare come termine di paragone per la scelta di linear probing, e la calibrazione delle probabilità più il test di coerenza sul report. Nessuna richiede nuove dipendenze esterne al progetto; tutte sono realizzabili con le competenze già trattate in questo libro.

## Domande di autoverifica

**1. Perché la realizzazione del test set indipendente ha richiesto di imputarlo con le statistiche del training set, non le proprie?**
Perché altrimenti si sarebbe introdotta esattamente la contaminazione fra training e test già evitata altrove nel progetto (capitolo 33.3): usare informazione del test set per calcolare i parametri di imputazione violerebbe l'indipendenza che rende il test set utile in primo luogo. È il motivo per cui il fix ha separato `fit_imputation_values()` da `apply_imputation()` (capitolo 21.2).

**2. Se un classificatore non lineare non migliorasse sostanzialmente le prestazioni rispetto alla regressione logistica, cosa suggerirebbe questo risultato?**
Che il segnale utile presente negli embedding è già ben rappresentabile con un confine di decisione lineare — un argomento indiretto a favore della scelta di linear probing fatta dal progetto originale, non solo un risultato "negativo".

**3. Perché la calibrazione delle probabilità misura qualcosa di diverso dall'accuratezza o dall'AUC già riportate nei capitoli 44-45?**
Perché riguarda se il valore numerico della probabilità stimata corrisponde davvero a una frequenza osservata coerente (una probabilità dello 0.7 dovrebbe verificarsi circa il 70% delle volte), una proprietà indipendente dalla capacità del modello di ordinare correttamente i casi (AUC) o di classificarli correttamente a una soglia data (accuratezza, F1).

> **MATERIALE PER LA TESI**
> 1. Le tre proposte con implementazione concreta e collegamento esplicito al limite che risolvono — riusabili integralmente come sezione "Lavori futuri" della tesi, già argomentate e non generiche.
> 2. L'osservazione sul rigore statistico necessario per un confronto onesto con un classificatore non lineare — riusabile come promemoria metodologico per chi realizzasse effettivamente questo confronto.
> 3. La distinzione fra calibrazione e discriminazione come proprietà distinte di un classificatore — riusabile come precisazione tecnica utile in una sezione che discuta l'utilità clinica reale del sistema.
