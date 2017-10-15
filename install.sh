apt-get update
apt-get install -y python3 python-dev python3-pip build-essential swig git libpulse-dev portaudio19-dev libasound2-dev mpg123 locales
sh el.sh
pip3 install -U -r requirements.txt
pip3 install --upgrade pocketsphinx --no-cache-dir