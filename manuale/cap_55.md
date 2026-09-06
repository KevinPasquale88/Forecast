# Capitolo 55 — Direzioni di sviluppo difendibili in sede di discussione

**Obiettivi del capitolo**
- Avere tre proposte di estensione concrete, ciascuna motivata da un limite già documentato in questo libro, non generiche.
- Sapere, per ciascuna, quale sforzo di implementazione richiederebbe e cosa dimostrerebbe se realizzata.
- Poter rispondere con sicurezza se un membro della commissione chiede "cosa faresti dopo?".

Ogni proposta di questo capitolo risponde a un limite specifico già identificato nel libro, con un rimando esatto — non è un elenco generico di "possibili miglioramenti futuri".

## 55.1 Aggiungere un test set finale indipendente

**[Fatto]** Risponde direttamente al limite più grave individuato al capitolo 51.1: `X_test`/`y_test`, già calcolati da `preprocessing.py:43` e mai usati (capitolo 21.1). **Implementazione concreta**: modificare `preprocessing_data()` per restituire anche `X_test`/`y_test` (imputati con le statistiche calcolate sul training set, mai su quelle del test — un'attenzione necessaria per non introdurre la contaminazione già evitata altrove, capitolo 33.3); aggiungere una fase 8 (capitolo 28.3 ha già mostrato come) che generi embedding per il test set con gli stessi sette modelli, applichi i classificatori già addestrati (senza riaddestrarli), e riporti le metriche finali su questo insieme mai toccato durante lo sviluppo.

**[Interpretazione]** Cosa dimostrerebbe: se le metriche sul test set indipendente fossero vicine a quelle di cross-validation già riportate (capitoli 44-45), rafforzerebbe sostanzialmente la fiducia nei risultati esistenti. Se fossero sensibilmente più basse, confermerebbe che la validazione incrociata aveva un margine di ottimismo non trascurabile — un risultato negativo altrettanto interessante, e più onesto di non verificarlo affatto.

## 55.2 Un classificatore non lineare come confronto

**[Fatto]** Risponde al suggerimento già presente, ma mai realizzato, nel testo statico di `generatereport.py:221` ("Introduce a non-linear classifier") e al posizionamento metodologico del capitolo 53.1 (linear probing come scelta specifica, non necessariamente ottimale in assoluto). **Implementazione concreta**: sostituire, in una copia di `classification.py`, `LogisticRegression` con un `GradientBoostingClassifier` o `RandomForestClassifier` di scikit-learn (nessuna nuova dipendenza da aggiungere a `requirements.txt`, già presente nella stessa libreria) — a parità di ogni altro passaggio della pipeline (stessi embedding, stessa `StratifiedKFold`, stesso protocollo di soglia).

**[Interpretazione]** Cosa dimostrerebbe: se un classificatore non lineare non migliorasse sostanzialmente le prestazioni rispetto alla regressione logistica, sarebbe una prova indiretta che il segnale utile negli embedding è già ben rappresentabile linearmente — coerente con l'idea di linear probing del capitolo 53.1, e un argomento a favore della scelta del progetto originale. Se lo migliorasse sostanzialmente, indicherebbe che il progetto ha lasciato del segnale non sfruttato sul tavolo, particolarmente rilevante per Heart Disease dove il capitolo 32.3 ha già mostrato un regime `p > n` sfavorevole a un modello semplice quanto a uno complesso, in modi diversi.

> **ATTENZIONE —** questo confronto avrebbe senso solo se accompagnato dallo stesso rigore statistico già applicato in questo libro (bootstrap, test di significatività, capitolo 36-37): una singola cifra di accuratezza più alta per il classificatore non lineare, senza un intervallo di confidenza o un test di significatività, ripeterebbe esattamente l'errore di lettura "solo descrittiva" già criticato ai capitoli 44.3-45.2.

## 55.3 Calibrazione delle probabilità e reportistica generata dai dati

**[Fatto]** Risponde a due limiti distinti trattati in dettaglio altrove: la soglia F1-ottima ottimisticamente calibrata (capitolo 35.3, capitolo 51.2), e il testo statico del report (capitolo 52). **Implementazione concreta, parte 1 (calibrazione)**: `sklearn.calibration.CalibratedClassifierCV` avvolgerebbe il classificatore esistente per produrre probabilità meglio calibrate (nel senso tecnico: una probabilità stimata dello 0.7 dovrebbe corrispondere, su molti casi, a una frequenza osservata di positivi vicina al 70%) — una proprietà distinta dall'accuratezza o dall'AUC, mai verificata in questo progetto. **Implementazione concreta, parte 2 (report)**: la correzione minima già proposta al capitolo 27.3 e al capitolo 52.3, con l'aggiunta di un test di coerenza automatico che verifichi che ogni nome di modello citato nel testo narrativo corrisponda davvero alla sua posizione in classifica.

**[Interpretazione]** Cosa dimostrerebbe: la calibrazione risponde a una domanda diversa da quella già misurata (discriminazione fra classi) — se le probabilità stimate sono utilizzabili direttamente come stime di rischio (rilevante per un contesto clinico, capitolo 1.2), non solo come un punteggio da sogliare. La correzione del report eliminerebbe, con lo sforzo minimo possibile, il singolo difetto più concreto e meglio documentato di tutto il progetto (capitolo 52).

## Riepilogo

Tre direzioni di sviluppo, ciascuna ancorata a un limite specifico già documentato: un test set finale indipendente per validare la stima di generalizzazione oltre la cross-validation; un classificatore non lineare come termine di paragone per la scelta di linear probing; calibrazione delle probabilità e un report generato dai dati, invece che scritto a priori. Nessuna richiede nuove dipendenze esterne al progetto; tutte sono realizzabili con le competenze già trattate in questo libro.

## Domande di autoverifica

**1. Perché aggiungere un test set finale indipendente richiederebbe imputare il test set con le statistiche del training set, non le proprie?**
Perché altrimenti si introdurrebbe esattamente il tipo di contaminazione fra training e test già evitato altrove nel progetto (capitolo 33.3): usare informazione del test set per calcolare i parametri di imputazione violerebbe l'indipendenza che rende il test set utile in primo luogo.

**2. Se un classificatore non lineare non migliorasse sostanzialmente le prestazioni rispetto alla regressione logistica, cosa suggerirebbe questo risultato?**
Che il segnale utile presente negli embedding è già ben rappresentabile con un confine di decisione lineare — un argomento indiretto a favore della scelta di linear probing fatta dal progetto originale, non solo un risultato "negativo".

**3. Perché la calibrazione delle probabilità misura qualcosa di diverso dall'accuratezza o dall'AUC già riportate nei capitoli 44-45?**
Perché riguarda se il valore numerico della probabilità stimata corrisponde davvero a una frequenza osservata coerente (una probabilità dello 0.7 dovrebbe verificarsi circa il 70% delle volte), una proprietà indipendente dalla capacità del modello di ordinare correttamente i casi (AUC) o di classificarli correttamente a una soglia data (accuratezza, F1).

> **MATERIALE PER LA TESI**
> 1. Le tre proposte con implementazione concreta e collegamento esplicito al limite che risolvono — riusabili integralmente come sezione "Lavori futuri" della tesi, già argomentate e non generiche.
> 2. L'osservazione sul rigore statistico necessario per un confronto onesto con un classificatore non lineare — riusabile come promemoria metodologico per chi realizzasse effettivamente questo confronto.
> 3. La distinzione fra calibrazione e discriminazione come proprietà distinte di un classificatore — riusabile come precisazione tecnica utile in una sezione che discuta l'utilità clinica reale del sistema.
