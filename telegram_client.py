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
        self.client = None  # type: telethon.TelegramClient
        super(TelegramClient, self).__init__()

    def on_start(self):
        self.try_login()

    def on_t_update(self, update):
        self.actor_ref.tell({"command": "update", "update": update})

    def try_login(self):
        try:
            api_id = 194070
            api_hash = '37f844e27d26693944bc229d8f9dd751'
            phone = '+79992191629'
            print("t login")
            client = telethon.TelegramClient('session_name', api_id, api_hash, update_workers=4)
            self.client = client
            self.connect(client)
            if not client.is_user_authorized():
                client.send_code_request(phone)
                client.sign_in(phone=phone)
                self.me = client.sign_in(code=int(input("Enter code:")))
            client.add_update_handler(self.on_t_update)
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
        if message["command"] == "update":
            update_ = message["update"]
            # and self.get_user(update_).bot
            if isinstance(update_, UpdateShortMessage) and not update_.out:
                self.on_update(update_)
        elif message["command"] == "ask":
            self.client.send_message(message["bot"], message["text"])
            # TODO handle conversations
            self.interceptor.tell({"command": "resume"})
        elif message["command"] == 'me':
            return self.client.get_me()


    # def get_user(self, message):
    #     usr = next(filter(lambda e: isinstance(e, User), message.entities))
    #     return usr

    def on_update(self, update):
        upd = update  # type: UpdateShortMessage
        if upd.message and len(upd.message) > 0:
            tts.say(upd.message)
