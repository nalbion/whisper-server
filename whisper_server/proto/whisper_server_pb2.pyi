from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
cpu: ProcessingDevice
gpu: ProcessingDevice

class AudioInputDeviceSelection(_message.Message):
    __slots__ = ["deviceName"]
    DEVICENAME_FIELD_NUMBER: _ClassVar[int]
    deviceName: str
    def __init__(self, deviceName: _Optional[str] = ...) -> None: ...

class DecodingOptions(_message.Message):
    __slots__ = ["beam_size", "best_of", "fp16", "language", "length_penalty", "max_initial_timestamp", "patience", "prefix", "prompt", "sample_len", "suppress_blank", "suppress_tokens", "task", "temperature", "without_timestamps"]
    BEAM_SIZE_FIELD_NUMBER: _ClassVar[int]
    BEST_OF_FIELD_NUMBER: _ClassVar[int]
    FP16_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_PENALTY_FIELD_NUMBER: _ClassVar[int]
    MAX_INITIAL_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PATIENCE_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_LEN_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_BLANK_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    WITHOUT_TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    beam_size: int
    best_of: int
    fp16: bool
    language: str
    length_penalty: float
    max_initial_timestamp: float
    patience: float
    prefix: str
    prompt: str
    sample_len: int
    suppress_blank: bool
    suppress_tokens: str
    task: str
    temperature: float
    without_timestamps: bool
    def __init__(self, task: _Optional[str] = ..., language: _Optional[str] = ..., temperature: _Optional[float] = ..., sample_len: _Optional[int] = ..., best_of: _Optional[int] = ..., beam_size: _Optional[int] = ..., patience: _Optional[float] = ..., length_penalty: _Optional[float] = ..., prompt: _Optional[str] = ..., prefix: _Optional[str] = ..., suppress_tokens: _Optional[str] = ..., suppress_blank: bool = ..., without_timestamps: bool = ..., max_initial_timestamp: _Optional[float] = ..., fp16: bool = ...) -> None: ...

class EmptyRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class EmptyResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class LoadModelRequest(_message.Message):
    __slots__ = ["device", "download_root", "in_memory", "language", "name"]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_ROOT_FIELD_NUMBER: _ClassVar[int]
    IN_MEMORY_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    device: ProcessingDevice
    download_root: str
    in_memory: bool
    language: str
    name: str
    def __init__(self, name: _Optional[str] = ..., language: _Optional[str] = ..., device: _Optional[_Union[ProcessingDevice, str]] = ..., download_root: _Optional[str] = ..., in_memory: bool = ...) -> None: ...

class Prefix(_message.Message):
    __slots__ = ["text", "tokens"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    text: str
    tokens: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, text: _Optional[str] = ..., tokens: _Optional[_Iterable[int]] = ...) -> None: ...

class Prompt(_message.Message):
    __slots__ = ["text", "tokens"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    text: str
    tokens: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, text: _Optional[str] = ..., tokens: _Optional[_Iterable[int]] = ...) -> None: ...

class WhisperSimpleOutput(_message.Message):
    __slots__ = ["alternatives"]
    ALTERNATIVES_FIELD_NUMBER: _ClassVar[int]
    alternatives: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, alternatives: _Optional[_Iterable[str]] = ...) -> None: ...

class ProcessingDevice(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
