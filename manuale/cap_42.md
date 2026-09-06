# Capitolo 42 — Caso d'uso 3: aggiungere un ottavo encoder passo per passo

**Obiettivi del capitolo**

- Percorrere, passo per passo, l'intero processo di estensione già anticipato a livello architetturale al capitolo 19.3.
- Vedere il codice esatto da scrivere, non solo il principio generale.
- Sapere quali verifiche fare, e in quale ordine, prima di considerare l'estensione riuscita.

Questo capitolo prende il principio architetturale del capitolo 19.3 e lo trasforma in un esercizio concreto, con codice vero da scrivere — l'ultimo dei tre casi d'uso end-to-end di questa parte.

## 42.1 Dove si registra in `function.py`

**[Fatto]** `generatereport.py:221` suggerisce esplicitamente, nel testo statico del report (capitolo 27.2), di provare "bge-large" come modello aggiuntivo — un suggerimento scritto nel codice del progetto stesso, mai realizzato. Usiamolo come esempio concreto per questo esercizio.

**[Interpretazione]** Il primo passo, seguendo esattamente lo schema degli altri quattro modelli generalisti (`function.py:38-43`), sarebbe aggiungere una voce a `models_ollama`:
```python
models_ollama = [
    {"type": "ollama", "model_name": "e5-base", "name": "jeffh/intfloat-e5-base-v2:q8_0", ...},
    {"type": "ollama", "model_name": "gte-base", "name": "twwch/m3e-base", ...},
    {"type": "ollama", "model_name": "gte-large", "name": "zyw0605688/gte-large-zh", ...},
    {"type": "ollama", "model_name": "e5-large", "name": "jeffh/intfloat-multilingual-e5-large-instruct:q8_0", ...},
    {"type": "ollama", "model_name": "bge-large", "name": "<tag-ollama-da-verificare>",
     "filename": "bge_large_embeddings.npy", "filename_label": "bge_large_embeddings_labels.npy",
     "family": "general-purpose"},
]
```
**[Da verificare]** L'identificativo esatto del modello sul registro di Ollama (il campo `name`) andrebbe verificato consultando `ollama.com/library` prima di eseguire `ollama pull` — non lo indico qui perché non l'ho verificato in questa sessione, e inventarlo violerebbe il vincolo di verità di questo libro. Il resto della voce segue esattamente il pattern già visto: `filename`/`filename_label` con una convenzione di nomi coerente con gli altri, `family` scelta fra quelle già esistenti (qui, `"general-purpose"`, dato che bge-large è un modello generalista, non biomedico).

## 42.2 Cosa fa la pipeline da sola

