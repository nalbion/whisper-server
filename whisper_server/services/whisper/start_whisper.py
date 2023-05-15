import queue
import signal
from multiprocessing import Process, Queue, Event
from threading import Thread


# from whisper_server.service.abstract_whisper_service import AbstractWhisperService
# from whisper_server.services.whisper.openai_whisper_service import OpenAiWhisperService
# from whisper_server.service.whisper_x_service import WhisperxService
from whisper_server.services.whisper.faster_whisper_service import FasterWhisperService

def signal_handler(interrupted_event):
    print("run_whisper_loop received SIGINT signal")
    interrupted_event.set()
    # _audio_queue.close()
    # _stt_results_queue.put(signal)
    # _stt_results_queue.close()
    # _stt_results_queue.cancel_join_thread()
    # sys.exit(0)


def run_whisper_loop(_audio_queue: Queue, _stt_results_queue: Queue, interrupted_event: Event):
    print("run_whisper_loop starting...")
    # whisper = OpenAiWhisperService(audio_queue)
    # whisper = WhisperxService(audio_queue)
    whisper = FasterWhisperService()

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(interrupted_event))
    # pcntl.signal(pcntl.SIGINT, signal_handler)

    while True:
        try:
            audio = _audio_queue.get()
            # if audio == "stop":
            #     print("process_speech_to_text received 'stop'")
            #     break
            alternatives = whisper.speech_to_text(audio)
            alternatives = list(alternatives)
            if len(alternatives) != 0:
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
            print("  run_whisper_loop process interrupted by keyboard")
            break

    print("  exit process_speech_to_text")


def start_whisper_process(audio_queue: Queue, stt_results_queue: Queue, interrupted_event: Event):
    print("starting whisper_process...")
    # interrupted_event = Event()
    whisper_process = Process(name="whisper_server speech to text",
                              target=run_whisper_loop,
                              args=(audio_queue, stt_results_queue, interrupted_event),
                              # daemon=True
                              )
    whisper_process.start()

    # os.killpg(os.getpgid(whisper_process.pid), signal.SIGINT)

    async def stop():
        print("terminating whisper_process")
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_process.terminate()
        whisper_process.join()
        print("  start_whisper_process.stop() terminated whisper_process")

    return stop


def start_whisper_thread(audio_queue: Queue, stt_results_queue: Queue):
    print("starting whisper_thread...")
    whisper_thread = Thread(name="whisper_server speech to text",
                            target=run_whisper_loop,
                            args=(audio_queue, stt_results_queue))
    whisper_thread.start()

    async def stop():
        print("terminating whisper_thread")
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_thread.join()
        print("  start_whisper_thread.stop() terminated whisper_thread")

    return stop