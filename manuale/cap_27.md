# Capitolo 27 — `generatereport.py`: l'ultimo miglio, e il suo limite più istruttivo

**Obiettivi del capitolo**

- Vedere come il progetto assembla, da solo, un report Markdown leggibile a partire da CSV e immagini già pronte.
- Conoscere il caso più istruttivo della storia di questo file: sezioni narrative che per lungo tempo non dipendevano affatto dai dati, fino a contraddirli.
- Vedere come il fix — calcolare la discussione e le conclusioni dai dati della run — ha trasformato il punto più debole del file nel suo punto più difendibile.

**[Fatto]** `generatereport.py` (311 righe) è la fase 8, l'ultima (`main.py:70`): non calcola nulla di nuovo, assembla in un unico documento tutto ciò che le sette fasi precedenti hanno già prodotto.

## 27.1 Come si assembla un report Markdown da CSV e PNG

**[Fatto]** `generate_markdown()` (righe 41-235) costruisce il report accumulando stringhe in una lista Python, unita alla fine con `"\n".join(md)` (riga 235):
```python
md = []
md.append(f"# 📊 Encoder Evaluation Report\n")
md.append(f"**Generated:** {now}\n")
...
md.append(summary.to_markdown(index=False))
```
`DataFrame.to_markdown()` — un metodo di pandas che richiede `tabulate` come dipendenza (presente in `requirements.txt`, usata solo per questo scopo in tutto il progetto, verificato negli import) — converte automaticamente un intero DataFrame in una tabella Markdown con l'allineamento delle colonne già corretto, senza dover scrivere a mano i separatori `|` e `-`. Ogni immagine viene inclusa con un percorso relativo costruito esplicitamente (`real_roc_path = "../graphics/ROC_comparison.png"`, riga 74): il report vive in `datas/<dataset>/reports/`, i grafici in `datas/<dataset>/graphics/` o `results/` — da cartelle sorelle, un percorso relativo con `../` è l'unico modo di riferirsi a un file in una cartella diversa senza scrivere il percorso assoluto.

**[Fatto]** Ogni sezione del report è inclusa **condizionalmente**, verificando prima che il file esista (`if os.path.exists(roc_path):`, riga 75, ripetuto per ogni grafico e CSV): un report generato dopo un'esecuzione parziale della pipeline (capitolo 18.3) conterrebbe quindi solo le sezioni i cui file sono effettivamente presenti, senza sollevare un errore per quelli mancanti — un report incompleto ma valido, invece di un `FileNotFoundError` che bloccherebbe l'intera generazione. **[Fatto]** Tra le sezioni condizionali c'è anche la nuova "Held-Out Test Set Evaluation" (righe 192-201), che include la tabella di `holdout_evaluation.csv` quando la fase 7 l'ha prodotta: le metriche sul 20% di test mai visto da addestramento, calibrazione della soglia o confronti fra modelli.

## 27.2 Il caso del testo narrativo statico: quando il report "mentiva" per omissione

**[Fatto]** Per gran parte della storia del progetto, le sezioni "Discussion and Observations", "Conclusions" e "Potential Improvements" non derivavano da alcun calcolo sui dati appena descritti: erano stringhe Python scritte una volta, incluse identiche ogni volta che il report veniva generato, indipendentemente dal dataset o dai risultati:
```python
md.append("## 🔍 Discussion and Observations\n")
md.append("""
- Larger embedding models (E5-large, GTE-large) generally show better performance.
- GTE-large tends to achieve higher ROC-AUC and tighter confidence intervals.
- Confusion matrices enable analysis of false positives and false negatives.
- Bootstrap is useful to verify metric stability and robustness.
""")
```
**[Fatto]** Il problema, scoperto confrontando carattere per carattere i due report reali allora presenti nel repository, era che le sezioni "Discussion and Observations" di Heart Disease e Diabetes130 erano identiche — e contraddette dalle tabelle numeriche nella stessa pagina: l'AUC di `gte-large` era inferiore a quella di `pubmedbert` e di altri modelli in **entrambi** i dataset. L'affermazione "GTE-large tends to achieve higher ROC-AUC" non era vera in nessuno dei due report che la contenevano — era un template, non una sintesi dei dati.

> **ATTENZIONE —** questo non era un dettaglio stilistico: in un contesto in cui questo genere di report informasse una decisione reale (per esempio, quale modello di embedding adottare per un sistema clinico di supporto alla decisione), una conclusione narrativa sbagliata ma presentata con la stessa autorevolezza tipografica delle tabelle numeriche corrette è un rischio concreto, non teorico. Il capitolo 52 tratta questo punto come caso di studio autonomo, con tutto il rigore critico che merita.

## 27.3 Come è stato riscritto — esattamente come lo avresti riscritto tu

