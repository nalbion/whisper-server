# Whisper Server

`whisper_server` listens for speech on the microphone and streams the results in real-time over [Server Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) or [gRPC](https://grpc.io/).

Integrates with the official [Open AI Whisper API](https://openai.com/research/whisper) and also
[whisperX](https://github.com/m-bain/whisperX) and [faster-whisper](https://github.com/guillaumekln/faster-whisper).


## Running Whisper Server

```bash
python -m whisper_server
```

### Running in Docker

Build the Docker image:
```bash
docker build -t nalbion/whisper_server .
```

```bash
docker run --rm -e "PULSE_SERVER=/mnt/wslg/PulseServer" -v /mnt/wslg/:/mnt/wslg/ nalbion/whisper_server
```


## Development

### Generate gRPC code

```bash
python -m grpc_tools.protoc -I./whisper_server/proto --python_out=./whisper_server/proto --pyi_out=./whisper_server/proto --grpc_python_out=./whisper_server/proto ./whisper_server/proto/whisper_server.proto
```
