# Capitolo 28 — `main.py`: l'orchestratore letto per ultimo apposta

**Obiettivi del capitolo**

- Rileggere l'intero file più corto e più centrale del progetto, ora che conosci ciascuna delle sette fasi che orchestra.
- Sapere esattamente cosa fa, e cosa non fa, il parsing degli argomenti da riga di comando.
- Capire dove e come inseriresti un'ottava fase, se dovessi estendere la pipeline.

**[Fatto]** `main.py` (56 righe) è il file più corto del progetto — e non a caso è l'ultimo che questo libro legge per intero: ogni riga chiama una funzione già vista nei capitoli 20-27, e leggerlo ora, con quella conoscenza già in mano, richiede pochi minuti invece di una nuova esplorazione.

## 28.1 Le sette fasi in ordine, con un occhio a ciò che già conosci

**[Fatto]** L'intera logica del file sta in `main()` (righe 20-55):
```python
def main():
    args = parse_args()
    dirs = get_output_dirs(args.dataset)
    delete_files_embeddings(dirs["embeddings"])
    delete_files_preprocessing(dirs["preprocessing"])
    delete_files_results(dirs["results"])
    delete_files_graphics(dirs["graphics"])
    X,y = preprocessing_data(dataset=args.dataset)
    embeddings(X, y, dataset=args.dataset)
    training_classifier(dataset=args.dataset)
    evaluate_results(dataset=args.dataset)
    analyze_errors(dataset=args.dataset)
    test_statistical_tests(dataset=args.dataset)
    generate_report(dataset=args.dataset)
```
Tredici righe, sette chiamate di fase più quattro di pulizia preliminare — ognuna delle quali hai già letto in dettaglio: `get_output_dirs` e le quattro `delete_files_*` al capitolo 20.2, `preprocessing_data` al capitolo 21, `embeddings` al capitolo 22, `training_classifier` al capitolo 23, `evaluate_results` al capitolo 24, `analyze_errors` al capitolo 25, `test_statistical_tests` al capitolo 26, `generate_report` al capitolo 27. Non c'è altro codice di rilievo in questo file: nessuna logica propria, solo composizione di funzioni altrui, nell'ordine esatto in cui il capitolo 17 (Figura 17.1) le ha già mostrate a diagramma.

**[Fatto]** Nota che `X, y = preprocessing_data(...)` è l'unico punto in cui `main()` maneggia dati concreti, non solo nomi di dataset: è la stessa asimmetria già notata al capitolo 17.1, qui visibile direttamente nella firma delle chiamate — solo la prima ha un valore di ritorno che il chiamante riusa esplicitamente (`embeddings(X, y, ...)`), tutte le altre restituiscono `None` implicitamente e comunicano solo tramite file su disco.

## 28.2 Il flag `--dataset` e il comportamento di default

**[Fatto]** `parse_args()` (righe 12-18) definisce un solo argomento da riga di comando:
```python
def parse_args():
    parser = argparse.ArgumentParser(description="Run the clinical embedding benchmark pipeline.")
    parser.add_argument(
        "--dataset", choices=["heart_disease", "diabetes130"], default="heart_disease",
        help="Clinical dataset to use (default: heart_disease)."
    )
    return parser.parse_args()
```
`choices=[...]` fa sì che `argparse` rifiuti da solo, prima ancora che il codice del progetto veda il valore, qualunque stringa diversa dalle due elencate — con un messaggio di errore e uscita dal programma, non un `ValueError` sollevato più a valle come quello di `get_output_dirs()` (capitolo 20.2, che a questo punto non può mai essere raggiunto con un valore non valido passato da riga di comando, ma resta comunque necessario per chi chiamasse `get_output_dirs()` direttamente da un altro punto del codice, bypassando `argparse`). `default="heart_disease"` è la fonte esatta del comportamento già segnalato in più punti del libro (capitolo 0.3, capitolo 15.2): eseguire `python main.py` senza alcun flag esegue silenziosamente solo Heart Disease.

> **SE VIENI DA JAVA —** `argparse` gioca, per uno script a riga di comando, un ruolo concettualmente simile a una libreria come `picocli` o `JCommander`: dichiari gli argomenti attesi con le loro proprietà (tipo implicito, valori ammessi, default, testo di aiuto), e la libreria genera da sola sia il parsing sia un messaggio di `--help` leggibile — non devi scrivere a mano l'analisi di `sys.argv`.

## 28.3 Cosa succederebbe ad aggiungere una fase 8

