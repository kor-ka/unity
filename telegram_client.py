import logging
import shelve
import time
import uuid
from threading import Thread

import pykka
import telethon
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage, User, InputPeerChat, UpdateShortChatMessage, UpdateNewChannelMessage, \
    UpdateNewMessage, Message, InputPeerChannel, Channel
from telethon.utils import get_peer_id

import tts


class TelegramClient(pykka.ThreadingActor):
    def __init__(self, interceptor, rec):
        db = shelve.open("chat_id")
        self.chat_peer = None if "chat_id" not in db else db["chat_id"]
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
        try:
            if message["command"] == "update":
                update_ = message["update"]
                # and self.get_user(update_).bot
                if isinstance(update_, (
                UpdateShortMessage, UpdateShortChatMessage, UpdateNewChannelMessage, UpdateNewMessage), ):
                    self.on_update(update_)
            elif message["command"] == "ask":
                if self.chat_peer:
                    self.delayed_resume()
                    self.client.send_message(self.chat_peer.build(), message["text"])
                else:
                    self.interceptor.tell({"command": "resume"})

            elif message["command"] == 'me':
                return self.client.get_me()
            elif message["command"] == 'resume':
                print("on resume" + str(self.going_to_resume) + " vs " + str(message["latest"]))
                if self.going_to_resume == message["latest"]:
                    self.interceptor.tell({"command": "resume"})
        except Exception as ex:
            logging.exception(ex)

    # def get_user(self, message):
    #     usr = next(filter(lambda e: isinstance(e, User), message.entities))
    #     return usr

    def on_update(self, update):

        peer_type = PeerType.COMMON
        access_hash = None

        if isinstance(update, UpdateShortChatMessage):
            upd = update  # type: UpdateShortChatMessage
            chat_peer = InputPeerChat(upd.chat_id)
            user_id = upd.from_id
        elif isinstance(update, UpdateShortMessage):
            upd = update  # type: UpdateShortMessage
            chat_peer = InputPeerChat(upd.user_id)
            user_id = upd.user_id
        else:
            upd = update.message  # type: Message
            chat_peer = get_peer_id(upd.to_id)
            user_id = upd.from_id
            peer_type = PeerType.CHANNEL



        message = upd.message

        print(message)

        if message.startswith('#here'):
            if peer_type == PeerType.CHANNEL:
                dialogs = self.client.get_dialogs(limit=None)
                access_hash = dialogs[1][chat_peer].access_hash
                print (access_hash)

            self.chat_peer = Peer(chat_peer, access_hash)
            db = shelve.open("chat_id")
            db["chat_id"] = self.chat_peer
            db.close()

        user = self.client.get_entity(user_id)  # type: User
        if message and len(message) > 0 and not upd.out and user.bot:
            if message.endswith('?'):
                reply = self.rec.ask({"command": "start", "tell": message})
                if reply and len(reply) > 0:
                    self.client.send_message(self.chat_peer.build(), reply)
                    self.delayed_resume()
                else:
                    self.delayed_resume(delay=1)

            else:
                tts.say(message)
                self.delayed_resume(delay=1)

    def delayed_resume(self, delay=10):
        latest = uuid.uuid1()
        print("delayed_resume " + str(latest))
        self.going_to_resume = latest

        def delayed():
            print("delayed_resume threaded " + str(latest))
            time.sleep(delay)
            self.actor_ref.tell({"command": "resume", "latest": latest})

        thread = Thread(target=delayed)
        thread.start()


class Peer(object):
    def __init__(self, type, id, asses_hash = None):
        self.id = id
        self.type = type
        self.access_hash = asses_hash

    def build(self):
        if type == PeerType.COMMON:
            return InputPeerChat(self.id)
        else:
            return InputPeerChannel(self.id, self.access_hash)


class PeerType:
    COMMON = 1
    CHANNEL = 2
