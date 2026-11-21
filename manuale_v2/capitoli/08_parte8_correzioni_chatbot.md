# Parte VIII — Evoluzione metodologica

## Capitolo 36 — La storia delle correzioni

La pipeline è stata corretta in due tornate: la revisione `fix/pipeline-quality` (unita a `master` il 6 settembre 2026) e il porting delle correzioni del repository `chatbot-forecast` (branch `fix/port-chatbot-corrections`, 14 novembre 2026). Il registro completo, in inglese, è `docs/CHANGES.md`, punti 1–16. Qui ogni correzione è raccontata con il problema, il codice prima e dopo e l'effetto.

### 36.1 Prima tornata (settembre 2026)

**Il test set veniva calcolato e scartato.** `preprocessing.py` eseguiva lo split 80/20 ma usava solo il training. È stata aggiunta la fase holdout (`holdout_evaluation.py`) e gli embedding del test set.

**La soglia era scelta sul fold di validazione.**

```python
# prima
precision, recall, thresholds = precision_recall_curve(y_val, y_score)   # etichette del fold valutato
# dopo (prima versione)
X_train, X_calib, y_train, y_calib = train_test_split(X_train_full, y_train_full, test_size=0.2, ...)
tau = optimal_f1_threshold(y_calib, calib_score)
```

**L'imputazione poteva usare statistiche del test.** Separate `fit_imputation_values` (stima sul training) e `apply_imputation` (applicazione).

**Valori imputati indistinguibili da quelli misurati.** Aggiunti indicatori `<col>_missing` per le colonne mancanti oltre il 30% e "not recorded" nel testo.

**Nessuna correzione per confronti multipli.** Aggiunte le colonne Benjamini-Hochberg.

