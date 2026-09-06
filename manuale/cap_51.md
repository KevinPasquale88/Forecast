# Capitolo 51 — Limiti metodologici del protocollo di valutazione

**Obiettivi del capitolo**
- Avere, in un solo capitolo, la sintesi organizzata dei tre limiti metodologici più rilevanti già incontrati separatamente nel libro.
- Sapere quale peso dare a ciascuno: quale è più grave, quale più facile da correggere.
- Collegare ogni limite a una proposta di correzione concreta, non solo alla sua diagnosi.

Questo capitolo non introduce fatti nuovi: raccoglie, con la disciplina critica che la Parte XI richiede, tre limiti già individuati nei capitoli precedenti, li pesa l'uno contro l'altro, e li collega a correzioni concrete (Parte XII).

## 51.1 Assenza di test set finale indipendente

**[Fatto]** `preprocessing.py:43` calcola un test set del 20% che non viene mai più usato (capitolo 21.1, capitolo 33.1). **[Interpretazione — gravità]** Fra i tre limiti di questo capitolo, è il più strutturale: non riguarda un dettaglio di implementazione ma l'intero disegno della valutazione. Il capitolo 47.3 ha reso concreto il suo costo con un numero preciso — un baseline sulla popolazione reale e sbilanciata di Diabetes130 raggiungerebbe 88.84%, un dato che nessuna misura di questo progetto conferma o smentisce direttamente, perché nessuna misura è mai stata condotta sulla distribuzione reale, solo su quella riequilibrata da SMOTENC. **[Interpretazione — correggibilità]** È anche, paradossalmente, il più facile da correggere in astratto: i dati del test set esistono già, calcolati e scartati; applicare i modelli già addestrati a quei dati richiederebbe modificare `preprocessing_data()` per restituire e salvare anche `X_test`/`y_test`, e una fase aggiuntiva che li usi (capitolo 55.1).

## 51.2 Soglia ottimizzata sullo stesso fold di validazione

**[Fatto]** La Formula 35.1 (capitolo 35.2) sceglie $\tau^\star$ massimizzando F1 su `y_val`, poi misura la prestazione sullo stesso `y_val`. **[Interpretazione — gravità]** È un ottimismo più contenuto del precedente: non tocca l'addestramento del modello (capitolo 33.3), solo la soglia — e il capitolo 34.3 ha già mostrato che l'AUC, l'unica metrica indipendente dalla soglia, non ne risente affatto. Riguarda solo accuratezza e F1, e solo nella misura in cui la soglia F1-ottima per fold si discosta da quella che si sceglierebbe su dati indipendenti. **[Interpretazione — correggibilità]** Facilmente corretto: la Formula 35.2 (un fold di calibrazione separato) richiederebbe solo una diversa suddivisione dei dati dentro il ciclo di `StratifiedKFold`, senza cambiare l'architettura della pipeline.

## 51.3 Il campionamento a 20.000 record di Diabetes130

**[Fatto]** `load_diabetes130(sample_size=20000)` (`function.py:116-132`, capitolo 30.1) usa un campione stratificato di un quinto delle 101.766 righe originali. **[Interpretazione — gravità]** Il più lieve dei tre: è una scelta dichiarata e motivata (tempi di esecuzione, capitolo 30.1), il campionamento è stratificato (preserva la proporzione di classe, capitolo 33.2), e con 20.000 righe il progetto ottiene comunque, dopo SMOTENC, un pool di 28.428 righe per la validazione (capitolo 43) — una dimensione ben più che sufficiente per le conclusioni statistiche del capitolo 45. **[Interpretazione — correggibilità]** Il più costoso da correggere in pratica: userebbe l'intero file, moltiplicando per cinque il tempo di generazione degli embedding per tutti e sette i modelli (capitolo 22), il passaggio più lento della pipeline.

## Una tabella di sintesi

| Limite | Gravità | Costo di correzione | Capitolo di riferimento |
|---|---|---|---|
| Test set mai usato | Alta (strutturale) | Basso | 21.1, 33.1, 47.3 |
| Soglia sul fold di validazione | Media (contenuta all'F1/accuratezza) | Basso | 23.2, 35.2 |
| Campionamento di Diabetes130 | Bassa (dichiarata, stratificata) | Alto | 30.1 |

> **ATTENZIONE —** questa tabella è la mia valutazione, motivata riga per riga sopra, non un fatto oggettivo misurabile con un solo numero: un revisore più severo potrebbe pesare diversamente la gravità del secondo limite, per esempio, se ritenesse che anche un ottimismo "contenuto" sia inaccettabile in un contesto clinico. È materiale da discutere, non da accettare passivamente in sede di tesi.

## Riepilogo

I tre limiti metodologici principali di questo progetto — test set mai usato, soglia ottimizzata sul fold di validazione, campionamento di Diabetes130 — hanno gravità e costo di correzione molto diversi fra loro. Il più grave (test set) è anche il più facile da correggere; il più lieve (campionamento) è il più costoso da correggere in pratica, richiedendo di rifare la fase più lenta della pipeline su cinque volte più dati.

## Domande di autoverifica

**1. Perché l'assenza di un test set finale indipendente è considerata, in questo capitolo, il limite più grave dei tre?**
Perché è strutturale, non un dettaglio di implementazione: significa che nessuna misura di questo progetto conferma le prestazioni sulla distribuzione reale e sbilanciata dei dati, solo su quella artificialmente riequilibrata da SMOTENC — un fatto reso concreto dal numero 88.84% del capitolo 47.3.

**2. Perché il limite della soglia ottimizzata sul fold di validazione non tocca l'AUC riportata nei capitoli 44-45?**
Perché l'AUC (capitolo 34.3) dipende solo dall'ordinamento dei punteggi di probabilità, non da una soglia specifica: la fuga di informazione riguarda solo la scelta di $\tau^\star$, che influenza esclusivamente le metriche calcolate su etichette già sogliate, cioè accuratezza e F1.

**3. Perché il campionamento di Diabetes130, pur essendo un limite reale, è valutato come il meno grave dei tre in questo capitolo?**
Perché è dichiarato esplicitamente e motivato da vincoli di tempo reali, il campionamento è stratificato (preserva la proporzione di classe), e il pool risultante dopo SMOTENC (28.428 righe) è comunque ampiamente sufficiente per le conclusioni statistiche già tratte nel capitolo 45.

> **MATERIALE PER LA TESI**
> 1. La tabella di sintesi con gravità e costo di correzione per ciascun limite — riusabile quasi direttamente come apertura della sezione "Discussione e limiti".
> 2. L'argomentazione sul perché la soglia ottimizzata non influenzi l'AUC — riusabile come precisazione tecnica che qualifica correttamente la portata di quel limite specifico.
> 3. Il riquadro Attenzione sulla soggettività della propria valutazione di gravità — riusabile come nota di onestà metodologica, utile in sede di discussione con la commissione.
