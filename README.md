# Whisper Server

`whisper_server` listens for speech on the microphone and provides the results in real-time over 
[Server Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) 
or [gRPC](https://grpc.io/).

This is intended as a local single-user server so that non-Python programs can use Whisper.

Integrates with the official [Open AI Whisper API](https://openai.com/research/whisper) and also
[faster-whisper](https://github.com/guillaumekln/faster-whisper).

## Requirements
- Python 3.10 or greater
- `pip install -r requirements.txt`

## Running Whisper Server

```bash
python -m whisper_server
```

### Options
```
  -h, --help            show this help message and exit
  --whisper_impl {OpenAI,Faster Whisper}
                        Which Whisper implementation to use
  --model {tiny,base,small,medium,large}
                        Name of the Whisper model to use (without the language suffix)
  --language {all,en}   Specify 'en' if only English transcription is required
  --device {cpu,gpu}    Device to use for PyTorch inference
  --task {transcribe,translate}
                        Whether to perform speech recognition ('transcribe') or X->English translation
  --logging {error,warning,info,debug}
  --ssdp, --no-ssdp     '--ssdp' to allow discoverability of host IP by SSDP (default: False)
  --http, --no-http     '--http' to run HTTP server (default: False)
  --http_port HTTP_PORT
                        By default runs gRPC server on port 8080
  --grpc, --no-grpc     '--no-grpc false' to disable gRPC server (default: True)
  --grpc_port GRPC_PORT
                        By default runs gRPC server on port 9090
  --localhost, --no-localhost
                        '--no-localhost' if you need to access the server from another computer (default: True)
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

### Adding dependencies

Add any direct dependencies to `requirements.in` and run:

```bash
python -m piptools compile requirements.in --resolver=backtracking
```


### Generate gRPC code

```bash
python -m grpc_tools.protoc -I./whisper_server/proto --python_out=./whisper_server/proto --pyi_out=./whisper_server/proto --grpc_python_out=./whisper_server/proto ./whisper_server/proto/whisper_server.proto

sed -i "s/import whisper_server_pb2 as whisper__server__pb2/from whisper_server.proto import whisper_server_pb2 as whisper__server__pb2/" whisper_server/proto/whisper_server_pb2_grpc.py 
```
