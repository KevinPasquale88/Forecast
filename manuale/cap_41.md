# Capitolo 41 — Caso d'uso 2: `python main.py --dataset diabetes130` e le differenze che contano

**Obiettivi del capitolo**

- Vedere le stesse sette fasi applicate a un dataset di scala completamente diversa.
- Avere un'ipotesi motivata, non solo un'osservazione, sul perché i punteggi assoluti sono più bassi qui che su Heart Disease.
- Verificare concretamente che le due esecuzioni non si sono mai toccate a vicenda.

## 41.1 Stesse fasi, numeri diversi

**[Fatto]** `python main.py --dataset diabetes130` attraversa esattamente le stesse otto tappe del capitolo 40, con numeri molto diversi: 101.766 righe grezze campionate a 20.000 (capitolo 30.1), split 80/20 (16.000 di training, 4.000 di test — anche qui mai più usato), SMOTENC che porta il training pool a **28.428 righe** (verificato caricando `bioclinicalbert_embeddings.npy`, capitolo 32.3) — un salto molto più grande di quello visto per Heart Disease (736→814), coerente con lo sbilanciamento di partenza molto più marcato (11.16% di classe positiva, capitolo 4.2, contro il quasi-equilibrio di Heart Disease).

**[Fatto]** La tabella riassuntiva reale, da `datas/diabetes130/reports/report.md` (già presente nel repository):

| Modello | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---|---|
| sentence-biobert | 0.6832 | 0.6715 | 0.7678 |
| bioclinicalbert | 0.6753 | 0.6655 | 0.7575 |
| pubmedbert | 0.6628 | 0.6466 | **0.7579** |
| e5-large | 0.6273 | 0.6013 | 0.7131 |
| gte-large | 0.6269 | 0.6008 | 0.7220 |
| e5-base | 0.6170 | 0.5838 | 0.7051 |
| gte-base | 0.6169 | 0.5891 | 0.6989 |

**[Fatto]** Lo stesso pattern qualitativo di Heart Disease si ripete: `sentence-biobert` ha accuratezza e F1 più alti, e l'AUC più alta è quasi un pareggio fra `pubmedbert` (0.7579) e `bioclinicalbert` (0.7575) — così vicino che vale la pena controllare cosa dice il test appropriato invece di fidarsi della sola classifica numerica. **[Fatto]** Il file `datas/diabetes130/results/delong_comparison.csv` (già presente, letto per intero all'inizio di questo lavoro) riporta, per questa coppia specifica, `p_value=0.6793`, `significant=0` — **la differenza fra i due modelli con l'AUC apparentemente più alta non è statisticamente significativa**. È esattamente il tipo di verifica che il capitolo 37 insegna a fare, applicata qui a un caso reale del progetto: la classifica numerica dice "pubmedbert vince", il test di DeLong dice "non puoi dirlo con sicurezza da questi dati".

## 41.2 Perché i punteggi assoluti sono più bassi

**[Fatto]** Ogni metrica, per ogni modello, è più bassa su Diabetes130 che su Heart Disease — anche il modello migliore in assoluto (`sentence-biobert`, AUC 0.7678 contro 0.8781). **[Interpretazione]** Tre ragioni concorrono plausibilmente a questa differenza, nessuna delle quali verificabile isolatamente con i dati disponibili in questo progetto, ma tutte ragionevoli:

1. **Il compito stesso è più difficile.** Prevedere una riammissione entro 30 giorni dipende da fattori che le 19 feature mantenute (capitolo 30.2) non catturano affatto — supporto familiare, aderenza alla terapia dopo la dimissione, comorbidità non registrate in questo sottoinsieme di colonne. Diagnosticare una malattia coronarica dai sintomi e da misure cliniche dirette (colesterolo, elettrocardiogramma) è, per contro, un compito con una relazione più diretta fra feature e target.
2. **Le feature mantenute sono più amministrative che cliniche.** `admission_type_id`, `discharge_disposition_id` sono codici di processo ospedaliero, non misure fisiologiche dirette come `chol` o `thalach` — meno segnale clinico diretto da tradurre in una frase informativa (capitolo 22.1).
3. **Il testo generato è strutturalmente più semplice.** Il capitolo 22.1 ha già notato che `record_to_text_diabetes130()` non applica alcuna traduzione di codici in etichette cliniche riconoscibili (usa `_fmt_raw()`, non `_fmt_cat()`): un modello di embedding testuale potrebbe estrarre meno segnale semantico da "admission type id: 1" che da "chest pain type: typical angina".

