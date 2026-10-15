# Capitolo 51 — Limiti metodologici del protocollo di valutazione

**Obiettivi del capitolo**
- Avere, in un solo capitolo, la sintesi organizzata dei tre limiti metodologici più rilevanti individuati durante l'analisi del progetto — due dei quali oggi corretti nel codice.
- Sapere quale peso dare a ciascuno: quale era più grave, cosa ha rivelato la sua correzione, cosa resta aperto.
- Collegare ogni limite alla sua storia completa: diagnosi, correzione (dove avvenuta), e conseguenze misurate.

Questo capitolo non introduce fatti nuovi: raccoglie, con la disciplina critica che la Parte XI richiede, tre limiti già individuati nei capitoli precedenti. Per due di essi la storia si è chiusa nel modo migliore possibile per una tesi: individuati dall'analisi, corretti nel codice (`docs/CHANGES.md`), e ri-misurati con la pipeline corretta — con esiti in un caso rassicuranti, nell'altro rivelatori.

## 51.1 Il test set calcolato e mai usato — individuato, corretto, e la correzione ha cambiato le conclusioni

**[Fatto]** Per gran parte della storia del progetto, `preprocessing.py` calcolava un test set del 20% che non veniva mai più usato (capitolo 21.1, capitolo 33.1). **[Interpretazione — gravità]** Fra i tre limiti di questo capitolo, era il più strutturale: non riguardava un dettaglio di implementazione ma l'intero disegno della valutazione — nessuna misura del progetto era mai stata condotta sulla distribuzione reale dei dati, solo su quella riequilibrata da SMOTENC. **[Fatto — correzione]** Il fix (`docs/CHANGES.md` §1) ha seguito esattamente la strada che questa analisi aveva indicato: il test set è oggi imputato con statistiche del solo training, salvato, embeddato separatamente, e valutato dalla fase 7 (`holdout_evaluation.py`).

**[Fatto — cosa ha rivelato]** La correzione non è stata un rito formale: ha cambiato le conclusioni. Su Heart Disease l'holdout ha **confermato** la validazione incrociata (AUC 0.87-0.92 sul test set, capitolo 44) — il sistema lì generalizza davvero. Su Diabetes130 l'ha **smentita nel punto che conta**: AUC 0.48-0.55 e accuratezze 0.40-0.50 sulla distribuzione reale (capitolo 45, Tabella 45.1bis), contro l'88.84% del baseline banale a maggioranza — il vantaggio misurato sul pool bilanciato non si trasferisce alla popolazione vera. È la dimostrazione più concreta possibile del perché questo limite fosse il più grave: finché il test set restava inutilizzato, questa differenza fra i due dataset era semplicemente invisibile.

## 51.2 La soglia ottimizzata sullo stesso fold — individuata e corretta

**[Fatto]** In una versione precedente, la soglia $\tau^\star$ era scelta massimizzando F1 su `y_val`, poi la prestazione era misurata sullo stesso `y_val` (Formula 35.2, capitolo 35.3). **[Interpretazione — gravità]** Era un ottimismo più contenuto del precedente: non toccava l'addestramento del modello (capitolo 33.3), solo la soglia — e l'AUC, l'unica metrica indipendente dalla soglia (capitolo 34.3), non ne risentiva affatto. Riguardava solo accuratezza e F1. **[Fatto — correzione]** Il fix (`docs/CHANGES.md` §4) ha introdotto la fetta di calibrazione: ogni fold divide la propria partizione di training 80/20, allena sull'80% e sceglie la soglia sul 20%, mai su `y_val` (capitolo 23.2). Il prezzo — un po' meno dati di addestramento per fold — è dichiarato nel codice stesso. **[Fatto]** Coerentemente con la diagnosi "ottimismo contenuto", le metriche della pipeline corretta sono leggermente più basse di quelle pre-fix (per esempio, l'accuratezza migliore su Heart Disease è passata da 0.8207 a 0.7936): la differenza è dell'ordine di 1-3 punti, il segno atteso di un ottimismo rimosso, non di un comportamento stravolto.

## 51.3 Il campionamento a 20.000 record di Diabetes130 — il limite che resta

**[Fatto]** `load_diabetes130(sample_size=20000)` (`function.py:116-132`, capitolo 30.1) usa un campione stratificato di un quinto delle 101.766 righe originali — invariato anche dopo i fix, per scelta dichiarata (`docs/CHANGES.md`, sezione "What this branch deliberately does not change"). **[Interpretazione — gravità]** Il più lieve dei tre: è una scelta dichiarata e motivata (tempi di esecuzione, capitolo 30.1), il campionamento è stratificato (preserva la proporzione di classe, capitolo 33.2), e con 20.000 righe il progetto ottiene comunque, dopo SMOTENC, un pool di 28.428 righe per la validazione (capitolo 43) — una dimensione ben più che sufficiente per le conclusioni statistiche del capitolo 45. **[Interpretazione — correggibilità]** Il più costoso da correggere in pratica: usare l'intero file moltiplicherebbe per cinque il tempo di generazione degli embedding per tutti e sette i modelli (capitolo 22), il passaggio più lento della pipeline. Alla luce dei risultati holdout del capitolo 45, peraltro, è dubbio che sia la correzione a più alto valore: il problema di Diabetes130 non sembra la quantità di dati, ma il segnale che le 19 feature scelte portano sul compito reale.

