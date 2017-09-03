#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

from lives_speech import LiveSpeech
from manager import ManagerActor

if __name__ == '__main__':

    model_path = "../pocketsphinx/model"
    ls = LiveSpeech(
        hmm=os.path.join(model_path, 'en-us/en-us'),
        lm=os.path.join(model_path, 'en-us/en-us.lm.bin'),
        dic=os.path.join(model_path, 'en-us/unity.dict'),
        keyphrase='UNITY',
        kws_threshold=1e+20)
    manager = ManagerActor.start(ls)


    while True:
        pass
