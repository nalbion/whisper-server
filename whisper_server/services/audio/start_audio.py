from multiprocessing import Process, Queue, Event
from threading import Thread

from whisper_server.services.audio.microphone import Microphone


def start_audio_process(audio_queue: Queue, audio_active_event: Event):
    mic = Microphone()

    if audio_active_event.is_set():
        mic.start()

    def process_record_audio():  # audio_queue: multiprocessing.Queue):
        while not mic.is_closed():
            if not audio_active_event.is_set():
                mic.stop()
                audio_active_event.wait()
                mic.start()

            for audio in mic.listen():
                if audio_active_event.is_set():
                    audio_queue.put(audio)
                else:
                    break

    audio_process = Process(name="whisper_server audio", target=process_record_audio)  # , args=(audio_queue,))

    async def stop():
        mic.stop()
        mic.close()
        audio_queue.close()
        audio_queue.cancel_join_thread()
        audio_process.terminate()
        audio_process.join()

    return stop


def start_audio_thread(audio_queue: Queue, audio_active_event: Event):
    mic = Microphone()

    if audio_active_event.is_set():
        mic.start()

    def run_audio_loop():
        while not mic.is_closed():
            if not audio_active_event.is_set():
                mic.stop()
                # print("run_audio_loop waiting for startRecognition()")
                audio_active_event.wait()
                if mic.is_closed():
                    break
                mic.start()

            for audio in mic.listen():
                if audio_active_event.is_set():
                    audio_queue.put(audio)
                else:
                    break

    audio_thread = Thread(name="whisper_server audio", target=run_audio_loop)
    audio_thread.start()

    async def stop():
        mic.stop()
        mic.close()
        audio_active_event.set()
        audio_queue.close()
        audio_queue.cancel_join_thread()
        audio_thread.join()

    return stop
