import logging

import os
import pykka
import subprocess

import tts
from func_resolver import FuncResolverActor
from google_recognizer import GoogleRecognizerActor
from lives_speech import LiveSpeech


class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager):
        super(InterceptorActor, self).__init__()
        self.rec = GoogleRecognizerActor.start(self.actor_ref)
        self.kw_detector = SphinxActor.start(self.actor_ref)
        self.resolver = FuncResolverActor.start(self.actor_ref)
        self.manager = manager

    def on_start(self):
        self.kw_detector.tell({"command": "detect"})

    def on_keyword(self):
        print("kw InterceptorActor")
        # args = []
        # args.insert(0, 'aplay')
        # args.insert(1, "../kw.waw")
        # subprocess.Popen(args)
        res = self.rec.ask({"command": "start"})
        self.resolver.tell({"text": res})
        tts.say("да да?")


    def on_receive(self, message):
        if message["command"] == "resume":
            self.kw_detector.tell({"command": "detect"})
        if message["command"] == "kw":
            self.on_keyword()

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)


class SphinxActor(pykka.ThreadingActor):
    def __init__(self, interceptor):
        super(SphinxActor, self).__init__()
        model_path = "../pocketsphinx/model"
        self.ls = LiveSpeech(
            hmm=os.path.join(model_path, 'en-us/en-us'),
            lm=os.path.join(model_path, 'en-us/en-us.lm.bin'),
            dic=os.path.join(model_path, 'en-us/unity.dict'),
            keyphrase='UNITY',
            kws_threshold=1e+20)
        self.interceptor = interceptor
        print("ls created")

    def on_receive(self, message):
        if message["command"] == "detect":
            print("on detect")

            self.ls.detect()
            self.interceptor.tell({"command": "kw"})

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)
