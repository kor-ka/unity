import os
import sys
import signal
from contextlib import contextmanager

import pyaudio
from sphinxbase import *
from pocketsphinx import *


class LiveSpeech(Pocketsphinx):
    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 16000)
        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)
        self.ad = PyAd(self.sampling_rate, buffer_size=self.buffer_size)

        super(LiveSpeech, self).__init__(**kwargs)

    def detect(self):
        with self.ad:
            with self.start_utterance():
                print("sphinx working...")
                while self.ad.readinto(self.buf) >= 0:
                    print(".")
                    self.process_raw(self.buf, self.no_search, self.full_utt)
                    if self.keyphrase and self.hyp():
                        with self.end_utterance():
                            self.ad.stop()
                            return

    def stop(self, *args, **kwargs):
        self.ad.stop()
        raise StopIteration

    def get_mic(self):
        return self.ad.stream


class PyAd(Ad):
    def __init__(self, sampling_rate, buffer_size):
        self.sampling_rate = sampling_rate
        self.buffer_size = buffer_size

        self.stream.start_stream()
        # super(PyAd, self).__init__()

    def __enter__(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16, channels=1, rate=sampling_rate, input=True,
                             frames_per_buffer=buffer_size)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stream.stop_stream()
        self.stream.close()

    def readinto(self, DATA):
        buf = self.stream.read(self.buffer_size, exception_on_overflow=False)
        DATA[:] = buf
        return buf


