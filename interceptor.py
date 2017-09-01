import logging
import pykka
import subprocess

from google_recognizer import GoogleRecognizerActor


class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager, mic):
        super(InterceptorActor, self).__init__()
        self.mic = mic
        self.rec = GoogleRecognizerActor.start(self.actor_ref, self.mic)
        self.manager = manager

    def on_keyword(self):
        print("hi there")
        args = []
        args.insert(0, 'aplay')
        args.insert(1, "../kw.waw")
        p = subprocess.Popen(args)
        self.rec.tell({"command":"start"})
        p.wait()



    def on_receive(self, message):
        if message["command"] == "kw":
            self.on_keyword()

