# Forecast — Manuale Completo

**Una pipeline locale di embedding testuale clinico per la classificazione di malattie**

*Guida completa al progetto per chi programma in Java*

Versione 1.1 — 10 settembre 2026

*Materiale tecnico verificato per lo studio del progetto e come base per una tesi triennale in Informatica*

---

**Forecast — Manuale Completo**

Versione 1.1, 10 settembre 2026 — aggiornata alla pipeline corretta dai fix di qualità (`docs/CHANGES.md`): test set trattenuto ora valutato (fase holdout), soglia calibrata su una fetta separata, indicatori di valore imputato nel testo generato, report calcolato dai dati, correzione di Benjamini-Hochberg, suite pytest. Tabelle e riferimenti `file:riga` riflettono le esecuzioni del 6 settembre 2026.

Questo manuale documenta un progetto software reale (nome storico della cartella: `Forecast`), una pipeline locale che confronta modelli di embedding testuale generalisti e biomedici per la classificazione clinica binaria a partire da due dataset pubblici UCI (Heart Disease, Diabetes 130-US Hospitals), convertiti da tabella a testo prima dell'embedding.

Ogni affermazione tecnica è marcata **Fatto** (verificata leggendo il codice sorgente o eseguendo un comando reale, con riferimento `file:riga` o comando), **Inferenza** (deduzione motivata) o **Da verificare** (ipotesi aperta, elencata per intero in Appendice E).

Scritto per uno sviluppatore software professionista con esperienza in Java, senza conoscenza pregressa di Python, dell'ecosistema di data science, o del dominio applicativo.

*Bibliografia esportata separatamente in `bibliografia.bib` (12 riferimenti, ciascuno verificato con identificativo concreto — DOI, arXiv ID o ISBN).*

**Colophon.** Scritto in Markdown, capitolo per capitolo, con formule in LaTeX e diagrammi in Mermaid. Questa edizione EPUB è composta direttamente con Pandoc (formule renderizzate come MathML, diagrammi come immagini raster) per una lettura comoda su schermi e-ink e tablet, in alternativa all'edizione PDF a impaginazione fissa (`Forecast_Manuale_Completo_v1.pdf`).
