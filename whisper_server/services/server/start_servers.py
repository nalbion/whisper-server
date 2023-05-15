from threading import Thread
from multiprocessing import Queue, Event

from whisper_server.services.server.http_server import HttpServer, use_results_queue
from whisper_server.services.server.grpc_server import GrpcServer


def start_http_server_thread(stt_results_queue: Queue):
    server = HttpServer()

    def run_server():  # stt_results_queue: Queue):
        print("run_server starting...")
        use_results_queue(stt_results_queue)

        # thread = Thread(target=server.startHttp)
        # thread.start()
        server.start_http()

        # server.start_discoverability()
        # return server

        # server.stop_discoverability()
        print("  exit run_server")

    server_thread = Thread(name="whisper_server server", target=run_server)
    server_thread.start()

    async def stop():
        print("stopping http_server_thread...")
        server.stop_http()
        server.stop_discoverability()
        server_thread.join()
        print("  server thread stopped")

    return stop


def start_grpc_server(stt_results_queue: Queue, audio_active_event: Event):
    print("starting grpc_server...")
    server = GrpcServer(stt_results_queue, audio_active_event)
    server.start()

    async def stop():
        print("stopping grpc_server_thread...")
        server.stop()
        print("  grpc_server_thread stopped")

    return stop
