# Capitolo 38 — Riduzione di dimensionalità e visualizzazione: UMAP

**Obiettivi del capitolo**

- Capire perché nessun grafico può mostrare direttamente uno spazio a 768 o 1024 dimensioni.
- Avere un'intuizione corretta di cosa fa UMAP, senza bisogno della sua matematica completa.
- Sapere cosa un grafico UMAP può dirti e cosa, con altrettanta certezza, non può dirti.

Questo è l'unico capitolo del libro dedicato a una tecnica **non supervisionata** (capitolo 2.1): UMAP non partecipa mai alla classificazione, serve solo a produrre due grafici del progetto.

## 38.1 Perché non si può "vedere" uno spazio a 768/1024 dimensioni

Un grafico a dispersione ordinario ha due assi: puoi disegnare punti in un piano, non in uno spazio a 768 coordinate. Se un embedding ha 768 (o 1024) numeri, e vuoi comunque farti un'idea visiva di come i punti si distribuiscono — se le due classi occupano regioni distinte o si sovrappongono, per esempio — devi prima **ridurre** quello spazio a due sole dimensioni, in un modo che preservi il più possibile la struttura importante dei dati originali.

**[Fatto]** Il progetto affronta questo problema in due punti distinti: `plot_umap()` (`function.py:223-234`, chiamata da `preprocessing.py:58`) proietta le feature *codificate* del preprocessing (non gli embedding testuali) in due dimensioni; nessun'altra parte della pipeline usa UMAP sugli embedding dei sette modelli — la proiezione visiva riguarda solo i dati tabellari codificati, non le rappresentazioni testuali su cui i classificatori vengono davvero addestrati.

## 38.2 UMAP in breve: vicinanza locale, ottimizzazione di un layout 2D

**[Livello: teoria consolidata del settore]** UMAP (*Uniform Manifold Approximation and Projection*) `[DA VERIFICARE — riferimento bibliografico completo: McInnes, Healy, Melville, 2018, da confermare con DOI/arXiv esatto prima della citazione finale]` funziona, a grandi linee, in due fasi. Nella prima, costruisce un grafo di vicinanza nello spazio ad alta dimensione: per ogni punto, individua i suoi vicini più prossimi e assegna un peso a ogni collegamento, più alto quanto più i due punti sono vicini — non una singola distanza globale, ma una struttura di relazioni **locali**. Nella seconda fase, UMAP cerca un layout a bassa dimensione (qui, 2D) che riproduca il più fedelmente possibile quelle stesse relazioni di vicinanza locale, ottimizzando iterativamente le posizioni dei punti — concettualmente simile a un sistema di molle che tira insieme i punti vicini e separa quelli lontani, fino a raggiungere una configurazione stabile.

**[Fatto]** `UMAP(n_components=2, random_state=42)` (`function.py:224`, da `umap-learn`, `requirements.txt`) usa i parametri di default della libreria per tutto il resto (numero di vicini considerati, distanza minima nel layout finale) — nessuno di questi iperparametri specifici di UMAP viene esplorato o discusso nel progetto, un punto che il capitolo 39 nota come parte della mappa completa degli iperparametri.

## 38.3 Cosa può e non può dirti un grafico UMAP

**[Livello: teoria consolidata del settore]** Un grafico UMAP può dirti, in modo affidabile, se punti **vicini nello spazio originale** restano vicini anche nella proiezione — è esattamente ciò per cui l'algoritmo è costruito. Se osservi due nuvole di punti ben separate, colorate secondo il target (`plot_umap()`, `function.py:227`, con `hue=y`), è ragionevole concludere che esiste una struttura locale nello spazio originale che separa le due classi almeno in parte.

