import whisper
import numpy as np
import torch
from whisper import DecodingResult
from whisper.audio import N_SAMPLES
from .abstract_whisper_service import AbstractWhisperService
from whisper_server.microphone import Microphone, FRAMES_TO_PROCESS


class OpenAiWhisperService(AbstractWhisperService):
    """
    See https://github.com/openai/whisper
    """

    def __init__(
            self, model: str = 'base', english: bool = True
    ):
        super().__init__(model, english)
        self.decodeOptions = whisper.DecodingOptions(
            fp16=torch.cuda.is_available(),
            language='en' if english else None,
            sample_len=FRAMES_TO_PROCESS,
            without_timestamps=True,
            # beam_size - use BeamSearchDecoder else GreedyDecoder
        )
        self.model = whisper.load_model(self.model_name)

    def speech_to_text(self, audio: np.ndarray):
        """
        :param audio:
        :return: Iterable of { text, avg_logprob, no_speech_prob }
        """
        # whisper.decode will error 'incorrect audio shape' if the mel dims are wrong, so pad with zero samples.
        padding = N_SAMPLES - len(audio)

        # The mel-spectrogram is a representation of audio that is used by machine learning models to learn the temporal
        # and spectral properties of audio. The mel-spectrogram is a 2D matrix where each row represents a time frame
        # and each column represents a frequency band. The values in the mel-spectrogram represent the energy of the
        # audio signal in each frequency band at each time frame.
        #
        # 480,000 (frames of audio) / 1500 (n_audio_ctx of Model) = 320 audio contexts.
        # Each of the 320 audio contexts is a sequence of 80 mel-spectrogram frames. (mel duration is 18.75 seconds)
        mel = whisper.log_mel_spectrogram(audio, padding=padding).to(self.model.device)

        # Decode the audio
        # TODO: add prompt/prefix kwargs
        results = whisper.decode(self.model, mel, self.decodeOptions)
        if isinstance(results, DecodingResult):
            results = [results]

        results = filter(self.filter_results, results)
        return map(lambda hypothesis: {"text": hypothesis.text, "avg_logprob": hypothesis.avg_logprob}, results)

    def filter_results(self, hypothesis: DecodingResult):
        # Ignore no_speech_prob >= 0.75
        # avg_logprob:
        #  >= -0.3 : good
        #     -0.4 : close
        #  >  -0.8 : clear speech mis-recognised or
        #  <= -0.8 : mis-pronounced
        #  <  -1.0 : is mumbled/hard to hear
        print('avg_logprob: {:.3f}, no_speech_prob: {:.3f}'.format(hypothesis.avg_logprob, hypothesis.no_speech_prob))
        self.logger.info('avg_logprob: %.3f, no_speech_prob: %.3f', hypothesis.avg_logprob, hypothesis.no_speech_prob)
        return hypothesis.no_speech_prob < 0.75 and hypothesis.avg_logprob > -1.0
