# coding=utf-8
import json
import logging
from datetime import datetime
import pykka

import plurals
import tts

from apiai.text import TextRequest


class FuncResolverActor(pykka.ThreadingActor):
    def __init__(self, interceptor, t_client):
        self.interceptor = interceptor
        self.t_client = t_client

        self.local = LocalFunctions.start(interceptor)
        super(FuncResolverActor, self).__init__()

    def on_receive(self, message):
        if not self.local.ask(message):

            request = TextRequest(
                "78d0cdf68bd8449cb6fcdde8d0b0cd02",
                'api.api.ai',
                '20150910',
                None
            )

            request.lang = 'ru'  # optional, default value equal 'en'
            request.session_id = self.t_client.ask({"command": "me"}).id
            request.query = message["text"]
            response = request.getresponse()
            if response.code // 100 == 2:
                string = response.read().decode('utf-8')
                res = json.loads(string)
                if res["result"]["action"]:
                    message.update({"command": "ask", 'bot': str.split(res["result"]["action"], ".")[0]})
                    self.t_client.tell(message)
                    return

            echo_strings = ["скажи", "tell"]

            if message and any(t in message["text"] for t in echo_strings):
                message.update({"bot": "uproarbot", "command": "ask"})
                self.t_client.tell(message)
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
