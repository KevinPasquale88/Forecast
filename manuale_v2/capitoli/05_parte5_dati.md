# Parte V — I dati

## Capitolo 19 — UCI Heart Disease

### 19.1 Origine

Il dataset nasce dallo studio di Detrano et al. (1989), che sviluppò un algoritmo probabilistico per la diagnosi di coronaropatia a Cleveland e lo verificò in tre centri esterni. Il deposito UCI (Janosi, Steinbrunn, Pfisterer, Detrano, 1988) contiene 76 attributi; quasi tutta la letteratura usa i 14 delle versioni "processed", come il progetto. Molti lavori usano solo Cleveland (303 record, di cui 297 senza valori mancanti in `ca`/`thal`: da qui il "297" della vecchia documentazione); Forecast unisce i quattro centri (920 record).

| Centro | Record | Prevalenza della malattia |
| --- | --- | --- |
| Cleveland Clinic Foundation (USA) | 303 | 45,9% |
| Hungarian Institute of Cardiology, Budapest | 294 | 36,1% |
| University Hospital Zurich e Basel (Svizzera) | 123 | 93,5% |
| V.A. Medical Center, Long Beach (USA) | 200 | 74,5% |
| **Totale** | **920** | **55,3%** |

### 19.2 Variabili e codifiche

| Variabile | Tipo | Valori | Testo generato |
| --- | --- | --- | --- |
| `age` | numerica | anni | "63 years old" |
| `sex` | binaria | 1 maschio, 0 femmina | "Male/Female patient" |
| `cp` | categorica | 1 angina tipica, 2 atipica, 3 dolore non anginoso, 4 asintomatico | "chest pain type: …" |
| `trestbps` | numerica | mm Hg all'ingresso | "resting blood pressure: 145 mm Hg" |
| `chol` | numerica | mg/dl | "serum cholesterol: 233 mg/dl" |
| `fbs` | binaria | glicemia a digiuno > 120 mg/dl | "fasting blood sugar > 120 mg/dl: yes/no" |
| `restecg` | categorica | 0 normale, 1 anomalia ST-T, 2 ipertrofia ventricolare sinistra | "resting electrocardiographic results: …" |
| `thalach` | numerica | battiti/minuto | "maximum heart rate achieved: 150" |
| `exang` | binaria | angina da sforzo | "exercise-induced angina: yes/no" |
| `oldpeak` | numerica | mm di sottoslivellamento ST | "ST depression induced by exercise: 2.3" |
| `slope` | categorica | 1 ascendente, 2 piatta, 3 discendente | "slope of the peak exercise ST segment: …" |
| `ca` | numerica discreta | 0–3 vasi | "number of major vessels colored by fluoroscopy: 0" |
| `thal` | categorica | 3 normale, 6 difetto fisso, 7 difetto reversibile | "thallium stress test: …" |
| `num` | target | 0 assente, 1–4 presente | — |

### 19.3 Valori mancanti, per centro

| Centro | `ca` | `thal` | `slope` | `chol` |
| --- | --- | --- | --- | --- |
| Cleveland | 1% | 1% | 0% | 0% |
| Ungheria | 99% | 90% | 65% | 8% |
| Svizzera | 96% | 42% | 14% | 100% |
| Long Beach VA | 99% | 83% | 51% | 28% |

Nel training set (736 record) mancano `ca` 65,9%, `thal` 51,8%, `slope` 32,7%, `chol` 21,6%, `fbs` 9,2%, `oldpeak` 7,1%, `trestbps` 6,8%, `thalach` ed `exang` 6,4%. La Svizzera non ha nessun valore di colesterolo (tutti zeri nel file originale).

