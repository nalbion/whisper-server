@echo off
REM gRPC Server
python -m whisper_server --model base --language en --grpc_port 1634 --logging info

REM on Docker
REM wsl docker run --rm -e "PULSE_SERVER=/mnt/wslg/PulseServer" -v /mnt/wslg/:/mnt/wslg/ nalbion/whisper_server
REM wsl docker run --rm -it --entrypoint /bin/bash -e "PULSE_SERVER=/mnt/wslg/PulseServer" -v /mnt/wslg/:/mnt/wslg/ nalbion/whisper_server

REM HTTP Server
REM python -m whisper_server --model base --language en --no-grpc --http --logging info
