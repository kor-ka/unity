import subprocess
from gtts import gTTS


def say(text):
    if isinstance(text, unicode):
        text = text.encode("utf8")
    tts = gTTS(text=text, lang='ru', slow=True)
    tts.save("speech.mp3")

    args = []
    args.insert(0, 'aplay')
    args.insert(1, "../speech.mp3")
    subprocess.Popen(args).wait()