> *Per la tesi.* La mancanza non è casuale: dipende dal centro, e il centro è legato alla prevalenza (dal 36% dell'Ungheria al 94% della Svizzera). Un modello può quindi usare "quali campi mancano" come indizio del centro, e il centro come indizio della diagnosi. Il capitolo 33 misura quanto pesa.

![Correlazioni tra le variabili numeriche del training di Heart Disease (copia imputata usata solo per i grafici).](figure/heatmap_correlation.png)

### 19.4 Limiti noti

- Dati di fine anni '80; criteri diagnostici e popolazioni sono cambiati.
- Popolazioni molto diverse per prevalenza: la Svizzera ha quasi solo malati, quindi dentro quel centro la discriminazione si misura su pochissimi sani (7 nel training).
- `ca` e `thal`, tra i predittori più noti, mancano per due terzi dei record.

## Capitolo 20 — Diabetes 130-US Hospitals

### 20.1 Origine

Il dataset (Strack et al., 2014) estrae dal database Health Facts (Cerner) ricoveri di pazienti diabetici in 130 ospedali statunitensi tra il 1999 e il 2008. Un ricovero entra nel dataset se è ospedaliero, con diagnosi di diabete, durata tra 1 e 14 giorni, con esami di laboratorio e farmaci somministrati. Contiene 101.766 ricoveri di 71.518 pazienti e circa 50 colonne.

L'articolo originale studia l'effetto della misura dell'HbA1c sulla riammissione. Il target `readmitted` ha tre valori: `<30` (entro 30 giorni), `>30` (dopo), `NO`. Il progetto, come la letteratura di benchmark, considera positivo solo `<30`.

### 20.2 Pulizia

| Passo | Motivo | Ricoveri restanti |
| --- | --- | --- |
| File originale | — | 101.766 |
| Esclusi decesso o hospice (`discharge_disposition_id` 11, 13, 14, 19, 20, 21) | La riammissione non è definita o non è un esito sensato | 99.343 |
| Primo ricovero per paziente | Osservazioni indipendenti; nessun paziente in training e test insieme | 69.990 |
| Campione stratificato | Tempo di calcolo degli embedding (7 modelli) | 20.000 |

Dopo la pulizia la prevalenza scende dall'11,2% (file grezzo) al 9,0%: i pazienti con molti ricoveri, più propensi alla riammissione, contano ora una volta sola.

> *Attenzione.* Senza la deduplicazione per paziente lo stesso paziente può comparire in training e test con ricoveri diversi: il modello "riconosce" il paziente e la stima è ottimistica. È una forma di leakage frequente nei lavori su questo dataset.

### 20.3 Le 19 variabili

| Gruppo | Variabili | Note |
| --- | --- | --- |
| Demografia | `race`, `gender`, `age` | `age` in fasce decennali (`[60-70)`) |
| Ricovero | `admission_type_id`, `discharge_disposition_id`, `admission_source_id` | Codici numerici; il significato è in `IDS_mapping.csv` (1 Emergency, 2 Urgent, 3 Elective...) |
| Utilizzo | `time_in_hospital`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient`, `number_diagnoses` | Conteggi |
| Esami | `max_glu_serum`, `A1Cresult` | `None` (non eseguito) 95,2% e 81,6% |
| Terapia | `insulin`, `change`, `diabetesMed` | Insulina No/Up/Down/Steady; cambio di terapia; farmaco per il diabete |

Escluse: diagnosi (`diag_1/2/3`, codici ICD-9), specialità medica, peso (97% mancante), pagatore, le 23 colonne dei singoli farmaci, gli identificativi.

### 20.4 Quanto predicono le singole variabili

Nel campione di 20.000 ricoveri la prevalenza è 9,0%. Alcune variabili la spostano visibilmente:

| Variabile | Valore | Riammessi entro 30 giorni | Ricoveri |
| --- | --- | --- | --- |
| Ricoveri nell'anno precedente (`number_inpatient`) | 0 | 8,1% | 17.711 |
| | 1 | 13,6% | 1.626 |
| | 2 | 19,4% | 403 |
| | 3 o più | 24,2% | 260 |
| Età | 40–50 | 7,3% | 1.934 |
| | 80–90 | 10,7% | 3.127 |
| Insulina | No | 8,1% | 9.735 |
| | Aumentata (Up) | 10,1% | 1.964 |
| A1C | Non misurata | 9,1% | 16.287 |
| | > 8 | 8,5% | 1.829 |

Il predittore più forte, i ricoveri precedenti, è anche il più "amministrativo". Le differenze sono di pochi punti percentuali: spiega perché nessun modello supera AUC 0,65.

### 20.5 Rappresentazione testuale e suoi limiti

Gli identificativi di ricovero e dimissione finiscono nel testo come numeri ("admission type id: 1"). Per un encoder di linguaggio "1" non significa "pronto soccorso"; la tabella di `IDS_mapping.csv` permetterebbe di scrivere "admission type: Emergency". È un miglioramento facile e misurabile (capitolo 40).

## Capitolo 21 — Dati mancanti: teoria e scelte

### 21.1 I tre meccanismi di Rubin

Rubin (1976) distingue tre meccanismi per cui un dato manca:

- **MCAR** (*missing completely at random*): la mancanza non dipende da nulla. Ignorarla non distorce i risultati, riduce solo i dati.
- **MAR** (*missing at random*): dipende da variabili osservate (qui: il centro). Si può correggere usando quelle variabili.
- **MNAR** (*missing not at random*): dipende dal valore mancante stesso o da fattori non osservati (un esame non fatto perché il medico lo riteneva inutile per quel paziente).

In Heart Disease la mancanza di `ca` e `thal` dipende soprattutto dal centro (MAR rispetto al centro, che però non è tra le variabili). In Diabetes130 un test HbA1c non eseguito è probabilmente MNAR: il medico decide se misurarlo in base al paziente, e lo studio di Strack trova proprio un'associazione tra misura ed esito.

### 21.2 Strategie

| Strategia | Pro | Contro |
| --- | --- | --- |
| Eliminare i record incompleti | Semplice | Su Heart Disease resterebbero quasi solo i record di Cleveland |
| Imputazione semplice (media, mediana, moda) | Semplice, conserva tutti i record | Inventa valori; riduce la variabilità; nasconde la mancanza |
| Imputazione + indicatore di mancanza | Il modello sa che il valore era assente | Nel testo il valore inventato resta scritto |
| Imputazione multipla, modelli | Statisticamente corretta sotto MAR | Complessa; non risolve MNAR |
| Mancanza come categoria / "not recorded" | Nessun valore inventato; la mancanza resta visibile | La mancanza può essere informativa (scorciatoia) |

### 21.3 La scelta del progetto

La pipeline scrive "not recorded" per ogni valore mancante. Le ragioni:

1. **Onestà del testo.** Un valore imputato scritto nella frase è indistinguibile da uno misurato.
2. **Coerenza training-inferenza.** Un campo ignoto nel chatbot o in `inference.py` produce la stessa frase usata in addestramento.
3. **Nessuna statistica da conservare.** L'imputazione richiederebbe di salvare mediane e mode del training per riusarle all'inferenza.

Il prezzo è che la mancanza resta un segnale per il modello. Se è legata all'esito (come in Heart Disease attraverso il centro), il modello la sfrutta. Non è un errore del modello, ma va dichiarato: parte della prestazione misurata viene da come i dati sono stati raccolti, non dalla clinica. Il capitolo 33 lo quantifica.

> *Per la tesi.* In passato la pipeline imputava `ca` e `thal`: la prima edizione del manuale mostrò che molti "casi più difficili" erano record sintetici o imputati con il profilo di default (`ca = 0`, `thal = 3`, cioè mediana e moda). È un buon esempio di come una scelta di preprocessing cambi l'interpretazione dei risultati.
