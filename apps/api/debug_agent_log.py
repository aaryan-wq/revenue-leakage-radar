import json
import time
from pathlib import Path
from typing import Any

_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-ede7cb.log"
_SESSION_ID = "ede7cb"


def agent_log(
    hypothesis_id: str,
    location: str,
    message: str,
    data: dict[str, Any] | None = None,
    run_id: str = "pre-fix",
) -> None:
    # region agent log
    try:
        payload = {
            "sessionId": _SESSION_ID,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
            "runId": run_id,
        }
        with _LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload) + "\n")
    except OSError:
        pass
    # endregion
