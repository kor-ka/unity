# coding=utf-8
import pykka

from google_recognizer import GoogleRecognizerActor


class FuncResolverActor(pykka.ThreadingActor):
    def __init__(self,interceptor):
        self.interceptor = interceptor
        self.local = LocalFunctions.start(interceptor)
        super(FuncResolverActor, self).__init__()

    def on_receive(self, message):
        if not self.local.ask(message):
            # TODO resolve bot, start T session
            self.interceptor.tell({"command": "resume"})


class LocalFunctions(pykka.ThreadingActor):
    def __init__(self, interceptor):
        self.interceptor = interceptor
        self.rec = GoogleRecognizerActor.start(self.actor_ref)
        self.time_strings = ["time", "врем"]
        super(LocalFunctions, self).__init__()

    def on_receive(self, message):
        if any(t in message["text"] for t in self.time_strings):
            self.on_time_ask()

    def on_time_ask(self):
        pass

    def end_session(self):
        self.interceptor.tell({"command": "resume"})

