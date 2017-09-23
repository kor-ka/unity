import subprocess
from gtts import gTTS


def say(text):
    tts = gTTS(text=text, lang='ru', slow=False)
    tts.save("speech.mp3")

    args = []
    args.insert(0, 'mplayer')
    args.insert(1, "speech.mp3")
    subprocess.Popen(args).wait()
