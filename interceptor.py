import pykka
import subprocess
import speech_recognition as sr

class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager):
        super(InterceptorActor, self).__init__()
        self.manager = manager

    def on_keyword(self):
        print("hi there")
        args = []
        args.insert(0, 'aplay')
        args.insert(1, "../kw.waw")
        p = subprocess.Popen(args)

        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)

        p.wait()

        try:

            print("Google Speech Recognition thinks you said " + r.recognize_google(audio, key = "AIzaSyA97hSk7WuA-w4fCdHAK9h7LWEhiExb7do"))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def on_receive(self, message):
        if message["command"] == "kw":
            self.on_keyword()
