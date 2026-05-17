#!/bin/bash

echo "====================================================="
echo "  🚀 STARTING FULL PIPELINE - PYTHON PROJECT"
echo "====================================================="

# ======================================================
# 1) Python check
# ======================================================

echo ""
echo "[INFO] Checking for Python..."

if ! command -v python3 &> /dev/null
then
    echo "[WARN] Python3 not found."

    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "[INFO] Installing Python with Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "[ERROR] Homebrew is not installed: install it from [brew.sh](https://brew.sh/)"
            exit 1
        fi
        brew install python
    # Linux (Ubuntu/Debian)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "[INFO] Installing Python via APT..."
        sudo apt update
        sudo apt install -y python3 python3-venv python3-pip
    else
        echo "[ERROR] Unsupported system for automatic Python installation."
        exit 1
    fi
else
    echo "[OK] Python3 found: $(python3 --version)"
fi

# ======================================================
# 2) Virtual Environment + requirements
# ======================================================

echo ""
echo "[INFO] Checking virtual environment..."

if [ ! -d "venv" ]; then
    echo "[INFO] Creating new Python virtual environment..."
    python3 -m venv venv
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[INFO] Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# ======================================================
# 3) Start Ollama
# ======================================================

echo ""
echo "[INFO] Checking Ollama status..."

if pgrep -x "ollama" > /dev/null
then
    echo "[OK] Ollama is already running."
else
    echo "[INFO] Starting Ollama..."
    ollama serve &
    sleep 3
fi

# ======================================================
# 4) Verify required models
# ======================================================

echo ""
echo "[INFO] Checking Ollama models..."

MODELS=("yxchia/multilingual-e5-base" "granite3-dense" "zyw0605688/gte-large-zh" "jeffh/intfloat-multilingual-e5-large-instruct:q8_0")

for m in "${MODELS[@]}"; do
    if ollama list | grep -q "$m"; then
        echo "[OK] Model '$m' is already installed."
    else
        echo "[DOWNLOAD] Downloading model '$m'..."
        ollama pull "$m"
    fi
 done

# ======================================================
# 5) Run Python pipeline
# ======================================================

echo ""
echo "====================================================="
echo "       🚀 STARTING PYTHON PIPELINE STEPS"
echo "====================================================="

echo ">>> START MAIN"
python3 main.py || exit 1

# ======================================================
# 6) Finish
# ======================================================

echo ""
echo "====================================================="
echo "      🎉 PIPELINE COMPLETED SUCCESSFULLY!"
echo " Results available in /results/"
echo " Report generated: report.md + report.pdf"
