# coding=utf-8
import subprocess

import time

import pyaudio
from gtts import gTTS

import flags


def say(text):
    if not flags.debug:

        PyAudio = pyaudio.PyAudio
        RATE = 16000
        data = ''
        p = PyAudio()

        stream = p.open(format=
                        p.get_format_from_width(1),
                        channels=1,
                        rate=RATE,
                        output=True)

        stream.write(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

        tts = gTTS(text=text, lang='ru', slow=False)
        tts.save("speech.mp3")

        args = []
        args.insert(0, 'mpg123')
        args.insert(1, "speech.mp3")
        subprocess.Popen(args).wait()
        time.sleep(1)
    else:
        print(text)
        time.sleep(3)
        pass
