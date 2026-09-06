# Indice definitivo — Manuale "Forecast"

> Versione approvata dall'utente il 2026-09-05, con le 4 aggiunte concordate dopo la verifica di completezza sui contenuti di machine learning. Questo è il riferimento autoritativo per numerazione dei capitoli e nomi dei file. Ogni capitolo numerato (1-58) è un file `manuale/cap_NN.md`. La Parte 0 è `manuale/cap_00.md`. Le appendici sono `manuale/app_A.md` ... `manuale/app_F.md`.

## Parte 0 — Come usare questo libro (`cap_00.md`)
- 0.1 Percorsi di lettura e a chi serve questo libro (0.1.1 se vieni da Java e non conosci Python; 0.1.2 se conosci già Python; 0.1.3 se stai preparando la tesi)
- 0.2 Convenzioni tipografiche e riquadri ricorrenti (0.2.1 le etichette Fatto/Inferenza/Da verificare; 0.2.2 i sei riquadri ricorrenti; 0.2.3 come leggere i riferimenti file:riga)
- 0.3 Mappa manuale → tesi (0.3.1 struttura tipica di una tesi triennale in informatica; 0.3.2 tabella di corrispondenza capitoli-sezioni, anteprima; 0.3.3 cosa non troverai in questo libro)

## Parte I — Il dominio
1. Perché questo progetto esiste (1.1 il problema clinico reale: diagnosi vs. rischio di riammissione; 1.2 chi decide, e con quali conseguenze; 1.3 cosa si faceva prima: classificazione diretta su dati tabellari)
2. **[nuovo]** Il quadro del machine learning supervisionato (2.1 apprendimento supervisionato, non supervisionato, per rinforzo: una mappa minima; 2.2 il ciclo addestramento → validazione → inferenza; 2.3 overfitting, underfitting, generalizzazione)
3. Dalla tabella al testo (3.1 limiti di una rappresentazione tabellare per i modelli linguistici; 3.2 l'idea del progetto: tabellare→testo→embedding→classificazione; 3.3 approcci alternativi esistenti)
4. Classificazione binaria: l'essenziale per seguire il libro (4.1 due classi, una probabilità, una soglia; 4.2 sbilanciamento delle classi; 4.3 vero/falso positivo/negativo)
5. Rappresentazioni testuali ed embedding (5.1 cos'è un embedding, in una frase, prima di ogni formula; 5.2 da testo a vettore: tokenizzazione, encoder transformer, pooling; 5.3 perché esistono modelli generalisti e modelli biomedici)
6. **[nuovo]** Il gergo del codice: dizionario variabili → concetti (6.1 tabella di corrispondenza completa; 6.2 i nomi che ingannano — `tau`, `family`, `results`; 6.3 le due domande di ricerca del progetto, ora leggibili nel codice)

## Parte II — Python per chi programma in Java
7. Sintassi minima e idiomi core (7.1 indentazione come sintassi; 7.2 tipizzazione dinamica e duck typing; 7.3 `self` esplicito)
8. Strutture dati e comprehension (8.1 liste/dizionari/tuple vs. List/Map; 8.2 list comprehension e generatori; 8.3 il dizionario globale mutabile di `function.py`)
9. Funzioni, argomenti, trappole (9.1 posizionali, keyword, default mutabili; 9.2 funzioni come cittadini di prima classe; 9.3 assenza di overloading)
10. Moduli, package, incapsulamento (10.1 un file `.py` è un modulo; 10.2 `import` vs. Java; 10.3 niente `private` reale: convenzione underscore)
11. Eccezioni, context manager, decoratori (11.1 `try/except/raise...from`; 11.2 context manager `with`; 11.3 decoratori: dove non compaiono qui)
12. Concorrenza e memoria (12.1 il GIL; 12.2 `ThreadPoolExecutor`+`Semaphore` in `embedding.py` vs. `ExecutorService`; 12.3 reference counting e garbage collector)
13. Tabella di traduzione Java→Python e trappole finali (13.1 tabella sistematica; 13.2 le cinque trappole più insidiose; 13.3 prova tu: leggere un traceback)

## Parte III — Ecosistema e ambiente
14. Interprete e ambienti virtuali (14.1 perché serve un "classpath" alternativo; 14.2 `env/` in questo progetto; 14.3 pip/requirements.txt vs. Maven/Gradle)
15. Installazione passo passo su macOS (15.1 prerequisiti: Python 3.14, Ollama, token HF; 15.2 procedura comando per comando; 15.3 prima esecuzione)
16. Troubleshooting e verifica dell'ambiente (16.1 errori più probabili; 16.2 verificare l'installazione; 16.3 cosa non esiste in Python: niente bytecode portabile, niente .jar)

## Parte IV — Architettura
17. Vista d'insieme: componenti e confini (17.1 diagramma architetturale commentato; 17.2 cosa entra/esce da ogni fase; 17.3 confronto con un'architettura Java a livelli)
18. Il ciclo di vita di un'esecuzione (18.1 diagramma di sequenza da `main.py` al report; 18.2 isolamento per dataset; 18.3 fallimento a metà pipeline)
19. Stato, configurazione, punti di estensione (19.1 `function.py` come config unica; 19.2 stato globale mutabile: dove, perché, rischi; 19.3 dove aggiungeresti un ottavo modello)

