#!/usr/bin/env bash
# One-time setup for stt-tts-button.py on a Raspberry Pi.
# Run from the project folder:  bash setup.sh
set -e

cd "$(dirname "$0")"

echo "== Installing system packages (needs your password) =="
sudo apt update
sudo apt install -y python3-venv swig liblgpio-dev alsa-utils

echo "== Creating the Python venv =="
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env -- open it and paste in your API keys"
fi

echo "== Checking =="
python -c "import RPi.GPIO, requests, dotenv; print('Python packages OK')"
echo
echo "Microphones:"
arecord -l
echo
echo "Speakers:"
aplay -l || true

echo
echo "Done! To run:"
echo "  source .venv/bin/activate"
echo "  python stt-tts-button.py"