set -e  # stop when a command exits with a non-zero status...
python3 demos/keys.py
python3 demos/images.py
python3 demos/layouts.py
python3 demos/animations.py
rm *.log
