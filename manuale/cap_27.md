# Capitolo 27 — `generatereport.py`: l'ultimo miglio, e il suo limite più istruttivo

**Obiettivi del capitolo**

- Vedere come il progetto assembla, da solo, un report Markdown leggibile a partire da CSV e immagini già pronte.
- Verificare con i tuoi occhi, confrontando due report reali, che una parte del testo generato non dipende affatto dai dati.
- Sapere esattamente cosa cambieresti per rendere questo report onesto rispetto a quello che i dati dicono davvero.

**[Fatto]** `generatereport.py` (249 righe) è la fase 7, l'ultima (`main.py:52`): non calcola nulla di nuovo, assembla in un unico documento tutto ciò che le sei fasi precedenti hanno già prodotto.

## 27.1 Come si assembla un report Markdown da CSV e PNG

**[Fatto]** `generate_markdown()` (righe 41-227) costruisce il report accumulando stringhe in una lista Python, unita alla fine con `"\n".join(md)` (riga 227, `main`):
```python
md = []
md.append(f"# 📊 Encoder Evaluation Report\n")
md.append(f"**Generated:** {now}\n")
...
md.append(summary.to_markdown(index=False))
```
`DataFrame.to_markdown()` — un metodo di pandas che richiede `tabulate` come dipendenza (presente in `requirements.txt`, usata solo per questo scopo in tutto il progetto, verificato negli import) — converte automaticamente un intero DataFrame in una tabella Markdown con l'allineamento delle colonne già corretto, senza dover scrivere a mano i separatori `|` e `-`. Ogni immagine viene inclusa con un percorso relativo costruito esplicitamente (`real_roc_path = "../graphics/ROC_comparison.png"`, riga 74): il report vive in `datas/<dataset>/reports/`, i grafici in `datas/<dataset>/graphics/` o `results/` — da cartelle sorelle, un percorso relativo con `../` è l'unico modo di riferirsi a un file in una cartella diversa senza scrivere il percorso assoluto.

**[Fatto]** Ogni sezione del report è inclusa **condizionalmente**, verificando prima che il file esista (`if os.path.exists(roc_path):`, riga 75, ripetuto per ogni grafico e CSV): un report generato dopo un'esecuzione parziale della pipeline (capitolo 18.3) conterrebbe quindi solo le sezioni i cui file sono effettivamente presenti, senza sollevare un errore per quelli mancanti — un report incompleto ma valido, invece di un `FileNotFoundError` che bloccherebbe l'intera generazione.

## 27.2 Il caso del testo narrativo statico: quando il report "mente" per omissione

**[Fatto]** Le sezioni "Discussion and Observations", "Conclusions" e "Potential Improvements" (righe 192-225) non derivano da alcun calcolo sui dati appena descritti: sono stringhe Python scritte una volta, incluse identiche ogni volta che il report viene generato, indipendentemente dal dataset o dai risultati:
```python
md.append("## 🔍 Discussion and Observations\n")
md.append("""
- Larger embedding models (E5-large, GTE-large) generally show better performance.
- GTE-large tends to achieve higher ROC-AUC and tighter confidence intervals.
- Confusion matrices enable analysis of false positives and false negatives.
- Bootstrap is useful to verify metric stability and robustness.
""")
```
**[Fatto]** Puoi verificarlo tu stesso, senza fidarti della mia parola: apri `datas/heart_disease/reports/report.md` e `datas/diabetes130/reports/report.md`, entrambi già presenti nel repository, e confronta le rispettive sezioni "Discussion and Observations". Sono identiche, carattere per carattere. **[Fatto]** Confronta ora quel testo con le tabelle numeriche nella stessa pagina: in Heart Disease, l'AUC di `gte-large` (0.854, capitolo 44) è inferiore a quella di `pubmedbert` (0.885) e di `e5-large` (0.866); in Diabetes130, è inferiore a `sentence-biobert` (0.768), `bioclinicalbert` e `pubmedbert` (~0.757-0.758, capitolo 45). L'affermazione "GTE-large tends to achieve higher ROC-AUC" non è vera in nessuno dei due dataset che il report stesso presenta — è un template, non una sintesi dei dati.

> **ATTENZIONE —** questo non è un dettaglio stilistico: in un contesto in cui questo genere di report informasse una decisione reale (per esempio, quale modello di embedding adottare per un sistema clinico di supporto alla decisione), una conclusione narrativa sbagliata ma presentata con la stessa autorevolezza tipografica delle tabelle numeriche corrette è un rischio concreto, non teorico. Il capitolo 52 tratta questo punto come caso di studio autonomo, con tutto il rigore critico che merita.

