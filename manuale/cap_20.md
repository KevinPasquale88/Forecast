# Capitolo 20 — `function.py`: la spina dorsale silenziosa

**Obiettivi del capitolo**

- Avere una mappa completa di tutto ciò che `function.py` mette a disposizione degli altri sette moduli.
- Leggere in dettaglio le due funzioni più significative del file: `get_output_dirs()` e `get_model_palette()`.
- Riconoscere il pattern comune a tutte le nove funzioni di plotting, senza doverle leggere una per una.

**[Fatto]** `function.py` (386 righe) è il file più lungo del progetto, e l'unico da cui tutti gli altri sette dipendono (Figura 17.1). Non contiene alcuna delle sette fasi della pipeline: è puro supporto — configurazione, percorsi, pulizia, grafici.

## 20.1 Config modelli e famiglie

**[Fatto]** Le prime 74 righe definiscono costanti di modulo, mai funzioni: gli schemi delle colonne per i due dataset (`columns`, `num_cols`, `cat_cols` per Heart Disease alle righe 10-15; `columns_diabetes130`, `num_cols_diabetes130`, `cat_cols_diabetes130` per Diabetes130 alle righe 21-35), la configurazione dei sette modelli (`models_ollama`, righe 38-43; `models_medical`, righe 45-49; `models_all`, riga 51), e due dizionari derivati: `MODEL_FAMILY` (riga 54, dict comprehension già vista al capitolo 8.2) e `FAMILY_COLORS` (righe 57-61).

## 20.2 Funzioni di I/O e pulizia cartelle

**[Fatto]** `get_output_dirs(dataset)` (righe 79-93) è probabilmente la funzione più chiamata dell'intero progetto — ogni fase, in ogni file, la invoca all'inizio:
```python
def get_output_dirs(dataset):
    if dataset not in datasets:
        raise ValueError(f"Invalid dataset '{dataset}'. Valid options are: {datasets}")
    base = os.path.join("datas", dataset)
    dirs = {
        "preprocessing": os.path.join(base, "preprocessing"),
        "embeddings": os.path.join(base, "embeddings"),
        "results": os.path.join(base, "results"),
        "graphics": os.path.join(base, "graphics"),
        "reports": os.path.join(base, "reports"),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs
```
Tre cose da notare, con lo sguardo di chi ha già letto la Parte II. Primo: la validazione (`if dataset not in datasets`) è l'unico controllo esplicito di correttezza su questo parametro in tutto il progetto — se non ci fosse, un nome di dataset sbagliato produrrebbe silenziosamente una nuova cartella `datas/<nomesbagliato>/` invece di un errore, perché `os.path.join` non sa cosa sia un dataset valido, sa solo concatenare stringhe. Secondo: `os.makedirs(d, exist_ok=True)` crea le cartelle se non esistono e non solleva errore se esistono già — l'opposto del comportamento di default di una `mkdir` che fallirebbe su una cartella esistente. Terzo: la funzione ha un **side-effect sul filesystem** (crea cartelle) dentro quella che sembra, dal nome, una semplice funzione "getter" — nulla nella firma lo segnala.

**[Fatto]** Le quattro funzioni `delete_files_*` (righe 179-209) condividono tutte la stessa struttura: ricevono una cartella, elencano i file al suo interno con `os.listdir()`, e cancellano quelli il cui nome contiene una delle stringhe di un elenco di pattern concordato a mano (per esempio `["model_performance","_y_true", "_y_score", ...]` per `delete_files_results`, riga 196). **[Interpretazione]** Questo significa che la sicurezza di questa pulizia dipende interamente dalla precisione di quegli elenchi di stringhe: un file che finisse per coincidenza per contenere una di quelle sottostringhe nel nome, anche se non prodotto da questo progetto, verrebbe cancellato senza distinzione — non c'è un controllo di formato o di provenienza, solo un controllo su una sottostringa nel nome del file.

## 20.3 Le nove funzioni di plotting

**[Fatto]** Le restanti circa 200 righe sono nove funzioni di plotting (`plot_data_heatmap`, `plot_umap`, `plot_boxplots`, `plot_roc_comparison`, `plot_confusion`, `plot_metric_comparison`, `plot_mean_ci`, `plot_family_comparison`, `plot_error_rates`, `plot_feature_deviation` — dieci, in realtà, contandole con cura), tutte costruite sullo stesso scheletro: ricevono dati già pronti (un DataFrame, un dizionario di risultati), costruiscono una figura con `matplotlib`/`seaborn`, e la salvano chiamando `save_figure()` (righe 157-159):
```python
def save_figure(fig, path_no_ext):
    fig.savefig(f"{path_no_ext}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(f"{path_no_ext}.pdf", bbox_inches="tight", facecolor="white")
```
Ogni grafico del progetto esiste quindi sempre in due formati — PNG a 300 DPI e PDF vettoriale — con un'unica funzione condivisa, non una duplicazione riga per riga in ciascuna delle nove funzioni.