**[Attenzione]** Un grafico UMAP **non può** dirti, con la stessa affidabilità, quanto siano davvero distanti due nuvole di punti, né se le dimensioni relative di due cluster nel grafico riflettano le dimensioni relative reali nello spazio originale: UMAP preserva la struttura di vicinanza *locale*, non le distanze *globali* fra regioni lontane — due cluster che appaiono ugualmente compatti nel grafico potrebbero avere una densità reale molto diversa nello spazio a 768 dimensioni. **[Interpretazione]** Questo è particolarmente rilevante per interpretare `datas/heart_disease/graphics/UMAP_Preprocessed Data + Embeddings.png` (già presente nel repository, capitolo 44): una separazione visiva incompleta fra le due classi in quel grafico non implica automaticamente che il problema sia difficile per un classificatore — un classificatore lineare (capitolo 32) lavora nello spazio a piena dimensione, non nella proiezione 2D, e può sfruttare separazioni che UMAP, per costruzione, non ha modo di mostrare fedelmente in due sole dimensioni.

> **PROVA TU —** apri il file UMAP già generato per Heart Disease e prova a descrivere, in una frase, cosa vedi — quante nuvole di punti distinte, quanto si sovrappongono le due classi. Poi confronta la tua impressione visiva con l'AUC media reale del modello migliore su questo dataset (capitolo 44): se l'AUC è alta ma la separazione visiva nel grafico UMAP ti sembra modesta, non è una contraddizione — è la conferma diretta che una proiezione 2D e un classificatore a piena dimensione possono legittimamente "vedere" gradi di separabilità diversi negli stessi dati.

## Riepilogo

Nessun grafico ordinario può mostrare direttamente uno spazio a centinaia di dimensioni: UMAP costruisce prima un grafo di vicinanza locale nello spazio originale, poi ottimizza un layout 2D che lo riproduca il più fedelmente possibile. È l'unica tecnica non supervisionata del progetto, usata solo per la visualizzazione delle feature codificate nella fase di preprocessing, mai per la classificazione. Un grafico UMAP è affidabile per giudicare la vicinanza locale fra punti, ma non le distanze globali fra cluster né, di riflesso, la difficoltà reale del problema per un classificatore che lavora nello spazio a piena dimensione.

## Domande di autoverifica

**1. Perché serve una tecnica come UMAP per visualizzare un embedding a 768 dimensioni, e non basterebbe scegliere due delle 768 coordinate a caso?**
Perché due coordinate scelte a caso conterrebbero solo una minima parte dell'informazione distribuita su tutte le 768 dimensioni. UMAP costruisce invece un layout 2D pensato apposta per preservare, il più fedelmente possibile, le relazioni di vicinanza locale presenti nell'intero spazio originale.

**2. In questo progetto, UMAP viene mai usato per decidere l'etichetta di un record o per addestrare il classificatore?**
No: `plot_umap()` produce solo un grafico a scopo di ispezione visiva, applicato alle feature codificate del preprocessing. I classificatori del progetto vengono sempre addestrati sugli embedding a piena dimensione, mai sulla loro proiezione 2D.

**3. Se due classi appaiono poco separate in un grafico UMAP, puoi concludere che il problema è difficile per un classificatore lineare che lavora sui dati originali?**
No, non automaticamente: UMAP preserva la struttura di vicinanza locale, non le distanze globali, e una proiezione a due dimensioni può nascondere una separabilità che esiste realmente nello spazio a piena dimensione. Il grafico UMAP e le prestazioni del classificatore misurano aspetti diversi, non necessariamente in accordo visivo diretto.

> **MATERIALE PER LA TESI**
> 1. La spiegazione in due fasi di UMAP (grafo di vicinanza locale, poi ottimizzazione del layout 2D), con l'avvertenza su cosa preserva e cosa no — riusabile in "Materiali e metodi" per la sezione sulla visualizzazione dei dati.
> 2. L'osservazione che UMAP, in questo progetto, opera solo sulle feature codificate del preprocessing e mai sugli embedding testuali usati per la classificazione — riusabile come chiarimento tecnico per prevenire un fraintendimento comune sul ruolo di questo grafico.
> 3. L'esercizio di confronto fra impressione visiva UMAP e AUC reale (§38.3) — riusabile come base per un paragrafo di discussione sui limiti interpretativi delle visualizzazioni a bassa dimensione.
