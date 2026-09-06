# Capitolo 30 — Il dataset Diabetes 130-US Hospitals

**Obiettivi del capitolo**

- Capire la scala reale di questo dataset e perché il progetto ne usa solo una parte campionata.
- Sapere quali 19 feature, fra le circa 50 originali, sono state scelte e perché le altre sono state escluse.
- Riconoscere un limite di qualità dei dati specifico di questo dataset, analogo ma indipendente da quello già visto per Heart Disease.

## 30.1 Scala, 101.766 righe, e campionamento a 20.000

**[Fatto]** Il file sorgente (`diabetic_data.csv`) contiene **101.766 righe** (verificato con `wc -l`, che dà 101.767 includendo l'intestazione), ciascuna un ricovero ospedaliero di un paziente diabetico in uno fra 130 ospedali statunitensi, raccolto fra il 1999 e il 2008 — **[Fatto]** con fonte citabile: Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., & Clore, J. (2014). *Diabetes 130-US Hospitals for Years 1999-2008*. UCI Machine Learning Repository. DOI: 10.24432/C5230J.

**[Fatto]** `load_diabetes130(sample_size=20000, random_state=42)` (`function.py:116-132`) non usa l'intero file: campiona 20.000 righe con `train_test_split(df, train_size=sample_size, stratify=df["readmitted"], random_state=random_state)` (riga 127-129) — uno split stratificato usato qui non per separare training e test, ma solo per **estrarre un sottoinsieme** che preservi la proporzione originale di riammissioni, scartando esplicitamente l'altra parte (`_`, l'assegnazione a variabile anonima già vista come convenzione al capitolo 8.2). **[Interpretazione]** Un campione stratificato di un quinto dei dati originali è una scelta ragionevole per contenere i tempi di generazione degli embedding (sette modelli, quattro dei quali via rete verso Ollama) — ma significa che ogni conclusione tratta su questo dataset riguarda quel campione specifico, non l'intera popolazione di 101.766 ricoveri, un punto che il capitolo 51 riprende.

## 30.2 Le 19 feature scelte tra ~50

**[Fatto]** Il file grezzo ha 50 colonne; `columns_diabetes130` (`function.py:21-27`) ne mantiene 19:

| Categoria | Colonne | Numero |
|---|---|---|
| Demografia | `race`, `gender`, `age` | 3 |
| Contesto del ricovero | `admission_type_id`, `discharge_disposition_id`, `admission_source_id` | 3 |
| Utilizzo dell'assistenza (numerico) | `time_in_hospital`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient`, `number_diagnoses` | 8 |
| Laboratorio/farmaci (categoriale) | `max_glu_serum`, `A1Cresult`, `insulin`, `change`, `diabetesMed` | 5 |
| Target | `readmitted` | 1 |

**[Fatto]** `docs/DATASET.md:83` motiva l'esclusione delle circa 31 colonne rimanenti: la maggior parte sono flag di dosaggio farmacologico quasi costanti (per esempio `examide`, `citoglipton` — nomi di farmaci specifici, ciascuno con una colonna dedicata nel file originale, quasi sempre allo stesso valore per ogni paziente) o identificatori ad altissima percentuale di valori mancanti (`weight`, `payer_code`) o non generalizzabili (`patient_nbr`, un identificativo di paziente). **[Da verificare]** Anche i codici diagnostici ICD (`diag_1`, `diag_2`, `diag_3`), potenzialmente informativi, sono esclusi — `docs/DATASET.md:106` lo dichiara una scelta esplicita per evitare l'alta cardinalità di questi campi, ma non ne quantifica il costo in termini di segnale perso: resta una domanda aperta se la loro esclusione influisca in modo sostanziale sulle prestazioni osservate.

**[Fatto]** Fra le 19 feature mantenute, due presentano lo stesso tipo di problema già visto per `ca`/`thal` in Heart Disease (capitolo 29.3), verificato sull'intero file grezzo prima del campionamento: **`max_glu_serum` manca nel 94.7%** delle 101.766 righe, **`A1Cresult` manca nell'83.3%**. **[Fatto]** Entrambe sono trattate come categoriali (`cat_cols_diabetes130`, `function.py:32-35`) e quindi imputate con la moda (`preprocessing.py:80-81`) — per la stragrande maggioranza dei pazienti, il valore di questi due esami di laboratorio non è mai stato osservato ma sostituito dal valore più frequente osservato nel 5.3%/16.7% dei casi in cui erano davvero presenti.

> **ATTENZIONE —** a differenza di `ca`/`thal` in Heart Disease, qui la causa della mancanza non è un centro clinico che ha smesso di raccogliere quel dato: `max_glu_serum` e `A1Cresult` sono esami di laboratorio specifici (glicemia e emoglobina glicata), richiesti solo quando clinicamente indicato — un'assenza che potrebbe essa stessa portare informazione clinica (il test non richiesto potrebbe correlare con una gestione meno intensiva del paziente), invece di essere puro rumore da imputare via. Trattarla come un semplice valore mancante da colmare con la moda, come fa questo progetto, scarta silenziosamente questa possibile informazione — un'assunzione implicita sui dati, non discussa da nessuna parte nella documentazione esistente.

## 30.3 La ridefinizione del target

**[Fatto]** La colonna originale `readmitted` ha tre valori possibili nel file sorgente: riammesso entro 30 giorni, riammesso dopo più di 30 giorni, mai riammesso. **[Fatto]** `function.py:124` la binarizza con `(df["readmitted"] == "<30").astype(int)`: la classe positiva è **solo** la riammissione entro 30 giorni; sia "riammesso più tardi" sia "mai riammesso" diventano entrambe classe negativa. **[Livello: teoria consolidata del settore]** Questa è effettivamente la definizione di benchmark più diffusa in letteratura per questo dataset (`docs/DATASET.md:80,107`), non un'invenzione del progetto — ma è una scelta di framing con una conseguenza precisa: il modello non impara a distinguere "paziente che tornerà" da "paziente che non tornerà mai", impara a distinguere "tornerà entro un mese" da "tutto il resto", incluso chi tornerà fra sei mesi. Il capitolo 53 lo riprende quando discute cosa questo progetto prova, e cosa no.

## Riepilogo

Diabetes130 conta 101.766 ricoveri originali, di cui il progetto ne usa un campione stratificato di 20.000; 19 delle circa 50 colonne originali sono mantenute, escludendo flag di dosaggio quasi costanti, identificatori ad alta cardinalità o mancanza, e i codici diagnostici ICD. Due delle 19 feature mantenute (`max_glu_serum`, `A1Cresult`) sono mancanti nella grande maggioranza dei casi e vengono comunque imputate con la moda, un limite di qualità dei dati analogo a quello di Heart Disease ma con una causa probabilmente diversa e potenzialmente più informativa. Il target è ristretto, per definizione di benchmark consolidata in letteratura, alla sola riammissione entro 30 giorni.

## Domande di autoverifica

**1. Perché il progetto usa un campione di 20.000 righe invece dell'intero file di 101.766?**
Per contenere i tempi della fase più costosa della pipeline — la generazione di embedding per sette modelli diversi, quattro dei quali via chiamate di rete a un server locale — mantenendo però, grazie al campionamento stratificato, la stessa proporzione di riammissioni del dataset completo.

**2. Perché l'assenza di `max_glu_serum` in un ricovero potrebbe essere informazione clinica, non solo rumore da imputare?**
Perché questo test di laboratorio viene richiesto solo quando clinicamente indicato: la sua assenza potrebbe correlare con una gestione meno intensiva o con un profilo di rischio diverso del paziente, un segnale che l'imputazione con la moda scarta trattando l'assenza come puro dato mancante.

**3. Cosa NON impara a distinguere un modello addestrato su questo target binarizzato?**
Non impara a distinguere "il paziente tornerà in ospedale" da "non tornerà mai": impara solo a distinguere "tornerà entro 30 giorni" da "tutto il resto", che include sia chi non tornerà mai sia chi tornerà, per esempio, dopo sei mesi — entrambi classificati allo stesso modo come classe negativa.

> **MATERIALE PER LA TESI**
> 1. La tabella delle 19 feature per categoria, con la motivazione dell'esclusione delle altre circa 31 colonne — riusabile in "Materiali e metodi" per descrivere la selezione delle feature.
> 2. Il dato quantificato sulla mancanza di `max_glu_serum` e `A1Cresult`, con l'ipotesi che l'assenza stessa sia informativa — riusabile come punto di discussione originale nella sezione "Limiti", parallelo ma distinto da quello di Heart Disease.
> 3. La spiegazione precisa di cosa il target binarizzato misura e cosa no — riusabile per calibrare correttamente, nell'introduzione della tesi, l'affermazione su cosa il sistema "prevede" davvero.
