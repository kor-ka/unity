import pykka
import os
from pykka import ActorRef
from ls import LiveSpeech


class KeywordActor(pykka.ThreadingActor):
    def __init__(self, manager, interceptor):
        super(KeywordActor, self).__init__()
        self.manager = manager  # type: ActorRef
        self.interceptor = interceptor

    def on_start(self):
        model_path = "../pocketsphinx/model"
        ls = LiveSpeech(
            hmm=os.path.join(model_path, 'en-us/en-us'),
            lm=os.path.join(model_path, 'en-us/en-us.lm.bin'),
            dic=os.path.join(model_path, 'en-us/unity.dict'),
            keyphrase='UNITY',
            kws_threshold=1e+20)
        for phrase in ls:
            self.on_keyword()

    def on_keyword(self):
        self.interceptor.tell({"command": "keyword"})
