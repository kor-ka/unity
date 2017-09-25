import subprocess

import time
from gtts import gTTS


def say(text):
    tts = gTTS(text=text, lang='ru', slow=False)
    tts.save("speech.mp3")

    args = []
    args.insert(0, 'mpg123')
    args.insert(1, "speech.mp3")
    subprocess.Popen(args).wait()
    time.sleep(1)
