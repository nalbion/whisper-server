from threading import Thread
from multiprocessing import Queue, Event

from whisper_server.services.server.http_server import HttpServer, use_results_queue
from whisper_server.services.server.grpc_server import GrpcServer


def start_http_server_thread(args, stt_results_queue: Queue):
    server = HttpServer(args)

    def run_server():  # stt_results_queue: Queue):
        use_results_queue(stt_results_queue)

        # thread = Thread(target=server.startHttp)
        # thread.start()
        server.start_http()

        # server.start_discoverability()
        # return server

        # server.stop_discoverability()

    server_thread = Thread(name="whisper_server server", target=run_server)
    server_thread.start()

    async def stop():
        await server.stop_http()
        server.stop_discoverability()
        server_thread.join()

    return stop


def start_grpc_server(args, stt_results_queue: Queue, audio_active_event: Event):
    """
    :param args: `localhost` and `grpc_port` as configured by the CLI args.
    :param stt_results_queue: The gRPC server receives speech-to-text events on this queue
    :param audio_active_event: The gRPC API can stop/start the audio input stream
    :return:
    """
    server = GrpcServer(stt_results_queue, audio_active_event)
    server.start(args.localhost, args.grpc_port)

    async def stop():
        server.stop()

    return stop
