FROM ubuntu:latest

RUN apt-get update && apt-get -y install python3 pip python3-pyaudio

WORKDIR /whisper_server

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY whisper_server ./whisper_server

CMD ["python3", "-m", "whisper_server" ]
