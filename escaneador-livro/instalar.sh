#!/usr/bin/env bash
# Instala o que o escaneador precisa (Linux/macOS). No Windows, veja o README.
set -euo pipefail
cd "$(dirname "$0")"

SUDO=""
[ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null && SUDO="sudo"

if ! command -v tesseract >/dev/null; then
  echo "▶ Instalando o Tesseract (OCR) com português…"
  if command -v apt-get >/dev/null; then
    $SUDO apt-get update && $SUDO apt-get install -y tesseract-ocr tesseract-ocr-por
  elif command -v brew >/dev/null; then
    brew install tesseract tesseract-lang
  elif command -v dnf >/dev/null; then
    $SUDO dnf install -y tesseract tesseract-langpack-por
  else
    echo "Instale o Tesseract manualmente: https://tesseract-ocr.github.io/tessdoc/Installation.html"
  fi
fi

echo "▶ Instalando bibliotecas Python…"
python3 -m pip install -r requirements.txt

echo "▶ Baixando o modelo de OCR em português mais preciso (tessdata_best, 8 MB)…"
mkdir -p modelos
curl -fL -o modelos/por.traineddata \
  https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/por.traineddata

echo "✔ Pronto. Teste com:  python3 escanear.py caminho/do/video.mp4"
