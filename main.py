#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

import signal

from manager import ManagerActor
from mic_stream import MicrophoneStream

if __name__ == '__main__':

    mic = MicrophoneStream()

    def term(arg1, arg2):
        mic.stop()

    manager = ManagerActor.start(mic)
    signal.signal(signal.SIGINT, term)
    signal.signal(signal.SIGTERM, term)


    while True:
        pass
