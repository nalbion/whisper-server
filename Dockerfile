FROM ubuntu:latest

# "tiny.en" "tiny" "base.en" "base" "small.en" "small" "medium.en" "medium" "large-v1" "large"
ARG MODEL=base.en

RUN apt-get update && apt-get -y install python3 pip portaudio19-dev

WORKDIR /whisper_server

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY whisper_server ./whisper_server

CMD ["python", "-m", "whisper_server" ]
