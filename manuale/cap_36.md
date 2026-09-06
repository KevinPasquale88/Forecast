# Capitolo 36 — Bootstrap e intervalli di confidenza

**Obiettivi del capitolo**

- Avere la formulazione matematica completa del bootstrap non parametrico usato in questo progetto.
- Sapere da dove viene, con una formula precisa, la deviazione standard riportata accanto a ogni metrica.
- Capire perché 10.000 iterazioni è una scelta di stabilità, non un numero arbitrario, con un modo concreto per verificarlo tu stesso.

Il capitolo 24 ha già letto il codice del bootstrap riga per riga. Questo capitolo ne dà la formulazione matematica completa, per collegare quel codice al modo in cui la tesi dovrebbe descriverlo formalmente.

## 36.1 Ricampionamento con reinserimento

**[Livello: teoria consolidata del settore]** Dato un insieme di $n$ osservazioni già raccolte — qui, le triple (etichetta vera, punteggio, predizione) di un modello su tutti i suoi fold di validazione, `all_y_true`/`all_y_score`/`all_y_pred` di `classification.py`, capitolo 23.3 — il bootstrap genera $B$ campioni ricampionati, ciascuno di dimensione $n$, estraendo indici **con reinserimento** dall'insieme originale:

$$
I^{(b)} = \{i_1, \dots, i_n\}, \quad i_j \sim \mathcal{U}\{1, \dots, n\} \text{ indipendenti}, \qquad b = 1, \dots, B \tag{36.1}
$$

dove $\mathcal{U}\{1,\dots,n\}$ è la distribuzione uniforme discreta sugli indici da 1 a $n$. **[Fatto]** `idx = rng.integers(0, len(y_true), len(y_true))` (`evaluation.py:66`) implementa esattamente questo campionamento: `len(y_true)` estrazioni indipendenti, ciascuna uniforme su `len(y_true)` possibili indici, **con reinserimento** — lo stesso indice può comparire più volte in uno stesso $I^{(b)}$, e altri indici possono non comparire affatto. Per ciascun campionamento $I^{(b)}$, la metrica di interesse (accuratezza, F1, o AUC) viene ricalcolata sul sotto-campione così ottenuto:

$$
\hat{M}^{(b)} = M\big(\{y_{\text{true},i}\}_{i \in I^{(b)}}, \{y_{\text{pred},i}\}_{i \in I^{(b)}}\big), \qquad b = 1, \dots, B \tag{36.2}
$$

**[Fatto]** `acc_list.append(accuracy_score(yt, yp))` e le righe analoghe per F1 e AUC (`evaluation.py:68-70`) calcolano esattamente $\hat{M}^{(b)}$ per $B = 10.000$ (`n_iter=10000`, riga 62), producendo tre distribuzioni empiriche di 10.000 valori ciascuna — non un ricampionamento dei dati grezzi né un nuovo addestramento del modello, ma un ricampionamento delle **predizioni già ottenute** (capitolo 24.1).

## 36.2 Intervalli percentile al 95%

**[Livello: teoria consolidata del settore]** Con i $B$ valori bootstrap $\hat{M}^{(1)}, \dots, \hat{M}^{(B)}$ ordinati, l'intervallo di confidenza percentile al livello $\alpha$ (qui $\alpha=0.95$) è definito dai due percentili empirici:

$$
\text{IC}_{\alpha} = \Big[\, \hat{M}_{\left(\frac{1-\alpha}{2}\right)}, \;\; \hat{M}_{\left(\frac{1+\alpha}{2}\right)} \,\Big] = \big[\, \hat{M}_{(0.025)}, \; \hat{M}_{(0.975)} \,\big] \tag{36.3}
$$

dove $\hat{M}_{(p)}$ denota il $p$-esimo percentile empirico della distribuzione bootstrap. **[Fatto]** `ci()` (`evaluation.py:77-81`, capitolo 24.2) implementa esattamente questa formula con `np.percentile(a, (1-alpha)/2 * 100)` e `np.percentile(a, (1+alpha)/2 * 100)`. **[Fatto]** La deviazione standard bootstrap, mostrata come barra d'errore più spessa nei grafici (capitolo 24.2), è la deviazione standard campionaria ordinaria applicata ai $B$ valori:

$$
\widehat{SE}_{\text{boot}}(M) = \sqrt{\frac{1}{B-1}\sum_{b=1}^{B}\big(\hat{M}^{(b)} - \bar{M}\big)^2}, \qquad \bar{M} = \frac{1}{B}\sum_{b=1}^{B}\hat{M}^{(b)} \tag{36.4}
$$

