import logging
import pykka
import subprocess

from google_recognizer import GoogleRecognizerActor


class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager, ls):
        super(InterceptorActor, self).__init__()
        self.ls = ls
        self.rec = GoogleRecognizerActor.start(self.actor_ref, self.ls.get_mic())
        self.manager = manager

    def on_start(self):
        self.ls.detect()

    def on_keyword(self):
        print("kw InterceptorActor")
        # args = []
        # args.insert(0, 'aplay')
        # args.insert(1, "../kw.waw")
        # subprocess.Popen(args)
        self.rec.tell({"command": "start"})



    def on_receive(self, message):
        if message["command"] == "resume":
            self.ls.detect()

