import os
import socket
import threading
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

from .service.abstract_whisper_service import AbstractWhisperService

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
    resp = EventSourceResponse()  # sep="\r\n\r\n")
    await resp.prepare(request)
    # resp.ping_interval = 1

    async with resp:
        for results in Server.whisper.run_speech_to_text():
            data = json.dumps({"results": results})
            print(f"sending: {data}")
            await resp.send(data)
            await asyncio.sleep(1)

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


def use_whisper(whisper_service: AbstractWhisperService):
    Server.whisper = whisper_service
    # for results in whisper.run_speech_to_text():
    #     sse.publish(results, type='whisper')


class Server:
    # thread: threading.Thread
    whisper: AbstractWhisperService = None

    def __init__(self, port: int = 1634):
        hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(hostname)
        self.port = port
        self.ssdp_server = SSDPServer('whisper-server',
                                      location='http://{0}:{1}'.format(self.ip_address, port)
                                      )
        self.ssdp_thread = threading.Thread(name='SSDP', target=self.ssdp_server.serve_forever)
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
        # print("Server started at http://127.0.0.1:8080")

        web.run_app(app, host='localhost', port=self.port)
        # start_server = sse.serve(SseHandler, self.ip_address, self.port)
        # asyncio.get_event_loop().run_until_complete(start_server)
        # asyncio.get_event_loop().run_forever()

        # Flask
        # app.run(
        #     port=self.port,
        #     debug=True,
        # )

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