## 27.3 Come lo riscriveresti tu

**[Interpretazione]** Rendere questa sezione onesta rispetto ai dati non richiederebbe una riscrittura complessa: `summary` (il DataFrame caricato da `encoder_comparison_summary.csv`, già disponibile in questa stessa funzione) contiene tutto il necessario per costruire la frase corretta a runtime — per esempio, `summary.loc[summary["auc_mean"].idxmax(), "model"]` restituirebbe il nome del modello con l'AUC media più alta per *quel* dataset specifico, sostituendo un'affermazione fissa e potenzialmente falsa con un'affermazione calcolata e sempre vera per costruzione.

> **PROVA TU —** scrivi tu la funzione che genera dinamicamente la frase "il modello con l'AUC più alta è X (Y)" a partire dal DataFrame `summary`, e confrontala con l'affermazione statica attuale su entrambi i dataset del progetto. Non è un esercizio puramente accademico: è precisamente il tipo di refactoring minimo, a basso rischio, che trasformerebbe il punto più debole di questo file nel suo punto di forza — un report che si adatta ai dati invece di ripetere sempre la stessa storia.

## Interfaccia pubblica

| Funzione | Parametri | Ritorna |
|---|---|---|
| `generate_report(dataset="heart_disease")` | Nome dataset | Nessuno (salva `report.md`) |
| `load_summary(summary_path)` | Percorso CSV | DataFrame |
| `load_statistical_results(wilcoxon_path, ttest_path, delong_path)` | 3 percorsi CSV | Dizionario di DataFrame o `None` |
| `generate_markdown(summary, dirs)` | DataFrame riassuntivo, percorsi | Stringa Markdown completa |

## Errori tipici

Un `FileNotFoundError` esplicito (non gestito condizionalmente, a differenza dei grafici) viene sollevato da `load_summary()` (righe 12-13) se `encoder_comparison_summary.csv` non esiste — l'unico file che questa fase considera davvero indispensabile, coerentemente con il fatto che è la tabella principale dell'intero report.

## Riepilogo

`generatereport.py` assembla un report Markdown completo da CSV e immagini già pronte, includendo ogni sezione solo se il file corrispondente esiste. Le sezioni discorsive finali (discussione, conclusioni, miglioramenti) sono però testo statico, identico in ogni esecuzione e per ogni dataset — al punto da contraddire, in almeno un caso verificabile, i numeri riportati nella stessa pagina. È il limite più istruttivo di tutto il progetto: un generatore di report che non legge i propri stessi dati per la parte più interpretativa del documento.

## Domande di autoverifica

**1. Perché il report può essere generato correttamente anche se, per esempio, il grafico UMAP non fosse mai stato prodotto?**
Perché ogni sezione verifica esplicitamente l'esistenza del proprio file prima di includerlo (`if os.path.exists(...)`), e in sua assenza semplicemente non aggiunge quella sezione, invece di sollevare un errore che bloccherebbe l'intero report.

**2. Come puoi dimostrare, senza fidarti di un'affermazione altrui, che il testo di "Discussion and Observations" non dipende dai dati?**
Confrontando carattere per carattere le sezioni corrispondenti dei due report reali già presenti nel repository (Heart Disease e Diabetes130): sono identiche, nonostante le tabelle numeriche sopra siano sostanzialmente diverse fra i due dataset.

**3. Con quale singola espressione, usando il DataFrame `summary` già disponibile nella funzione, potresti sostituire l'affermazione statica sul modello con l'AUC più alta?**
`summary.loc[summary["auc_mean"].idxmax(), "model"]` — restituisce il nome del modello con l'AUC media massima per il dataset corrente, calcolato a runtime invece di scritto a priori.

> **MATERIALE PER LA TESI**
> 1. Il confronto testuale diretto fra le due sezioni "Discussion and Observations" identiche, con i numeri reali che le contraddicono — è probabilmente l'osservazione critica singola più forte di tutto il libro: riusabile come caso di studio autonomo nella sezione "Discussione e limiti".
> 2. La proposta concreta di refactoring (§27.3), con l'espressione pandas esatta — riusabile nella sezione "Lavori futuri" come miglioramento a basso costo e alto impatto.
> 3. Lo schema di inclusione condizionale delle sezioni basato sull'esistenza del file — riusabile come esempio di buona pratica di robustezza, da contrapporre esplicitamente al problema del testo statico nello stesso file.
