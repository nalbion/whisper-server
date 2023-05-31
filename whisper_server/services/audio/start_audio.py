import queue
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


def start_audio_thread(audio_queue: Queue, command_queue: Queue, audio_active_event: Event):
    mic = Microphone()

    if audio_active_event.is_set():
        mic.start()

    def run_audio_loop():
        while not mic.is_closed():
            if not audio_active_event.is_set():
                mic.stop()
                audio_active_event.wait()
                if mic.is_closed():
                    break
                mic.start()

            for audio in mic.listen():
                if audio_active_event.is_set():
                    audio_queue.put(audio)
                else:
                    break

    def run_command_loop():
        while not mic.is_closed():
            try:
                command = command_queue.get()
                if command['type'] == 'input_device':
                    mic.select_device(command['payload'])
                elif command['type'] == 'exit':
                    break
            except queue.Empty:
                break

    audio_thread = Thread(name="whisper_server audio", target=run_audio_loop)
    audio_thread.start()

    command_thread = Thread(name="whisper_server audio_command", target=run_command_loop)
    command_thread.start()

    async def stop():
        mic.stop()
        mic.close()
        audio_active_event.set()
        audio_queue.close()
        audio_queue.cancel_join_thread()
        audio_thread.join()
        print("stopping command loop...")
        command_queue.put(dict(type='exit'))
        command_thread.join()
        print("audio stopped")

    return stop
