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
Traccia: massimizzando F1 su ciascun fold di validazione (Formula 35.1) — con la precisazione onesta che questo introduce un ottimismo statistico contenuto, distinto e più lieve di un vero data leakage (capitolo 35.3, capitolo 33.3).

**9. "Quali metriche avete usato, e perché non altre?"**
Traccia: accuratezza, F1 macro, ROC-AUC (capitolo 34) — non metriche di regressione (MAE, RMSE), perché il problema è di classificazione, non di previsione di un valore continuo.

**10. "Come avete stimato l'incertezza dei risultati?"**
Traccia: bootstrap non parametrico a 10.000 iterazioni sulle predizioni già ottenute (capitolo 36), con intervalli di confidenza al 95% con il metodo percentile.

**11. "Perché tre test statistici diversi invece di uno solo?"**
Traccia: triangolazione metodologica — Wilcoxon (non parametrico), t-test appaiato (più potente se la normalità regge), DeLong (specifico per l'AUC, tiene conto della correlazione fra modelli sugli stessi casi) — la concordanza fra i tre rafforza la fiducia nelle conclusioni (capitolo 26.3, capitolo 37).

**12. "Avete applicato una correzione per confronti multipli?"**
Traccia: no — con 21 confronti a coppie per metrica, questo è un limite dichiarato esplicitamente (capitolo 39.2), non scoperto dalla commissione: menzionarlo prima che venga chiesto è più forte che doverlo ammettere in risposta.

**13. "Come garantite la riproducibilità dei risultati?"**
Traccia: sei semi casuali fissati a 42 in punti indipendenti del codice (capitolo 39.3) — con la precisazione onesta che non esiste una costante centralizzata, e che la riproducibilità copre le componenti seedate del progetto, non necessariamente ogni sorgente di variabilità esterna (per esempio versioni dei modelli su Ollama).

## 58.3 Limiti e validità (7 domande)

**14. "Qual è, secondo voi, il limite più serio di questo lavoro?"**
Traccia: l'assenza di un test set finale indipendente (capitolo 51.1) — un limite strutturale, reso concreto da un numero specifico (il baseline sulla popolazione reale di Diabetes130 raggiungerebbe 88.84%, capitolo 47.3), non solo un principio metodologico astratto.

**15. "I risultati generalizzano oltre questi due dataset?"**
Traccia: no, esplicitamente — due dataset storici, di provenienza occidentale, uno campionato parzialmente; nessuna base per generalizzare a testo clinico autentico o ad altre popolazioni (capitolo 53.2).

**16. "Come giustificate l'affermazione che i modelli biomedici sono superiori?"**
Traccia: con cautela differenziata per dataset — su Diabetes130 il test di DeLong conferma una superiorità netta e quasi universale (20 coppie su 21 significative, capitolo 45.2); su Heart Disease il quadro è più sfumato, con i modelli generalisti più grandi statisticamente indistinguibili da alcuni biomedici (capitolo 44.3).

**17. "Avete trovato bug o inconsistenze nel codice originale?"**
Traccia: sì, diverse, verificate e documentate — la discrepanza fra la documentazione (297 record) e il codice reale (920 righe) per Heart Disease (capitolo 29.1), il testo narrativo statico del report che contraddice le proprie tabelle (capitolo 52), il comando di installazione errato per un modello Ollama (capitolo 15.2).

**18. "Come avete verificato la qualità dei dati?"**
Traccia: scomponendo la mancanza dei dati per centro clinico e per feature, non fermandosi a un controllo aggregato — la scoperta che `ca` e `thal` sono dati reali quasi solo per Cleveland (capitolo 29.3) è un esempio diretto di questo livello di verifica.

**19. "Gli 'hardest cases' del vostro sistema sono casi clinicamente interessanti?"**
Traccia: in parte no — verificato che alcuni sono record sintetici (età non intera) e che la maggioranza condivide esattamente i valori di imputazione più comuni per `ca`/`thal`, non necessariamente un profilo clinico raro (capitolo 46.2).

**20. "Che uso responsabile fareste di un sistema come questo in un contesto reale?"**
Traccia: nessuno diretto senza ulteriore lavoro — servirebbe come minimo un test set indipendente sulla popolazione reale (capitolo 55.1), una calibrazione esplicita delle probabilità (capitolo 55.3), e una validazione specifica per qualunque interfaccia utente (capitolo 54.3) prima di considerare un uso anche solo di supporto informativo.

## Riepilogo

Venti domande organizzate in tre aree — dominio e motivazione, metodo e implementazione, limiti e validità — ciascuna con una traccia di risposta ancorata a un capitolo specifico di questo libro. Le domande sui limiti (58.3) sono probabilmente le più probabili in una discussione seria, ed è per questo che il libro le tratta con lo stesso rigore delle domande sui risultati positivi.

## Domande di autoverifica

**1. Quale domanda di questo capitolo riguarda direttamente la scoperta più forte e meglio verificata di tutto il libro?**
La domanda 19, sugli "hardest cases": la risposta si basa sulla verifica diretta (età non intera, valori di imputazione confermati con mediana e moda calcolate) del capitolo 46.2.

**2. Perché menzionare da soli, senza aspettare la domanda, l'assenza di correzione per confronti multipli (domanda 12) è una strategia migliore che aspettare di doverlo ammettere?**
Perché dichiarare un limite prima che venga scoperto mostra padronanza critica del proprio lavoro, mentre doverlo ammettere solo dopo una domanda diretta può apparire come una lacuna nascosta o non notata.

**3. La domanda 16 richiede una risposta uniforme per entrambi i dataset, o differenziata?**
Differenziata: la superiorità dei modelli biomedici è statisticamente netta su Diabetes130 ma più sfumata su Heart Disease, dove alcuni modelli generalisti grandi non sono distinguibili statisticamente da alcuni modelli biomedici — una risposta uniforme sarebbe imprecisa.

> **MATERIALE PER LA TESI**
> 1. Le venti domande con traccia di risposta — riusabili direttamente come materiale di preparazione alla discussione, capitolo per capitolo.
> 2. La distinzione fra domande con risposta fattuale diretta e domande che richiedono un giudizio motivato — riusabile per calibrare il proprio livello di sicurezza nella risposta durante la discussione.
> 3. L'insieme delle sette domande sui limiti (58.3) — riusabile come base per la propria autovalutazione critica prima della consegna finale della tesi, non solo come preparazione a una domanda altrui.
