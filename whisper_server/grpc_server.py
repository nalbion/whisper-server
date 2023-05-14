from concurrent import futures
import grpc
from whisper_server.whisper_server_pb2_grpc import WhisperServerServicer, add_WhisperServerServicer_to_server
from whisper_server.whisper_server_pb2 import WhisperSimpleOutput
from multiprocessing import Queue, Event


class GrpcServer(WhisperServerServicer):

    def __init__(self, stt_results_queue: Queue, audio_active_event: Event):
        self.stt_results_queue = stt_results_queue
        self.audio_active_event = audio_active_event
        self.server = None

    def start(self, port: int = 1634):
        print(f"Starting gRPC server on port {port}")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_WhisperServerServicer_to_server(self, server)
        server.add_insecure_port(port)
        server.start()
        server.wait_for_termination()
        self.server = server
        print("  gRPC server started")

    def stop(self):
        # TODO: this returns an Event, and probably won't do anything by itself
        self.server.stop()

    def loadModel(self, request, context):
        # request.name  language, device, download_root, in_memory
        # TODO:
        print("load model not implemented, but could set name, language, ")

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

    def setPrompt(self, request, context):
        # TODO: setPrompt
        print("TODO: setPrompt")

    def startRecognition(self, request, context):
        print("startRecognition")
        self.audio_active_event.set()

    def stopRecognition(self, request, context):
        print("stopRecognition")
        self.audio_active_event.clear()

    def waitForSpeech(self, request, context):
        print("waitForSpeech...")
        alternatives = self.stt_results_queue.get()
        print(f"  sending alternatives: {alternatives}")
        return WhisperSimpleOutput(alternatives=alternatives)
