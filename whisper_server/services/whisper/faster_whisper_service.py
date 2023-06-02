import numpy as np
import torch
from faster_whisper import WhisperModel, vad
from faster_whisper.transcribe import Segment

from .abstract_whisper_service import AbstractWhisperService
from whisper_server.services.utils import logger


class FasterWhisperService(AbstractWhisperService):
    """
    See https://github.com/guillaumekln/faster-whisper
    """

    def __init__(
            self, args
    ):
        super().__init__(args)
        # logging.getLogger('faster_whisper').setLevel(logging.DEBUG)

        if torch.cuda.is_available():
            compute_type = 'float16'
        else:
            compute_type = 'float32'

        print(f"Faster Whisper loading model {self.model_name}...")
        self.model = WhisperModel(self.model_name, compute_type=compute_type, device=args.device)
        self.task = args.task
        # self.vad = vad.get_vad_model()

    def speech_to_text(self, audio: np.ndarray):
        print(f"transcribing {len(audio)}")
        [segments, _] = self.model.transcribe(audio,
                                              task=self.task,
                                              # vad_filter=True,
                                              # vad_parameters=dict()
                                              )

        alternatives = filter(self.filter_results, segments)
        return map(lambda segment: {"text": segment.text.lstrip(), "avg_logprob": segment.avg_logprob},
                   alternatives)

    def filter_results(self, hypothesis: Segment):
        # Ignore no_speech_prob >= 0.75
        # avg_logprob:
        #  >= -0.3 : good
        #     -0.4 : close
        #  >  -0.8 : clear speech mis-recognised or
        #  <= -0.8 : mis-pronounced
        #  <  -1.0 : is mumbled/hard to hear
        # print('avg_logprob: {:.3f}, no_speech_prob: {:.3f}'.format(hypothesis.avg_logprob, hypothesis.no_speech_prob))
        logger.debug('avg_logprob: %.3f, no_speech_prob: %.3f', hypothesis.avg_logprob, hypothesis.no_speech_prob)
        return hypothesis.no_speech_prob < 0.75 and hypothesis.avg_logprob > -1.0
