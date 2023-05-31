import numpy as np
import pyaudio

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
        # self.list_input_devices()
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=SAMPLE_RATE,
                                      input=True,
                                      frames_per_buffer=FRAMES_PER_BUFFER)

    def __exit__(self, *err):
        self.close()

    def __del__(self):
        self.close()

    def list_input_devices(self):
        hosts = self.audio.get_host_api_count()
        device_count = self.audio.get_device_count()

        for index in range(hosts):
            host = self.audio.get_host_api_info_by_index(index)
            print("-----------------------")
            print(f"Host audio API {index}: {host['name']}")

            for d in range(device_count):
                device_info = self.audio.get_device_info_by_index(d)
                inputs = device_info['maxInputChannels']

                try:
                    #if 1 <= inputs <= 2 and \
                    if inputs >= 1 and \
                            device_info['hostApi'] == index and \
                            self.audio.is_format_supported(rate=SAMPLE_RATE,
                                                           input_device=d,
                                                           input_format=FORMAT,
                                                           input_channels=1):
                        # print(str(device_info))
                        print(f"  Device {d}: {device_info['name']}")
                except ValueError:
                    # print(str(device_info))
                    pass

    def select_device(self, name):
        input_device_index = -1
        device_count = self.audio.get_device_count()
        for d in range(device_count):
            device_info = self.audio.get_device_info_by_index(d)
            inputs = device_info['maxInputChannels']
            if inputs >= 1 and \
                    self.audio.is_format_supported(rate=SAMPLE_RATE,
                                                   input_device=d,
                                                   input_format=FORMAT,
                                                   input_channels=1):
                input_device_index = d
                break

        if input_device_index != -1:
            logger.info(f"selecting audio input device: {name}")
            if self.run:
                self.stop()

            self.stream = self.audio.open(format=FORMAT,
                                          channels=CHANNELS,
                                          rate=SAMPLE_RATE,
                                          input=True,
                                          frames_per_buffer=FRAMES_PER_BUFFER,
                                          input_device_index=input_device_index)

    def listen(self):
        while self.run:
            if self.stream.is_active():
                data = self.stream.read(FRAMES_TO_PROCESS)
                yield np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
            else:
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
