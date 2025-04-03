set -e
rm -rf build prisma_tui.egg-info
python3 demos/keys.py
python3 demos/images.py
python3 demos/layouts.py
python3 demos/animations.py
rm -f logs/*.log
