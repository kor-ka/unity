apt-get update
apt-get install -y python python-dev python-pip build-essential swig git libpulse-dev portaudio19-dev libasound2-dev mpg123
# locales should be installed and dpkg-reconfigured before it
sh el.sh
pip install -U -r requirements.txt
pip install --upgrade pocketsphinx --no-cache-dir