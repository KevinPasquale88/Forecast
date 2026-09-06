# Capitolo 31 — Qualità dei dati e casi limite

**Obiettivi del capitolo**

- Avere una vista d'insieme, sui due dataset insieme, di come il progetto tratta i valori mancanti in tutte le loro forme.
- Capire cosa genera esattamente SMOTENC quando crea un record sintetico, con un esempio concreto.
- Sapere cosa succede, nella conversione a testo, ai casi limite: valori mancanti residui, categorie sconosciute, record sintetici.

## 31.1 Valori mancanti espliciti e impliciti

**[Fatto]** I capitoli 29 e 30 hanno già mostrato, con numeri precisi, che entrambi i dataset di questo progetto hanno un problema di mancanza dei dati molto più serio di quanto la documentazione esistente lasci intendere: `ca` e `thal` mancanti nel 66% e 53% dei casi in Heart Disease (quasi solo nei tre centri non-Cleveland), `max_glu_serum` e `A1Cresult` mancanti nel 95% e 83% dei casi in Diabetes130. Vale la pena, qui, distinguere esplicitamente le **tre forme diverse** in cui "mancante" si presenta in questo progetto, perché il codice le tratta con meccanismi diversi:

1. **Mancante esplicito, marcato `?`** — la forma più comune, letta direttamente come `NaN` da pandas con `na_values="?"` (`function.py:103,118`).
2. **Mancante mascherato da un valore fisiologicamente impossibile** — solo per `chol`/`trestbps` di Heart Disease, convertito esplicitamente in `NaN` da una riga dedicata (`function.py:110-111`, capitolo 29.2). Nessun controllo equivalente esiste per Diabetes130: se quel dataset avesse un problema analogo su una colonna numerica (per esempio un valore implausibile per `time_in_hospital`), il codice attuale non lo intercetterebbe.
3. **Mancante per assenza di indicazione clinica**, non per un guasto di raccolta dati — il caso di `max_glu_serum`/`A1Cresult` discusso al capitolo 30.2, dove l'assenza stessa potrebbe essere informazione, trattata invece come le altre due forme.

**[Fatto]** Tutte e tre le forme, una volta arrivate a `impute_raw()` (`preprocessing.py:76-82`), ricevono lo stesso trattamento indistinto: mediana per le colonne numeriche, moda per le categoriali. Il codice non distingue in alcun modo, a questo stadio, se un valore mancante rappresenti un dato perso, un dato impossibile da misurare in quel centro, o un test clinicamente non richiesto.

## 31.2 SMOTENC su feature miste: cosa genera un record sintetico

**[Livello: teoria consolidata del settore]** Per un record sintetico che deve sostituire una feature numerica, SMOTENC sceglie due (o più) vicini reali della classe minoritaria e interpola linearmente fra i loro valori — un'età sintetica di 54.3 anni, per esempio, se i due vicini hanno 52 e 58 anni. Per una feature categoriale, l'interpolazione lineare non avrebbe senso ("interpolare" fra "maschio" e "femmina" non produce una categoria valida), quindi SMOTENC assegna invece il valore **più frequente fra i vicini usati per generare quel record** — non un'invenzione, ma un prestito diretto da un caso reale osservato nelle vicinanze.

**[Fatto]** `balance_classes()` (`preprocessing.py:84-92`) applica questo meccanismo dopo l'imputazione (righe 47-53 di `preprocessing.py`, ordine confermato leggendo `preprocessing_data()`), il che significa che un record sintetico può a sua volta essere costruito interpolando fra valori già imputati — se due vicini reali avessero entrambi `ca` imputato con la stessa mediana (probabile, dato che il 66% dei valori di `ca` in Heart Disease sono quella stessa mediana, capitolo 29.3), il record sintetico erediterebbe quello stesso valore imputato, non uno nuovo. **[Interpretazione]** Questo significa che un record sintetico "eredita" silenziosamente il problema di qualità dei dati del capitolo 31.1: non lo introduce, ma nemmeno lo corregge — un record sintetico basato su vicini con `ca` imputato avrà quasi certamente anch'esso `ca` uguale al valore imputato, amplificando ulteriormente, nel training set finale, la presenza di quel singolo valore centrale al posto di una vera variabilità clinica.

