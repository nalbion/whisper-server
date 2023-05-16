@echo off
REM gRPC Server
python -m whisper_server --model base --language en --grpc_port 1634 --logging info

REM HTTP Server
REM python -m whisper_server --model base --language en --no-grpc --http --logging info
