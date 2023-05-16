import queue
import signal
from multiprocessing import Process, Queue, Event
from threading import Thread

from whisper_server.services.whisper.openai_whisper_service import OpenAiWhisperService
# from whisper_server.services.whisper.whisper_x_service import WhisperxService
from whisper_server.services.whisper.faster_whisper_service import FasterWhisperService
from whisper_server.services.utils import logger

def signal_handler(interrupted_event):
    interrupted_event.set()


def run_whisper_loop(args, _audio_queue: Queue, _stt_results_queue: Queue, interrupted_event: Event):
    implementations = {
        "OpenAI": OpenAiWhisperService,
        "Faster Whisper": FasterWhisperService,
        # "WhisperX": WhisperxService,
    }

    whisper = implementations[args.whisper_impl](args)

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(interrupted_event))

    while True:
        try:
            audio = _audio_queue.get()
            # if audio == "stop":
            #     print("process_speech_to_text received 'stop'")
            #     break
            # logger.debug("sending audio to Whisper...")
            alternatives = whisper.speech_to_text(audio)
            alternatives = list(alternatives)
            if len(alternatives) != 0:
                logger.info("Whisper recognised: %s", alternatives)
                _stt_results_queue.put(alternatives)
        except ValueError:
            print("  ValueError in reading from audio_queue")
            break
        except queue.Empty:
            print("empty audio queue")
            break
        except (KeyboardInterrupt, InterruptedError, SystemExit):
            _audio_queue.close()
            _audio_queue.cancel_join_thread()
            _stt_results_queue.close()
            _stt_results_queue.cancel_join_thread()
            print("---------- whisper process interrupted by keyboard ---------")
            break



def start_whisper_process(args, audio_queue: Queue, stt_results_queue: Queue, interrupted_event: Event):
    # interrupted_event = Event()
    whisper_process = Process(name="whisper_server speech to text",
                              target=run_whisper_loop,
                              args=(args, audio_queue, stt_results_queue, interrupted_event),
                              # daemon=True
                              )
    whisper_process.start()

    async def stop():
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_process.terminate()
        whisper_process.join()

    return stop


def start_whisper_thread(audio_queue: Queue, stt_results_queue: Queue):
    whisper_thread = Thread(name="whisper_server speech to text",
                            target=run_whisper_loop,
                            args=(audio_queue, stt_results_queue))
    whisper_thread.start()

    async def stop():
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_thread.join()

    return stop
