# Capitolo 26 — `statisticaltest.py`: tre test, tre garanzie diverse

**Obiettivi del capitolo**

- Leggere come il progetto confronta a coppie tutti e sette i modelli, per tre metriche, con tre test diversi.
- Sapere cosa testano davvero Wilcoxon, t-test appaiato e DeLong, e su quali dati esattamente.
- Riconoscere perché usarli insieme è una scelta di robustezza, non una ridondanza.

**[Fatto]** `statisticaltest.py` (123 righe) è la fase 6 (`main.py:49`): l'unico file che confronta esplicitamente i modelli fra loro, invece di descriverli uno alla volta.

## 26.1 Wilcoxon e t-test appaiato sulle distribuzioni bootstrap

**[Fatto]** `test_statistical_tests()` (righe 10-68) confronta ogni coppia possibile fra i sette modelli, per ciascuna delle tre metriche, usando le distribuzioni bootstrap già salvate da `evaluation.py`:
```python
for metric in metrics:
    boot_scores = {}
    for model_name in models:
        boot_scores[model_name] = np.load(os.path.join(dirs["results"], f"{model_name}_boot_{metric}.npy"))
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            a, b = models[i], models[j]
            scores_a, scores_b = boot_scores[a], boot_scores[b]
            stat_w, p_w = wilcoxon(scores_a, scores_b)
            ...
            stat_t, p_t = ttest_rel(scores_a, scores_b)
```
`for j in range(i + 1, len(models))`, non `range(len(models))`, è la forma standard per generare ogni coppia **una sola volta** (confrontare A con B è la stessa cosa di confrontare B con A, non serve farlo due volte) — con 7 modelli, questo produce $\binom{7}{2} = 21$ confronti per metrica, 63 in totale per i tre test Wilcoxon/t-test, più 21 per DeLong (capitolo 26.2).

**[Livello: teoria consolidata del settore]** Sia Wilcoxon sia il t-test appaiato confrontano due campioni **accoppiati** — qui, i 10.000 valori bootstrap di un modello contro i 10.000 valori bootstrap corrispondenti dell'altro, ricampionati con lo stesso seme (capitolo 24.1) e quindi confrontabili posizione per posizione. Il **test di Wilcoxon signed-rank** è non parametrico: non assume che le differenze fra coppie seguano una distribuzione normale, e si basa sui ranghi delle differenze, non sui loro valori esatti — più robusto quando la distribuzione reale si discosta dalla normalità, un'ipotesi spesso ragionevole per dati clinici. Il **t-test appaiato** assume invece che le differenze siano approssimativamente normali, e in cambio ha più potenza statistica (rileva differenze più piccole come significative) se quell'assunzione regge davvero. **[Fatto]** Entrambi restituiscono una statistica del test e un p-value, salvati insieme alle medie dei due modelli e a un flag binario di significatività a $\alpha = 0.05$ (righe 44,57: `"1" if p_w < 0.05 else "0"`) — **[Attenzione]** notato come stringa `"1"`/`"0"`, non come intero o booleano: un dettaglio da tenere presente se in futuro si volesse filtrare il CSV risultante per riga significativa, perché un confronto numerico diretto (`== 1`) fallirebbe silenziosamente contro una stringa.

## 26.2 Il test di DeLong e la libreria `MLstatkit`

**[Fatto]** `test_delong()` (righe 70-124) confronta, per ogni coppia di modelli, l'AUC calcolata sugli stessi dati di validazione, usando una libreria esterna:
```python
from MLstatkit import Delong_test
...
z, p, auc_a, auc_b = Delong_test(
    y_true_a, scores[a]["y_score"], scores[b]["y_score"],
    return_ci=False, return_auc=True, verbose=0,
)
```
**[Livello: teoria consolidata del settore]** Il **test di DeLong** è specifico per confrontare due AUC calcolate sugli *stessi* casi (stesse etichette vere): a differenza di Wilcoxon e t-test applicati qui alle distribuzioni bootstrap, DeLong lavora direttamente sui punteggi di probabilità originali (`y_score`) e tiene conto esplicitamente della correlazione fra le due AUC che nasce dal fatto che entrambi i modelli sono valutati sugli stessi pazienti — ignorare questa correlazione (per esempio trattando le due AUC come se venissero da campioni indipendenti) produrrebbe una stima della significatività meno accurata. **[Fatto]** Prima di ogni confronto, il codice verifica esplicitamente che le etichette vere dei due modelli coincidano (righe 91-93: `if not np.array_equal(y_true_a, y_true_b): print("[WARNING] ...") continue`) — una precondizione necessaria perché il test di DeLong abbia senso, dato che confronta AUC sugli stessi casi.

