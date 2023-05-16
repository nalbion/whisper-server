import argparse
import asyncio
from multiprocessing import Queue, Event
import queue
import signal
import sys
import torch

from whisper_server.services.audio.start_audio import start_audio_thread
from whisper_server.services.server.start_servers import start_grpc_server, start_http_server_thread
from whisper_server.services.whisper.start_whisper import start_whisper_process
from whisper_server.services.utils import not_started, configure_logging


async def main():
    args = parse_args()

    print("================ whisper_server starting... ================")
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    audio_active_event = Event()
    interrupted_event = Event()
    audio_queue = Queue()
    stt_results_queue = Queue()
    # commands_process = multiprocessing.Process(target=command_handler)

    stop_audio = not_started("audio")
    stop_whisper = not_started("whisper")
    stop_http_server = not_started("http server")
    stop_grpc_server = not_started("grpc server")

    try:
        stop_audio = start_audio_thread(audio_queue, audio_active_event)
        stop_whisper = start_whisper_process(args, audio_queue, stt_results_queue, interrupted_event)
        # stop_whisper = start_whisper_thread(audio_queue, stt_results_queue)

        if args.http:
            audio_active_event.set()
            # log_whisper(stt_results_queue)
            stop_http_server = start_http_server_thread(args, stt_results_queue)

        if args.grpc:
            stop_grpc_server = start_grpc_server(args, stt_results_queue, audio_active_event)

        async def stop_all():
            await asyncio.gather(
                stop_http_server(),
                stop_audio(),
                stop_whisper(),
                stop_grpc_server(),
            )

        signal.signal(signal.SIGINT, lambda signum, frame: asyncio.ensure_future(stop_all()))
        print("------------------ whisper_server running ------------------")

        # sleep forever by 1 hour intervals,
        # on Windows before Python 3.8 wake up every 1 second to handle
        # Ctrl+C smoothly
        if sys.platform == "win32":  # and sys.version_info < (3, 8):
            delay = 1
        else:
            delay = 3600

        while not interrupted_event.is_set():
            await asyncio.sleep(delay)

        # await stop_all()
    except (KeyboardInterrupt, SystemExit):
        print("Whisper main() interrupted by keyboard")
        pass

    print("================== whisper_server stopped ==================")
    # sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser()
    # Based on Whisper args: https://github.com/openai/whisper/blob/main/whisper/transcribe.py#L374
    parser.add_argument("--whisper_impl", default="OpenAI",
                        choices=["OpenAI", "Faster Whisper"],
                        help="Which Whisper implementation to use")
    parser.add_argument("--model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Name of the Whisper model to use (without the language suffix)")
    parser.add_argument("--language", default="all",
                        choices=["all", "en"],
                        help="Specify 'en' if only English transcription is required")
    parser.add_argument("--device",
                        default="cuda" if torch.cuda.is_available() else "cpu",
                        choices=["cpu", "gpu"],
                        help="Device to use for PyTorch inference")

    parser.add_argument("--task", type=str, default="transcribe", choices=["transcribe", "translate"],
                        help="Whether to perform speech recognition ('transcribe') or X->English translation")

    # ----- Server args -----
    parser.add_argument("--logging", default="warning", choices=["error", "warning", "info", "debug"])
    parser.add_argument("--ssdp", action=argparse.BooleanOptionalAction, default=False,
                        help="'--ssdp' to allow discoverability of host IP by SSDP")
    parser.add_argument("--http", action=argparse.BooleanOptionalAction, default=False,
                        help="'--http' to run HTTP server")
    parser.add_argument("--http_port", type=int,
                        help="By default runs gRPC server on port 8080")
    parser.add_argument("--grpc", action=argparse.BooleanOptionalAction, default=True,
                        help="'--no-grpc false' to disable gRPC server")
    parser.add_argument("--grpc_port", type=int,
                        help="By default runs gRPC server on port 9090")
    parser.add_argument("--localhost", action=argparse.BooleanOptionalAction, default=True,
                        help="'--no-localhost' if you need to access the server from another computer")
    args = parser.parse_args()

    if hasattr(args, 'help'):
        parser.print_help()
        exit(0)

    if hasattr(args, 'usage'):
        parser.print_usage()
        exit(0)

    configure_logging(args.logging)

    if args.language == "all":
        args.language = None
    elif args.language == "en":
        args.model += "." + args.language
    else:
        args.language = None

    if args.http_port is not None:
        args.http = True
    elif args.http:
        args.http_port = 8080

    if args.grpc_port is not None:
        args.grpc = True
    elif args.grpc:
        args.grpc_port = 9090

    print(str(args))
    return args

def log_whisper(stt_results_queue: Queue):
    while True:
        try:
            alternatives = stt_results_queue.get()
            # print("app has " + str(len(list(alternatives))))
            print("app has " + str(len(alternatives)))
            for alternative in alternatives:
                print("  '" + str(alternative) + "'")
        except queue.Empty:
            print("empty stt_results queue")
            break


if __name__ == "__main__":
    asyncio.run(main())
