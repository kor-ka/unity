import logging
import pykka
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


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
                    for chunk in StreamIterator(self.mic))

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

class StreamIterator:
    def __init__(self, mic, **kwargs):
        self.mic_stream = mic

    def __iter__(self):
        yield self.mic_stream.read(2048, exception_on_overflow=False)
