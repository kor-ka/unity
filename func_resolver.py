# coding=utf-8
from datetime import datetime
import pykka

import i18n

import tts
from google_recognizer import GoogleRecognizerActor


class FuncResolverActor(pykka.ThreadingActor):
    def __init__(self, interceptor):
        self.interceptor = interceptor
        self.local = LocalFunctions.start(interceptor)
        super(FuncResolverActor, self).__init__()

    def on_receive(self, message):
        if not self.local.ask(message):
            # TODO resolve bot, start T session
            tts.say(u"не понимаю")

            self.interceptor.tell({"command": "resume"})


i18n.add_translation('hour', {
    'zero': u'часов',
    'one': u'час',
    'few': u'часа',
    'many': u'часов'
})

i18n.add_translation('min', {
    'zero': u'минут',
    'one': u'минута',
    'few': u'минуты',
    'many': u'минут'
})


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
        now = datetime.now()

        tts.say(u"Cейчас {} {} {} {}".format(now.hour, i18n.t("hour", count= now.hour), now.minute, i18n.t("min", count= now.minute)))
        self.end_session()

    def end_session(self):
        self.interceptor.tell({"command": "resume"})
