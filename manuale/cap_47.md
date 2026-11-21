# Capitolo 47 — Confronto con un modello di riferimento banale

**Obiettivi del capitolo**

- Sapere perché un baseline non è un dettaglio accessorio, ma la base di ogni affermazione difendibile su "quanto è bravo" un sistema.
- Vedere il calcolo reale, eseguito per questo libro, di un baseline banale sugli stessi dati di validazione dei sette modelli.
- Capire come questo confronto, unito alla valutazione holdout, quantifichi il divario fra il pool bilanciato e la popolazione reale.

## 47.1 Cos'è un baseline e perché la tesi ne ha bisogno

**[Livello: teoria consolidata del settore]** Un modello di riferimento banale (*baseline*) è il sistema più semplice possibile per lo stesso compito — nel caso più estremo, uno che ignora completamente l'input e prevede sempre la stessa cosa. Non serve a "vincere": serve a stabilire un pavimento. Ogni affermazione del tipo "il modello X ottiene un'accuratezza dell'80%" è priva di significato senza sapere quanto otterrebbe la cosa più ovvia possibile sullo stesso identico problema — il capitolo 34.1 lo ha già anticipato con l'esempio dell'88.84% di accuratezza "gratuita" su Diabetes130 nella popolazione reale.

**[Fatto]** Questo progetto **non include** un baseline di alcun tipo: nessuno degli undici file del progetto calcola o riporta la prestazione di un classificatore banale. Questo capitolo lo costruisce da zero, usando dati già presenti nel repository (coerentemente con la decisione dichiarata al capitolo 43.1 di non rieseguire la pipeline).

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
| Heart Disease | 0.5000 | e5-large: 0.7629 (+26.3 punti) | pubmedbert: 0.7936 (+29.4 punti) |
| Diabetes130 | 0.5000 | gte-base: 0.6247 (+12.5 punti) | sentence-biobert: 0.6811 (+18.1 punti) |

**[Fatto]** Ogni singolo modello, su entrambi i dataset, supera nettamente il baseline a maggioranza sul pool di validazione — un risultato che, a differenza del confronto fra famiglie di modelli (capitoli 44-45), non richiede alcun test statistico per essere convincente: il margine (12.5-29.4 punti di accuratezza) è troppo ampio per essere spiegato da variazione casuale, anche sul dataset più piccolo.

> **ATTENZIONE —** questo confronto, per quanto rassicurante, misura il vantaggio dell'embedding **sul pool bilanciato artificialmente da SMOTENC**, non sulla popolazione reale e sbilanciata da cui i dati originano (55.3%/44.7% per Heart Disease, 11.16%/88.84% per Diabetes130, capitolo 4.2). Un baseline "a maggioranza sulla popolazione reale" di Diabetes130 avrebbe un'accuratezza dell'**88.84%**. E qui il progetto, dopo il fix del test set, fornisce finalmente la misura che una prima versione di questo capitolo poteva solo invocare come esperimento mancante: la valutazione holdout (capitolo 45, Tabella 45.1bis) applica i classificatori alla distribuzione reale del 20% trattenuto, e su Diabetes130 il risultato è impietoso — accuratezze fra 0.40 e 0.50 (contro l'88.84% del baseline banale) e AUC fra 0.48 e 0.55, appena sopra il caso. Il baseline a maggioranza non "capisce" nulla (AUC 0.5 per costruzione, nessun riammesso individuato), quindi il confronto va letto con la metrica giusta: ma la conclusione onesta è che, sulla popolazione reale di Diabetes130, il valore aggiunto di questi embedding con una testa lineare è marginale. Su Heart Disease, per contro, l'holdout conferma il quadro della validazione (accuratezze 0.76-0.84 contro il 55.3% del baseline a maggioranza reale, AUC 0.87-0.92): il sistema lì funziona anche sulla distribuzione vera.

## Riepilogo

Questo progetto non include alcun baseline: questo capitolo ne ha costruito uno da zero, con un calcolo reale sui dati già tracciati. Ogni modello supera nettamente (12.5-29.4 punti di accuratezza) un baseline a maggioranza calcolato sul pool bilanciato da SMOTENC, un margine troppo ampio per essere casuale. Ma il confronto con la popolazione reale — oggi misurato davvero dalla valutazione holdout — divide i due dataset: su Heart Disease il sistema batte ampiamente il baseline reale anche sul test set mai visto; su Diabetes130 le accuratezze holdout (0.40-0.50) restano lontanissime dall'88.84% del baseline banale e le AUC appena sopra il caso, rendendo concreto, con numeri misurati e non solo ipotizzati, quanto il pool riequilibrato sovrastimasse il valore pratico del sistema su quel compito.

## Domande di autoverifica

**1. Perché il baseline a maggioranza ha, per costruzione matematica, esattamente accuratezza 0.5000 e macro-F1 0.3333 su entrambi i dataset di questo progetto?**
Perché il pool di validazione concatenato è esattamente bilanciato al 50%/50%, conseguenza diretta di SMOTENC (che pareggia le classi nel training) e della stratificazione di `StratifiedKFold` (che preserva quella proporzione in ogni fold): una previsione costante su un pool perfettamente bilanciato ottiene sempre questi due valori, indipendentemente dai dati specifici.

**2. Perché il confronto "ogni modello batte nettamente il baseline a maggioranza" non richiede un test statistico formale per essere convincente?**
Perché il margine (da 12.5 a 29.4 punti percentuali di accuratezza) è così ampio da non poter essere ragionevolmente attribuito a variazione casuale, a differenza dei confronti fra famiglie di modelli del capitolo 44-45, dove i margini più piccoli richiedono davvero un test come DeLong per essere valutati con rigore.

**3. Cosa dice, oggi che la valutazione holdout esiste, il confronto con il baseline a maggioranza sulla popolazione reale di Diabetes130 (88.84%)?**
Che sulla distribuzione reale i sette modelli ottengono accuratezze fra 0.40 e 0.50 — lontanissime dal baseline banale — e AUC fra 0.48 e 0.55, appena sopra il caso: il vantaggio misurato sul pool riequilibrato non si trasferisce. Il confronto va letto con la metrica giusta (il baseline ha AUC 0.5 e non individua alcun riammesso), ma la conclusione resta: il valore pratico del sistema su quel compito, misurato onestamente, è marginale — mentre su Heart Disease l'holdout conferma un vantaggio ampio e reale.

> **MATERIALE PER LA TESI**
> 1. Il calcolo del baseline con il comando `DummyClassifier` e i risultati reali — riusabile integralmente nella sezione "Materiali e metodi" come baseline mancante nel progetto originale, colmata per la tesi.
> 2. La tabella di confronto con i margini reali (§47.3) — riusabile direttamente nella sezione "Risultati" come evidenza che il sistema supera un riferimento banale.
> 3. Il confronto a tre — baseline sul pool bilanciato, baseline sulla popolazione reale (88.84%), e le metriche holdout effettivamente misurate — probabilmente l'argomento più efficace di tutto il libro per la sezione "Discussione e limiti": la storia completa di un limite prima ipotizzato con un numero, poi misurato davvero grazie al fix del test set.
