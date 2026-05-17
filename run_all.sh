#!/bin/bash

echo "====================================================="
echo "  🚀 AVVIO PIPELINE COMPLETA - PROGETTO PYTHON"
echo "====================================================="

# ======================================================
# 1) Controllo Python
# ======================================================

echo ""
echo "[INFO] Verifico presenza Python..."

if ! command -v python3 &> /dev/null
then
    echo "[WARN] Python3 non trovato."

    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "[INFO] Installo Python con Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "[ERROR] Homebrew non presente: installalo da [brew.sh](https://brew.sh/)"
            exit 1
        fi
        brew install python
    # Linux (Ubuntu/Debian)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "[INFO] Installo Python tramite APT..."
        sudo apt update
        sudo apt install -y python3 python3-venv python3-pip
    else
        echo "[ERROR] Sistema non supportato per installazione automatica Python."
        exit 1
    fi
else
    echo "[OK] Python3 trovato: $(python3 --version)"
fi

# ======================================================
# 2) Virtual Environment + requirements
# ======================================================

echo ""
echo "[INFO] Verifico ambiente virtuale..."

if [ ! -d "venv" ]; then
    echo "[INFO] Creo nuovo ambiente virtuale Python..."
    python3 -m venv venv
fi

echo "[INFO] Attivo ambiente virtuale..."
source venv/bin/activate

echo ""
echo "[INFO] Installo dipendenze da requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# ======================================================
# 3) Avvio Ollama
# ======================================================

echo ""
echo "[INFO] Verifico Ollama in esecuzione..."

if pgrep -x "ollama" > /dev/null
then
    echo "[OK] Ollama è già attivo."
else
    echo "[INFO] Avvio Ollama..."
    ollama serve &
    sleep 3
fi

# ======================================================
# 4) Verifica modelli necessari
# ======================================================

echo ""
echo "[INFO] Controllo modelli Ollama..."

MODELS=("yxchia/multilingual-e5-base" "granite3-dense" "zyw0605688/gte-large-zh" "jeffh/intfloat-multilingual-e5-large-instruct:q8_0")

for m in "${MODELS[@]}"; do
    if ollama list | grep -q "$m"; then
        echo "[OK] Modello '$m' già installato."
    else
        echo "[DOWNLOAD] Scarico modello '$m'..."
        ollama pull "$m"
    fi
done

# ======================================================
# 5) Esecuzione pipeline Python
# ======================================================

echo ""
echo "====================================================="
echo "       🚀 AVVIO PASSI DELLA PIPELINE PYTHON"
echo "====================================================="

echo ">>> STEP 1 — Generazione testi descrittivi"
python3 src/generate_texts.py || exit 1

echo ""
echo ">>> STEP 2 — Generazione embedding (Ollama)"
python3 src/generate_embeddings.py || exit 1

echo ""
echo ">>> STEP 3 — Addestramento modelli"
python3 src/train_models.py || exit 1

echo ""
echo ">>> STEP 4 — Valutazione statistica"
python3 src/evaluation.py || exit 1

echo ""
echo ">>> STEP 5 — Generazione report (Markdown + PDF)"
python3 src/generate_report.py --pdf || exit 1

# ======================================================
# 6) FINE
# ======================================================

echo ""
echo "====================================================="
echo "      🎉 PIPELINE COMPLETATA SENZA ERRORI!"
echo " Risultati disponibili nella cartella /results/"
echo " Report generato: report.md + report.pdf"
echo "====================================================="
