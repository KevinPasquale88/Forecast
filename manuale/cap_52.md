# Capitolo 52 — Il caso del reporting automatico non aggiornato

**Obiettivi del capitolo**
- Vedere, messo a fuoco come caso di studio autonomo, il limite più concreto e meglio dimostrabile di tutto il progetto.
- Capire perché questo tipo di problema è più pericoloso in un contesto clinico che in molti altri contesti software.
- Avere una proposta di correzione precisa, non solo la diagnosi del problema.

Il capitolo 27.2 ha già individuato questo problema leggendo il codice. Questo capitolo lo tratta con tutto il peso critico che merita, come esempio paradigmatico di un tipo di difetto che il solo "il codice funziona senza errori" non intercetta mai.

## 52.1 Confronto riga per riga dei due report reali

**[Fatto]** `generatereport.py:192-198` scrive, come stringa Python statica, la sezione "Discussion and Observations":
```
- Larger embedding models (E5-large, GTE-large) generally show better performance.
- GTE-large tends to achieve higher ROC-AUC and tighter confidence intervals.
- Confusion matrices enable analysis of false positives and false negatives.
- Bootstrap is useful to verify metric stability and robustness.
```
**[Fatto]** Questo identico testo compare, carattere per carattere, sia in `datas/heart_disease/reports/report.md` sia in `datas/diabetes130/reports/report.md` — verificabile aprendo entrambi i file, già presenti nel repository. **[Fatto]** Confrontando questa affermazione con le tabelle reali dello stesso file: su Heart Disease (Tabella 44.1), l'AUC di gte-large è 0.8540, inferiore a pubmedbert (0.8855), bioclinicalbert (0.8795) ed e5-large (0.8661); su Diabetes130 (Tabella 45.1), è 0.7220, inferiore a sentence-biobert (0.7678), bioclinicalbert (0.7575) e pubmedbert (0.7579). **In nessuno dei due dataset che il report stesso presenta, gte-large ha l'AUC più alta** — l'affermazione "GTE-large tends to achieve higher ROC-AUC" è falsa per entrambi i casi disponibili nel repository.

## 52.2 Perché è pericoloso in contesto clinico

**[Interpretazione]** In un contesto software generico, un testo descrittivo sbagliato in un report generato automaticamente sarebbe un difetto fastidioso ma facilmente corretto una volta scoperto. In un contesto di supporto a decisioni cliniche — anche solo di ricerca, come questo progetto — il rischio è di natura diversa: **[Interpretazione]** un report che presenta un'affermazione narrativa con la stessa autorevolezza tipografica di una tabella numerica calcolata correttamente non dà a chi legge alcun segnale che quella specifica riga non sia stata verificata contro i dati. Chi leggesse solo la sezione "Discussion" (più leggibile di una tabella di 12 colonne) per farsi un'idea rapida di "quale modello è il migliore", concluderebbe erroneamente che sia GTE-large — l'opposto di ciò che le tabelle nello stesso documento mostrano.

**[Interpretazione]** Il problema è aggravato, non attenuato, dal fatto che il resto del report è genuinamente calcolato dai dati (le tabelle, i grafici, i test statistici, capitolo 27.1): un lettore che si fidi giustamente dell'accuratezza della maggior parte del documento non ha motivo di sospettare che una sezione specifica non lo sia. Un report interamente inventato sarebbe, paradossalmente, meno pericoloso: nessuno si fiderebbe di niente. Un report per il 90% corretto e per il 10% sistematicamente sbagliato in un modo indistinguibile a occhio è il caso più insidioso.

> **ATTENZIONE —** questo non è un'affermazione sul progetto nel suo complesso: la pipeline di calcolo (preprocessing, embedding, classificazione, bootstrap, test statistici) è, per quanto verificato in questo libro, corretta nella sua implementazione. Il problema riguarda specificamente e soltanto l'ultimo miglio — la sintesi in linguaggio naturale di quei calcoli, in `generatereport.py:192-225`.

## 52.3 Come si preverrebbe

