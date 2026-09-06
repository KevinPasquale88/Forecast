# Capitolo 29 — Il dataset UCI Heart Disease

**Obiettivi del capitolo**

- Sapere da dove viene davvero questo dataset, e perché non è un dataset a centro unico nonostante il nome comune "Cleveland" che spesso lo accompagna.
- Conoscere lo schema completo delle 14 feature standard, con le loro unità di misura e i loro codici.
- Avere i numeri reali di quanti dati mancano, centro per centro — non un'affermazione generica.

## 29.1 Origine e centri clinici

**[Fatto]** Il dataset proviene da quattro centri clinici distinti, integrati in un solo file dal progetto (`load_heart_disease()`, `function.py:96-113`): Cleveland Clinic Foundation (Stati Uniti), Hungarian Institute of Cardiology di Budapest, University Hospital di Zurigo (Svizzera), e V.A. Medical Center di Long Beach (Stati Uniti) — **[Fatto]** documentato in `docs/DATASET.md:11-15`, con fonte citabile: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1988). *Heart Disease*. UCI Machine Learning Repository. DOI: 10.24432/C52P4W.

**[Fatto]** Il progetto concatena tutti e quattro i file senza alcuna selezione (`pd.concat(dfs, ignore_index=True)`, `function.py:104`), per un totale di **920 righe** — non 297, la cifra che sia `README.md:78` sia `docs/DATASET.md:17` dichiarano. Il capitolo 4.2 ha già mostrato questa discrepanza; questo capitolo ne chiude l'origine con un dato preciso: **[Fatto]** il sottoinsieme Cleveland da solo, verificato in questa sessione, ha esattamente 4 righe con `ca` mancante e 2 con `thal` mancante — **4 + 2 = 6**, e 303 − 6 = 297. La cifra storicamente citata in letteratura corrisponde, con ogni evidenza, al solo centro di Cleveland dopo aver scartato le righe con dati mancanti nelle due feature più problematiche — non ai quattro centri concatenati che questo progetto usa davvero.

## 29.2 Schema delle 14 feature e valori mancanti mascherati da zero

**[Fatto]** Le 14 colonne standard, nell'ordine usato dal progetto (`function.py:10-13`):

| # | Colonna | Significato | Tipo | Note |
|---|---|---|---|---|
| 1 | `age` | Età in anni | Numerica | |
| 2 | `sex` | Sesso (1=maschio, 0=femmina) | Categoriale | |
| 3 | `cp` | Tipo di dolore toracico | Categoriale | 4 codici, `CP_LABELS` in `embedding.py:23` |
| 4 | `trestbps` | Pressione arteriosa a riposo | Numerica | mm Hg |
| 5 | `chol` | Colesterolo sierico | Numerica | mg/dl |
| 6 | `fbs` | Glicemia a digiuno > 120 mg/dl | Categoriale | booleano |
| 7 | `restecg` | Risultati elettrocardiografici a riposo | Categoriale | 3 codici, `RESTECG_LABELS` |
| 8 | `thalach` | Frequenza cardiaca massima raggiunta | Numerica | |
| 9 | `exang` | Angina indotta da sforzo | Categoriale | booleano |
| 10 | `oldpeak` | Depressione ST indotta da sforzo | Numerica | |
| 11 | `slope` | Pendenza del segmento ST da sforzo | Categoriale | 3 codici, `SLOPE_LABELS` |
| 12 | `ca` | Numero di vasi principali colorati da fluoroscopia | Numerica | 0-3 |
| 13 | `thal` | Talassemia | Categoriale | 3 codici, `THAL_LABELS` |
| 14 | `num` | Diagnosi (target) | — | binarizzato `(num>0)` |

**[Fatto]** Oltre ai valori mancanti espliciti (marcati `?` nel file sorgente, letti come `NaN` da pandas con `na_values="?"`, `function.py:103`), `function.py:110-111` applica una correzione specifica:
```python
df["chol"] = df["chol"].replace(0, np.nan)
df["trestbps"] = df["trestbps"].replace(0, np.nan)
```
**[Fatto]** Un valore di colesterolo o di pressione arteriosa pari a zero non è fisiologicamente possibile per un paziente vivo: è, con ogni evidenza, un secondo modo — oltre al `?` — con cui alcuni dei quattro centri hanno codificato l'assenza di misurazione. **[Fatto]** Verificato per file sorgente in questa sessione: **Switzerland ha `chol == 0` in tutte e 123 le righe**, VA in 49 delle sue 200, mentre Cleveland e Hungarian non hanno mai questo valore per il colesterolo; `trestbps == 0` compare una sola volta, in VA. **[Da verificare]** Questo dato misurato non corrisponde perfettamente al commento del codice (`function.py:107-109`) e a `docs/DATASET.md:56`, che attribuiscono il fenomeno a "Switzerland e Hungary": la mia verifica diretta sul file sorgente non trova alcuna occorrenza di `chol==0` nel file Hungarian — è una piccola imprecisione nella documentazione/commento del progetto, non nel comportamento del codice stesso (la riga `function.py:110` applica comunque la correzione corretta, converte 0 in NaN indipendentemente dal centro di provenienza).

