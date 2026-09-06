# Capitolo 47 — Confronto con un modello di riferimento banale

**Obiettivi del capitolo**

- Sapere perché un baseline non è un dettaglio accessorio, ma la base di ogni affermazione difendibile su "quanto è bravo" un sistema.
- Vedere il calcolo reale, eseguito per questo libro, di un baseline banale sugli stessi dati di validazione dei sette modelli.
- Capire perché questo confronto, da solo, rivela anche il costo reale di uno dei limiti già discussi: il test set mai usato.

## 47.1 Cos'è un baseline e perché la tesi ne ha bisogno

**[Livello: teoria consolidata del settore]** Un modello di riferimento banale (*baseline*) è il sistema più semplice possibile per lo stesso compito — nel caso più estremo, uno che ignora completamente l'input e prevede sempre la stessa cosa. Non serve a "vincere": serve a stabilire un pavimento. Ogni affermazione del tipo "il modello X ottiene un'accuratezza dell'80%" è priva di significato senza sapere quanto otterrebbe la cosa più ovvia possibile sullo stesso identico problema — il capitolo 34.1 lo ha già anticipato con l'esempio dell'88.84% di accuratezza "gratuita" su Diabetes130 nella popolazione reale.

**[Fatto]** Questo progetto **non include** un baseline di alcun tipo: nessuno dei nove file del progetto calcola o riporta la prestazione di un classificatore banale. Questo capitolo lo costruisce da zero, usando dati già presenti nel repository (coerentemente con la decisione dichiarata al capitolo 43.1 di non rieseguire la pipeline).

## 47.2 Costruzione di un classificatore banale sugli stessi fold

**[Fatto]** Ho calcolato due baseline, usando `sklearn.dummy.DummyClassifier` sui file `{modello}_y_true.npy` già salvati da `classification.py` (identici per tutti e sette i modelli di uno stesso dataset, verificato con `np.array_equal` — comando eseguito in questa sessione):

```python
from sklearn.dummy import DummyClassifier
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(X_qualunque, y_true)
y_pred = dummy.predict(X_qualunque)
```

Il primo, **baseline a maggioranza**, prevede sempre la classe più frequente. Il secondo, **baseline casuale stratificato**, genera previsioni casuali che rispettano la proporzione osservata delle due classi — un confronto leggermente più informativo del primo, perché non è banalmente "sempre la stessa risposta".

**[Fatto]** Risultato reale (comando eseguito in questa sessione, su entrambi i dataset):

| Dataset | Baseline a maggioranza (Acc / Macro-F1) | Baseline casuale stratificato (Acc / Macro-F1) |
|---|---|---|
| Heart Disease | 0.5000 / 0.3333 | 0.5111 / 0.5110 |
| Diabetes130 | 0.5000 / 0.3333 | 0.4980 / 0.4980 |

