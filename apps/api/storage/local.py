from pathlib import Path

from storage.backend import StorageBucket


class LocalStorageBackend:
    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)

    def _resolve(self, key: str, bucket: StorageBucket) -> Path:
        if bucket == "reports":
            return self._base_dir / "reports" / key.removeprefix("reports/")
        normalized = key.removeprefix("uploads/")
        return self._base_dir / normalized

    def put(self, key: str, content: bytes, *, bucket: StorageBucket = "uploads") -> None:
        path = self._resolve(key, bucket)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def get(self, key: str, *, bucket: StorageBucket = "uploads") -> bytes:
        path = self._resolve(key, bucket)
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    def delete(self, key: str, *, bucket: StorageBucket = "uploads") -> None:
        path = self._resolve(key, bucket)
        if path.exists():
            path.unlink()

    def exists(self, key: str, *, bucket: StorageBucket = "uploads") -> bool:
        return self._resolve(key, bucket).exists()

    def signed_url(
        self,
        key: str,
        *,
        bucket: StorageBucket = "uploads",
        expires_in: int = 3600,
    ) -> str:
        return str(self._resolve(key, bucket).resolve())
