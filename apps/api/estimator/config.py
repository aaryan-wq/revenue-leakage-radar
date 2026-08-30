from pathlib import Path
import os

_BUNDLED_SCHEMA_ROOT = Path(__file__).resolve().parent / "schema"
_MONOREPO_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "packages" / "estimator-schema"


def _resolve_schema_root() -> Path:
    env_root = os.getenv("ESTIMATOR_SCHEMA_ROOT")
    if env_root:
        return Path(env_root)
    if _BUNDLED_SCHEMA_ROOT.exists():
        return _BUNDLED_SCHEMA_ROOT
    if _MONOREPO_SCHEMA_ROOT.exists():
        return _MONOREPO_SCHEMA_ROOT
    raise RuntimeError(
        "Estimator schema files not found. Expected bundled schema at "
        f"{_BUNDLED_SCHEMA_ROOT} or monorepo schema at {_MONOREPO_SCHEMA_ROOT}."
    )


SCHEMA_ROOT = _resolve_schema_root()
QUESTIONNAIRE_VERSION = "2.0"
MODEL_VERSION = "1.0.0"
