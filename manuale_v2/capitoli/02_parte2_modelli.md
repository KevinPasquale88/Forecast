# Parte II — Modelli di linguaggio ed embedding

## Capitolo 5 — Dal testo ai vettori: transformer e BERT

Un embedding di frase è un vettore di numeri reali (768 o 1024 nel progetto) che rappresenta il significato di una frase: frasi simili producono vettori vicini. Per capire da dove viene servono quattro passaggi: tokenizzazione, embedding dei token, encoder transformer, pooling.

### 5.1 Tokenizzazione

Il modello non legge caratteri né parole intere, ma **token**: pezzi di parola presi da un vocabolario fisso di circa 30.000 voci. BERT e i modelli derivati usano WordPiece: le parole frequenti sono un token, quelle rare vengono spezzate in sotto-parole marcate con `##`.

Esempio (tokenizer di BioBERT, cased): "ST depression induced by exercise: 2.3" diventa all'incirca `ST`, `depression`, `induced`, `by`, `exercise`, `:`, `2`, `.`, `3`. I numeri vengono spezzati cifra per cifra o in piccoli gruppi. Ne derivano due conseguenze per il progetto:

- le frasi sono più lunghe in token che in parole (116–137 token per frasi di 60–80 parole, capitolo 15);
- il modello non vede "233" come quantità ma come sequenza di simboli; la relazione "233 è più di 200" va appresa dai dati di pre-addestramento, e i modelli la conoscono solo in modo approssimativo.

Il vocabolario dipende dal modello. BioBERT e Bio_ClinicalBERT riusano il vocabolario cased di BERT (per questo producono lo stesso numero di token sulle frasi del progetto); PubMedBERT ha un vocabolario costruito sul testo biomedico, uncased, che spezza meno i termini medici (97–126 token sulle stesse frasi).

### 5.2 Embedding dei token e posizione

Ogni token viene sostituito da un vettore appreso (embedding del token) a cui si somma un vettore che codifica la posizione nella frase. BERT usa posizioni apprese fino a 512: è il limite massimo di lunghezza, e il motivo per cui `max_seq_length` non può superare 512.

### 5.3 L'encoder transformer

Il transformer (Vaswani et al., 2017) elabora tutti i token in parallelo con strati di **self-attention**. In ogni strato ogni token costruisce la propria nuova rappresentazione come media pesata delle rappresentazioni di tutti gli altri token, con pesi che dipendono da quanto sono rilevanti per lui.

```latex
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{Q K^{\top}}{\sqrt{d_k}}\right) V
```

Q, K e V (query, key, value) sono proiezioni lineari delle rappresentazioni dei token; d_k è la loro dimensione. Il prodotto QKᵀ misura la compatibilità tra ogni coppia di token; la softmax la trasforma in pesi che sommano a 1; la moltiplicazione per V produce la media pesata. Più "teste" di attenzione in parallelo catturano relazioni diverse. Ogni strato aggiunge poi una piccola rete feed-forward, connessioni residue e normalizzazione.

I modelli base hanno 12 strati e rappresentazioni da 768; i modelli large 24 strati e 1024. Dopo l'ultimo strato ogni token ha un vettore contestuale: lo stesso token "pain" ha rappresentazioni diverse in "chest pain type: typical angina" e in "no pain".

### 5.4 Pre-addestramento di BERT

BERT (Devlin et al., 2019) è un encoder transformer pre-addestrato su grandi corpora con due obiettivi:

- **Masked Language Modeling**: il 15% dei token viene mascherato e il modello deve indovinarlo dal contesto;
- **Next Sentence Prediction**: dato un paio di frasi, dire se la seconda segue la prima.

Il risultato è un modello che conosce la lingua ma non è addestrato a produrre un vettore di frase: per quello serve il pooling e, idealmente, un addestramento dedicato (capitolo 6).

### 5.5 Pooling: da molti vettori di token a un vettore di frase

L'encoder restituisce un vettore per token. Per avere un vettore per frase si usa:

- **CLS pooling**: il vettore del token speciale `[CLS]` all'inizio della frase;
- **mean pooling**: la media dei vettori di tutti i token (escludendo il padding);
- **max pooling**: il massimo per dimensione.

I modelli sentence-transformers del progetto usano mean pooling. Per Bio_ClinicalBERT, che non ha una configurazione sentence-transformers, la libreria crea automaticamente un mean pooling sopra il BERT pre-addestrato.

### 5.6 Lunghezza massima e troncamento

Ogni modello ha una lunghezza massima di sequenza; il testo oltre il limite viene **troncato senza avviso**. `sentence-biobert` dichiara 100 token nel suo `sentence_bert_config.json`, pensato per frasi brevi di NLI e STS. Le frasi del progetto sono lunghe 116–137 token: fino alla correzione del 14/11/2026 gli ultimi campi (`slope`, `ca`, `thal` su Heart Disease, i campi di terapia su Diabetes130) non arrivavano mai al modello. Il capitolo 15 mostra il punto esatto in cui la frase veniva tagliata.

