from pathlib import Path
import os

_BUNDLED_SCHEMA_ROOT = Path(__file__).resolve().parent / "schema"


def _monorepo_schema_root() -> Path | None:
    parents = Path(__file__).resolve().parents
    if len(parents) <= 3:
        return None
    root = parents[3] / "packages" / "estimator-schema"
    return root if root.exists() else None


def _resolve_schema_root() -> Path:
    env_root = os.getenv("ESTIMATOR_SCHEMA_ROOT")
    if env_root:
        return Path(env_root)
    if _BUNDLED_SCHEMA_ROOT.exists():
        return _BUNDLED_SCHEMA_ROOT
    monorepo_root = _monorepo_schema_root()
    if monorepo_root is not None:
        return monorepo_root
    raise RuntimeError(
        "Estimator schema files not found. Expected bundled schema at "
        f"{_BUNDLED_SCHEMA_ROOT} or monorepo schema under packages/estimator-schema."
    )


SCHEMA_ROOT = _resolve_schema_root()
QUESTIONNAIRE_VERSION = "2.0"
MODEL_VERSION = "1.0.0"
