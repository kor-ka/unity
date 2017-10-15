import logging

import pykka
import telethon
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage, User

import tts


class TelegramClient(pykka.ThreadingActor):
    def __init__(self, interceptor, rec):
        self.interceptor = interceptor
        self.rec = rec
        self.me = None
        self.client = None # type: telethon.TelegramClient
        super(TelegramClient, self).__init__()

    def on_start(self):
        self.try_login()

    def try_login(self):
        try:
            api_id = 194070
            api_hash = '37f844e27d26693944bc229d8f9dd751'
            phone = '+79992191629'
            print("t login")
            client = telethon.TelegramClient('session_name', api_id, api_hash)
            self.client = client
            self.connect(client)
            if not client.is_user_authorized():
                res = input("sms code:")
                client.sign_in(phone=phone)
                self.me = client.sign_in(code=int(res.replace(" ", "")))
            client.add_update_handler(lambda update: self.actor_ref.tell(update))
            self.interceptor.tell({"command": "detect"})
        except Exception as e:
            logging.exception(e)
            self.try_login()

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)

    def connect(self, client):
        try:
            client.connect()
        except:
            self.connect(client)

    def on_receive(self, message):
        usr = self.get_user(message)
        if isinstance(message, UpdateShortMessage) and not message.out and usr.bot:
            self.on_update(message)
        elif message["command"] == "ask":
            self.client.send_message(self.get_user(message["bot"]), message["text"])
            #TODO handle conversations
            self.interceptor.tell({"command": "resume"})

    def get_user(self, message):
        usr = next(filter(lambda e: isinstance(e, User), message.entities))
        return usr

    def on_update(self, update):
        upd = update  # type: UpdateShortMessage
        if upd.message and len(upd.message) > 0:
            tts.say(upd.message)