> *Attenzione.* Il troncamento è silenzioso: nessun errore, nessun avviso. È un esempio di bug che si trova solo misurando (qui, contando i token delle frasi reali).

## Capitolo 6 — Embedding di frase e apprendimento contrastivo

### 6.1 Perché BERT "nudo" non basta

La media dei vettori di token di un BERT pre-addestrato solo con MLM produce vettori di frase poco discriminanti: tendono a occupare un cono stretto dello spazio (**anisotropia**), così tutte le frasi risultano molto simili tra loro. Nel progetto lo si vede in Bio_ClinicalBERT: il coseno medio tra due record qualsiasi è 0,995, contro 0,889 di sentence-biobert, che è stato addestrato per produrre vettori di frase.

### 6.2 Sentence-BERT

Sentence-BERT (Reimers e Gurevych, 2019) addestra BERT in configurazione siamese: due frasi passano nello stesso encoder, i vettori ottenuti vengono confrontati, e la perdita spinge frasi semanticamente equivalenti (coppie da dataset di NLI e STS) ad avere vettori vicini. Dopo questo addestramento il coseno tra vettori misura la similarità semantica.

### 6.3 Apprendimento contrastivo

I moderni encoder generalisti (E5, GTE, M3E) sono addestrati con una perdita contrastiva su milioni di coppie di testi correlati (domanda e risposta, titolo e paragrafo, post e commento). Per ogni coppia (q, p⁺) la perdita InfoNCE (van den Oord et al., 2018) chiede che q sia più simile al proprio positivo che a tutti gli altri esempi del batch, usati come negativi:

```latex
\mathcal{L} = -\log \frac{\exp(\mathrm{sim}(q, p^{+}) / t)}{\sum_{j} \exp(\mathrm{sim}(q, p_{j}) / t)}
```

dove sim è il coseno e t una temperatura. Di solito l'addestramento ha due fasi: un pre-addestramento contrastivo su coppie raccolte dal web con supervisione debole, poi un fine-tuning su dataset etichettati (ricerca di passaggi, NLI).

### 6.4 Prefissi e istruzioni

Alcuni encoder sono addestrati con un prefisso che indica il ruolo del testo:

- la famiglia **E5** usa `query: ` e `passage: ` davanti al testo;
- **multilingual-e5-large-instruct** si aspetta, per le query, un'istruzione del tipo `Instruct: <descrizione del compito>\nQuery: <testo>`.

Il progetto passa le frasi senza prefisso a tutti i modelli. È una scelta uniforme e semplice, ma può penalizzare E5: i suoi autori raccomandano il prefisso anche per usi diversi dalla ricerca (con `query: ` per classificazione e clustering). È un punto da dichiarare tra i limiti e un esperimento facile da aggiungere.

> *Da verificare.* La raccomandazione esatta sui prefissi si trova nelle model card ufficiali di `intfloat/e5-base-v2` e `intfloat/multilingual-e5-large-instruct` su Hugging Face; citarla da lì.

## Capitolo 7 — Encoder biomedici

### 7.1 Adattamento al dominio

Il testo biomedico ha un lessico e uno stile diversi dal testo generico. Due strategie per adattare un modello:

1. **Pre-addestramento continuato**: si parte da BERT e si prosegue il pre-addestramento su testo del dominio. Il vocabolario resta quello generale.
2. **Pre-addestramento da zero**: si addestra un nuovo modello solo su testo del dominio, con un vocabolario costruito su quel testo.

### 7.2 BioBERT, PubMedBERT, Clinical BERT

- **BioBERT** (Lee et al., 2020): BERT-base con pre-addestramento continuato su abstract di PubMed e articoli completi di PubMed Central. Vocabolario di BERT (cased).
- **PubMedBERT** (Gu et al., 2021): pre-addestrato da zero su PubMed, con vocabolario proprio. Gli autori mostrano che per il dominio biomedico il pre-addestramento da zero rende meglio di quello continuato.
- **Bio_ClinicalBERT** (Alsentzer et al., 2019): parte da BioBERT e prosegue sulle note cliniche del database MIMIC-III (Johnson et al., 2016), cioè su testo scritto da medici e infermieri in terapia intensiva.

### 7.3 Dalle rappresentazioni di token ai vettori di frase

I tre modelli di base sono encoder di token. Nel progetto:

- `bioclinicalbert` è Bio_ClinicalBERT con mean pooling aggiunto automaticamente, senza addestramento per i vettori di frase;
- `pubmedbert` (`NeuML/pubmedbert-base-embeddings`) è PubMedBERT messo a punto con sentence-transformers per produrre vettori di frase;
- `sentence-biobert` (`pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb`) è BioBERT messo a punto su sei dataset di inferenza e similarità, tra cui MedNLI (Romanov e Shivade, 2018), un dataset di inferenza costruito su note cliniche.

> *Da verificare.* Le procedure di fine-tuning di `NeuML/pubmedbert-base-embeddings` e di `pritamdeka/BioBERT-...` sono descritte nelle model card dei rispettivi autori, non in articoli peer-reviewed. Citarle come "model card, Hugging Face, consultata il …".

