import os
import sys
import signal
from contextlib import contextmanager

import pyaudio, audioop
from sphinxbase import *
from pocketsphinx import *
from six.moves import queue

RATE = 16000
CHUNK = 1024  # 100ms

class LiveSpeech(Pocketsphinx):
    def __init__(self, **kwargs):

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 16000)
        self.buffer_size = kwargs.pop('buffer_size', 1024)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)

        super(LiveSpeech, self).__init__(**kwargs)

    def detect(self):
        with MicrophoneStream(RATE, CHUNK) as ad:
            with self.start_utterance():
                progress = 0
                num_chars_printed = 0
                for buf in ad.generator():
                    volume_norm = audioop.max(buf, 2)
                    count = "|" * (int(volume_norm) / 1000)
                    transcript = "sphinx working {}".format(count)
                    overwrite_chars = ' ' * (num_chars_printed - len(transcript))

                    sys.stdout.write(transcript + overwrite_chars + '\r')
                    sys.stdout.flush()
                    num_chars_printed = len(transcript)

                    self.process_raw(buf, self.no_search, self.full_utt)
                    if self.keyphrase and self.hyp():
                        with self.end_utterance():
                            return



class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

        signal.signal(signal.SIGTERM, self.stop)

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]


