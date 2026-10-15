# Capitolo 58 — Venti domande della commissione, con traccia di risposta

**Obiettivi del capitolo**
- Arrivare alla discussione con una risposta già pensata per le domande più prevedibili.
- Avere, per ciascuna domanda, il capitolo esatto del libro da cui la risposta completa proviene.
- Distinguere le domande a cui puoi rispondere con un fatto verificato da quelle che richiedono un'opinione motivata.

Ogni traccia di risposta è un punto di partenza, non un testo da recitare a memoria: la commissione nota la differenza fra una risposta capita e una imparata.

## 58.1 Dominio e motivazione (5 domande)

**1. "Perché avete convertito dati tabellari in testo invece di classificarli direttamente?"**
Traccia: per testare se le rappresentazioni di modelli linguistici pre-addestrati catturano segnale clinico da dati strutturati — una domanda di ricerca specifica (capitolo 3.2, capitolo 6.3), non un'affermazione che questo approccio sia superiore alla classificazione diretta, mai testata in questo progetto (capitolo 1.3, capitolo 53.2).

**2. "Cosa prevede esattamente il sistema, in termini clinici concreti?"**
Traccia: due cose diverse per i due dataset — presenza di malattia coronarica (diagnosi) per Heart Disease, riammissione ospedaliera entro 30 giorni (non "riammissione in generale") per Diabetes130 (capitolo 1.1, capitolo 30.3).

**3. "Perché confrontare modelli generalisti e biomedici, e non solo usare il migliore in assoluto?"**
Traccia: è la seconda domanda di ricerca esplicita del progetto (capitolo 6.3, `README.md:60-61`) — l'obiettivo è isolare l'effetto del dominio di pre-addestramento, non solo massimizzare una metrica.

**4. "Il nome del progetto è 'Forecast': fate previsioni di serie temporali?"**
Traccia: no — nonostante il nome storico, il codice non tratta alcuna dimensione temporale: è classificazione binaria su dati clinici in un singolo momento (capitolo 0.3.3, capitolo 1).

**5. "Che tipo di utente finale trarrebbe beneficio da questo sistema?"**
Traccia: nella forma attuale, nessuno direttamente — la pipeline produce report di ricerca, non un'interfaccia utilizzabile in produzione; solo il prototipo di chatbot su un branch separato (capitolo 54) si avvicina a un'interfaccia utente, e non è stato integrato né validato per questo scopo.

## 58.2 Metodo e implementazione (8 domande)

**6. "Perché regressione logistica e non una rete neurale più complessa?"**
Traccia: linear probing su un embedding congelato è una scelta metodologica specifica per isolare il segnale già presente nella rappresentazione (capitolo 32.3, capitolo 53.1); per Heart Disease è anche prudente dato il regime `p > n` per i modelli a 1024 dimensioni.

**7. "Come avete gestito lo sbilanciamento delle classi?"**
Traccia: SMOTENC sulle feature grezze, prima della codifica, per mantenere i record sintetici convertibili in testo (capitolo 21.2) — con la precisazione che Heart Disease è in realtà quasi bilanciato (55.3%/44.7%), mentre Diabetes130 è marcatamente sbilanciato (11.16%/88.84%, capitolo 4.2).

**8. "Come scegliete la soglia di decisione?"**
Traccia: massimizzando F1 su una fetta di calibrazione ricavata dalla partizione di training di ciascun fold, mai sulle etichette di validazione (Formula 35.1, capitolo 23.2) — con la storia onesta che una versione precedente la sceglieva sul fold stesso, un ottimismo contenuto individuato dall'analisi e corretto nel codice (capitolo 35.3, capitolo 51.2).

**9. "Quali metriche avete usato, e perché non altre?"**
Traccia: accuratezza, F1 macro, ROC-AUC (capitolo 34) — non metriche di regressione (MAE, RMSE), perché il problema è di classificazione, non di previsione di un valore continuo.

**10. "Come avete stimato l'incertezza dei risultati?"**
Traccia: bootstrap non parametrico a 10.000 iterazioni sulle predizioni già ottenute (capitolo 36), con intervalli di confidenza al 95% con il metodo percentile.

**11. "Perché tre test statistici diversi invece di uno solo?"**
Traccia: triangolazione metodologica — Wilcoxon (non parametrico), t-test appaiato (più potente se la normalità regge), DeLong (specifico per l'AUC, tiene conto della correlazione fra modelli sugli stessi casi) — la concordanza fra i tre rafforza la fiducia nelle conclusioni (capitolo 26.3, capitolo 37).

**12. "Avete applicato una correzione per confronti multipli?"**
Traccia: sì — Benjamini-Hochberg su tutti e 21 i confronti a coppie per metrica, con le colonne corrette (`p_value_bh`, `significant_bh`) affiancate ai p-value grezzi (capitolo 26.2bis); e i risultati citano entrambe le letture, segnalando i casi limite che cambiano esito con la correzione (capitolo 44.3). Vale la pena aggiungere che in una prima versione la correzione mancava: è uno dei limiti individuati dall'analisi e corretti nel codice.

**13. "Come garantite la riproducibilità dei risultati?"**
Traccia: otto semi casuali fissati a 42 in punti indipendenti del codice (capitolo 39.3) — con la precisazione onesta che non esiste una costante centralizzata, e che la riproducibilità copre le componenti seedate del progetto, non necessariamente ogni sorgente di variabilità esterna (per esempio versioni dei modelli su Ollama).

## 58.3 Limiti e validità (7 domande)

**14. "Qual è, secondo voi, il limite più serio di questo lavoro?"**
Traccia: lo *è stato* l'assenza di un test set finale indipendente (capitolo 51.1), corretta con la fase holdout — e proprio la correzione ha rivelato il limite sostanziale che resta: su Diabetes130 le prestazioni sulla popolazione reale sono vicine al caso (AUC 0.48-0.55 contro il baseline banale all'88.84% di accuratezza, capitoli 45 e 47.3). Poter rispondere con un limite *misurato*, non solo ipotizzato, è la posizione più forte possibile.

