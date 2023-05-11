FROM ubuntu:latest AS whisper

# "tiny.en" "tiny" "base.en" "base" "small.en" "small" "medium.en" "medium" "large-v1" "large"
ARG MODEL=base.en

RUN apt-get update && apt-get -y install git make wget curl build-essential libsdl2-dev
# python3 cmake
RUN git clone https://github.com/ggerganov/whisper.cpp

WORKDIR whisper.cpp

# Download the Whisper model in ggml format
RUN ./models/download-ggml-model.sh $MODEL

# Build
RUN make stream

# Build stream.wasm
#FROM emscripten/emsdk
#WORKDIR whisper.cpp
#COPY --from=whisper /whisper.cpp ./
#WORKDIR build-em
#RUN emcmake cmake .. && make -j

# -t 4       : number of threads to use during computation
# --step 0   : transcribe only after speech activity
# --step 500 :
# --length   : (max 30s) milliseconds of audio and output a transcription block that is suitable for parsing
# printf("### Transcription %d START | t0 = %d ms | t1 = %d ms\n", n_iter, (int) t0, (int) t1);
# no_timestamps
ARG MODEL=base.en
ENV MODEL=$MODEL
ENTRYPOINT ["/bin/bash", "-c", "exec ./stream", "-m ./models/ggml-${MODEL}.bin", "--step 0", "--length 5000"]
