# coding=utf-8
import json
import logging
from datetime import datetime
import pykka

import plurals
import tts


class FuncResolverActor(pykka.ThreadingActor):
    def __init__(self, interceptor, t_client):
        self.interceptor = interceptor
        self.t_client = t_client

        self.local = LocalFunctions.start(interceptor)
        super(FuncResolverActor, self).__init__()

    def on_receive(self, message):
        if not self.local.ask(message):
            message.update({"command": "ask"})
            self.t_client.tell(message)
            return

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
        if message and any(t in message["text"] for t in self.time_strings):
            self.on_time_ask()
            return True

        if message and any(t in message["text"] for t in self.exit_strings):
            quit()
            return True
        return False

    def on_time_ask(self):
        now = datetime.now()
        tts.say(u" Cейчас {} {} {} {}".format(now.hour, plurals.t('hour', count=now.hour), now.minute,
                                              plurals.t('min', count=now.minute)))