> **PROVA TU —** apri `datas/heart_disease/preprocessing/X_train_raw.csv` (già presente nel repository, generato da un'esecuzione precedente) e conta quante righe hanno lo stesso identico valore di `ca` — un numero sorprendentemente alto per una feature che dovrebbe assumere solo 4 valori interi (0-3) osservati su un continuo di pazienti reali e sintetici. Non è un errore: è la conseguenza diretta e verificabile di quanto appena descritto.

## 31.3 Casi limite nella conversione a testo

**[Fatto]** Il capitolo 22.1 ha già mostrato che `_fmt_num()`, `_fmt_cat()`, `_fmt_bool()` e `_fmt_raw()` (`embedding.py:28-41,61-62`) gestiscono tutte esplicitamente un valore `NaN` residuo, scrivendo `"not recorded"` — un margine di sicurezza che, dato quanto visto in questo capitolo, non dovrebbe mai attivarsi nella pratica: se l'imputazione ha già sostituito ogni `NaN` con un valore concreto prima di questo punto della pipeline, `pd.isna(value)` dovrebbe restituire sempre `False` quando queste funzioni vengono chiamate. **[Da verificare]** Se questo margine di sicurezza sia mai stato osservato attivarsi in una vera esecuzione, o sia puro codice difensivo per un caso che nella pipeline attuale non si presenta mai — non ho eseguito la pipeline in questa sessione (per scelta esplicita, si veda il capitolo 43) per verificarlo direttamente, e resta una domanda aperta per l'Appendice E.

**[Fatto]** Un secondo caso limite riguarda `_fmt_cat()` (`embedding.py:33-36`), che traduce un codice numerico in un'etichetta leggibile cercandolo in un dizionario come `CP_LABELS`:
```python
def _fmt_cat(value, labels):
    if pd.isna(value):
        return "not recorded"
    return labels.get(int(round(float(value))), "unknown")
```
`labels.get(chiave, "unknown")` restituisce `"unknown"` se il codice, dopo essere stato arrotondato all'intero più vicino, non compare fra le chiavi del dizionario — un valore come `2.6` per `cp` (che non dovrebbe mai comparire in un dato reale, dove `cp` è un codice intero fra 1 e 4, ma **potrebbe** comparire in un record sintetico se SMOTENC, per errore di configurazione, trattasse per sbaglio una colonna categoriale come numerica) diventerebbe `3` dopo l'arrotondamento, e cercherebbe comunque una voce valida nel dizionario. **[Interpretazione]** Questo non è, in questo progetto, un rischio reale: `balance_classes()` (capitolo 21.2) passa esplicitamente l'elenco delle colonne categoriali a SMOTENC (`categorical_features=cat_idx`), che le tratta correttamente senza mai interpolarle come numeriche — ma il fatto che `_fmt_cat()` gestisca comunque il caso "codice sconosciuto" con un ripiego pulito (`"unknown"`, non un errore) è una buona pratica difensiva, verificabile a colpo d'occhio, indipendentemente dal fatto che si attivi mai nella pratica.

## Riepilogo

I due dataset di questo progetto presentano tre forme distinte di mancanza dei dati — esplicita, mascherata da un valore impossibile, e implicita per assenza di indicazione clinica — trattate tutte allo stesso modo indistinto dall'imputazione. SMOTENC, applicato dopo l'imputazione, può ereditare e amplificare silenziosamente questo problema nei record sintetici. La conversione finale a testo gestisce con cura i casi limite residui (valori ancora mancanti, codici categoriali sconosciuti), anche se almeno uno di questi margini di sicurezza non risulta mai attivarsi nella pipeline così come è costruita oggi.

## Domande di autoverifica

**1. Quali sono le tre forme distinte di "valore mancante" che compaiono in questo progetto, e come le tratta ciascuna il codice?**
Mancante esplicito (marcato `?`, letto come `NaN`), mancante mascherato da un valore fisiologicamente impossibile (0 per colesterolo/pressione, convertito esplicitamente in `NaN` solo per Heart Disease), e mancante per assenza di indicazione clinica (esami di laboratorio non richiesti in Diabetes130). Tutte e tre ricevono lo stesso trattamento indistinto in `impute_raw()`: mediana o moda, senza distinzione di causa.

**2. Perché un record sintetico generato da SMOTENC può avere lo stesso valore imputato di `ca` dei suoi vicini reali, invece di un valore nuovo?**
Perché SMOTENC interpola fra vicini reali già passati per l'imputazione: se quei vicini condividono lo stesso valore imputato (molto probabile per `ca`, imputato con la stessa mediana nel 66% dei casi), il record sintetico erediterà quel valore o uno molto simile, non una nuova osservazione indipendente.

**3. In quale scenario, teoricamente possibile ma non realizzato in questo progetto, `_fmt_cat()` restituirebbe `"unknown"` invece di un'etichetta valida?**
Se un valore categoriale, dopo arrotondamento all'intero più vicino, non corrispondesse a nessuna chiave del dizionario di etichette — uno scenario che richiederebbe un record con un codice categoriale non standard, cosa che SMOTENC non produce in questo progetto perché tratta correttamente le colonne categoriali come tali, non come numeriche.

> **MATERIALE PER LA TESI**
> 1. La tassonomia delle tre forme di mancanza dei dati, con il trattamento uniforme che il codice applica a tutte — riusabile in "Materiali e metodi" per una descrizione rigorosa della qualità dei dati.
> 2. L'analisi dell'interazione fra imputazione e SMOTENC, con l'ipotesi verificabile sull'amplificazione del valore imputato nei record sintetici — riusabile come punto di discussione originale, con l'esercizio pratico di verifica (§31.2) come base per una figura o una tabella nella tesi.
> 3. L'osservazione sul margine di sicurezza mai attivato in `_fmt_num`/`_fmt_cat`/`_fmt_bool`, esplicitamente marcata come domanda aperta — riusabile in Appendice E, e come esempio di codice difensivo scritto per un caso che la pipeline attuale non produce mai.