## Capitolo 8 — I sette encoder del progetto

### 8.1 Tabella riassuntiva

| Nome nella pipeline | Modello effettivo | Base | Strati / dim. | Lingue | Vettore di frase | Backend |
| --- | --- | --- | --- | --- | --- | --- |
| `e5-base` | `intfloat/e5-base-v2` (GGUF `q8_0`) | BERT-base | 12 / 768 | inglese | contrastivo | Ollama |
| `gte-base` | `twwch/m3e-base` (M3E-base) | RoBERTa cinese | 12 / 768 | cinese, inglese | contrastivo | Ollama |
| `gte-large` | `zyw0605688/gte-large-zh` (GTE-large cinese) | BERT-large cinese | 24 / 1024 | cinese | contrastivo | Ollama |
| `e5-large` | `intfloat/multilingual-e5-large-instruct` (`q8_0`) | XLM-RoBERTa-large | 24 / 1024 | multilingue | contrastivo con istruzioni | Ollama |
| `bioclinicalbert` | `emilyalsentzer/Bio_ClinicalBERT` | BioBERT | 12 / 768 | inglese | nessuno (mean pooling) | Hugging Face |
| `pubmedbert` | `NeuML/pubmedbert-base-embeddings` | PubMedBERT | 12 / 768 | inglese | sentence-transformers | Hugging Face |
| `sentence-biobert` | `pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb` | BioBERT | 12 / 768 | inglese | NLI + STS | Hugging Face |

> *Attenzione.* Tre nomi della pipeline non corrispondono al modello: `gte-base` è M3E-base, `gte-large` è la versione cinese di GTE-large, `e5-large` è la versione multilingue instruct. Due dei quattro generalisti sono addestrati principalmente su testo cinese. In tesi vanno indicati con il nome reale.

> *Da verificare.* Base, numero di strati e lingue di M3E-base e gte-large-zh sono riportati dalle rispettive model card (Moka AI per M3E, Alibaba per GTE); controllarle prima di citarle.

### 8.2 Quantizzazione

`q8_0` indica che i pesi sono memorizzati a 8 bit nel formato GGUF usato da Ollama (derivato da llama.cpp). La quantizzazione a 8 bit riduce memoria e tempo con una perdita di qualità di solito trascurabile, ma non nulla. Secondo `ollama show`, i due modelli E5 sono quantizzati `Q8_0` (108,9 e 558,8 milioni di parametri), mentre M3E-base (101,7 milioni) e gte-large-zh (324,5 milioni) sono in mezza precisione `F16`. Tutti e quattro dichiarano un contesto di 512 token, quindi le frasi del progetto non vengono troncate.

### 8.3 La scala dei vettori: un fattore che conta

Ollama restituisce vettori normalizzati a norma 1; sentence-transformers, per i tre modelli Hugging Face del progetto, no. Misurati sugli embedding di training di Heart Disease:

| Modello | Norma media | Deviazione standard media per dimensione | Coseno medio tra due record |
| --- | --- | --- | --- |
| e5-base | 1,000 | 0,005 | 0,978 |
| gte-base | 1,000 | 0,006 | 0,975 |
| gte-large | 1,000 | 0,009 | 0,912 |
| e5-large | 1,000 | 0,006 | 0,968 |
| bioclinicalbert | 10,78 | 0,027 | 0,995 |
| pubmedbert | 12,86 | 0,066 | 0,977 |
| sentence-biobert | 11,38 | 0,132 | 0,889 |

Le variazioni dei vettori biomedici sono da 5 a 25 volte più ampie. La prima versione della pipeline non standardizzava gli ingressi e usava la stessa regolarizzazione (C = 1) per tutti: su vettori piccoli la penalità L2 pesa molto di più, e il classificatore resta più vicino alla costante. **Il confronto tra famiglie non era quindi alla pari.** Per questo la pipeline ora standardizza ogni encoder e sceglie C per ciascuno con una CV interna; il capitolo 32.4 confronta i due protocolli.

> *Per la tesi.* È un punto che una commissione attenta può sollevare ("avete standardizzato gli embedding?"). Meglio sollevarlo per primi: il problema è stato trovato misurando le scale, corretto, e i due protocolli sono confrontati nel capitolo 32.4.

### 8.4 Come vengono generati

- **Ollama** (`generate_embeddings_batch()` in `embedding.py`): il client Python invia lotti di 16 frasi al server locale (`client.embed`), un lotto alla volta grazie a un semaforo; in caso di errore riprova fino a 5 volte con attesa crescente (2, 4, 6, 8 secondi).
- **Hugging Face** (`generate_embeddings_hf()`): carica il modello con `SentenceTransformer`, imposta `max_seq_length = 512`, autentica con il token di `.env` se presente, può lavorare offline, e chiama `model.encode()` su tutte le frasi.
- **Parallelismo**: `generate_all_embeddings()` elabora i sette modelli con un pool di tre thread; per ogni modello salva vettori (`float32`) ed etichette (`int32`) in file `.npy`.
