# coding=utf-8
import logging
from datetime import datetime
import pykka

import plurals
import tts
import re
from google_recognizer import GoogleRecognizerActor


class FuncResolverActor(pykka.ThreadingActor):
    def __init__(self, interceptor):
        self.interceptor = interceptor
        self.local = LocalFunctions.start(interceptor)
        super(FuncResolverActor, self).__init__()

    def on_receive(self, message):
        if not self.local.ask(message):
            # TODO resolve bot remotely
            if re.match("^скажи|^tell", message["text"]):
                message.add("bot", "uproar")
                message.add("command", "ask")
                return
            tts.say(u" не понимаю")

        self.interceptor.tell({"command": "resume"})

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)


class LocalFunctions(pykka.ThreadingActor):
    def __init__(self, interceptor):
        self.interceptor = interceptor
        self.time_strings = ["time", "врем"]
        self.exit_strings = ["exit", "quit", "terminate", "выход", "пока"]

        plurals.add('hour', {
            'zero': u'часов',
            'one': u'час',
            'few': u'часа',
            'many': u'часов'
        })

        plurals.add('min', {
            'zero': u'минут',
            'one': u'минута',
            'few': u'минуты',
            'many': u'минут'
        })

        super(LocalFunctions, self).__init__()

    def on_receive(self, message):
        if any(t in message["text"] for t in self.time_strings):
            self.on_time_ask()
            return True

        if any(t in message["text"] for t in self.exit_strings):
            quit()
            return True
        return False

    def on_time_ask(self):
        now = datetime.now()
        tts.say(u" Cейчас {} {} {} {}".format(now.hour, plurals.t('hour', count=now.hour), now.minute,
                                              plurals.t('min', count=now.minute)))
