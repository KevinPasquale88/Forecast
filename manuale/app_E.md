# Appendice E — Zone d'ombra

> Domande aperte che questo libro non ha potuto chiudere leggendo solo il codice e i dati disponibili. Da girare a chi ha scritto il progetto, o da trattare esplicitamente come limite dichiarato in tesi. Ordinate per capitolo di prima comparsa.

1. **(capitolo 6, tech sheet §8.1)** A cosa serve `ucimlrepo` in `requirements.txt` se non risulta importata in nessuno dei nove file di `master`? Possibile residuo di uno script di download dati precedente, mai rimosso dal file delle dipendenze.

2. **(capitolo 15.2, capitolo 16.1)** Il comando `ollama pull yxchia/multilingual-e5-base` in `README.md:104` è un refuso di battitura o il residuo di una versione precedente del progetto che usava davvero quel modello, prima di passare a `jeffh/intfloat-e5-base-v2:q8_0` in `function.py:39`?

3. **(capitolo 27.2, capitolo 52)** Il testo narrativo statico di `generatereport.py:192-225` è una funzionalità incompleta (mai finita di implementare) o una scelta consapevole per un primo prototipo di report, poi mai rivista?

4. **(capitolo 29.1, tech sheet §7bis)** La cifra "297" in `docs/DATASET.md:17`/`README.md:78` è un refuso ereditato dalla letteratura, il residuo di una versione precedente del progetto che usava solo il sottoinsieme Cleveland, o un'altra causa? Il capitolo 29.1 fornisce un'inferenza motivata (4+2=6 righe scartate spiegano esattamente 303-6=297) ma non una conferma diretta da chi ha scritto la documentazione.

5. **(capitolo 29.3, capitolo 31.1, capitolo 46.2)** L'imputazione di `ca`/`thal` (Heart Disease) e `max_glu_serum`/`A1Cresult` (Diabetes130) su una maggioranza di valori mancanti è una scelta consapevole (per esempio, per mantenere il numero di feature costante fra i due dataset) o un'assunzione non esaminata dagli autori originali? Un'alternativa — escludere queste feature, o aggiungere un indicatore esplicito di "valore imputato" — non risulta mai considerata nel codice.

6. **(capitolo 31.3)** Il margine di sicurezza per valori `NaN` residui in `_fmt_num()`, `_fmt_cat()`, `_fmt_bool()` (`embedding.py:28-41`) si è mai attivato in una vera esecuzione della pipeline, o è codice difensivo per un caso che l'attuale sequenza imputazione→SMOTENC→conversione a testo non produce mai?

7. **(capitolo 54.1, tech sheet §8.2)** Quale dei tre modelli biomedici (o, meno probabilmente, uno dei quattro generalisti) è effettivamente designato da `EMBEDDING_MODEL` nella copia divergente di `function.py` sul branch `chatbot`? Il capitolo 54.1 offre un'inferenza motivata (l'uso di `SentenceTransformer` suggerisce un modello biomedico, non uno via Ollama) ma non ha letto quella versione specifica del file.

8. **(Appendice D)** L'elenco completo degli autori del paper E5 (Wang et al., 2022) riportato in questo libro proviene da una fonte secondaria (aggregatori di paper), non dal PDF originale: va confermato prima di una citazione che richieda precisione assoluta sull'ordine degli autori.

9. **(Appendice D)** Il modello `pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb` (sentence-biobert, `function.py:48`) è una variante fine-tuned di BioBERT: quale pubblicazione, se esiste, descrive esattamente questo fine-tuning specifico (oltre al BioBERT di base, già citato)? Non cercata in questa sessione.

10. **(Appendice D)** L'attribuzione del modello `NeuML/pubmedbert-base-embeddings` (`function.py:47`) alla linea di ricerca PubMedBERT non è stata verificata con una ricerca dedicata in questa sessione: non citare l'origine accademica di questo modello specifico senza prima confermarla.

## Come usare questa lista

Ogni voce è formulata come domanda diretta, pronta per essere girata al relatore o a chi ha scritto il codice originale. Le voci 1-7 riguardano il codice e i dati del progetto; le voci 8-10 riguardano solo la precisione bibliografica e non intaccano la comprensione tecnica del progetto.