## 29.3 Limiti noti

**[Fatto]** `docs/DATASET.md:52-56` dichiara esplicitamente quattro limiti: dati storici (anni '80-'90, possibile obsolescenza rispetto agli standard diagnostici attuali), sbilanciamento di classe nei dati originali (mitigato da SMOTENC, capitolo 21.2 — ma il capitolo 4.2 ha già mostrato che lo sbilanciamento reale è comunque mite, 55.3%/44.7%), bias geografico (prevalentemente centri occidentali), e valori mancanti gestiti tramite imputazione.

**[Fatto]** Quest'ultimo punto merita la precisione che la documentazione del progetto non fornisce: sulle 920 righe concatenate, `ca` manca nel **66.4%** dei casi e `thal` nel **52.8%** (comando Python eseguito, capitolo 4.2 aveva già introdotto questi due numeri). Scomposto per centro: `ca` manca nell'1% di Cleveland ma nel **99% di Hungarian, 96% di Switzerland, 99% di VA**; `thal` manca nell'1% di Cleveland ma nel **90% di Hungarian, 42% di Switzerland, 83% di VA**. **[Interpretazione]** In pratica, per due delle 14 feature standard di questo dataset, il valore reale è disponibile quasi solo per il centro di Cleveland: negli altri tre centri, l'imputazione con mediana o moda (`preprocessing.py:76-82`) non sta "colmando qualche buco" — sta assegnando lo stesso valore centrale, derivato quasi interamente da un quarto dei centri, alla stragrande maggioranza dei pazienti degli altri tre. Questo non emerge in nessun punto della documentazione esistente del progetto, ed è un limite sostanzialmente più serio di quanto "gestito tramite imputazione" lasci intendere.

> **ATTENZIONE —** questo limite si propaga silenziosamente fino al testo generato per l'embedding: `record_to_text_heart_disease()` (capitolo 22.1) scrive sempre un valore concreto per `thal` (per esempio "thalassemia: normal"), mai "non registrato", perché a quel punto della pipeline il valore mancante è già stato sostituito dall'imputazione. Un lettore del testo — umano o modello linguistico — non ha alcun modo di distinguere una misurazione reale da un valore imputato sulla maggioranza dei casi.

## Riepilogo

Heart Disease è un dataset a quattro centri, non a centro singolo: la cifra "297" della documentazione del progetto corrisponde al solo Cleveland dopo aver scartato 6 righe con dati mancanti critici, mentre il codice reale concatena tutti e quattro i centri per un totale di 920 righe. Due delle 14 feature standard (`ca`, `thal`) hanno dati realmente osservati quasi solo per Cleveland: negli altri tre centri, l'imputazione sostituisce con un valore centrale dal 42% al 99% dei valori, un limite quantificato qui per la prima volta con precisione.

## Domande di autoverifica

**1. Da dove viene, con ogni evidenza, la cifra "297" citata da `README.md` e `docs/DATASET.md` per questo dataset?**
Dal solo centro di Cleveland (303 righe) dopo aver scartato le 6 righe con valori mancanti in `ca` (4 righe) o `thal` (2 righe) — un sottoinsieme diverso, più piccolo e mono-centro, da quello che il codice del progetto carica realmente (4 centri, 920 righe, nessuna riga scartata).

**2. Perché la correzione `chol.replace(0, np.nan)` in `function.py:110` è necessaria oltre alla gestione dei `?` già presenti nel file?**
Perché alcuni centri clinici (verificato: Switzerland per tutte le sue righe, VA per una parte) codificano un valore mancante di colesterolo come 0 invece che come `?` — 0 mg/dl non è un valore fisiologicamente possibile, quindi va trattato come mancante quanto un `?` esplicito.

**3. Perché "l'imputazione gestisce i valori mancanti" è una descrizione insufficiente per le colonne `ca` e `thal` di questo dataset?**
Perché per queste due colonne i valori mancanti non sono un'eccezione isolata ma la norma in tre dei quattro centri (dal 42% al 99%): l'imputazione con mediana o moda, in questi casi, non completa dati sporadicamente assenti ma sostituisce la stragrande maggioranza dei valori con una singola stima aggregata derivata quasi interamente da un solo centro.

> **MATERIALE PER LA TESI**
> 1. La tabella completa delle 14 feature con tipo e significato (§29.2) — riusabile direttamente come tabella descrittiva del dataset in "Materiali e metodi".
> 2. La scomposizione per centro clinico della mancanza di dati in `ca` e `thal`, con la spiegazione precisa dell'origine della cifra "297" — è probabilmente la seconda osservazione critica più forte del libro dopo quella sul report statico: riusabile integralmente nella sezione "Discussione e limiti".
> 3. L'osservazione sulla propagazione silenziosa del valore imputato nel testo generato per l'embedding — riusabile come argomento specifico contro un'interpretazione troppo ottimistica delle prestazioni dei modelli biomedici su queste due feature.