**Il report conteneva testo fisso**, in parte smentito dai dati (affermava che GTE-large aveva l'AUC più alta, falso in entrambi i dataset). Discussione e conclusioni ora sono calcolate.

**Coerenza del codice.** Il dizionario `results` è generato da `models_all`; il grafico per famiglia non perde famiglie sconosciute; la pulizia delle cartelle copre tutti i file; il README indicava un modello Ollama sbagliato.

### 36.2 Seconda tornata (novembre 2026)

**Niente oversampling.**

```python
# prima
X_train_bal, y_train_bal = balance_classes(X_train_imputed, y_train, cat_cols_used)   # SMOTENC
return X_train_bal, y_train_bal
# dopo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
return X_train, X_test, y_train, y_test
```

Effetto: su Diabetes130 l'AUC in CV passa da 0,71–0,77 apparenti a 0,60–0,61 reali, e quella sul test sale da 0,48–0,55 a 0,61–0,62.

**Niente imputazione per il testo.** Indicatori e `_masked()` eliminati: ogni mancante è "not recorded". L'imputazione resta su una copia per i grafici.

**Soglia out-of-fold, classificatore su tutto il fold.**

```python
# dopo
tau = out_of_fold_threshold(X_train_full, y_train_full)
logisticReg.fit(X_train_full, y_train_full)
```

**Pulizia di Diabetes130.** `keep_default_na=False`, esclusione di decessi e hospice, un ricovero per paziente, `Unknown/Invalid` come mancante; test set passato in memoria.

**512 token.** `model.max_seq_length = HF_MAX_SEQ_LENGTH` per i modelli Hugging Face.

**`thal`.** "thalassemia" diventa "thallium stress test"; "reversable" diventa "reversible".

**Metriche.** PR-AUC, Brier, precision, recall, prevalenza; il report non parla più di una baseline al 50% "per costruzione".

**Inferenza.** Un campo può essere ignoto solo se mancava anche nel training.

**Standardizzazione e regolarizzazione per encoder.** Gli embedding Ollama hanno norma 1, quelli Hugging Face 11–13: con C = 1 su vettori grezzi la penalità L2 era molto più forte per i generalisti, e il confronto tra famiglie ne risultava falsato (capitolo 32.4). Ora ogni encoder viene standardizzato e riceve il proprio C, scelto per CV interna.

```python
# prima
logisticReg = LogisticRegression(max_iter=2000)            # C = 1, vettori grezzi
# dopo
logisticReg, tau, C = fit_classifier(X_train_full, y_train_full)   # StandardScaler + C da CV interna
```

### 36.3 Una lezione generale

Quasi ogni correzione riguarda informazione che passava dalla valutazione all'addestramento, o dati che non descrivevano ciò che si credeva (valori inventati, frasi troncate, etichette sbagliate). Nessuno di questi problemi produceva un errore: il codice girava e i numeri sembravano plausibili. Sono emersi confrontando misure che avrebbero dovuto coincidere (CV e test), leggendo i dati intermedi (le frasi, i token) e ricalcolando le metriche su sottoinsiemi.

> *Per la tesi.* Questo capitolo si presta a una sezione "Validità e correzioni del protocollo". È un contributo reale: documenta errori frequenti nella letteratura applicata e come riconoscerli.

# Parte IX — Il chatbot

## Capitolo 37 — Sistemi di dialogo e il chatbot Forecast

### 37.1 Tipi di sistemi conversazionali

- **Open-domain**: conversano su qualunque argomento (oggi tipicamente basati su grandi modelli generativi).
- **Task-oriented**: aiutano a completare un compito preciso (prenotare, compilare un modulo). L'architettura classica ha quattro componenti: comprensione del linguaggio (riconoscere intenzione e valori), tracciamento dello stato del dialogo, politica (decidere la prossima mossa), generazione della risposta.

Il chatbot di Forecast è un sistema task-oriented minimale a **riempimento di slot** (*slot filling*): ogni variabile clinica è uno slot; lo stato è l'insieme degli slot già riempiti; la politica è fissa (chiedere il prossimo slot vuoto); la generazione usa testi predefiniti. La decisione clinica non è nel dialogo ma nel modello statistico.

### 37.2 Perché un dialogo deterministico

- **Prevedibile e verificabile**: ogni domanda, risposta di errore e messaggio è scritto e testato.
- **Nessuna allucinazione**: un modello generativo potrebbe inventare spiegazioni o valori; qui non può succedere.
- **Separazione delle responsabilità**: il dialogo raccoglie dati validi, il modello stima il rischio, e ciascuna parte si può valutare da sola.

Il prezzo è la rigidità: l'utente deve rispondere nel formato atteso (un numero, "sì/no", un codice).

### 37.3 Architettura

![Architettura del chatbot (repository `chatbot-forecast`).](figure/schema_chatbot.png)

| Componente | Ruolo |
| --- | --- |
| `chatbot_core.py` | Liste di domande per dataset (campo, testo, spiegazione, parser, messaggio di errore), `ConversationSession`, `handle_message()`, `_predict()` |
| `app_streamlit.py` | Interfaccia web; sessione in `st.session_state` |
| `bot_telegram.py` | Bot Telegram asincrono a polling; una sessione per `chat_id`; token in `.env` |
| `main.py` | Ricostruisce dati, embedding e classificatore del dataset scelto, poi avvia l'interfaccia |
| `classification.py` | CV annidata, soglia out-of-fold, misura sul test, salvataggio di `deployed_bundle.joblib` |

### 37.4 Il flusso di una conversazione

1. Benvenuto e avvertenza ("non sono uno strumento diagnostico").
2. Per ogni domanda: testo, spiegazione, invito a rispondere "Non lo so" se non si conosce il dato.
3. Il parser valida la risposta (intervalli numerici, scelte ammesse, sinonimi come "uomo/maschio/m"). Se non è valida, la domanda viene ripetuta con un messaggio di errore.
4. "Non lo so", "non ricordo", "?" e simili lasciano il campo vuoto.
5. A domande finite: se meno del 50% delle risposte è nota, il bot non dà la stima. Altrimenti genera la frase con `record_to_text_*`, la trasforma in vettore con sentence-biobert, calcola la probabilità e la confronta con τ.
6. Risposta: "a RISCHIO" o "a BASSO rischio", probabilità, soglia, numero di risposte ignote, avvertenza. "nuovo" ricomincia.

### 37.5 Il modello in produzione

`classification.py` del chatbot salva in `deployed_bundle.joblib` il classificatore addestrato su tutto il training, la soglia, il nome dell'encoder e `max_seq_length`. Al caricamento il bot verifica che encoder e lunghezza coincidano con la configurazione attuale e rifiuta un bundle incoerente. Il modello in uso è esattamente quello misurato sul test set: Heart Disease AUC 0,911, Diabetes130 AUC 0,611.

### 37.6 Limiti da correggere

1. **"Non lo so" su campi mai mancanti.** Su Diabetes130 17 campi su 19 non mancano mai nel training; su Heart Disease età, sesso, `cp` e `restecg`. Per questi la frase con "not recorded" non è mai stata vista dal classificatore: la probabilità non ha base empirica. Correzione: accettare "Non lo so" solo per i campi mancanti nel training, come `inference.py`.
2. **Verdetto binario su Diabetes130.** Con precision 0,148 circa 6 "a RISCHIO" su 7 non vengono riammessi. Meglio mostrare la probabilità confrontata con la media (9%).
3. **"Non lo so" può alzare il rischio.** Su Heart Disease la mancanza di `ca`/`thal` è associata ai centri ad alta prevalenza (capitolo 33): un utente che non conosce un esame può vedere salire la stima.
4. **Domande da specialista.** Fluoroscopia e sottoslivellamento ST non sono dati che un paziente conosce: lo strumento ha senso per un operatore sanitario con il referto, non per il pubblico.
5. **Sessioni in memoria**: un riavvio perde le conversazioni.

### 37.7 Test del chatbot

`tests/test_chatbot_core.py` (12 test) verifica: ogni domanda ha una spiegazione; "Non lo so" fa avanzare e produce "not recorded"; troppe risposte ignote bloccano la stima; il parser intero rifiuta infinito e decimali; le categorie di Diabetes130 sono validate e normalizzate; `None` resta una categoria; l'encoder legge la frase intera; la probabilità usata è quella della classe positiva; la soglia è calibrata separatamente dal classificatore.

## Capitolo 38 — Etica, privacy e regolamentazione

### 38.1 Dati sanitari e privacy

Nel Regolamento generale sulla protezione dei dati (GDPR, Regolamento UE 2016/679) i dati relativi alla salute sono una categoria particolare (articolo 9): il loro trattamento è vietato salvo eccezioni (consenso esplicito, finalità di cura, ricerca scientifica con garanzie adeguate). I dataset del progetto sono pubblici e de-identificati, ma un sistema che riceve dati di pazienti reali rientrerebbe pienamente nel regolamento.

L'esecuzione **interamente locale** di Forecast è un vantaggio concreto: le frasi descrittive dei pazienti non vengono inviate a servizi esterni (nessuna API cloud). Il chatbot via Telegram, invece, fa transitare le risposte sui server di Telegram: per dati reali andrebbe evitato o valutato con attenzione.

### 38.2 Software come dispositivo medico

Nell'Unione Europea un software destinato a fornire informazioni usate per decisioni diagnostiche o terapeutiche può essere un dispositivo medico ai sensi del Regolamento UE 2017/745 (MDR); la regola 11 dell'allegato VIII ne disciplina la classificazione, di norma almeno in classe IIa. Un chatbot che stima un rischio clinico per un paziente specifico, se messo in uso, ricadrebbe probabilmente in questa definizione e richiederebbe marcatura CE, valutazione clinica e gestione del rischio. Come prototipo di ricerca, con avvertenze esplicite, non è destinato a quell'uso.

### 38.3 AI Act

Il Regolamento UE 2024/1689 (AI Act) classifica come ad alto rischio, tra gli altri, i sistemi di IA che sono componenti di sicurezza di dispositivi medici soggetti a valutazione di terza parte. Gli obblighi riguardano gestione del rischio, qualità dei dati, documentazione tecnica, trasparenza, supervisione umana e accuratezza. Molti di questi temi coincidono con quelli del progetto: qualità e rappresentatività dei dati (capitolo 19), documentazione (questo libro), trasparenza verso l'utente (le avvertenze del chatbot).

> *Da verificare.* Classificazioni e tempi di applicazione di MDR e AI Act vanno citati dai testi ufficiali (EUR-Lex) e, se servono dettagli, da guide della Commissione o del Medical Device Coordination Group.

### 38.4 Rischi specifici

- **Bias di automazione**: l'utente tende a fidarsi del verdetto della macchina anche quando contraddice altri indizi.
- **Popolazioni non rappresentate**: dati statunitensi ed europei degli anni '80 (Heart) e 1999–2008 (Diabetes); nessuna garanzia su altre popolazioni.
- **Calibrazione**: una probabilità mostrata all'utente deve essere affidabile; il progetto non ha ancora curve di calibrazione.
- **Scorciatoie**: la dipendenza dal centro e dalla mancanza (capitolo 33) significa che il modello può reagire al modo in cui un dato è stato raccolto.

### 38.5 Linee guida di reporting

Per riportare un modello predittivo clinico la linea guida di riferimento è TRIPOD, aggiornata per l'intelligenza artificiale in TRIPOD+AI (Collins et al., 2024). Elenca ciò che una pubblicazione deve dire: fonte dei dati, partecipanti, esito, predittori, dati mancanti, sviluppo del modello, validazione, prestazioni (discriminazione e calibrazione), limiti. Usarla come lista di controllo per la tesi è un modo semplice di non dimenticare nulla.