**[Fatto]** Il fix (documentato in `docs/CHANGES.md`, §8) segue precisamente la strada che questa analisi suggeriva: `_build_discussion(summary)` (righe 238-266) calcola i propri punti dal DataFrame `summary` della run corrente — il modello con l'accuratezza, la macro-F1 e l'AUC medie più alte (`summary.loc[summary["auc_mean"].idxmax()]`), il modello con l'intervallo di confidenza AUC più stretto, e la famiglia con l'AUC media più alta, con l'avvertenza esplicita che quella media è descrittiva, non un test statistico. `_build_conclusions(summary, stat_results)` (righe 269-289) aggiunge il confronto con il baseline a maggioranza (50% per costruzione sul pool bilanciato) e, quando `delong_comparison.csv` esiste, conta quanti dei 21 confronti a coppie sono davvero significativi invece di dichiarare superiorità in blocco. Solo "Potential Improvements" resta un elenco fisso (righe 225-233) — legittimamente, perché è un elenco di suggerimenti futuri, non un'affermazione fattuale sui dati — aggiornato per non elencare più ciò che il fix stesso ha già realizzato.

> **PROVA TU —** rigenera i report per entrambi i dataset (o confronta i due `report.md` già nel repository, prodotti dalla pipeline corretta): le sezioni "Discussion and Observations" ora sono **diverse** fra Heart Disease e Diabetes130, e ciascuna nomina il modello che è davvero il migliore per quel dataset in quella run. È la dimostrazione più concreta del principio: un report che si adatta ai dati invece di ripetere sempre la stessa storia.

## Interfaccia pubblica

| Funzione | Parametri | Ritorna |
|---|---|---|
| `generate_report(dataset="heart_disease")` | Nome dataset | Nessuno (salva `report.md`) |
| `load_summary(summary_path)` | Percorso CSV | DataFrame |
| `load_statistical_results(wilcoxon_path, ttest_path, delong_path)` | 3 percorsi CSV | Dizionario di DataFrame o `None` |
| `generate_markdown(summary, dirs)` | DataFrame riassuntivo, percorsi | Stringa Markdown completa |
| `_build_discussion(summary)` | DataFrame riassuntivo | Stringa: osservazioni calcolate dai dati della run |
| `_build_conclusions(summary, stat_results)` | DataFrame riassuntivo, test statistici | Stringa: conclusioni calcolate dai dati della run |

## Errori tipici

Un `FileNotFoundError` esplicito (non gestito condizionalmente, a differenza dei grafici) viene sollevato da `load_summary()` (righe 12-13) se `encoder_comparison_summary.csv` non esiste — l'unico file che questa fase considera davvero indispensabile, coerentemente con il fatto che è la tabella principale dell'intero report.

## Riepilogo

`generatereport.py` assembla un report Markdown completo da CSV e immagini già pronte, includendo ogni sezione solo se il file corrispondente esiste, ora inclusa la valutazione holdout. Le sezioni discorsive (discussione e conclusioni) sono oggi calcolate dai dati della run corrente; per gran parte della storia del progetto erano invece testo statico, identico per ogni dataset — al punto da contraddire, in un caso verificato, i numeri riportati nella stessa pagina. Resta il caso più istruttivo di tutto il progetto: un generatore di report che non leggeva i propri stessi dati per la parte più interpretativa del documento, corretto esattamente con il refactoring minimo che l'analisi critica suggeriva.

## Domande di autoverifica

**1. Perché il report può essere generato correttamente anche se, per esempio, il grafico UMAP non fosse mai stato prodotto?**
Perché ogni sezione verifica esplicitamente l'esistenza del proprio file prima di includerlo (`if os.path.exists(...)`), e in sua assenza semplicemente non aggiunge quella sezione, invece di sollevare un errore che bloccherebbe l'intero report.

**2. Come era stato dimostrato, senza fidarsi di un'affermazione altrui, che il vecchio testo di "Discussion and Observations" non dipendeva dai dati?**
Confrontando carattere per carattere le sezioni corrispondenti dei due report reali allora presenti nel repository (Heart Disease e Diabetes130): erano identiche, nonostante le tabelle numeriche sopra fossero sostanzialmente diverse fra i due dataset — e la frase su GTE-large era smentita dai numeri in entrambi.

**3. Con quale espressione il codice attuale individua il modello con l'AUC più alta, invece di affermarlo a priori?**
`summary.loc[summary["auc_mean"].idxmax()]` in `_build_discussion()` — seleziona la riga del modello con l'AUC media massima per il dataset corrente, calcolata a runtime dal `summary` della run, ed è la stessa espressione che questa analisi proponeva come refactoring minimo prima che venisse implementata.

> **MATERIALE PER LA TESI**
> 1. Il caso di studio completo: le due sezioni "Discussion and Observations" identiche, i numeri reali che le contraddicevano, e il fix data-driven che le ha sostituite — probabilmente l'argomento critico singolo più forte di tutto il libro, riusabile come caso di studio autonomo nella sezione "Discussione e limiti".
> 2. Il refactoring realizzato (§27.3), con l'espressione pandas esatta e il riferimento a `docs/CHANGES.md` §8 — riusabile come esempio concreto di miglioramento a basso costo e alto impatto individuato dall'analisi e poi implementato.
> 3. Lo schema di inclusione condizionale delle sezioni basato sull'esistenza del file — riusabile come esempio di buona pratica di robustezza, da contrapporre esplicitamente al problema del testo statico nello stesso file.
