import numpy as np
import pyaudio
import time

from whisper.audio import SAMPLE_RATE, CHUNK_LENGTH

RECORD_SECONDS = CHUNK_LENGTH  # 30
# TODO: bring FRAMES_PER_BUFFER down and see if it breaks anything or improves latency
# FRAMES_PER_BUFFER = 1024
# FRAMES_PER_BUFFER = 3000
# OpenAI Whisper complains if not 480000: assert x.shape[1:] == self.positional_embedding.shape, "incorrect audio shape"
FRAMES_PER_BUFFER = RECORD_SECONDS * SAMPLE_RATE  # 480,000 = N_SAMPLES
FORMAT = pyaudio.paInt16
CHANNELS = 1


class Microphone:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.run = False
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=SAMPLE_RATE,
                                      input=True,
                                      frames_per_buffer=FRAMES_PER_BUFFER)
        # start=True

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def start(self):
        self.run = True
        self.stream.start_stream()

    def listen(self):
        while self.run:
            prev = time.time()
            if self.stream.is_active():
                start = time.time()
                # print("listening...")  # {:.3f}".format(time.time() - start))
                data = self.stream.read(FRAMES_PER_BUFFER >> 3)
                # print("got audio from the mic, {:.3f}".format(time.time() - start))
                prev = time.time()
                yield np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
                # print("after yield, {:.3f}".format(time.time() - prev))
            else:
                break
    def stop(self):
        self.run = False
        self.stream.stop_stream()
