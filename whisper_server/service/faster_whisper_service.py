import numpy as np
import torch
from faster_whisper import WhisperModel, vad

from .abstract_whisper_service import AbstractWhisperService
from whisper_server.microphone import Microphone


class FasterWhisperService(AbstractWhisperService):
    def __init__(
            self, mic: Microphone, model: str = "base", english: bool = True
    ):
        super().__init__(mic, model, english)
        # logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
        if torch.cuda.is_available():
            device = "gpu"
            compute_type = "float16"
        else:
            device="cpu"
            compute_type = "float32"

        self.model = WhisperModel(self.model_name, compute_type=compute_type, device=device)
        # self.vad = vad.get_vad_model()

    def run_speech_to_text(self):
        for audio in self.mic.listen():
            # yield self.speech_to_text(audio)
            [segments, _] = self.model.transcribe(audio, vad_filter=True)
            for segment in segments:
                yield segment.text.lstrip()

    def speech_to_text(self, audio: np.ndarray):
        pass
    #     [segments, _] = self.model.transcribe(audio, vad_filter=True)
    #     for segment in segments:
    #         yield segment.text
