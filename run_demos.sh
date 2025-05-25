set -eu
./build.sh
clear
mkdir -p logs
python3 demos/keys.py
python3 demos/images.py
python3 demos/layouts.py
python3 demos/movement.py
python3 demos/game-pong.py
rm -rf logs
