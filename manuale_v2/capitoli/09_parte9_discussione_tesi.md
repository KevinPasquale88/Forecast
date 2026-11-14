# Parte X — Discussione

## Capitolo 39 — Limiti e minacce alla validità

Le minacce alla validità si dividono di solito in quattro tipi. Per ciascuno: cosa può andare storto, quanto pesa nel progetto, cosa è stato fatto.

### 39.1 Validità interna (il risultato è causato da ciò che crediamo?)

| Minaccia | Peso | Stato |
| --- | --- | --- |
| Leakage da oversampling, soglia, pazienti ripetuti | Alto (Diabetes) | Corretto (capitolo 36) |
| Scorciatoia centro/mancanza su Heart Disease | Medio | Misurato: centro da solo 0,70, mancanza 0,74; dentro Cleveland AUC 0,86–0,89 |
| Confronto tra famiglie influenzato dalla scala dei vettori | Alto per la domanda secondaria | Corretto: standardizzazione e C per encoder (capitolo 32.4) |
| Prefissi E5 non usati | Basso-medio | Non misurato |
| Nomi dei modelli fuorvianti (gte = M3E e GTE cinese) | Basso, ma da dichiarare | Documentato |
| Quantizzazione `q8_0` di due modelli | Basso | Documentato |

### 39.2 Validità esterna (vale altrove?)

- Due soli dataset, storici, statunitensi ed europei.
- Diabetes130 campionato a 20.000 ricoveri su 69.990.
- Heart Disease: centri con prevalenze molto diverse; il modello può non trasferirsi a un centro nuovo. Un esperimento "addestra su tre centri, verifica sul quarto" darebbe una stima più realistica.
- Frasi generate da un modello fisso; descrizioni scritte da medici (testo libero) sarebbero diverse.

### 39.3 Validità di costrutto (misuriamo ciò che diciamo?)

- La soglia F1 non è una soglia clinica; accuracy e F1 dipendono da essa, AUC no.
- Il Brier score mescola discriminazione e calibrazione; manca una misura di calibrazione dedicata.
- "Efficacia" degli embedding è stata resa operativa come AUC di un linear probe: è una scelta, non l'unica possibile.

### 39.4 Validità statistica (le conclusioni statistiche sono corrette?)

- Intervalli bootstrap che ignorano la variabilità dell'addestramento (capitolo 28.3).
- Wilcoxon e t-test sui bootstrap con potenza dipendente dal numero di ricampionamenti (capitolo 29.4): da leggere con le differenze.
- Test set di Heart Disease piccolo (184): classifiche sul test non affidabili.
- Confronti multipli corretti con BH.

## Capitolo 40 — Lavori futuri

In ordine di rapporto costo/beneficio:

1. **Prefissi E5** (`query: `) e istruzione per e5-large-instruct: misura l'effetto di un uso conforme alle model card.
2. **Tradurre i codici di Diabetes130** con `IDS_mapping.csv` ("admission type: Emergency").
3. **Validazione per centro** su Heart Disease (lasciare fuori un centro alla volta).
4. **Curve di calibrazione** ed eventuale ricalibrazione (Platt, isotonica).
5. **CV ripetuta** con semi diversi, per intervalli che includano la variabilità dell'addestramento e per il t-test corretto di Nadeau-Bengio.
6. **Classificatore non lineare** sugli embedding (gradient boosting, piccola rete).
7. **Chatbot**: "Non lo so" solo sui campi mancanti nel training; probabilità contro prevalenza su Diabetes130; nessun canale esterno per dati reali.
8. **Encoder più recenti o più grandi**, anche generativi usati come encoder, purché eseguibili in locale.

# Parte XI — Dalla tesi alla discussione

## Capitolo 41 — Come usare questo materiale nella tesi

### 41.1 Struttura suggerita

| Capitolo della tesi | Contenuto | Capitoli di questo libro |
| --- | --- | --- |
| 1. Introduzione | Problema clinico, motivazione, domande e ipotesi, contributi | 1, 3.4, 4 |
| 2. Stato dell'arte | ML su dati tabellari, serializzazione in testo, embedding, encoder biomedici, linear probing | 3, 5, 6, 7 |
| 3. Materiali | I due dataset, pulizia, dati mancanti | 19, 20, 21 |
| 4. Metodi | Pipeline, conversione in testo, encoder, classificatore, validazione, soglia, metriche, bootstrap, test | 8, 12–17, 22–29 |
| 5. Implementazione | Architettura, moduli, riproducibilità, test automatici | 9–18, 31 |
| 6. Risultati | Heart Disease, analisi per centro, baseline tabellari, confronto equo, Diabetes130 | 32–35 |
| 7. Discussione | Risposta alle ipotesi, correzioni metodologiche, limiti | 33, 34, 36, 39 |
| 8. Applicazione | Il chatbot, rischi, regolamentazione | 37, 38 |
| 9. Conclusioni | Sintesi, lavori futuri | 4.3, 40 |

