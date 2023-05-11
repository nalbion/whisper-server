# Facere Whisper Demo

## Whisper
Follow the setup instructions at [https://github.com/openai/whisper](Whisper on GitHub):
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

| Model  | Disk   | Mem     | SHA                                        |
| ---    | ---    | ---     | ---                                        |
| tiny   |  75 MB | ~125 MB | `bd577a113a864445d4c299885e0cb97d4ba92b5f` |
| base   | 142 MB | ~210 MB | `465707469ff3a37a2b9b8d8f89f2f99de7299dac` |
| small  | 466 MB | ~600 MB | `55356645c2b361a969dfd0ef2c5a50d530afd8d5` |
| medium | 1.5 GB | ~1.7 GB | `fd9727b6e1217c2f614f9b698455c4ffd82463b4` |
| large  | 2.9 GB | ~3.3 GB | `0f4c8e34f21cf1a914c59d8b3ce882345ad349d6` |

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
