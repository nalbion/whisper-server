FROM ubuntu:latest

# "tiny.en" "tiny" "base.en" "base" "small.en" "small" "medium.en" "medium" "large-v1" "large"
ARG MODEL=base.en

RUN apt-get update && apt-get -y install python3 pip ffmpeg

WORKDIR /whisper-server

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY whisper-server ./whisper-server
#RUN py.test tests

ENTRYPOINT ["python3", "-m", "whisper-server"]