**15. "I risultati generalizzano oltre questi due dataset?"**
Traccia: no, esplicitamente — due dataset storici, di provenienza occidentale, uno campionato parzialmente; nessuna base per generalizzare a testo clinico autentico o ad altre popolazioni (capitolo 53.2).

**16. "Come giustificate l'affermazione che i modelli biomedici sono superiori?"**
Traccia: con la doppia qualificazione che i dati impongono — in cross-validation la superiorità in AUC di ogni biomedico su ogni generalista è statisticamente solida su entrambi i dataset (12/12 confronti fra famiglie significativi su Diabetes130, 11/12 dopo la correzione su Heart Disease, capitoli 44.3 e 45.2), mentre dentro ciascuna famiglia i modelli non si distinguono; e questa superiorità *relativa* non implica utilità *assoluta*, come l'holdout di Diabetes130 dimostra (capitolo 45).

**17. "Avete trovato bug o inconsistenze nel codice originale?"**
Traccia: sì, diverse, verificate, documentate — e corrette nel codice, con la storia tracciata in `docs/CHANGES.md`: il test set calcolato e scartato (capitolo 51.1), il testo narrativo statico del report che contraddiceva le proprie tabelle (capitolo 52), la soglia scelta sulle etichette poi misurate (capitolo 23.2), il comando di installazione errato per un modello Ollama (capitolo 15.2), oltre alla discrepanza documentale 297/920 per Heart Disease (capitolo 29.1). La sequenza scoperta → correzione → ri-misura è essa stessa un contributo della tesi.

**18. "Come avete verificato la qualità dei dati?"**
Traccia: scomponendo la mancanza dei dati per centro clinico e per feature, non fermandosi a un controllo aggregato — la scoperta che `ca` e `thal` sono dati reali quasi solo per Cleveland (capitolo 29.3) è un esempio diretto di questo livello di verifica.

**19. "Gli 'hardest cases' del vostro sistema sono casi clinicamente interessanti?"**
Traccia: in maggioranza sono casi in cui le feature più informative (`ca`, `thal`) non sono mai state misurate — nell'analisi pre-fix questo si manifestava come profili imputati presentati come osservati (età non intere da SMOTENC, valori coincidenti con mediana/moda dell'imputazione); dopo il fix degli indicatori di mancanza, il legame è osservabile direttamente: 14 dei 20 casi sbagliati da tutti i modelli hanno `ca_missing=1` (capitolo 46.2).

**20. "Che uso responsabile fareste di un sistema come questo in un contesto reale?"**
Traccia: nessuno diretto — e ora con evidenza misurata: la valutazione holdout mostra che su Diabetes130 il sistema è vicino al caso sulla popolazione reale (capitolo 45), quindi qualunque uso sarebbe ingiustificato; su Heart Disease, dove l'holdout è solido, servirebbero comunque una calibrazione esplicita delle probabilità (capitolo 55.3), una validazione su popolazioni attuali e non storiche, e una validazione specifica per qualunque interfaccia utente (capitolo 54.3) prima di considerare un uso anche solo di supporto informativo.

## Riepilogo

Venti domande organizzate in tre aree — dominio e motivazione, metodo e implementazione, limiti e validità — ciascuna con una traccia di risposta ancorata a un capitolo specifico di questo libro. Le domande sui limiti (58.3) sono probabilmente le più probabili in una discussione seria, ed è per questo che il libro le tratta con lo stesso rigore delle domande sui risultati positivi.

## Domande di autoverifica

**1. Quale domanda di questo capitolo riguarda direttamente la scoperta più forte e meglio verificata di tutto il libro?**
La domanda 19, sugli "hardest cases": la risposta si basa sulla catena completa del capitolo 46.2 — la verifica pre-fix (età non intere, valori di imputazione confermati con mediana e moda calcolate) e la conferma diretta post-fix tramite gli indicatori di mancanza nel CSV.

**2. Perché raccontare da soli, senza aspettare la domanda, la storia della correzione per confronti multipli (domanda 12) è una strategia migliore che una semplice risposta affermativa?**
Perché dichiarare che un limite è stato individuato dalla propria analisi e poi corretto mostra padronanza critica del lavoro a un livello superiore sia del nasconderlo, sia del limitarsi a dire "sì, c'è Benjamini-Hochberg" — la sequenza diagnosi → correzione → doppia lettura dei p-value è essa stessa un argomento metodologico.

**3. La domanda 16 richiede una risposta uniforme per entrambi i dataset, o differenziata?**
Differenziata su un asse diverso da quello atteso: la superiorità *relativa* fra famiglie è statisticamente solida su entrambi i dataset, ma solo su Heart Disease essa si accompagna a prestazioni assolute che si trasferiscono alla popolazione reale — su Diabetes130 l'holdout mostra che nemmeno il migliore dei biomedici è praticamente utile. Una risposta uniforme sarebbe imprecisa.

> **MATERIALE PER LA TESI**
> 1. Le venti domande con traccia di risposta — riusabili direttamente come materiale di preparazione alla discussione, capitolo per capitolo.
> 2. La distinzione fra domande con risposta fattuale diretta e domande che richiedono un giudizio motivato — riusabile per calibrare il proprio livello di sicurezza nella risposta durante la discussione.
> 3. L'insieme delle sette domande sui limiti (58.3) — riusabile come base per la propria autovalutazione critica prima della consegna finale della tesi, non solo come preparazione a una domanda altrui.
