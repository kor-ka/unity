import pyaudio
from six.moves import queue

RATE = 22000
CHUNK = 1024  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self):
        self._rate = RATE
        self._chunk = CHUNK

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()

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

        self.paused = False

    def stop(self):
        self.paused = True
        self._audio_stream.stop_stream()
        self._audio_stream.close()

        self._buff.put(None)
        self._audio_interface.terminate()

        self.pause_clear()

    def pause_clear(self):
        self.paused = True
        with self._buff.mutex:
            self._buff.queue.clear_pause()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        if not self.paused:
            self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        self.paused = False
        return self._generator()

    def _generator(self):
        while not self.paused:
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