> **ATTENZIONE —** nessuna di queste tre ipotesi è isolata o testata in questo progetto: sono spiegazioni plausibili, non risultati dimostrati. Presentarle in tesi come fatti accertati, invece che come interpretazioni motivate, sarebbe un errore di calibrazione — esattamente la distinzione fra i tre livelli (fatto, teoria consolidata, interpretazione) che questo libro segue dal capitolo 0.

## 41.3 Isolamento tra run

**[Fatto]** Le due tabelle di questo capitolo e del precedente provengono da cartelle completamente separate (`datas/heart_disease/` e `datas/diabetes130/`, capitolo 18.2): puoi verificarlo tu stesso confrontando le date di generazione riportate in cima a ciascun `report.md` — `2026-08-02 16:51` per Heart Disease, `2026-08-02 18:56` per Diabetes130 (due ore di distanza, coerente con esecuzioni separate, non simultanee) — e osservando che nessun file sotto `datas/heart_disease/` porta traccia di un valore riconducibile a Diabetes130 o viceversa.

## Riepilogo

La stessa pipeline, applicata a Diabetes130, produce metriche assolute più basse su tutti e sette i modelli — un compito plausibilmente più difficile, con feature più amministrative e un testo generato meno ricco semanticamente, anche se nessuna di queste ipotesi è verificata isolatamente in questo progetto. Il pattern qualitativo (modelli biomedici in testa) si ripete comunque identico a Heart Disease, con un'importante lezione di metodo: la differenza fra le due AUC più alte non è statisticamente significativa secondo il test di DeLong, nonostante la classifica numerica suggerisca un vincitore netto.

## Domande di autoverifica

**1. Il modello con l'AUC numericamente più alta su Diabetes130 (`pubmedbert`) batte davvero, in senso statistico, il secondo classificato (`bioclinicalbert`)?**
No: il test di DeLong su questa coppia riporta un p-value di 0.6793, ben sopra la soglia di significatività 0.05 — la differenza osservata (0.7579 contro 0.7575) è compatibile con variazione casuale, non con una superiorità reale e sistematica di un modello sull'altro.

**2. Quali tre ragioni, nessuna delle quali dimostrata isolatamente, potrebbero spiegare perché tutte le metriche sono più basse su Diabetes130?**
Il compito di prevedere una riammissione futura è intrinsecamente più difficile di una diagnosi diretta; le feature mantenute sono più amministrative che cliniche; il testo generato per questo dataset non traduce i codici in etichette cliniche riconoscibili, a differenza di Heart Disease.

**3. Come puoi verificare, senza fidarti della sola affermazione di questo libro, che le due esecuzioni non si sono mai sovrapposte?**
Confrontando le date di generazione riportate in cima ai due `report.md` (due ore di distanza) e osservando che ciascuna cartella `datas/<dataset>/` contiene solo file coerenti con il proprio dataset, senza alcuna sovrapposizione di nomi o valori.

> **MATERIALE PER LA TESI**
> 1. La tabella riassuntiva reale per Diabetes130 (§41.1), affiancata a quella di Heart Disease del capitolo 40 — riusabile come tabella comparativa centrale della sezione "Risultati".
> 2. L'esempio concreto del confronto pubmedbert/bioclinicalbert, dove la classifica numerica e il test statistico danno risposte diverse — è probabilmente il miglior esempio didattico del libro sulla differenza fra "sembra diverso" e "è statisticamente diverso": riusabile quasi integralmente nella sezione "Discussione".
> 3. Le tre ipotesi motivate sul perché i punteggi assoluti sono più bassi, esplicitamente marcate come interpretazione e non fatto accertato — riusabile come paragrafo di discussione calibrato, evitando affermazioni causali non supportate dai dati.