**[Fatto]** implementata semplicemente da `bootstrap_metrics_dict['acc'].std()` (`evaluation.py:37`) — il metodo `.std()` di NumPy, applicato all'array dei 10.000 valori.

## 36.3 10.000 iterazioni: perché questo numero, cosa cambierebbe con 100 o 1.000.000

**[Livello: teoria consolidata del settore]** All'aumentare di $B$, la distribuzione empirica bootstrap converge alla vera distribuzione campionaria della metrica (nel limite $B \to \infty$), e l'errore di Monte Carlo sulla stima dei percentili della Formula 36.3 diminuisce proporzionalmente a $1/\sqrt{B}$. Con $B=100$, i percentili al 2.5%/97.5% sarebbero stimati da appena 2-3 osservazioni estreme in coda — una stima rumorosa. Con $B=10.000$, l'errore di Monte Carlo residuo è tipicamente trascurabile rispetto all'incertezza intrinseca della metrica stessa; **[Livello: teoria consolidata del settore]** valori come $B=1.000$ o $B=10.000$ sono comunemente considerati sufficienti in letteratura per stime percentili stabili, mentre $B=1.000.000$ ridurrebbe ulteriormente l'errore di Monte Carlo residuo a un costo computazionale centomila volte superiore, per un guadagno di precisione che, oltre una certa soglia, non è più praticamente rilevante rispetto alla variabilità intrinseca dei dati.

> **PROVA TU —** verifica tu stesso la stabilità di $B=10.000$ su un file già presente nel repository: carica `datas/heart_disease/results/e5-base_boot_auc.npy` (10.000 valori già calcolati), calcola l'intervallo di confidenza percentile sui primi 1.000 valori, poi sui primi 5.000, poi su tutti e 10.000. Se i tre intervalli sono già molto simili fra loro, hai una prova empirica diretta, specifica per questo progetto, che $B=10.000$ non è un numero scelto a caso ma un punto in cui la stima si è già stabilizzata.

## Riepilogo

Il bootstrap ricampiona con reinserimento le predizioni già ottenute (Formula 36.1), ricalcolando la metrica su ciascun ricampionamento (Formula 36.2) per costruire una distribuzione empirica di 10.000 valori, da cui si derivano sia l'intervallo di confidenza percentile (Formula 36.3) sia la deviazione standard bootstrap (Formula 36.4). Il numero di iterazioni, 10.000, è una scelta di stabilità statistica verificabile empiricamente sui dati stessi, non un valore arbitrario.

## Domande di autoverifica

**1. Cosa significa "con reinserimento" nella Formula 36.1, e perché è essenziale per il bootstrap?**
Significa che, estraendo un indice per il campione ricampionato, quell'indice resta disponibile per essere estratto di nuovo nelle estrazioni successive — lo stesso record può comparire più volte in un singolo ricampionamento, e altri record possono non comparire affatto. Senza reinserimento, ogni ricampionamento sarebbe identico all'insieme originale, e non ci sarebbe alcuna variabilità da misurare.

**2. Quale funzione di libreria implementa direttamente la Formula 36.4 (la deviazione standard bootstrap), e su quale oggetto viene chiamata?**
Il metodo `.std()` di NumPy, chiamato direttamente sull'array dei 10.000 valori bootstrap di una metrica (per esempio `bootstrap_metrics_dict['acc'].std()`).

**3. Come potresti verificare empiricamente, senza rieseguire la pipeline, che 10.000 iterazioni sono sufficienti per una stima stabile?**
Ricalcolando l'intervallo di confidenza percentile su un numero crescente delle 10.000 osservazioni bootstrap già salvate su disco (per esempio 1.000, poi 5.000, poi tutte e 10.000): se i risultati convergono e restano stabili ben prima di raggiungere le 10.000 osservazioni complete, è una prova diretta di adeguatezza per questo caso specifico.

> **MATERIALE PER LA TESI**
> 1. Le Formule 36.1-36.4 con la derivazione completa dall'idea generale del bootstrap al codice specifico — riusabili integralmente in "Materiali e metodi" per una descrizione rigorosa della metodologia di valutazione dell'incertezza.
> 2. L'argomento sulla convergenza dell'errore di Monte Carlo con $1/\sqrt{B}$, applicato alla scelta di $B=10.000$ — riusabile per giustificare formalmente, nella tesi, un parametro altrimenti presentato come arbitrario.
> 3. L'esercizio di verifica empirica di stabilità (§36.3), eseguibile sui dati già presenti nel repository — riusabile come misura originale e riproducibile da includere nella sezione "Risultati" o in un'appendice metodologica.
