import os
import queue
import socket
import threading
import multiprocessing
import json
from ssdpy import SSDPServer
from aiohttp import web
import asyncio
from aiohttp_sse import EventSourceResponse
from whisper_server.services.utils import logger

app = web.Application()


async def root_handler(request):
    return web.HTTPFound('/index.html')


async def whisper(request):
    """
    Server Sent Events endpoint which streams STT results
    :param request:
    :return:
    """
    resp = EventSourceResponse()  # sep="\r\n\r\n")
    await resp.prepare(request)
    # resp.ping_interval = 1

    async with resp:
        while True:
            try:
                alternatives = HttpServer.stt_results_queue.get()
                data = json.dumps({"results": alternatives})
                logger.debug("Whisper SSE sending: %s", data)
                await resp.send(data)
                await asyncio.sleep(1)
            except ValueError:
                print("value error reading from stt_results_queue")
                break
            except queue.Empty:
                print("empty results queue")
                break

    #     resp.stop_streaming()
    return resp


app.router.add_route('*', '/', root_handler)
app.router.add_route('*', '/whisper', whisper)
STATIC_PATH = os.path.join(os.path.dirname(__file__), "templates")
app.router.add_static('/', path=STATIC_PATH)


def use_results_queue(stt_results_queue: multiprocessing.Queue):
    HttpServer.stt_results_queue = stt_results_queue
    # for results in whisper.run_speech_to_text():
    #     sse.publish(results, type='whisper')


class HttpServer:
    # thread: threading.Thread
    stt_results_queue: multiprocessing.Queue = None

    def __init__(self, args):  # localhost: bool = True, port: int = 8080):
        self.loop = asyncio.new_event_loop()
        self.port = args.http_port

        if args.localhost:
            self.host = '127.0.0.1'
            self.location = 'localhost'
        else:
            self.host = '0.0.0.0'
            hostname = socket.gethostname()
            self.location = socket.gethostbyname(hostname)

        if args.ssdp:
            logger.info("Starting SSDP server, location: http://%s:%d", self.location, self.port)
            self.ssdp_server = SSDPServer('whisper-server',
                                          location='http://{0}:{1}'.format(self.location, self.port))
            self.ssdp_thread = threading.Thread(name='whisper_server SSDP', target=self.ssdp_server.serve_forever)
            self.start_discoverability()

    def start_discoverability(self):
        self.ssdp_thread.start()

    def stop_discoverability(self):
        self.ssdp_server.stopped = True

    def start_http(self):
        web.run_app(app,
                    host=self.host,
                    port=self.port,
                    # handle_signals=False,
                    loop=self.loop,
                    )

    async def stop_http(self):
        await app.shutdown()
        await app.cleanup()
