# -*- coding: utf-8 -*-
import logging
from pprint import pprint

import pyaudio as pyaudio
import pykka
import sys

import re

import signal
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from six.moves import queue
RATE = 22000
CHUNK = 1024  # 100ms


class GoogleRecognizerActor(pykka.ThreadingActor):
    def __init__(self, interceptor, mic):
        super(GoogleRecognizerActor, self).__init__()
        self.interceptor = interceptor
        self.client = speech.SpeechClient()
        self.mic = mic

    def on_receive(self, message):
        try:
            if message["command"] == "start":
                return self.start_recognize()

        except Exception as ex:
            logging.exception(ex)
            return ""

    def on_failure(self, exception_type, exception_value, traceback):
        logging.exception(exception_value)


    def start_recognize(self):
        print("kw GoogleRecognizerActor")

        language_code = 'en-US'  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        print (self.mic._buff.size)
        audio_generator = self.mic.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        print(self.mic.qsize())
        res = self.listen_print_loop(responses)
        self.mic.pause_clear()
        return res

    def listen_print_loop(self, responses):
        """Iterates through server responses and prints them.
        The responses passed is a generator that will block until a response
        is provided by the server.
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        print('G rec enabled, speak..')

        num_chars_printed = 0
        for response in responses:
            pprint(response)

            if not response.results:
                continue

            # There could be multiple results in each response.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript.encode('utf-8').strip()

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                # if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                return transcript
