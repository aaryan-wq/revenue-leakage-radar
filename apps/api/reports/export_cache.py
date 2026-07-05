"""Report export caching in object storage."""

from fastapi.responses import RedirectResponse, Response

from core.config import settings
from storage.factory import get_storage, report_export_key


def serve_cached_export(
    report_id: str,
    filename: str,
    content_type: str,
    content: bytes,
    *,
    redirect_when_cached: bool = True,
) -> Response:
    storage = get_storage()
    key = report_export_key(report_id, filename)

    if storage.exists(key, bucket="reports"):
        if redirect_when_cached and settings.storage_backend == "r2":
            url = storage.signed_url(key, bucket="reports", expires_in=3600)
            return RedirectResponse(url=url, status_code=302)
        cached = storage.get(key, bucket="reports")
        return Response(
            content=cached,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    storage.put(key, content, bucket="reports")

    if redirect_when_cached and settings.storage_backend == "r2":
        url = storage.signed_url(key, bucket="reports", expires_in=3600)
        return RedirectResponse(url=url, status_code=302)

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
