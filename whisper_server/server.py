import socket
import threading
from ssdpy import SSDPServer
from flask_sse import sse
from flask import Flask, render_template
import time

from .service.abstract_whisper_service import AbstractWhisperService

app = Flask(__name__)
# sse.register()
app.register_blueprint(sse, url_prefix='/whisper')


class Server:
    # thread: threading.Thread
    whisper: AbstractWhisperService = None

    def __init__(self, port: int = 1634):
        hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(hostname)
        self.port = port
        self.server = SSDPServer('whisper-server',
                                 location='http://{0}:{1}'.format(self.ip_address, port)
                                 )

    def startHttp(self):
        # print('HTTP server started at http://{0}:{1}'.format(self.ip_address, self.port))
        app.run(
            port=self.port,
            debug=True,
        )

    def start_discoverability(self):
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop_discoverability(self):
        self.server.stopped = True

    def use_whisper(self, whisper: AbstractWhisperService):
        # self.whisper = whisper
        for results in whisper.run_speech_to_text():
            sse.publish(results, type='whisper')


@app.route('/')
def index():
    return render_template("index.html")

# @app.route("/whisper")
# def whisperEventSource():
    # event_source = sse.EventSource()

    # for results in self.whisper.run_speech_to_text():
    #     event_source.send(results)

    # while True:
    #     event_source.send("Hello, world!")
    #     time.sleep(1)
    # return event_source