**[Fatto]** Il pool di validazione concatenato è, per entrambi i dataset, **esattamente 50.00% / 50.00%** fra le due classi — non una coincidenza: è la conseguenza diretta del bilanciamento SMOTENC (capitolo 21.2), che pareggia le classi nel training set, e della stratificazione di `StratifiedKFold` (capitolo 33.2), che preserva quella stessa proporzione in ogni fold di validazione. **[Interpretazione]** Il baseline a maggioranza su un pool esattamente bilanciato ha, per costruzione matematica, sempre accuratezza 0.5000 e macro-F1 0.3333 (una previsione costante ottiene $F1=2/3$ sulla classe prevista e $F1=0$ sull'altra, media $1/3$) — un fatto puramente aritmetico, non specifico di questi dati, ma utile da verificare comunque.

## 47.3 Il confronto numerico: quanto valore aggiunge davvero l'embedding

**[Fatto]** Confrontando questi baseline con le tabelle reali dei capitoli 44 e 45:

| Dataset | Baseline maggioranza (Acc) | Modello peggiore | Modello migliore |
|---|---|---|---|
| Heart Disease | 0.5000 | e5-base: 0.7777 (+27.8 punti) | sentence-biobert: 0.8207 (+32.1 punti) |
| Diabetes130 | 0.5000 | gte-base: 0.6169 (+11.7 punti) | sentence-biobert: 0.6832 (+18.3 punti) |

**[Fatto]** Ogni singolo modello, su entrambi i dataset, supera nettamente il baseline a maggioranza — un risultato che, a differenza del confronto fra famiglie di modelli (capitoli 44-45), non richiede alcun test statistico per essere convincente: il margine (11.7-32.1 punti di accuratezza) è troppo ampio per essere spiegato da variazione casuale, anche sul dataset più piccolo.

> **ATTENZIONE —** questo confronto, per quanto rassicurante, misura il vantaggio dell'embedding **sul pool bilanciato artificialmente da SMOTENC**, non sulla popolazione reale e sbilanciata da cui i dati originano (55.3%/44.7% per Heart Disease, 11.16%/88.84% per Diabetes130, capitolo 4.2). Un baseline "a maggioranza sulla popolazione reale" avrebbe un'accuratezza ben diversa — per Diabetes130, **88.84%**, più alta di ogni singolo modello di questo progetto misurato sul pool bilanciato (61.7-68.3%). Questo non significa che i modelli del progetto siano peggiori di "non fare nulla": significa che **non è mai stata misurata**, in questo progetto, la prestazione dei sette modelli sulla distribuzione reale e sbilanciata della popolazione di origine — è precisamente la conseguenza pratica, ora quantificata con un numero concreto, del test set calcolato e mai usato (capitolo 21.1, capitolo 33.1, capitolo 43.3). Il confronto onesto con "non fare nulla sulla popolazione reale" richiederebbe applicare i sette classificatori già addestrati al test set del 20% originale — mai fatto in questo progetto, e non rifatto in questo libro per rispettare la decisione di non rieseguire la pipeline (capitolo 43.1), ma tecnicamente possibile con i dati già presenti, e una direzione concreta per il capitolo 55.

## Riepilogo

Questo progetto non include alcun baseline: questo capitolo ne ha costruito uno da zero, con un calcolo reale sui dati già tracciati. Ogni modello supera nettamente (11.7-32.1 punti di accuratezza) un baseline a maggioranza calcolato sul pool bilanciato da SMOTENC, un margine troppo ampio per essere casuale. Ma questo stesso confronto rivela, con un numero preciso, il costo del test set mai usato: un baseline a maggioranza sulla popolazione reale e sbilanciata di Diabetes130 raggiungerebbe l'88.84%, più alto di ogni modello misurato sul pool riequilibrato — un confronto che sarebbe fuorviante prendere alla lettera, ma che rende concreto perché la mancanza di un test set indipendente sia un limite reale, non solo teorico.

## Domande di autoverifica

**1. Perché il baseline a maggioranza ha, per costruzione matematica, esattamente accuratezza 0.5000 e macro-F1 0.3333 su entrambi i dataset di questo progetto?**
Perché il pool di validazione concatenato è esattamente bilanciato al 50%/50%, conseguenza diretta di SMOTENC (che pareggia le classi nel training) e della stratificazione di `StratifiedKFold` (che preserva quella proporzione in ogni fold): una previsione costante su un pool perfettamente bilanciato ottiene sempre questi due valori, indipendentemente dai dati specifici.

**2. Perché il confronto "ogni modello batte nettamente il baseline a maggioranza" non richiede un test statistico formale per essere convincente?**
Perché il margine (da 11.7 a 32.1 punti percentuali di accuratezza) è così ampio da non poter essere ragionevolmente attribuito a variazione casuale, a differenza dei confronti fra famiglie di modelli del capitolo 44-45, dove i margini più piccoli richiedono davvero un test come DeLong per essere valutati con rigore.

**3. Perché il numero "88.84%" (baseline a maggioranza sulla popolazione reale di Diabetes130) non va confrontato direttamente con le accuratezze dei modelli riportate nei capitoli 44-45?**
Perché quel numero si riferisce alla popolazione reale e sbilanciata, mentre le accuratezze dei modelli sono misurate sul pool riequilibrato artificialmente da SMOTENC: sono due popolazioni diverse, e confrontarle direttamente sarebbe un errore metodologico — ma il fatto stesso che questo confronto "sbagliato" sia impossibile da escludere con certezza è la conseguenza diretta dell'assenza di un test set sulla popolazione reale.

> **MATERIALE PER LA TESI**
> 1. Il calcolo del baseline con il comando `DummyClassifier` e i risultati reali — riusabile integralmente nella sezione "Materiali e metodi" come baseline mancante nel progetto originale, colmata per la tesi.
> 2. La tabella di confronto con i margini reali (§47.3) — riusabile direttamente nella sezione "Risultati" come evidenza che il sistema supera un riferimento banale.
> 3. L'analisi del limite del test set mai usato, resa concreta con il numero 88.84%, invece che solo enunciata in astratto — probabilmente l'argomento più efficace di tutto il libro per la sezione "Discussione e limiti": mostra un numero preciso, non solo un principio metodologico generico.
