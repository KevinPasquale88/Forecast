# Capitolo 49 — Scrivere il primo test per questo progetto

**Obiettivi del capitolo**
- Avere un test reale, eseguibile, per una funzione pura del progetto.
- Vedere come isolare la logica della soglia F1-ottima da tutto il resto di `classification.py`.
- Sapere quale tecnica servirebbe per testare le funzioni che toccano rete o disco, senza doverle eseguire davvero.

## 49.1 Un test per `record_to_text_heart_disease`

**[Fatto]** `record_to_text_heart_disease(row)` (`embedding.py:43-59`, capitolo 22.1) riceve una riga di DataFrame e restituisce una stringa — l'ideale per un primo test, secondo il capitolo 48.2. Un test minimo, con `pytest`:

```python
import pandas as pd
from embedding import record_to_text_heart_disease

def test_record_to_text_paziente_completo():
    row = pd.Series({
        "sex": 1, "age": 63, "cp": 1, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6,
    })
    testo = record_to_text_heart_disease(row)
    assert "Male patient, 63 years old" in testo
    assert "chest pain type: typical angina" in testo
    assert "thalassemia: fixed defect" in testo

def test_record_to_text_valore_mancante():
    row = pd.Series({
        "sex": 0, "age": 55, "cp": 4, "trestbps": float("nan"), "chol": 200,
        "fbs": 0, "restecg": 0, "thalach": 140, "exang": 1,
        "oldpeak": 1.0, "slope": 2, "ca": 1, "thal": 3,
    })
    testo = record_to_text_heart_disease(row)
    assert "resting blood pressure: not recorded" in testo
```
Il primo test verifica che i codici numerici (`cp=1`, `thal=6`) vengano tradotti correttamente nelle etichette leggibili attese (capitolo 22.1, `CP_LABELS`, `THAL_LABELS`); il secondo verifica il caso limite già discusso al capitolo 31.3 — un valore `NaN` residuo diventa `"not recorded"`, non un errore né la stringa letterale `"nan"`.

> **RIFERIMENTO AL CODICE —** questi test non richiedono importare l'intero progetto: solo `embedding.py` e `pandas`. Eseguirli con `pytest test_embedding.py` (o il nome scelto per il file) richiede solo che l'ambiente virtuale del capitolo 15 sia attivo, non Ollama né una connessione di rete.

## 49.2 Un test per la logica di soglia F1-ottima con dati sintetici

**[Fatto]** La ricerca della soglia F1-ottima (`classification.py:30-35`, Formula 35.1) è incorporata dentro un ciclo più ampio, non isolata in una propria funzione — un limite di progettazione che rende il test seguente più laborioso di quanto dovrebbe essere (un punto su cui torna il capitolo 55). Isolandola manualmente per il test:

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

def soglia_f1_ottima(y_val, y_score):
    precision, recall, thresholds = precision_recall_curve(y_val, y_score)
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-6)
    return thresholds[f1_scores.argmax()]

def test_soglia_su_separazione_perfetta():
    # 4 casi negativi con punteggio basso, 4 positivi con punteggio alto: separazione netta
    y_val = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_score = np.array([0.1, 0.2, 0.15, 0.05, 0.9, 0.8, 0.95, 0.85])
    tau = soglia_f1_ottima(y_val, y_score)
    assert 0.2 < tau <= 0.8  # qualunque soglia in questo intervallo separa perfettamente le due classi

def test_soglia_su_dati_non_informativi():
    # punteggi casuali, senza relazione con l'etichetta: la soglia scelta è comunque un numero valido
    rng = np.random.default_rng(42)
    y_val = rng.integers(0, 2, 50)
    y_score = rng.random(50)
    tau = soglia_f1_ottima(y_val, y_score)
    assert 0.0 <= tau <= 1.0
```
Il primo test verifica il caso "facile": con una separazione perfetta fra le due classi, qualunque soglia nell'intervallo giusto massimizza F1, e il test lo verifica con un margine, non un valore esatto (`0.2 < tau <= 0.8`), perché la funzione potrebbe legittimamente scegliere una soglia diversa a seconda di dove cadono i punti di discontinuità della curva precisione-recall. Il secondo verifica solo che la funzione non fallisca e restituisca un valore nell'intervallo valido, anche quando i dati non portano alcun segnale reale — un test di robustezza, non di correttezza del risultato specifico.

## 49.3 Cosa serve per testare le funzioni che toccano il disco o la rete

**[Livello: teoria consolidata del settore]** Testare `generate_embeddings_batch()` (`embedding.py:103-137`, capitolo 22.2) così com'è richiederebbe un server Ollama realmente in esecuzione — un test lento, fragile (dipende dalla disponibilità di un servizio esterno), e non ripetibile in isolamento. La tecnica standard per evitarlo è il **mocking**: sostituire, solo durante il test, l'oggetto `Client` di Ollama con un oggetto finto che restituisce risposte predefinite, senza fare alcuna vera chiamata di rete.

```python
from unittest.mock import patch, MagicMock
from embedding import generate_embeddings_batch

