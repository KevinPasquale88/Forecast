# Capitolo 4 — Classificazione binaria: l'essenziale per seguire il libro

**Obiettivi del capitolo**

- Sapere cosa significa, con precisione, che un modello "classifica" qualcosa in due categorie.
- Riconoscere lo sbilanciamento delle classi come problema concreto, con i numeri reali di questo progetto.
- Padroneggiare il vocabolario minimo — vero/falso positivo/negativo — su cui si appoggia ogni metrica del capitolo 34.

## 4.1 Due classi, una probabilità, una soglia

Un classificatore binario, nella sua forma più comune — quella usata in questo progetto — non produce direttamente un'etichetta "sì" o "no". Produce un numero fra 0 e 1, interpretabile come una probabilità stimata che l'esempio appartenga alla classe positiva. **[Fatto]** Nel codice, questo numero è `y_score`, prodotto da `logisticReg.predict_proba(X_val)[:, 1]` (`classification.py:28`) — la seconda colonna dell'output di `predict_proba`, quella associata alla classe 1.

Per ottenere un'etichetta vera e propria — "malattia presente" oppure "malattia assente" — serve un secondo passaggio: confrontare quel numero con una **soglia di decisione**. Se il punteggio supera la soglia, l'etichetta prevista è 1; altrimenti è 0. La soglia più ovvia è 0.5, ma non è affatto obbligata, e il capitolo 35 mostra perché questo progetto ne sceglie una diversa, calcolata per ogni fold di validazione.

> **SE VIENI DA JAVA —** non c'è un `enum` a due valori da qualche parte nel codice. La classe prevista è sempre calcolata al volo con un confronto numerico — `(y_score >= tau).astype(int)` (`classification.py:37`) — e non esiste, in nessun punto della pipeline, un tipo che rappresenti esplicitamente "la classe": è sempre e solo un intero 0 o 1, con il significato che gli attribuisci tu leggendo il codice, non il compilatore.

## 4.2 Sbilanciamento delle classi

**[Livello: teoria consolidata del settore]** Uno sbilanciamento delle classi si ha quando le due categorie da distinguere non compaiono con la stessa frequenza nei dati. È un problema pratico, non solo statistico: un classificatore che si limitasse a rispondere sempre "classe maggioritaria" otterrebbe già un'accuratezza numericamente alta, senza aver imparato nulla di utile — un punto a cui torniamo con un calcolo preciso al capitolo 47, quando costruiamo un modello di riferimento banale.

**[Fatto]** I due dataset di questo progetto hanno un grado di sbilanciamento molto diverso, entrambi verificati caricando i file grezzi con lo stesso procedimento usato dal codice (comando Python eseguito in questa sessione):

| Dataset | Righe totali (prima di split e SMOTE) | Classe positiva | Classe negativa | % positiva |
|---|---|---|---|---|
| Heart Disease | 920 | 509 | 411 | 55.3% |
| Diabetes130 (intero file, pre-campionamento) | 101.766 | 11.357 | 90.409 | 11.16% |

Heart Disease è, sorprendentemente, quasi bilanciato: la classe "malattia presente" è addirittura leggermente maggioritaria. Diabetes130 è invece marcatamente sbilanciato: solo un ricovero su nove circa produce una riammissione entro 30 giorni. Sono due situazioni realistiche e diverse, ed è un bene che il libro le tratti entrambe: il grado di sbilanciamento cambia quali metriche sono informative (capitolo 34) e quanto lavoro deve fare il bilanciamento sintetico delle classi (capitolo 31.2).

> **ATTENZIONE —** la tabella riporta lo sbilanciamento **prima** della suddivisione training/test e prima di SMOTENC (capitolo 31.2), che poi riequilibra artificialmente il set di addestramento. Il numero informativo su "quanto è difficile il problema nella realtà" è quello di questa tabella, non quello — reso paritario ad arte — degli embedding effettivamente usati per l'addestramento.

**[Fatto]** La cifra di 920 righe per Heart Disease merita una precisazione, perché contraddice la documentazione del progetto: sia `README.md:78` sia `docs/DATASET.md:17` dichiarano "297" record per questo dataset. Il codice reale (`load_heart_disease()`, `function.py:96-113`) concatena però tutti e quattro i file grezzi senza scartare nessuna riga, per un totale verificabile di 920. **[Inferenza]** La cifra "297" è quella storicamente citata in letteratura per il solo sottoinsieme Cleveland dopo aver scartato le righe con dati mancanti nelle feature più critiche — un dataset diverso da quello che il codice di questo progetto carica davvero. Ne riparliamo, con tutto il dettaglio, al capitolo 29.3 e di nuovo, in chiave critica, al capitolo 51.

