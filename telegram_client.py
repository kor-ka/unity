import logging
from threading import Thread
import uuid

import pykka
import telethon
import time
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage, User, Chat, InputPeerChat

import tts
import shelve


class TelegramClient(pykka.ThreadingActor):
    def __init__(self, interceptor, rec):
        db = shelve.open("chat_id")
        self.chat_id = db["chat_id"]
        db.close()
        self.interceptor = interceptor
        self.rec = rec
        self.me = None
        self.client = None  # type: telethon.TelegramClient
        self.going_to_resume = uuid.uuid4()
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
        elif message["command"] == "ask" and self.chat_id:
            self.client.send_message(InputPeerChat(self.chat_id), message["text"])
            self.delayed_resume()
        elif message["command"] == 'me':
            return self.client.get_me()
        elif message["command"] == 'resume' and self.going_to_resume == message["latest"]:
            self.interceptor.tell({"command": "resume"})

    # def get_user(self, message):
    #     usr = next(filter(lambda e: isinstance(e, User), message.entities))
    #     return usr

    def on_update(self, update):
        upd = update  # type: UpdateShortMessage
        message = upd.message

        if message == '#here':
            for e in upd.entities:
                if isinstance(e, Chat):
                    self.chat_id = e.id
                    db = shelve.open("chat_id")
                    db["chat_id"] = self.chat_id
                    db.close()

        user = self.client.get_entity(upd.user_id)  # type: User
        if message and len(message) > 0 and not upd.out and user.bot:

            if update.message.endswith('?'):
                reply = self.rec.ask({"command": "ask", "tell": message})
                if reply and len(reply) > 0:
                    self.client.send_message(InputPeerChat(self.chat_id), message["text"])
                    self.delayed_resume()
                else:
                    self.delayed_resume(delay=1)

            else:
                tts.say(message)
                self.delayed_resume(delay=1)

    def delayed_resume(self, delay=10):
        latest = uuid.uuid4()
        self.going_to_resume = latest

        def delayed():
            time.sleep(delay)
            self.actor_ref.tell({"command": "resume", "latest": latest})

        thread = Thread(target=delayed, args=(10,))
        thread.start()
