import whisper
import numpy as np
import torch

from .abstract_whisper_service import AbstractWhisperService
from whisper_server.microphone import Microphone


class OpenAiWhisperService(AbstractWhisperService):
    def __init__(
            self, mic: Microphone, model: str = "base", english: bool = True
    ):
        super().__init__(mic, model, english)
        self.decodeOptions = whisper.DecodingOptions(
            fp16=torch.cuda.is_available(),
            language="en" if english else None,
        )
        self.model = whisper.load_model(self.model_name)

    def speech_to_text(self, audio: np.ndarray):
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # decode the audio
        options = whisper.DecodingOptions(
            fp16=False,
            language="en",
        )
        # Performs decoding of 30-second audio segment(s)
        result = whisper.decode(self.model, mel, options)
        print("text: " + result.text + ", " + str(result.avg_logprob) + ", " + str(result.no_speech_prob))
        return result.text

    # model.decode()