## Parte V — Il codice, modulo per modulo
20. `function.py`: la spina dorsale silenziosa (20.1 config modelli e famiglie; 20.2 funzioni di I/O e pulizia cartelle; 20.3 le nove funzioni di plotting)
21. `preprocessing.py`: dalla tabella grezza al training set bilanciato (21.1 caricamento e unione sorgenti; 21.2 imputazione, SMOTENC, codifica; 21.3 cosa viene salvato e perché)
22. `embedding.py`: tabellare → testo → vettore (22.1 `record_to_text_*` riga per riga; 22.2 generazione batch verso Ollama: retry, semaforo; 22.3 generazione verso Hugging Face: autenticazione, offline)
23. `classification.py`: addestrare e validare (23.1 `StratifiedKFold` e perché "stratified" conta; 23.2 la soglia F1-ottima per fold; 23.3 cosa viene salvato e a cosa serve dopo)
24. `evaluation.py`: bootstrap e grafici (24.1 il bootstrap in poche righe; 24.2 intervalli di confidenza: come si leggono i grafici; 24.3 dal dizionario Python al PNG/PDF)
25. `error_analysis.py`: dall'errore statistico al caso clinico (25.1 ricostruire il record dall'indice di validazione; 25.2 "hardest cases"; 25.3 deviazione di feature)
26. `statisticaltest.py`: tre test, tre garanzie diverse (26.1 Wilcoxon e t-test appaiato; 26.2 DeLong e `MLstatkit`; 26.3 perché tre test invece di uno)
27. `generatereport.py`: l'ultimo miglio, e il suo limite più istruttivo (27.1 come si assembla un report Markdown da CSV/PNG; 27.2 il caso del testo narrativo statico; 27.3 come lo riscriveresti tu)
28. `main.py`: l'orchestratore letto per ultimo apposta (28.1 le sette fasi in ordine; 28.2 il flag `--dataset` e il default; 28.3 cosa succederebbe ad aggiungere una fase 8)

## Parte VI — I dati e la pipeline
29. Il dataset UCI Heart Disease (29.1 origine e centri clinici; 29.2 schema delle 14 feature e valori mancanti mascherati da zero; 29.3 limiti noti)
30. Il dataset Diabetes 130-US Hospitals (30.1 scala, 101.766 righe, e campionamento a 20.000; 30.2 le 19 feature scelte tra ~50; 30.3 la ridefinizione del target)
31. Qualità dei dati e casi limite (31.1 valori mancanti espliciti e impliciti; 31.2 SMOTENC su feature miste: cosa genera un record sintetico; 31.3 casi limite nella conversione a testo)

## Parte VII — Il modello: matematica e implementazione
32. La regressione logistica, dalle basi alla riga di codice (32.1 funzione logistica come probabilità; 32.2 funzione di costo e ottimizzazione; 32.3 perché lineare su embedding, non una rete profonda)
33. **[nuovo]** Come si valida correttamente un modello di classificazione (33.1 train/validation/test: a cosa serve ciascuno; 33.2 k-fold e k-fold stratificato: formula e procedura; 33.3 data leakage: tassonomia generale e perché è la minaccia più insidiosa)
34. Le tre metriche del progetto (34.1 accuracy; 34.2 macro-F1; 34.3 ROC-AUC)
35. Soglie di decisione (35.1 perché 0.5 non basta sempre; 35.2 la soglia F1-ottima: formula e codice; 35.3 il costo nascosto della sua ottimizzazione)
36. Bootstrap e intervalli di confidenza (36.1 ricampionamento con reinserimento; 36.2 intervalli percentile al 95%; 36.3 perché 10.000 iterazioni)
37. I tre test di significatività (37.1 Wilcoxon; 37.2 t-test appaiato; 37.3 DeLong)
38. **[nuovo]** Riduzione di dimensionalità e visualizzazione: UMAP (38.1 perché non si può "vedere" uno spazio a 768/1024 dimensioni; 38.2 UMAP in breve: vicinanza locale, ottimizzazione di un layout 2D; 38.3 cosa può e non può dirti un grafico UMAP)
39. Iperparametri del progetto: valori e razionale (39.1 tabella completa, incluso `C=1.0` di default mai esplorato; 39.2 effetto di valori alternativi; 39.3 mappa dei semi casuali)