### 41.2 Figure e tabelle pronte

- Schema della pipeline (capitolo 12), schema CV e soglia (16), architettura del chatbot (37).
- Tabella dei dataset (2), dei centri (19), degli encoder (8).
- Risultati CV e test (32), confronto equo (32.4), analisi per centro (33), baseline (34).
- Grafici prodotti dalla pipeline: ROC, media con intervalli, boxplot, confronto per famiglia, errori.

### 41.3 Cosa manca prima della consegna

- Verificare le 11 voci bibliografiche senza † (Appendice E): classici, testi normativi e model card.
- Riportare il protocollo standardizzato come principale e quello originale (C = 1 su vettori grezzi) come analisi di sensibilità, spiegando perché differiscono.

## Capitolo 42 — Domande della commissione

### Dominio e motivazione

**1. Perché convertire dati tabellari in testo, se i modelli tabellari funzionano già?**
Per tre ragioni: uniformità (un solo formato per dataset diversi), possibilità di usare la conoscenza linguistica degli encoder, e compatibilità con un'interfaccia conversazionale. I risultati mostrano che la conversione conserva il segnale (Heart Disease: 0,891 del miglior encoder contro 0,896 della regressione logistica tabellare) ma non lo migliora; il valore dell'approccio non è la prestazione pura.

**2. Perché due dataset?**
Rappresentano compiti opposti: diagnosi con misure dirette e segnale forte, prognosi con dati amministrativi e segnale debole. Permettono di vedere come si comporta l'approccio in entrambe le condizioni.

**3. Perché tutto in locale?**
I dati sanitari sono categoria particolare nel GDPR; non inviarli a servizi esterni riduce rischi e vincoli. Inoltre rende il progetto riproducibile senza account o costi.

**4. Il modello può essere usato in clinica?**
No. Non è validato clinicamente, è addestrato su dati storici, la soglia non è clinica, e come software di supporto alla decisione ricadrebbe nel regolamento sui dispositivi medici.

**5. Cosa significa "biomedico" per un encoder?**
Che è stato pre-addestrato o adattato su testo biomedico (PubMed, note cliniche). Cambiano lessico appreso e, per PubMedBERT, il vocabolario del tokenizer.

### Metodo e implementazione

**6. Perché una regressione logistica e non una rete?**
È il linear probe standard per valutare rappresentazioni: attribuisce la prestazione all'embedding, non al classificatore, e con 736 record limita l'overfitting.

**7. Avete standardizzato gli embedding? Come avete scelto la regolarizzazione?**
Sì, nella versione finale. All'inizio usavamo C = 1 su vettori grezzi; misurando le scale abbiamo visto che differiscono molto (norma 1 per Ollama, 11–13 per Hugging Face), e che con la stessa penalità i generalisti erano svantaggiati. Ora ogni encoder viene standardizzato e riceve il suo C per CV interna; il protocollo originale è riportato come analisi di sensibilità (capitolo 32.4).

**8. Come scegliete la soglia? Perché non 0,5?**
Massimizzando l'F1 su punteggi out-of-fold di una CV interna al training. 0,5 non ha senso con il 9% di positivi. È una scelta statistica, non clinica.

**9. Perché non avete bilanciato le classi?**
Lo facevamo con SMOTENC prima della CV, ed era la causa di un leakage grave su Diabetes130 (AUC apparente 0,76, reale 0,55). Ora gestiamo lo sbilanciamento con la soglia, il che lascia le probabilità calibrate.

**10. Come trattate i valori mancanti?**
Non li imputiamo: diventano "not recorded" nella frase. Così il testo non contiene valori inventati e coincide con ciò che si genera in inferenza per un campo ignoto.

**11. Perché 5 fold?**
Compromesso standard tra varianza della stima e costo; con 736 record ogni fold di validazione ha circa 147 record, sufficiente per un'AUC stabile.

