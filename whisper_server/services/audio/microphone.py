import numpy as np
import pyaudio
import time

from whisper.audio import SAMPLE_RATE, CHUNK_LENGTH
from whisper_server.services.utils import logger

RECORD_SECONDS = CHUNK_LENGTH  # 30
# TODO: bring FRAMES_PER_BUFFER down and see if it breaks anything or improves latency
# FRAMES_PER_BUFFER = 1024
# FRAMES_PER_BUFFER = 3000
# OpenAI Whisper complains if not 480000: assert x.shape[1:] == self.positional_embedding.shape, "incorrect audio shape"
FRAMES_PER_BUFFER = RECORD_SECONDS * SAMPLE_RATE  # 480,000 = N_SAMPLES
FRAMES_TO_PROCESS = FRAMES_PER_BUFFER >> 3
FORMAT = pyaudio.paInt16
CHANNELS = 1


class Microphone:
    def __init__(self):
        self.closed = False
        self.audio = pyaudio.PyAudio()
        self.run = False
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=SAMPLE_RATE,
                                      input=True,
                                      frames_per_buffer=FRAMES_PER_BUFFER)

    def __exit__(self, *err):
        self.close()

    def __del__(self):
        self.close()

    def listen(self):
        while self.run:
            prev = time.time()
            if self.stream.is_active():
                start = time.time()
                # print("listening...")  # {:.3f}".format(time.time() - start))
                data = self.stream.read(FRAMES_TO_PROCESS)
                # print("got audio from the mic, {:.3f}".format(time.time() - start))
                prev = time.time()
                yield np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
                # print("after yield, {:.3f}".format(time.time() - prev))
            else:
                print("break from microphone.listen()")
                break

    def start(self):
        self.run = True
        self.stream.start_stream()
        logger.debug("microphone started")

    def stop(self):
        logger.debug("microphone stopped")
        self.run = False
        self.stream.stop_stream()

    def close(self):
        if not self.closed:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.closed = True

    def is_closed(self):
        return self.closed
