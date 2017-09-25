# coding=utf-8
import logging
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
            tts.say(u" не понимаю")

        self.interceptor.tell({"command": "resume"})

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)



class LocalFunctions(pykka.ThreadingActor):
    def __init__(self, interceptor):
        self.interceptor = interceptor
        self.time_strings = ["time", "врем"]

        i18n.set('fallback', 'en')

        i18n.add_translation('hour', {
            'zero': u'часов',
            'one': u'час',
            'few': u'часа',
            'many': u'часов'
        }, locale='en')

        i18n.add_translation('min', {
            'zero': u'минут',
            'one': u'минута',
            'few': u'минуты',
            'many': u'минут'
        }, locale='en')

        super(LocalFunctions, self).__init__()

    def on_receive(self, message):
        if any(t in message["text"] for t in self.time_strings):
            self.on_time_ask()
            return True
        return False

    def on_time_ask(self):
        now = datetime.now()
        tts.say(u" Cейчас {} {} {} {}".format(now.hour, i18n.t('hour', count=now.hour), now.minute, i18n.t('min', count=now.minute)))