**12. Perché il bootstrap e non solo la CV?**
La CV dà 5 valori; il bootstrap delle predizioni out-of-fold dà un intervallo di confidenza e distribuzioni appaiate per i test.

**13. Cosa testa DeLong e perché serve oltre a Wilcoxon?**
Confronta due AUC correlate sugli stessi pazienti, stimandone la covarianza: è il test standard in letteratura clinica e non dipende dal numero di ricampionamenti.

### Risultati, limiti e validità

**14. I biomedici sono migliori?**
Di poco. Con il protocollo attuale (embedding standardizzati, C per encoder) i biomedici hanno AUC media 0,882 contro 0,870; DeLong è significativo in 5 confronti su 12, soprattutto contro gte-large; PubMedBERT è il migliore. Con il protocollo originale il vantaggio sembrava netto (12 su 12), ma era in gran parte un effetto della regolarizzazione (capitolo 32.4).

**15. Il modello riconosce la malattia o il centro?**
Entrambi. Il centro da solo dà AUC 0,70, la sola mancanza dei campi 0,74. Ma dentro Cleveland, dove quasi nulla manca, gli encoder arrivano a 0,86–0,89: il segnale clinico c'è.

**16. Perché sul test set i risultati sono migliori che in CV?**
Il modello finale usa tutto il training (736 contro 589 record) e il test è piccolo (184), con variabilità di circa ±0,04 di AUC. Non è un segno di problemi, ma l'ordine tra modelli vicini sul test non va interpretato.

**17. Perché Diabetes130 va così male?**
Il compito dipende da fattori assenti dai dati (aderenza, supporto sociale); anche i modelli tabellari arrivano solo a 0,62 in CV e 0,64 sul test, in linea con la letteratura. I sette encoder stanno tutti tra 0,600 e 0,609 in CV, indistinguibili al test di DeLong: il testo perde 1–2 punti rispetto al tabellare, probabilmente perché i codici di ricovero sono scritti come numeri.

**18. Come vi siete accorti del leakage?**
Confrontando CV (0,76) e test (0,55) su Diabetes130, poi ricalcolando l'AUC dei soli record reali dalle predizioni salvate (0,56) e quella dei negativi reali contro positivi sintetici (0,79).

**19. Cosa fareste con più tempo?**
Validazione per centro, curve di calibrazione, prefissi E5, codici di Diabetes130 tradotti, classificatore non lineare (capitolo 40).

**20. Che garanzie di riproducibilità ci sono?**
Seme fisso ovunque, versioni delle librerie fissate, un comando per dataset, 31 test automatici, risultati salvati per ogni fase, e script separati per ogni analisi aggiuntiva.

**21. I p-value di Wilcoxon sono tutti significativi: non è sospetto?**
È atteso: con 10.000 coppie la potenza è altissima. Li leggiamo come conferma che la differenza ha lo stesso segno nei ricampionamenti, sempre insieme alla differenza media e agli intervalli; per l'AUC usiamo anche DeLong.

**22. Su Diabetes130 Wilcoxon dà 63 confronti significativi e DeLong nessuno: chi ha ragione?**
Entrambi, perché rispondono a domande diverse. DeLong confronta le AUC tenendo conto dell'incertezza dovuta ai pazienti osservati: le differenze (al massimo 0,009) sono compatibili con il caso. Wilcoxon e t-test sui bootstrap dicono che il segno della differenza è stabile nei ricampionamenti, il che con 10.000 coppie succede anche per differenze di 0,0008. La conclusione è che gli encoder sono equivalenti su questo compito.

**23. Perché alcuni modelli si chiamano "gte" ma non sono GTE?**
Sono etichette interne della pipeline: `gte-base` è M3E-base, `gte-large` è GTE-large in versione cinese. In tesi li indichiamo con il nome reale. Due dei generalisti sono quindi addestrati soprattutto su testo cinese, il che può spiegare parte del loro svantaggio.

**24. Il troncamento a 100 token ha influito sui risultati precedenti?**
Sì, per sentence-biobert: tutte le frasi erano più lunghe di 100 token, e su Heart Disease venivano tagliati `slope`, `ca` e `thal`. Ora il limite è 512.

**25. In che senso il chatbot è "sicuro"?**
Non lo è in senso clinico. È prevedibile (dialogo deterministico, nessun testo generato), avverte due volte che non è diagnostico, rifiuta la stima con troppe risposte ignote, e usa esattamente il modello misurato sul test.
