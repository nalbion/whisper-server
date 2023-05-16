from concurrent import futures
import grpc
from whisper_server.proto.whisper_server_pb2_grpc import WhisperServerServicer, add_WhisperServerServicer_to_server
from whisper_server.proto.whisper_server_pb2 import WhisperSimpleOutput, EmptyResponse
from multiprocessing import Queue, Event
from whisper_server.services.utils import logger

empty_response = EmptyResponse()


class GrpcServer(WhisperServerServicer):
    def __init__(self, stt_results_queue: Queue, audio_active_event: Event):
        self.stt_results_queue = stt_results_queue
        self.audio_active_event = audio_active_event
        self.server: grpc.server = None

    def start(self, localhost: bool = True, port: int = 9090):
        print(f"Starting gRPC server on port {port}")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_WhisperServerServicer_to_server(self, server)
        server.add_insecure_port(f'{"localhost" if localhost else "[::]"}:{port}')
        server.start()
        self.server = server
        # server.wait_for_termination()

    def stop(self):
        # TODO: this returns an Event, and probably won't do anything by itself
        self.server.stop(None)

    def loadModel(self, request, context):
        # request.name  language, device, download_root, in_memory
        # TODO:
        print("load model not implemented, but could set name, language, ")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)

    # TODO: gain adjustable from client

    def setPrefix(self, request, context):
        """
        initial prompt to provide context - words & named entities which are likely to be included in the speech
        :param request:
        :param context:
        :return:
        """
        # TODO: setPrefix
        print("TODO: setPrefix")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)

    def setPrompt(self, request, context):
        # TODO: setPrompt
        print("TODO: setPrompt")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)

    def startRecognition(self, request, context):
        # print("startRecognition")
        self.audio_active_event.set()
        return empty_response

    def stopRecognition(self, request, context):
        logger.debug("stopRecognition")
        self.audio_active_event.clear()
        return empty_response

    def waitForSpeech(self, request, context):
        logger.debug("waitForSpeech...")

        alternatives = self.stt_results_queue.get()
        logger.debug("  sending alternatives: %s", alternatives)
        alternatives = [alt["text"] for alt in alternatives]
        return WhisperSimpleOutput(alternatives=alternatives)