## Parte VIII — Esecuzione end-to-end
40. Caso d'uso 1: Heart Disease dall'inizio alla fine (40.1 cosa succede fase per fase; 40.2 come cambiano forma i dati; 40.3 cosa trovi su disco)
41. Caso d'uso 2: Diabetes130 e le differenze che contano (41.1 stesse fasi, numeri diversi; 41.2 perché i punteggi assoluti sono più bassi; 41.3 isolamento tra run)
42. Caso d'uso 3: aggiungere un ottavo encoder passo per passo (42.1 dove si registra in `function.py`; 42.2 cosa fa la pipeline da sola; 42.3 verifica finale)

## Parte IX — Valutazione e risultati
43. Protocollo sperimentale (43.1 cosa è stato eseguito da chi, e quando; 43.2 comandi eseguiti con output reale vs. comandi da eseguire tu; 43.3 limiti dichiarati del protocollo)
44. Risultati — Heart Disease (44.1 tabella metriche con CI, dato reale; 44.2 generalisti vs. biomedici; 44.3 cosa dicono davvero i test statistici)
45. Risultati — Diabetes130 (45.1 tabella metriche con CI, dato reale; 45.2 generalisti vs. biomedici; 45.3 perché è il caso più interessante)
46. Analisi degli errori sui due dataset (46.1 tassi FP/FN per modello; 46.2 i casi più difficili; 46.3 deviazione di feature)
47. Confronto con un modello di riferimento banale (47.1 cos'è un baseline e perché serve alla tesi; 47.2 costruzione di un baseline sugli stessi fold; 47.3 il confronto numerico)

## Parte X — Test, debugging, qualità
48. Lo stato attuale: nessun test automatico (48.1 conseguenze per l'affidabilità; 48.2 cosa testeresti per primo; 48.3 pytest vs. JUnit)
49. Scrivere il primo test per questo progetto (49.1 test per `record_to_text_heart_disease`; 49.2 test per la soglia F1-ottima con dati sintetici; 49.3 mocking di disco/rete)
50. Debugging e log in pratica (50.1 debugger Python vs. Java; 50.2 leggere i `print()` come log strutturati; 50.3 percorso guidato su un bug reale)

## Parte XI — Analisi critica
51. Limiti metodologici del protocollo di valutazione (51.1 assenza di test set finale indipendente; 51.2 soglia ottimizzata sullo stesso fold; 51.3 il campionamento a 20.000 di Diabetes130)
52. Il caso del reporting automatico non aggiornato (52.1 confronto riga per riga dei due report reali; 52.2 perché è pericoloso in contesto clinico; 52.3 come si preverrebbe)
53. Posizionamento rispetto allo stato dell'arte (53.1 tabellare→testo→embedding vs. classificazione tabellare diretta, "linear probing" su embedding congelati; 53.2 cosa NON prova questo progetto; 53.3 minacce alla validità: interna, esterna, di costrutto, statistica)

## Parte XII — Estensioni e lavori futuri
54. Il chatbot clinico: cosa esiste già, non integrato (54.1 architettura di `chatbot_core.py`/Streamlit/Telegram sul branch `chatbot`; 54.2 cosa manca per l'integrazione pulita; 54.3 rischi di un chatbot di rischio clinico non validato)
55. Direzioni di sviluppo difendibili in sede di discussione (55.1 test set finale indipendente; 55.2 un classificatore non lineare come confronto; 55.3 calibrazione delle probabilità e reportistica generata dai dati)

## Parte XIII — Dal manuale alla tesi
56. Mappa capitolo per capitolo verso le sezioni tipiche di una tesi triennale (56.1 introduzione e motivazione; 56.2 stato dell'arte; 56.3 materiali e metodi; 56.4 risultati; 56.5 discussione e limiti; 56.6 conclusioni e lavori futuri)
57. Cosa è già pronto e cosa manca ancora (57.1 figure e tabelle riutilizzabili, capitolo per capitolo; 57.2 misure ancora da produrre, con procedura; 57.3 riferimenti bibliografici da recuperare e verificare)
58. Venti domande della commissione, con traccia di risposta (58.1 dominio e motivazione, 5 domande; 58.2 metodo e implementazione, 8 domande; 58.3 limiti e validità, 7 domande)

## Appendici
- A. Glossario generale (`app_A.md`) — dominio + statistica, non programmazione generale
- B. Riferimento completo delle funzioni pubbliche (`app_B.md`) — tutti i 9 file di `master`
- C. Formulario (`app_C.md`) — tutte le formule del libro, numerate, con rimando al capitolo
- D. Bibliografia annotata + `bibliografia.bib` (`app_D.md`) — affidabilità di ogni riferimento dichiarata
- E. Zone d'ombra (`app_E.md`) — elenco completo delle domande aperte per il relatore
- F. Indice analitico (`app_F.md`)

**Totale: 58 capitoli numerati + Parte 0 + 6 appendici.**