**[Fatto]** La funzione più interessante di questo gruppo, non per la grafica che produce ma per la logica che contiene, è `get_model_palette()` (righe 162-174):
```python
def get_model_palette(model_names):
    family_members = {}
    for name in model_names:
        family = MODEL_FAMILY.get(name, "general-purpose")
        family_members.setdefault(family, []).append(name)
    palette = {}
    for family, members in family_members.items():
        base_color = FAMILY_COLORS.get(family, "#888888")
        shades = sns.light_palette(base_color, n_colors=len(members) + 1)[1:]
        for name, shade in zip(members, shades):
            palette[name] = shade
    return palette
```
Raggruppa prima i modelli per famiglia, poi genera per ciascuna famiglia tante sfumature del suo colore base quanti sono i suoi membri (`sns.light_palette`, scartando la prima sfumata più chiara con `[1:]` perché troppo simile allo sfondo bianco dei grafici), e infine associa ogni modello alla propria sfumatura con `zip()` (capitolo 8, uno dei due usi di `zip` nel progetto). Il risultato: modelli della stessa famiglia sono visivamente imparentati (stessa tonalità), ma distinguibili fra loro (sfumatura diversa) — un dettaglio di design che rende leggibile, a colpo d'occhio, la distinzione generalista/biomedico su cui si basa la seconda domanda di ricerca del progetto (capitolo 6.3).

> **RIFERIMENTO AL CODICE —** le altre otto funzioni di plotting seguono lo stesso schema di `save_figure()` + palette condivisa; non le leggiamo una per una qui — il riferimento completo di ognuna, con firma e parametri esatti, è in Appendice B. Le incontri comunque in azione, una alla volta, nei capitoli 21-27, dove ciascuna fase le richiama nel proprio contesto.

## Interfaccia pubblica (sintesi)

| Categoria | Nomi | Righe |
|---|---|---|
| Costanti di schema | `columns`, `num_cols`, `cat_cols`, `columns_diabetes130`, `num_cols_diabetes130`, `cat_cols_diabetes130` | 10-35 |
| Configurazione modelli | `models_ollama`, `models_medical`, `models_all`, `MODEL_FAMILY`, `FAMILY_COLORS` | 38-61 |
| Stato condiviso | `results`, `datasets` | 67-74 |
| Percorsi e pulizia | `get_output_dirs()`, `delete_files_embeddings()`, `delete_files_preprocessing()`, `delete_files_results()`, `delete_files_graphics()` | 79-93, 179-209 |
| Caricamento dati | `load_heart_disease()`, `load_diabetes130()` | 96-132 |
| Plotting | `save_figure()`, `get_model_palette()`, e nove funzioni `plot_*` | 134-387 |

## Errori tipici

Un `ValueError: Invalid dataset '...'` significa che `--dataset` (o il valore passato direttamente a una funzione) non è esattamente `"heart_disease"` o `"diabetes130"` — nessuna normalizzazione di maiuscole/minuscole o di spazi è applicata. Un grafico mancante o con colori inattesi, dopo aver aggiunto un modello (capitolo 19.3), è quasi sempre riconducibile a `FAMILY_COLORS` o `family_order` non aggiornati per una famiglia nuova.

## Riepilogo

`function.py` non implementa nessuna fase della pipeline: fornisce a tutte le altre la configurazione dei modelli, la risoluzione dei percorsi di output, la pulizia dei file di run precedenti, e ogni funzione di plotting del progetto. `get_output_dirs()` nasconde un side-effect sul filesystem dietro un nome che suggerisce una semplice lettura; `get_model_palette()` è l'unica funzione del file con una logica non banale, e garantisce coerenza visiva fra famiglie di modelli in ogni grafico.

## Domande di autoverifica

**1. Perché `get_output_dirs()` non è una funzione "pura" nel senso stretto del termine, nonostante il nome suggerisca solo una lettura?**
Perché, oltre a restituire un dizionario di percorsi, crea effettivamente le cartelle sul filesystem con `os.makedirs(..., exist_ok=True)` — un side-effect non visibile dalla sola firma della funzione.

**2. A cosa serve scartare la prima sfumatura generata da `sns.light_palette()` in `get_model_palette()`?**
Perché la prima sfumatura di una palette "chiara" tende a essere troppo simile allo sfondo bianco dei grafici del progetto, e quindi poco leggibile; scartarla (`[1:]`) garantisce che tutte le sfumature usate siano sufficientemente distinguibili dallo sfondo.

**3. Se cancellare un file per errore capitasse per una coincidenza di nome, quale funzione ne sarebbe responsabile e perché?**
Una delle quattro funzioni `delete_files_*`: cancellano qualunque file la cui cartella contenga una sottostringa di un elenco concordato a mano nel proprio nome, senza controllare che il file sia stato effettivamente prodotto da questo progetto.

> **MATERIALE PER LA TESI**
> 1. La tabella dell'interfaccia pubblica sintetica di `function.py` — riusabile come base per la sezione "Materiali e metodi" che descrive i componenti condivisi del sistema.
> 2. La lettura commentata di `get_model_palette()`, con la spiegazione del raggruppamento per famiglia — riusabile per motivare, nella tesi, la scelta di visualizzazione usata in tutti i grafici comparativi.
> 3. L'osservazione sulla fragilità delle funzioni `delete_files_*` basate su sottostringhe di nome file — riusabile come punto di discussione nella sezione critica sulla robustezza del codice.
