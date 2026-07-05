import logging

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from storage.backend import StorageBucket

logger = logging.getLogger(__name__)


class R2StorageBackend:
    def __init__(
        self,
        *,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        endpoint: str,
        bucket_uploads: str,
        bucket_reports: str,
    ) -> None:
        self._bucket_uploads = bucket_uploads
        self._bucket_reports = bucket_reports
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )
        self._account_id = account_id

    def _bucket_name(self, bucket: StorageBucket) -> str:
        return self._bucket_uploads if bucket == "uploads" else self._bucket_reports

    def put(self, key: str, content: bytes, *, bucket: StorageBucket = "uploads") -> None:
        self._client.put_object(
            Bucket=self._bucket_name(bucket),
            Key=key,
            Body=content,
        )

    def get(self, key: str, *, bucket: StorageBucket = "uploads") -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket_name(bucket), Key=key)
            return response["Body"].read()
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "NoSuchKey":
                raise FileNotFoundError(key) from exc
            raise

    def delete(self, key: str, *, bucket: StorageBucket = "uploads") -> None:
        try:
            self._client.delete_object(Bucket=self._bucket_name(bucket), Key=key)
        except ClientError:
            logger.exception("Failed to delete R2 object %s", key)

    def exists(self, key: str, *, bucket: StorageBucket = "uploads") -> bool:
        try:
            self._client.head_object(Bucket=self._bucket_name(bucket), Key=key)
            return True
        except ClientError:
            return False

    def signed_url(
        self,
        key: str,
        *,
        bucket: StorageBucket = "uploads",
        expires_in: int = 3600,
    ) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name(bucket), "Key": key},
            ExpiresIn=expires_in,
        )
