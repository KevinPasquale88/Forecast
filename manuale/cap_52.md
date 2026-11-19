# Capitolo 52 — Il caso del reporting automatico non aggiornato

**Obiettivi del capitolo**
- Vedere, messo a fuoco come caso di studio autonomo, il difetto più concreto e meglio dimostrabile individuato in questo progetto — e la sua correzione.
- Capire perché questo tipo di problema è più pericoloso in un contesto clinico che in molti altri contesti software.
- Vedere quale dei tre livelli di prevenzione proposti dall'analisi è stato effettivamente implementato, e cosa resta da fare.

Il capitolo 27.2 ha già individuato questo problema leggendo il codice. Questo capitolo lo tratta con tutto il peso critico che merita, come esempio paradigmatico di un tipo di difetto che il solo "il codice funziona senza errori" non intercetta mai — e come esempio, ormai completo, del ciclo diagnosi → correzione → verifica.

## 52.1 Confronto riga per riga dei due report reali (pre-fix)

**[Fatto]** Fino ai fix di revisione, `generatereport.py` scriveva, come stringa Python statica, la sezione "Discussion and Observations":
```
- Larger embedding models (E5-large, GTE-large) generally show better performance.
- GTE-large tends to achieve higher ROC-AUC and tighter confidence intervals.
- Confusion matrices enable analysis of false positives and false negatives.
- Bootstrap is useful to verify metric stability and robustness.
```
**[Fatto]** Questo identico testo compariva, carattere per carattere, sia in `datas/heart_disease/reports/report.md` sia in `datas/diabetes130/reports/report.md` — verificato confrontando i due file allora tracciati nel repository. **[Fatto]** Confrontando quell'affermazione con le tabelle reali degli stessi file: in entrambi i dataset l'AUC di gte-large era inferiore a quella di tutti e tre i modelli biomedici. **In nessuno dei due dataset che il report stesso presentava, gte-large aveva l'AUC più alta** — l'affermazione "GTE-large tends to achieve higher ROC-AUC" era falsa per entrambi i casi disponibili nel repository. (Il quadro non è cambiato con la pipeline corretta: nei report attuali, capitoli 44-45, gte-large resta dietro ai biomedici in AUC su entrambi i dataset.)

## 52.2 Perché è pericoloso in contesto clinico

**[Interpretazione]** In un contesto software generico, un testo descrittivo sbagliato in un report generato automaticamente sarebbe un difetto fastidioso ma facilmente corretto una volta scoperto. In un contesto di supporto a decisioni cliniche — anche solo di ricerca, come questo progetto — il rischio è di natura diversa: **[Interpretazione]** un report che presenta un'affermazione narrativa con la stessa autorevolezza tipografica di una tabella numerica calcolata correttamente non dà a chi legge alcun segnale che quella specifica riga non sia stata verificata contro i dati. Chi avesse letto solo la sezione "Discussion" (più leggibile di una tabella di 12 colonne) per farsi un'idea rapida di "quale modello è il migliore", avrebbe concluso erroneamente che fosse GTE-large — l'opposto di ciò che le tabelle nello stesso documento mostravano.

**[Interpretazione]** Il problema era aggravato, non attenuato, dal fatto che il resto del report era genuinamente calcolato dai dati (le tabelle, i grafici, i test statistici, capitolo 27.1): un lettore che si fidasse giustamente dell'accuratezza della maggior parte del documento non aveva motivo di sospettare che una sezione specifica non lo fosse. Un report interamente inventato sarebbe, paradossalmente, meno pericoloso: nessuno si fiderebbe di niente. Un report per il 90% corretto e per il 10% sistematicamente sbagliato in un modo indistinguibile a occhio è il caso più insidioso.

> **ATTENZIONE —** questa non era un'accusa al progetto nel suo complesso: la pipeline di calcolo (preprocessing, embedding, classificazione, bootstrap, test statistici) era, per quanto verificato in questo libro, corretta nella sua implementazione. Il problema riguardava specificamente e soltanto l'ultimo miglio — la sintesi in linguaggio naturale di quei calcoli.

## 52.3 Come si previene — e cosa è stato fatto davvero

**[Interpretazione]** Tre livelli di prevenzione, dal più semplice al più robusto, come proposti dall'analisi originale:

1. **Generare il testo dai dati**, come già proposto al capitolo 27.3: sostituire l'affermazione statica con espressioni calcolate (`summary.loc[summary["auc_mean"].idxmax()]`) elimina il problema alla radice.
2. **Un test di coerenza automatico**: una funzione che, dopo aver generato il report, verifichi che ogni nome di modello menzionato nel testo narrativo compaia effettivamente al posto giusto nella classifica delle tabelle.
3. **Etichettare esplicitamente il testo generato a mano**: marcare chiaramente le sezioni scritte a priori (per esempio, "Osservazioni generali, non specifiche di questa esecuzione") eviterebbe che un lettore le scambi per una sintesi dei dati appena mostrati.

**[Fatto]** Il primo livello è stato implementato per intero dai fix di revisione (`docs/CHANGES.md` §8, capitolo 27.3): `_build_discussion()` e `_build_conclusions()` calcolano ora ogni affermazione dal `summary` e dai test statistici della run corrente, e i report attuali dei due dataset hanno sezioni "Discussion" **diverse**, ciascuna coerente con le proprie tabelle. Il terzo livello è stato applicato all'unica sezione rimasta fissa ("Potential Improvements"), che è per sua natura un elenco di suggerimenti futuri, non un'affermazione fattuale sui dati. **[Interpretazione]** Il secondo livello — un test di coerenza automatico sul report generato — resta non implementato: è la naturale estensione della suite pytest del capitolo 48 per chi volesse portare questo caso di studio un passo oltre in tesi.

> **PROVA TU —** implementa il secondo livello: un test pytest che generi un report da un `summary` sintetico costruito ad arte e verifichi che il modello nominato come "highest mean ROC-AUC" in `_build_discussion()` sia davvero quello con l'AUC massima nel `summary`. È un esercizio realistico, e completa l'unico livello di prevenzione che i fix non hanno coperto.

## Riepilogo

Le sezioni narrative del report generato erano, per gran parte della storia del progetto, testo statico non calcolato dai dati — verificato confrontando i due report reali, identici nonostante tabelle diverse, con un'affermazione ("GTE-large ha l'AUC più alta") falsa in entrambi i casi. Questo tipo di difetto è particolarmente insidioso in un contesto clinico perché si nasconde dietro un documento altrimenti corretto. Dei tre livelli di prevenzione proposti dall'analisi, il primo (testo generato dai dati) è stato implementato per intero dai fix di revisione, il terzo applicato alla sezione rimasta fissa, e il secondo (test di coerenza automatico) resta un'estensione naturale per la tesi.

## Domande di autoverifica

**1. Come si dimostrava, senza fidarsi di un'affermazione altrui, che il vecchio testo di "Discussion and Observations" non dipendeva dai dati?**
Confrontando carattere per carattere le sezioni corrispondenti nei due report reali di Heart Disease e Diabetes130: erano identiche, nonostante le tabelle numeriche sopra fossero sostanzialmente diverse fra i due dataset. Nei report attuali, generati dal codice corretto, le stesse sezioni sono diverse fra loro.

**2. Perché un report per il 90% corretto e per il 10% sistematicamente sbagliato è, in un certo senso, più pericoloso di un report interamente inaffidabile?**
Perché la correttezza della maggior parte del documento induce una fiducia generalizzata che si estende, senza motivo, anche alla parte sbagliata — un lettore non ha alcun segnale visibile per distinguere le due parti, mentre un documento interamente inaffidabile non ispirerebbe fiducia in nessuna sua parte.

**3. Quale dei tre livelli di prevenzione è stato implementato dai fix, e quale resta aperto?**
Il primo (generare discussione e conclusioni dai dati della run, `_build_discussion`/`_build_conclusions`) è implementato; il terzo è applicato nella misura in cui l'unica sezione fissa rimasta è dichiaratamente un elenco di suggerimenti futuri; il secondo (un test automatico di coerenza fra testo narrativo e tabelle) resta da scrivere.

> **MATERIALE PER LA TESI**
> 1. Il caso di studio completo — l'affermazione falsificata, verificata sui due report reali, e il fix data-driven che l'ha sostituita — probabilmente il singolo argomento più forte e più facilmente presentabile alla commissione di tutto il libro: riusabile come caso di studio autonomo in "Discussione e limiti".
> 2. L'analisi del perché questo tipo di difetto sia più pericoloso in contesto clinico che altrove — riusabile come argomento generale sulla fiducia nei sistemi di reporting automatico, applicabile oltre questo progetto specifico.
> 3. Il livello di prevenzione rimasto aperto (test di coerenza sul report), con la traccia concreta del riquadro Prova tu — riusabile come contributo di miglioramento realmente implementabile e discusso in tesi.
