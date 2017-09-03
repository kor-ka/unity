import logging

import pyaudio as pyaudio
import pykka
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from six.moves import queue
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms




class GoogleRecognizerActor(pykka.ThreadingActor):
    def __init__(self, interceptor, mic_stream):
        super(GoogleRecognizerActor, self).__init__()
        self.interceptor = interceptor
        self.mic = mic_stream
        self.client = speech.SpeechClient()

    def on_receive(self, message):
        if message["command"] == "start":
            self.start_recognize()

    def start_recognize(self):
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in MicrophoneStream(self.mic).generator())

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='ru-RU')
        streaming_config = types.StreamingRecognitionConfig(config=config)

        # streaming_recognize returns a generator.
        responses = self.client.streaming_recognize(streaming_config, requests)

        for response in responses:
            for result in response.results:
                print('Finished: {}'.format(result.is_final))
                print('Stability: {}'.format(result.stability))
                alternatives = result.alternatives
                for alternative in alternatives:
                    print('Confidence: {}'.format(alternative.confidence))
                    print('Transcript: {}'.format(alternative.transcript))

                if result.is_final:
                    print('End talk')
                    break
            else:
                continue  # executed if the loop ended normally (no break)
            break  # executed if 'continue' was skipped (break)

            # self.interceptor.tell({"command":"talk", ""})

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, mic):
        self._mic = mic

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_stream = self._mic
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        # self._audio_interface.terminate()

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
