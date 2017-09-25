#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

import signal

from lives_speech import LiveSpeech
from manager import ManagerActor

if __name__ == '__main__':


    manager = ManagerActor.start()
    # signal.signal(signal.SIGINT, manager.tell({"command":"term"}))
    # signal.signal(signal.SIGTERM, manager.tell({"command":"term"}))


    while True:
        pass
