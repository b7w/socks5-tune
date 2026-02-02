from typing import Any, Type, TypeVar

import msgspec

T = TypeVar('T')


class JsonMapper:

    def __init__(self):
        self.encoder = msgspec.json.Encoder()
        self.decoder = msgspec.json.Decoder()

    def serialize(self, value: Any) -> bytes:
        if hasattr(value, 'to_dict'):
            return self.encoder.encode(value.to_dict())
        return self.encoder.encode(value)

    def deserialize(self, value: str, type: Type[T] = None) -> T:
        if type:
            return msgspec.json.decode(value, type=type)
        return self.decoder.decode(value)