**[Fatto]** `MLstatkit` (`requirements.txt`, versione 0.1.91) è l'unica dipendenza del progetto dedicata a un singolo test statistico specifico, non a una libreria generalista come `scipy` (da cui vengono `wilcoxon` e `ttest_rel`, riga 6-7) — una scelta che riflette quanto un'implementazione corretta del test di DeLong sia più delicata da scrivere da zero rispetto a un t-test o a un Wilcoxon, entrambi disponibili direttamente in `scipy.stats`.

## 26.3 Perché tre test invece di uno

**[Fatto]** `docs/STATISTICAL_TESTS.md:84-90` motiva esplicitamente la scelta di tutti e tre: Wilcoxon è più robusto se la normalità non regge, il t-test appaiato è più potente se regge, DeLong è specifico per l'AUC e tiene conto della correlazione fra modelli valutati sugli stessi casi. **[Interpretazione]** La logica sottostante è quella della **triangolazione metodologica**: se tre test con assunzioni diverse concordano tutti sulla stessa conclusione (differenza significativa o meno), la fiducia in quella conclusione è più alta che se si fosse usato un solo test — e se invece i tre test discordassero fra loro su uno stesso confronto, sarebbe un segnale che il risultato è al limite della soglia di significatività, non un errore da correggere scegliendo il test che dà la risposta preferita.

> **PROVA TU —** apri `datas/heart_disease/results/wilcoxon_comparison.csv`, `ttest_comparison.csv` e `delong_comparison.csv` (già presenti nel repository, capitolo 44) e cerca una coppia di modelli per cui i tre test non concordino tutti sulla stessa conclusione di significatività. Se la trovi, è un candidato naturale per una discussione più approfondita nella tesi — un punto in cui la robustezza della "significatività" del confronto meriterebbe una frase in più, non solo una tabella.

## Interfaccia pubblica

| Funzione | Parametri | Effetti |
|---|---|---|
| `test_statistical_tests(dataset="heart_disease")` | Nome dataset | Salva `wilcoxon_comparison.csv`, `ttest_comparison.csv`; chiama `test_delong()` |
| `test_delong(dirs)` | Dizionario percorsi | Salva `delong_comparison.csv` |

## Errori tipici

Un avviso `[WARNING] y_true diversi per A vs B — skip` in console indica che due modelli hanno numeri di record di validazione diversi o etichette diverse per lo stesso indice — atteso solo se le fasi precedenti sono state eseguite in modo incoerente fra loro (per esempio rieseguendo `classification.py` per un solo modello dopo aver cambiato il numero di fold). Un `FileNotFoundError` su un file `_boot_*.npy` segnala che `evaluation.py` non ha completato per quel modello.

## Riepilogo

`statisticaltest.py` confronta ogni coppia dei sette modelli con tre test diversi — Wilcoxon e t-test appaiato sulle distribuzioni bootstrap, DeLong sull'AUC diretta con una libreria dedicata — motivati dalla logica della triangolazione: tre garanzie statistiche diverse, la cui concordanza rafforza la fiducia nella conclusione più di quanto farebbe un singolo test.

## Domande di autoverifica

**1. Perché il ciclo di confronto usa `range(i + 1, len(models))` per l'indice interno, invece di ripartire sempre da zero?**
Per generare ogni coppia di modelli una sola volta: confrontare il modello A con il modello B è statisticamente equivalente a confrontare B con A, e ripetere entrambi i confronti raddoppierebbe il lavoro senza aggiungere informazione.

**2. Perché il test di DeLong non può essere applicato a due modelli le cui etichette vere di validazione non coincidono esattamente?**
Perché il test è pensato per confrontare due AUC calcolate sugli stessi casi, tenendo conto della correlazione che nasce da questa condivisione — se le etichette vere differiscono, i due modelli non sono stati valutati sugli stessi record, e il confronto perderebbe il suo fondamento statistico.

**3. Cosa significherebbe, in pratica, se Wilcoxon e t-test appaiato concordassero su una differenza significativa fra due modelli, ma DeLong sull'AUC non la trovasse significativa?**
Che le distribuzioni bootstrap di accuratezza e F1 differiscono in modo significativo fra i due modelli, ma la differenza di AUC specifica, calcolata direttamente sui punteggi originali, non raggiunge la soglia di significatività — un segnale che la differenza è reale su alcune metriche ma non necessariamente sulla capacità discriminante complessiva misurata dall'AUC.

> **MATERIALE PER LA TESI**
> 1. La spiegazione comparata dei tre test con le rispettive assunzioni e garanzie — riusabile in "Materiali e metodi" per motivare il protocollo di confronto statistico.
> 2. L'argomento della triangolazione metodologica, con il rimando a `docs/STATISTICAL_TESTS.md` — riusabile per giustificare, nella tesi, perché tre test concordanti rafforzino la fiducia nei risultati più di un singolo test.
> 3. L'esercizio di ricerca di un disaccordo fra i tre test sui dati reali (§26.3) — riusabile come base concreta per un paragrafo di discussione sui confronti statisticamente "al limite".
