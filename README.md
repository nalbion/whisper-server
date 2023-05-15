# Whisper Server

`whisper_server` listens for speech on the microphone and streams the results in real-time over [Server Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) or [gRPC](https://grpc.io/).

Integrates with the official [Open AI Whisper API](https://openai.com/research/whisper) and also
[whisperX](https://github.com/m-bain/whisperX) and [faster-whisper](https://github.com/guillaumekln/faster-whisper).


## Running Whisper Server

```bash
python -m whisper_server
```

## Development

### Generate gRPC code

```bash
python -m grpc_tools.protoc -I./whisper_server/proto --python_out=./whisper_server/proto --pyi_out=./whisper_server/proto --grpc_python_out=./whisper_server/proto ./whisper_server/proto/whisper_server.proto
```

# Running Whisper
The following notes have little to do with `whisper_server`, but might be of interest if you want to run Whisper directly.

## Whisper
Follow the setup instructions at [Whisper on GitHub](https://github.com/openai/whisper):
- install Python
- `pip install -U openai-whisper`

### Linux
```bash
sudo apt update && sudo apt install ffmpeg
```

### Windows

```bash
choco install ffmpeg
```

### whisper-server in Docker

```bash
docker build -t nalbion/whisper_server .
```

```bash
docker run --rm -e "PULSE_SERVER=/mnt/wslg/PulseServer" -v /mnt/wslg/:/mnt/wslg/ nalbion/whisper_server
```


## Whisper.cpp on the Web
[whisper.cpp](https://github.com/ggerganov/whisper.cpp) can also be run in the [browser](https://github.com/ggerganov/whisper.cpp/tree/master/examples/stream.wasm).

The [online examples](https://whisper.ggerganov.com/stream/) are not too impressive on a laptop.

## Whisper.cpp in Docker

### Memory usage

| Model  | Disk   | Mem     |
| ---    | ---    | ---     |
| tiny   |  75 MB | ~125 MB |
| base   | 142 MB | ~210 MB |
| small  | 466 MB | ~600 MB |
| medium | 1.5 GB | ~1.7 GB |
| large  | 2.9 GB | ~3.3 GB |

### Build
Choose a model from the table above and run:

```bash
MODEL=base & LANG=".en" & docker build -f Dockerfile.cpp -t nalbion/whisper-cpp-$MODEL --build-arg MODEL=$MODEL$LANG .
```
or on **Windows**:
```bash
set MODEL=base& set LANG=.en& docker build -f Dockerfile.cpp -t nalbion/whisper-cpp-%MODEL% --build-arg MODEL=%MODEL%%LANG% .
```

### Run Whisper
```bash
docker run --rm -v /dev/snd:/dev/snd nalbion/whisper-cpp-base
```

or on **WSL**:
```bash
docker run --rm -e "PULSE_SERVER=/mnt/wslg/PulseServer" -v /mnt/wslg/:/mnt/wslg/ nalbion/whisper-cpp-base
```

or for an interactive shell:

```bash
docker run --rm -it -v "$(pwd)/build:/artifacts" --entrypoint /bin/bash nalbion/whisper-cpp-base
```

or from **Windows**:

```bash
docker run --rm -it -v %cd%/build:/artifacts --entrypoint /bin/bash nalbion/whisper-cpp-base
```

From the shell you can copy the wasm files:

```bash
cp -r bin/stream.wasm/* bin/libstream.worker.js /artifacts/wasm
```