def test_generate_embeddings_batch_con_client_finto():
    risposta_finta = MagicMock()
    risposta_finta.embeddings = [[0.1, 0.2, 0.3]] * 16
    with patch("embedding.Client") as ClientFinto:
        ClientFinto.return_value.embed.return_value = risposta_finta
        risultati = generate_embeddings_batch("modello-finto", ["frase"] * 16, batch_size=16)
    assert len(risultati) == 16
```
`patch("embedding.Client")` sostituisce temporaneamente, solo dentro il blocco `with`, la classe `Client` importata in `embedding.py` con un oggetto finto (`MagicMock`) che restituisce `risposta_finta.embeddings` ogni volta che viene chiamato `.embed(...)` — nessuna connessione di rete viene mai aperta, e il test verifica solo che la funzione elabori correttamente la struttura della risposta, non che Ollama funzioni davvero.

> **SE VIENI DA JAVA —** `unittest.mock.patch` gioca un ruolo concettualmente simile a Mockito: sostituisce una dipendenza con un doppio di test, per la durata del test. La differenza pratica più notevole: `patch` qui sostituisce un nome importato in un modulo specifico (`"embedding.Client"`, non semplicemente `"ollama.Client"`) — un dettaglio che confonde spesso chi arriva da un framework di mocking basato su iniezione di dipendenze esplicita, dove l'oggetto da sostituire è passato come parametro, non risolto per nome del modulo che lo importa.

## Riepilogo

Un primo test su `record_to_text_heart_disease()` verifica la traduzione dei codici e la gestione dei valori mancanti, senza toccare rete o disco. Isolare la logica della soglia F1-ottima in una funzione a sé permette di testarla su dati sintetici, sia nel caso di separazione perfetta sia su dati privi di segnale. Testare le funzioni che chiamano Ollama richiede il mocking del client, sostituendo temporaneamente la dipendenza esterna con un oggetto finto che restituisce risposte predefinite.

## Domande di autoverifica

**1. Perché il test sulla separazione perfetta verifica un intervallo (`0.2 < tau <= 0.8`) invece di un valore esatto di soglia?**
Perché la funzione sceglie la soglia fra i punti di discontinuità della curva precisione-recall, che dipendono dai valori esatti dei punteggi: più soglie diverse, in questo esempio, separano ugualmente bene le due classi e massimizzano F1 allo stesso modo, quindi il test verifica solo che il risultato sia in un intervallo ragionevole, non un singolo valore.

**2. Perché testare `generate_embeddings_batch()` senza mocking sarebbe un test fragile, non solo lento?**
Perché dipenderebbe dalla disponibilità reale di un server Ollama in esecuzione con il modello richiesto scaricato: un problema di rete, un server non avviato, o un modello mancante farebbero fallire il test per ragioni indipendenti dalla correttezza del codice che si vuole verificare.

**3. Cosa sostituisce esattamente `patch("embedding.Client")`, e perché non basta scrivere `patch("ollama.Client")`?**
Sostituisce il nome `Client` così come è stato importato dentro il modulo `embedding.py` (`from ollama import Client`, `embedding.py:10`), non la classe originale nel modulo `ollama`: `embedding.py` ha già il proprio riferimento locale a `Client`, ed è quello che va sostituito perché la funzione sotto test lo usi.

> **MATERIALE PER LA TESI**
> 1. I quattro test completi di questo capitolo — riusabili direttamente come contributo di test scritto per la tesi, con la spiegazione del perché ciascuno è stato progettato in quel modo.
> 2. L'osservazione che la logica della soglia non è isolata in una propria funzione nel codice originale — riusabile come esempio concreto di come la mancanza di test scoraggi (o sia scoraggiata da) una progettazione più modulare.
> 3. La spiegazione del mocking applicata a `Client` di Ollama — riusabile come nota tecnica per chi debba scrivere test per qualunque altra parte del progetto che tocchi servizi esterni.
