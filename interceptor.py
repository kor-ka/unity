import logging
import pykka
import subprocess

from google_recognizer import GoogleRecognizerActor


class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager, ls):
        super(InterceptorActor, self).__init__()
        self.ls = ls
        self.rec = GoogleRecognizerActor.start(self.actor_ref, self.ls.get_mic())
        self.kw_detector = SphinxActor.start(self.actor_ref, self.ls)
        self.manager = manager

    def on_start(self):
        self.kw_detector.tell({"command": "detect"})

    def on_keyword(self):
        print("kw InterceptorActor")
        # args = []
        # args.insert(0, 'aplay')
        # args.insert(1, "../kw.waw")
        # subprocess.Popen(args)
        self.rec.tell({"command": "start"})



    def on_receive(self, message):
        if message["command"] == "resume":
            self.kw_detector.tell({"command": "detect"})
        if message["command"] == "kw":
            self.on_keyword()


class SphinxActor(pykka.ThreadingActor):
    def __init__(self, interceptor, ls):
        super(SphinxActor, self).__init__()
        self.ls = ls
        self.interceptor = interceptor

    def on_receive(self, message):
        if message["command"] == "detect":
            self.ls.detect()
            self.interceptor.tell({"command": "kw"})

