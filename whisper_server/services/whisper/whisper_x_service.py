import whisperx
import faster_whisper
import numpy as np
import os
import sys
import torch
from whisperx.audio import log_mel_spectrogram, SAMPLE_RATE, CHUNK_LENGTH, N_SAMPLES
from whisperx.vad import load_vad_model, merge_chunks

from .abstract_whisper_service import AbstractWhisperService

_stdout = sys.stdout
_notout = open(os.devnull, 'w')


class WhisperxService(AbstractWhisperService):
    """
    See https://github.com/m-bain/whisperX
    """

    def __init__(
            self, args
    ):
        super().__init__(args)
        device = args.device

        self.default_asr_options = faster_whisper.transcribe.TranscriptionOptions(
            beam_size=5,
            best_of=5,
            patience=1,
            length_penalty=1,
            temperatures=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=False,
            initial_prompt=None,
            prefix=None,
            suppress_blank=True,
            suppress_tokens=[-1],
            without_timestamps=True,
            max_initial_timestamp=0.0,
            word_timestamps=False,
            prepend_punctuations="\"'“¿([{-",
            append_punctuations="\"'.。,，!！?？:：”)]}、"
        )

        # options = faster_whisper.transcribe.TranscriptionOptions()
        compute_type = 'auto'  # 'default'  # float16 for GPU. For CPU: int16, float32 or int8
        self.model = whisperx.load_model(self.model_name, device, compute_type)
        self.vad_model = load_vad_model(torch.device(device))
        language = args.language
        # self.tokenizer = faster_whisper.tokenizer.Tokenizer(self.model.tokenizer, not english,
        #                                                     task='transcribe', language=language)

    def speech_to_text(self, audio: np.ndarray):
        # whisperx FasterWhisperPipeline.transcribe() runs the audio through a VAD, tokenizer

        # self.model.transcribe(audio)
        # default_vad_options = { 'vad_onset': 0.500, 'vad_offset': 0.363 }

        vad_segments = self.vad_model({'waveform': torch.from_numpy(audio).unsqueeze(0), 'sample_rate': SAMPLE_RATE})
        sys.stdout = _notout
        vad_segments = merge_chunks(vad_segments, CHUNK_LENGTH)
        sys.stdout = _stdout

        features = log_mel_spectrogram(audio, padding=N_SAMPLES - audio.shape[0])

        results = self.model.model.generate_segment_batched(features, self.model.tokenizer, self.default_asr_options)
        return map(lambda hypothesis: {"text": hypothesis.lstrip()}, results)
