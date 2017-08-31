#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

from ls import LiveSpeech
from manager import ManagerActor

if __name__ == '__main__':
    manager = ManagerActor.start()

    model_path = "../pocketsphinx/model"
    ls = LiveSpeech(
        hmm=os.path.join(model_path, 'en-us/en-us'),
        lm=os.path.join(model_path, 'en-us/en-us.lm.bin'),
        dic=os.path.join(model_path, 'en-us/unity.dict'),
        keyphrase='UNITY',
        kws_threshold=1e+20)
    print("kws inited")
    for phrase in ls:
        manager.tell({"command":"kw"})