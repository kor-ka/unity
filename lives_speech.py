import os
import sys
import signal
from contextlib import contextmanager

import pyaudio, audioop
from sphinxbase import *
from pocketsphinx import *

RATE = 22000
CHUNK = 1024  # 100ms


class LiveSpeech(Pocketsphinx):
    def __init__(self, mic, **kwargs):

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 22000)
        self.buffer_size = kwargs.pop('buffer_size', 1024)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)

        self.ad = mic
        self.utterance = self.start_utterance()
        self.utterance.__enter__()
        super(LiveSpeech, self).__init__(**kwargs)

    def detect(self):
        num_chars_printed = 0
        for buf in self.ad.generator():
            volume_norm = audioop.max(buf, 2)
            count = "|" * int((int(volume_norm) / 1000))
            transcript = "sphinx working {}".format(count)
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)

            self.process_raw(buf, self.no_search, self.full_utt)
            if self.keyphrase and self.hyp():
                self.ad.pause_clear()
                return