**[Interpretazione]** Tre livelli di prevenzione, dal più semplice al più robusto:

1. **Generare il testo dai dati**, come già proposto al capitolo 27.3: sostituire l'affermazione statica con un'espressione calcolata (`summary.loc[summary["auc_mean"].idxmax(), "model"]`) elimina il problema alla radice per questa specifica affermazione.
2. **Un test di coerenza automatico**: una funzione che, dopo aver generato il report, verifichi che ogni nome di modello menzionato nel testo narrativo compaia effettivamente al posto giusto nella classifica delle tabelle — un test più laborioso da scrivere, ma capace di intercettare anche errori futuri simili, non solo questo specifico.
3. **Etichettare esplicitamente il testo generato a mano**: se generare dinamicamente ogni affermazione fosse troppo costoso, marcare chiaramente le sezioni scritte a priori (per esempio, "Osservazioni generali, non specifiche di questa esecuzione") eviterebbe che un lettore le scambi per una sintesi dei dati appena mostrati.

> **PROVA TU —** scegli uno dei tre livelli di prevenzione e implementalo per intero su `generatereport.py`. Il primo (rigenerare il testo dai dati) è il più concreto da realizzare con le competenze già acquisite in questo libro (Parte VII, Parte V capitolo 27): è un esercizio realistico, non solo teorico, per una tesi che voglia includere un contributo di miglioramento verificabile.

## Riepilogo

Le sezioni narrative del report generato automaticamente sono testo statico, non calcolato dai dati — verificato confrontando i due report reali già presenti nel repository, che condividono lo stesso testo nonostante tabelle numeriche diverse, e che contiene un'affermazione ("GTE-large ha l'AUC più alta") falsa in entrambi i casi disponibili. Questo tipo di difetto è particolarmente insidioso in un contesto clinico perché si nasconde dietro un documento altrimenti corretto, con la stessa autorevolezza tipografica delle parti genuinamente calcolate. Tre livelli di prevenzione, dal generare il testo dai dati fino a etichettare esplicitamente le parti scritte a priori, correggerebbero il problema con sforzo crescente ma robustezza crescente.

## Domande di autoverifica

**1. Come si dimostra, senza fidarsi di un'affermazione altrui, che il testo di "Discussion and Observations" non dipende dai dati?**
Confrontando carattere per carattere le sezioni corrispondenti nei due report reali di Heart Disease e Diabetes130: sono identiche, nonostante le tabelle numeriche sopra siano sostanzialmente diverse fra i due dataset.

**2. Perché un report per il 90% corretto e per il 10% sistematicamente sbagliato è, in un certo senso, più pericoloso di un report interamente inaffidabile?**
Perché la correttezza della maggior parte del documento induce una fiducia generalizzata che si estende, senza motivo, anche alla parte sbagliata — un lettore non ha alcun segnale visibile per distinguere le due parti, mentre un documento interamente inaffidabile non ispirerebbe fiducia in nessuna sua parte.

**3. Qual è il livello di prevenzione più facile da implementare con le sole competenze già presenti in questo libro?**
Sostituire l'affermazione statica con un'espressione pandas calcolata a runtime (per esempio `summary.loc[summary["auc_mean"].idxmax(), "model"]`), già proposta al capitolo 27.3 — richiede solo la conoscenza di pandas già trattata nella Parte V, non un nuovo strumento di test o convenzione documentale.

> **MATERIALE PER LA TESI**
> 1. Il confronto riga per riga dei due report, con l'affermazione falsificata evidenziata — probabilmente il singolo argomento più forte e più facilmente presentabile alla commissione di tutto il libro: riusabile come caso di studio autonomo in "Discussione e limiti".
> 2. L'analisi del perché questo tipo di difetto sia più pericoloso in contesto clinico che altrove — riusabile come argomento generale sulla fiducia nei sistemi di reporting automatico, applicabile oltre questo progetto specifico.
> 3. I tre livelli di prevenzione proposti — riusabile come base per un contributo di miglioramento realmente implementato e discusso in tesi.
