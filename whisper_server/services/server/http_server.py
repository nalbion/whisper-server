import os
import queue
import socket
import threading
import multiprocessing
import json
from ssdpy import SSDPServer
from aiohttp import web
import aiohttp_jinja2
import jinja2
import asyncio
from aiohttp.web import Application, Response
from aiohttp_sse import EventSourceResponse
# import sse
# from flask_sse import sse
from flask import Flask, render_template
import time

from whisper_server.services.whisper.abstract_whisper_service import AbstractWhisperService

# Flask
# app = Flask(__name__)
# # sse = sse(app)
# app.register_blueprint(sse, url_prefix='/whisper')

# AIOHTTP
app = web.Application()


async def root_handler(request):
    print('root')
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
                print(f"Whisper SSE sending: {data}")
                await resp.send(data)
                await asyncio.sleep(1)
            except ValueError:
                print("value error reading from stt_results_queue")
                break
            except queue.Empty:
                print("empty results queue")
                break

        print("exit whisper SSE async loop")

    print("returning from whisper SSE async def")
    #     resp.stop_streaming()
    return resp


app.router.add_route('*', '/', root_handler)
app.router.add_route('*', '/whisper', whisper)
STATIC_PATH = os.path.join(os.path.dirname(__file__), "templates")
app.router.add_static('/', path=STATIC_PATH)


# @aiohttp_jinja2.template('index.html')
# def root_handler():
#     return {}


# app.router.add_get('/{path:.*}', index_factory)
# app.add_routes([web.templates('/', 'templates')])
# web.templates('/', __file__ + '/templates', show_index=True)
# aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))


#
#
# app.add_routes([
#     web.get('/', index),
# ])


# app.add_routes([web.get('/', hello),
#                 web.get('/{name}', hello)])

# class SseHandler(sse.Handler):
#     @asyncio.coroutine
#     def handle_request(self):
#         yield from asyncio.sleep(2)
#         self.send('foo')
#         yield from asyncio.sleep(2)
#         self.send('bar', event='wakeup')


def use_results_queue(stt_results_queue: multiprocessing.Queue):
    HttpServer.stt_results_queue = stt_results_queue
    # for results in whisper.run_speech_to_text():
    #     sse.publish(results, type='whisper')


class HttpServer:
    # thread: threading.Thread
    stt_results_queue: multiprocessing.Queue = None

    def __init__(self, port: int = 80):
        self.loop = asyncio.new_event_loop()
        hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(hostname)
        self.port = port
        self.ssdp_server = SSDPServer('whisper-server',
                                      location='http://{0}:{1}'.format(self.ip_address, port)
                                      )
        self.ssdp_thread = threading.Thread(name='whisper_server SSDP', target=self.ssdp_server.serve_forever)
        # self.httpThread = threading.Thread(name='HTTP', target=self._run_Http)

    def start_discoverability(self):
        self.ssdp_thread.start()

    def stop_discoverability(self):
        self.ssdp_server.stopped = True

    def start_http(self):
        # self.httpThread.start()

        # def _run_Http(self):
        # AIO
        # handler = app.make_handler()
        # srv = yield from loop.create_server(handler, '127.0.0.1', 8080)
        host = 'localhost'
        # host = self.ip_address
        # print(f"Server started at http://{host}:{self.port}")

        web.run_app(app,
                    host=host,
                    port=self.port,
                    handle_signals=False,
                    loop=self.loop,
                    )
        # start_server = sse.serve(SseHandler, self.ip_address, self.port)
        # asyncio.get_event_loop().run_until_complete(start_server)
        # asyncio.get_event_loop().run_forever()

        # Flask
        # app.run(
        #     port=self.port,
        #     debug=True,
        # )

    def stop_http(self):
        self.loop.stop()
        self.loop.close()

# @app.route('/')
# def index():
#     return render_template("index.html")


# @app.route("/whisper")
# def whisperEventSource():
#     # event_source = sse.EventSource()
#     while True:
#         time.sleep(1)
#         sse.publish('Hello')

# for results in self.whisper.run_speech_to_text():
#     event_source.send(results)

# while True:
#     event_source.send("Hello, world!")
#     time.sleep(1)
# return event_source
