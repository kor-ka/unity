#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

import signal

from lives_speech import LiveSpeech
from manager import ManagerActor




if __name__ == '__main__':

    def term(arg1, arg2):
        manager.tell({"command": "term"})


    manager = ManagerActor.start()
    signal.signal(signal.SIGINT, term)
    signal.signal(signal.SIGTERM, term)


    while True:
        pass