## 4.3 Vero/falso positivo/negativo

**[Livello: teoria consolidata del settore]** Per qualunque coppia (etichetta prevista, etichetta vera), esistono esattamente quattro esiti possibili, riassunti nella matrice di confusione che il capitolo 24 mostra per ogni modello del progetto:

|  | Etichetta vera: positiva | Etichetta vera: negativa |
|---|---|---|
| **Prevista: positiva** | Vero positivo (VP) | Falso positivo (FP) |
| **Prevista: negativa** | Falso negativo (FN) | Vero negativo (VN) |

Un **vero positivo** è un caso positivo correttamente riconosciuto come tale; un **vero negativo**, un caso negativo correttamente riconosciuto come tale. Un **falso positivo** è un caso negativo scambiato per positivo; un **falso negativo**, un caso positivo scambiato per negativo. Nel linguaggio del capitolo 1.2: per Heart Disease, un falso negativo è una malattia coronarica non individuata; per Diabetes130, un falso negativo è un paziente ad alto rischio di riammissione lasciato senza follow-up rinforzato.

**[Fatto]** Il codice calcola esplicitamente questi quattro esiti in `error_analysis.py:26-27`:
```python
fp_mask = (y_true == 0) & (y_pred == 1)
fn_mask = (y_true == 1) & (y_pred == 0)
```
Nota, per chi viene da Java, l'operatore `&` fra due array booleani NumPy: non è l'AND logico di Python (`and`), che qui darebbe un errore — è l'AND *elemento per elemento* fra due vettori di verità, un'operazione che in Java richiederebbe un ciclo esplicito o uno stream. Ne parliamo con tutto il dettaglio necessario al capitolo 8.

## Riepilogo

Un classificatore binario in questo progetto produce sempre una probabilità, non direttamente un'etichetta: l'etichetta nasce dal confronto con una soglia. Heart Disease è quasi bilanciato (55.3%/44.7%, su 920 righe reali — non 297 come dichiarato nella documentazione del progetto), mentre Diabetes130 è marcatamente sbilanciato (11.16% di classe positiva su oltre 100.000 righe). I quattro esiti possibili di una previsione — vero/falso positivo/negativo — sono il vocabolario su cui si costruisce ogni metrica dei capitoli successivi.

## Domande di autoverifica

**1. Perché `y_score` non è già una previsione utilizzabile da sola?**
Perché è un numero continuo fra 0 e 1 (una probabilità stimata), non un'etichetta binaria. Serve un secondo passaggio — il confronto con una soglia — per ottenere `y_pred`, l'etichetta vera e propria.

**2. Quale dei due dataset del progetto è più sbilanciato, e di quanto?**
Diabetes130, nettamente: 11.16% di classe positiva contro l'88.84% negativa, calcolato sull'intero file grezzo. Heart Disease è invece quasi bilanciato, 55.3%/44.7%.

**3. Un modello segnala "riammissione probabile" per un paziente che poi non torna in ospedale entro 30 giorni. Che tipo di esito è, e qual è il suo "gemello" nella matrice di confusione?**
È un falso positivo. Il suo gemello concettuale — l'altro tipo di errore — è il falso negativo: un paziente che il modello giudica a basso rischio, ma che invece torna in ospedale entro 30 giorni.

> **MATERIALE PER LA TESI**
> 1. La tabella con i numeri reali di sbilanciamento per entrambi i dataset (§4.2), con il comando Python usato per ottenerli — riusabile direttamente nella sezione "Materiali e metodi" o in una tabella descrittiva dei dati.
> 2. La discrepanza numerica 297 vs. 920 per Heart Disease, con la spiegazione della causa più probabile — riusabile come osservazione critica autonoma, con rimando al capitolo 51 per il trattamento esteso.
> 3. La matrice di confusione generica con la traduzione clinica di ciascun esito per entrambi i dataset — riusabile come figura o tabella nella sezione "Discussione", per motivare perché una metrica aggregata da sola non basta a giudicare un sistema di supporto clinico.
