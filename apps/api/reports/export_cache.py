"""Report export caching in object storage."""

from fastapi.responses import Response

from storage.factory import get_storage, report_export_key


def serve_cached_export(
    report_id: str,
    filename: str,
    content_type: str,
    content: bytes,
) -> Response:
    # Content is always streamed through the API rather than issuing a 302
    # redirect to a storage presigned URL. The frontend downloads exports via
    # fetch() + Blob, and cross-origin presigned URLs (e.g. R2) do not send the
    # CORS headers the browser requires to read the response body, which breaks
    # downloads in production. Reports are small, so proxying is inexpensive.
    storage = get_storage()
    key = report_export_key(report_id, filename)

    if storage.exists(key, bucket="reports"):
        content = storage.get(key, bucket="reports")
    else:
        storage.put(key, content, bucket="reports")

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
