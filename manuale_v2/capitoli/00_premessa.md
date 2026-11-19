# Premessa

## A chi serve questo libro e come leggerlo

Questo libro raccoglie tutto ciò che serve per scrivere e discutere la tesi sul progetto Forecast: il problema clinico, la teoria di machine learning e statistica che il progetto usa, il codice modulo per modulo, i dati, i risultati, la storia delle correzioni metodologiche, il chatbot, i limiti e le domande che una commissione può fare.

È la seconda edizione del manuale. La prima (`manuale/`, settembre 2026) descriveva una versione della pipeline che è stata poi corretta in punti sostanziali: oversampling con SMOTENC prima della cross-validation, imputazione dei valori mancanti, soglia scelta su una porzione separata, frasi troncate a 100 token. Questa edizione descrive la pipeline del branch `fix/port-chatbot-corrections` (14 novembre 2026) e sostituisce la prima per tutto ciò che riguarda metodo e risultati.

Tre percorsi di lettura:

- **Per scrivere la tesi**: Parte I (contesto), Parte II (modelli di linguaggio), Parte V (dati), Parte VI (metodo), Parte VII (risultati), Parte VIII (correzioni), Parte X (discussione) e Parte XI (dalla tesi alla discussione).
- **Per capire il codice**: Parte III (Python per chi viene da Java), Parte IV (architettura e codice), Appendice D (comandi e file).
- **Per preparare la discussione**: capitolo 42 (domande della commissione), capitolo 39 (limiti), capitolo 36 (correzioni), capitoli 32.4 e 33 (le due analisi più delicate), Appendice A (glossario).

## Convenzioni

- I nomi di file, funzioni, variabili e parametri sono scritti in `monospazio`.
- I numeri usano la virgola decimale nel testo ("0,887") e il punto nel codice e nei nomi di file.
- Ogni risultato numerico viene da un file preciso della run citata; il file è indicato accanto alla tabella.
- **Riquadri.** Le note marcate *Per la tesi* indicano come usare un argomento nel testo della tesi; quelle marcate *Attenzione* segnalano un errore facile da commettere; quelle marcate *Da verificare* indicano un'informazione che va controllata su fonte primaria prima di citarla.

## Lo stato dei risultati al 14 novembre 2026

| Elemento | Stato |
| --- | --- |
| Heart Disease, confronto dei 7 encoder, pipeline definitiva | Eseguito il 14/11/2026, risultati in `datas/heart_disease/` |
| Diabetes130, confronto dei 7 encoder, pipeline definitiva | Eseguito il 14/11/2026, risultati in `datas/diabetes130/` |
| Baseline tabellari, analisi per centro, modello "solo mancanza" | Eseguite il 14/11/2026, `manuale_v2/analisi/risultati_aggiuntivi.json` |
| Analisi di sensibilità sulla scala degli embedding | Eseguita il 14/11/2026, `manuale_v2/analisi/scala_embedding.json` |

"Pipeline definitiva" significa: nessun oversampling, nessuna imputazione per il testo, pulizia di Diabetes130, 512 token, embedding standardizzati con regolarizzazione scelta per ogni encoder, soglia out-of-fold (capitolo 36). L'Appendice C (tabelle complete) è generata automaticamente dai file dei risultati: dopo ogni nuova run basta rieseguire il build del libro (Appendice D).

## Ringraziamenti tecnici e strumenti

Il progetto usa software libero: Python, NumPy, pandas, scikit-learn, SciPy, sentence-transformers, Hugging Face Transformers, PyTorch, Ollama, UMAP, MLstatkit, Matplotlib, seaborn, Streamlit, python-telegram-bot. I dataset provengono dall'UCI Machine Learning Repository. Questo libro è stato composto in Markdown e convertito con pandoc.
