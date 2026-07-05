from typing import Literal, Protocol

StorageBucket = Literal["uploads", "reports"]


class StorageBackend(Protocol):
    def put(self, key: str, content: bytes, *, bucket: StorageBucket = "uploads") -> None: ...

    def get(self, key: str, *, bucket: StorageBucket = "uploads") -> bytes: ...

    def delete(self, key: str, *, bucket: StorageBucket = "uploads") -> None: ...

    def exists(self, key: str, *, bucket: StorageBucket = "uploads") -> bool: ...

    def signed_url(
        self,
        key: str,
        *,
        bucket: StorageBucket = "uploads",
        expires_in: int = 3600,
    ) -> str: ...