**[Interpretazione]** Aggiungere una fase 8 — per esempio, una calibrazione delle probabilità (capitolo 55) da eseguire dopo la classificazione — richiederebbe, seguendo esattamente il pattern già stabilito da questo file: (1) un nuovo modulo `calibration.py` con una funzione `calibrate_probabilities(dataset="heart_disease")` che riceve solo il nome del dataset e rilegge da disco ciò che le serve, coerentemente con lo stile delle fasi 3-7 (capitolo 17.1); (2) un `import` aggiuntivo in cima a `main.py`; (3) una riga in più dentro `main()`, nella posizione giusta della sequenza. Nessuna delle sette fasi esistenti dovrebbe cambiare.

> **ATTENZIONE —** questa semplicità apparente nasconde lo stesso limite già visto al capitolo 18.3: la nuova fase erediterebbe automaticamente l'assenza di gestione degli errori (nessun `try`/`except` attorno alle chiamate in `main()`) e l'assenza di ripartenza da un punto intermedio. Estendere la pipeline seguendo il pattern esistente è facile; renderla più robusta nel farlo richiederebbe intervenire anche sul file che, in questo capitolo, sembra il più semplice di tutti.

## Interfaccia pubblica

| Funzione | Parametri | Effetti |
|---|---|---|
| `main()` | Nessuno (legge `sys.argv` tramite `parse_args()`) | Esegue l'intera pipeline per il dataset scelto |
| `parse_args()` | Nessuno | Restituisce un oggetto `Namespace` con l'attributo `dataset` |

`if __name__ == "__main__": main()` (riga 54) è l'idioma standard che permette a questo file di essere sia eseguito direttamente (`python main.py`) sia importato da un altro modulo senza eseguire automaticamente `main()` — un pattern che nessun altro file di questo progetto usa, perché nessun altro file è pensato per essere il punto di ingresso da riga di comando.

## Errori tipici

Un messaggio `error: argument --dataset: invalid choice` proviene direttamente da `argparse`, prima ancora che una sola riga del progetto venga eseguita — segnala un valore diverso da `heart_disease` o `diabetes130` passato al flag. Qualunque altro errore, a valle di questo punto, appartiene a una delle sette fasi già trattate nei capitoli precedenti, non a `main.py` stesso.

## Riepilogo

`main.py` non contiene alcuna logica propria: compone, in un ordine fisso, la pulizia preliminare e le sette fasi già lette nei capitoli 20-27, passando sempre e solo il nome del dataset scelto. `argparse` gestisce da solo la validazione dell'unico argomento del progetto, con un default (`heart_disease`) che determina il comportamento più frequentemente frainteso dell'intera pipeline. Estendere la sequenza con una fase aggiuntiva è meccanicamente semplice, ma erediterebbe gli stessi limiti di gestione degli errori già discussi al capitolo 18.3.

## Domande di autoverifica

**1. Perché `main.py` è, a ragione, il file più semplice da leggere una volta arrivati a questo punto del libro?**
Perché non contiene logica propria: ogni riga chiama una funzione appartenente a uno degli otto file già letti nei capitoli precedenti, nell'ordine già visto nel diagramma architetturale del capitolo 17.

**2. Perché un valore non valido passato a `--dataset` non arriva mai a far scattare il `ValueError` di `get_output_dirs()` in `function.py`?**
Perché `argparse`, grazie a `choices=["heart_disease", "diabetes130"]`, intercetta e rifiuta un valore non valido prima ancora che il codice del progetto venga eseguito, terminando il programma con un proprio messaggio d'errore.

**3. Quali tre modifiche servirebbero, in linea di principio, per aggiungere una fase 8 alla pipeline?**
Un nuovo modulo con una funzione che segue lo stesso pattern delle fasi esistenti (riceve solo il nome del dataset, rilegge da disco ciò che le serve), un nuovo `import` in cima a `main.py`, e una riga aggiuntiva dentro `main()` nella posizione corretta della sequenza — senza modificare nessuna delle fasi esistenti.

> **MATERIALE PER LA TESI**
> 1. Il diagramma testuale delle tredici righe di `main()`, con il rimando a ciascun capitolo che tratta la fase corrispondente — riusabile come sintesi finale della sezione "Materiali e metodi".
> 2. La spiegazione precisa del meccanismo `choices`/`default` di `argparse` e delle sue conseguenze pratiche — riusabile come nota tecnica su un comportamento di default facilmente frainteso.
> 3. La guida meccanica per aggiungere una fase 8, con l'avvertenza sui limiti ereditati — riusabile come base diretta per una proposta concreta nella Parte XII (Estensioni e lavori futuri).