**[Fatto]** Con questa sola modifica, `models_all` (`function.py:51`, l'unione di `models_ollama` e `models_medical`) diventa automaticamente una lista di otto elementi — e ogni fase che itera su `models_all` (`embeddings()`, `training_classifier()`, `evaluate_results()`, `analyze_errors()`, `test_statistical_tests()`) processerebbe l'ottavo modello **senza alcuna ulteriore modifica**, esattamente come mostrato al capitolo 19.3: nessuna di queste funzioni nomina un modello specifico per nome, tutte iterano genericamente sulla lista.

**[Fatto]** Poiché `bge-large` appartiene a una famiglia già esistente (`"general-purpose"`), anche `get_model_palette()` (`function.py:162-174`, capitolo 20.3) gestirebbe la nuova voce automaticamente: la famiglia `general-purpose` passerebbe da 4 a 5 membri, e `sns.light_palette()` genererebbe semplicemente cinque sfumature invece di quattro, tutte ancora distinguibili.

## 42.3 Verifica finale

**[Interpretazione]** Prima di considerare l'estensione completa, andrebbero verificati, in ordine:

1. **Il modello è raggiungibile**: `ollama pull <tag>` completa senza errori, poi `ollama list` lo mostra (capitolo 16.2).
2. **La pipeline genera il suo embedding**: dopo `python main.py`, `datas/<dataset>/embeddings/bge_large_embeddings.npy` esiste, con la forma attesa (numero di righe pari agli altri modelli, capitolo 40.2; numero di colonne pari alla dimensione dichiarata dal modello).
3. **Compare nei risultati**: `model_performance.csv` e `encoder_comparison_summary.csv` (capitolo 23.3, capitolo 24.3) hanno una riga in più, con `bge-large` come nome.
4. **Compare correttamente nei grafici**: la matrice di confusione dedicata esiste (`CM_bge-large.png`), e il modello compare con un colore distinto (non grigio, capitolo 19.3) nei grafici di confronto per famiglia.
5. **Compare nei confronti statistici**: `wilcoxon_comparison.csv`, `ttest_comparison.csv`, `delong_comparison.csv` (capitolo 26) mostrano ora $\binom{8}{2}=28$ righe per metrica invece di 21 — un modo indiretto ma verificabile di confermare che il modello è stato incluso in ogni fase.

> **PROVA TU —** l'ultima verifica di questo elenco è quella più facile da dimenticare, ed è anche quella più istruttiva: conta tu stesso le righe di uno dei tre CSV di confronto statistico dopo un'estensione reale (o, se non hai eseguito l'estensione, verifica che i CSV già presenti nel repository abbiano esattamente 21 righe per metrica, $\binom{7}{2}$, coerente con i sette modelli attuali). Se il numero di righe non corrisponde al numero atteso di combinazioni, una fase ha silenziosamente escluso un modello — un controllo di integrità che il progetto stesso non fa in automatico (capitolo 18.3).

## Riepilogo

Aggiungere un ottavo modello di una famiglia esistente richiede, in linea di principio, una sola modifica a `function.py` — una voce nella lista `models_ollama` o `models_medical`, seguendo il pattern degli altri modelli. Ogni fase della pipeline lo include automaticamente grazie all'iterazione generica su `models_all`. La verifica finale più affidabile non è guardare un singolo grafico, ma contare le righe dei CSV di confronto statistico: con $n$ modelli, ci si aspettano esattamente $\binom{n}{2}$ confronti per metrica.

## Domande di autoverifica

**1. Perché aggiungere `bge-large` a `models_ollama` non richiede toccare `classification.py`, `evaluation.py` o `error_analysis.py`?**
Perché tutte queste fasi iterano genericamente su `models_all`, senza mai nominare un modello specifico per nome: la lista con l'ottavo elemento propaga automaticamente la modifica a ogni fase che la consulta.

**2. Perché `bge-large`, appartenendo alla famiglia `"general-purpose"` già esistente, non richiede alcuna modifica a `FAMILY_COLORS`?**
Perché `FAMILY_COLORS` associa un colore a ogni *famiglia*, non a ogni modello: `get_model_palette()` genera automaticamente una sfumatura aggiuntiva del colore già assegnato a `"general-purpose"` per il quinto membro di quella famiglia, senza bisogno di una nuova voce.

**3. Con 8 modelli invece di 7, quante righe per metrica dovrebbero comparire in `wilcoxon_comparison.csv`, e come verificarlo praticamente?**
$\binom{8}{2} = 28$ righe per metrica, contro le 21 attuali con 7 modelli. Verificarlo è semplice quanto contare le righe del CSV filtrate per una singola metrica — un controllo indiretto ma affidabile che nessuna fase ha escluso silenziosamente il nuovo modello.

> **MATERIALE PER LA TESI**
> 1. La guida passo-passo completa, con il codice esatto della nuova voce di configurazione — riusabile come sezione "riproducibilità ed estensibilità" in appendice alla tesi, o come base per un esperimento aggiuntivo realmente eseguito.
> 2. La checklist di verifica in cinque punti (§42.3) — riusabile come protocollo di test manuale per qualunque estensione futura del progetto, citabile in "Lavori futuri".
> 3. Il controllo del numero atteso di combinazioni $\binom{n}{2}$ come verifica di integrità indiretta — riusabile come esempio di test di regressione minimale, utile anche per la Parte X (test e qualità).