## Una tabella di sintesi

| Limite | Gravità (quando presente) | Stato | Capitolo di riferimento |
|---|---|---|---|
| Test set mai usato | Alta (strutturale) | **Corretto** — la fase holdout ha confermato Heart Disease e ridimensionato Diabetes130 | 21.1, 33.1, 45, 47.3 |
| Soglia sul fold di validazione | Media (contenuta a F1/accuratezza) | **Corretto** — fetta di calibrazione; metriche più basse di 1-3 punti, come atteso | 23.2, 35.3 |
| Campionamento di Diabetes130 | Bassa (dichiarata, stratificata) | Aperto (scelta consapevole) | 30.1 |

> **ATTENZIONE —** questa tabella è la mia valutazione, motivata riga per riga sopra, non un fatto oggettivo misurabile con un solo numero: un revisore più severo potrebbe pesare diversamente la gravità del secondo limite, per esempio, se ritenesse che anche un ottimismo "contenuto" fosse inaccettabile in un contesto clinico. È materiale da discutere, non da accettare passivamente in sede di tesi. E la correzione dei primi due limiti non chiude la discussione: la valutazione holdout resta una singola misura su un singolo split (capitolo 43.3), e le nuove domande aperte da Diabetes130 (perché il segnale non si trasferisce?) sono materiale per la Parte XII.

## Riepilogo

Dei tre limiti metodologici principali individuati in questo progetto, due — il test set mai usato e la soglia ottimizzata sul fold di validazione — sono stati corretti nel codice, e la correzione ha prodotto esattamente ciò che una buona metodologia promette: su Heart Disease una conferma indipendente, su Diabetes130 la scoperta che il vantaggio misurato sul pool bilanciato non si trasferisce alla popolazione reale, e metriche di validazione leggermente più basse coerenti con la rimozione di un ottimismo noto. Il terzo limite (campionamento di Diabetes130) resta, per scelta dichiarata, ed è il meno grave e il più costoso da correggere.

## Domande di autoverifica

**1. Perché l'assenza di un test set finale indipendente era considerata il limite più grave dei tre, e cosa lo ha confermato?**
Perché era strutturale: nessuna misura del progetto riguardava la distribuzione reale dei dati. La sua correzione lo ha confermato nel modo più concreto: la valutazione holdout ha rivelato che su Diabetes130 le prestazioni reali sono vicine al caso (AUC 0.48-0.55), un fatto che l'intera valutazione precedente non poteva vedere — mentre su Heart Disease ha confermato la validità della stima incrociata.

**2. Perché il limite della soglia ottimizzata sul fold di validazione non toccava l'AUC riportata nei capitoli 44-45?**
Perché l'AUC (capitolo 34.3) dipende solo dall'ordinamento dei punteggi di probabilità, non da una soglia specifica: la fuga di informazione riguardava solo la scelta di $\tau^\star$, che influenza esclusivamente le metriche calcolate su etichette già sogliate, cioè accuratezza e F1 — ed è coerente che, dopo il fix, siano proprio accuratezza e F1 a essere leggermente più basse.

**3. Perché il campionamento di Diabetes130, pur essendo un limite reale e tuttora presente, è valutato come il meno grave dei tre?**
Perché è dichiarato esplicitamente e motivato da vincoli di tempo reali, il campionamento è stratificato (preserva la proporzione di classe), e il pool risultante dopo SMOTENC (28.428 righe) è ampiamente sufficiente per le conclusioni statistiche del capitolo 45 — e i risultati holdout suggeriscono che il collo di bottiglia su quel dataset sia il segnale delle feature, non la quantità di righe.

> **MATERIALE PER LA TESI**
> 1. La tabella di sintesi con gravità e stato di ciascun limite — riusabile quasi direttamente come apertura della sezione "Discussione e limiti", con il valore aggiunto della storia diagnosi → correzione → ri-misura.
> 2. Il confronto pre/post-fix delle metriche (leggermente più basse dopo la rimozione dell'ottimismo della soglia) e il divario cross-validation/holdout su Diabetes130 — riusabili come evidenza quantitativa che le correzioni metodologiche hanno conseguenze misurabili.
> 3. Il riquadro Attenzione sulla soggettività della propria valutazione di gravità — riusabile come nota di onestà metodologica, utile in sede di discussione con la commissione.
