#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from manager import ManagerActor

if __name__ == '__main__':
    ManagerActor.start()
    while True:
        sleep(100)