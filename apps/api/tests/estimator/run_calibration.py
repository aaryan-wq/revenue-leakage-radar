"""Run calibration cases against justified leakage targets."""

from __future__ import annotations

from estimator.modeling.pipeline import run_model
from tests.estimator.calibration_fixtures import CALIBRATION_CASES


def main() -> None:
    print(f"{'Case':<20} {'ARR':>10} {'Justified':>10} {'Model':>10} {'Err%':>8}")
    print("-" * 62)
    errors: list[float] = []
    for case in CALIBRATION_CASES:
        result = run_model(case["answers"], random_seed=42)
        model = result["estimate"]["central"]
        justified = case["justified_leakage_usd"]
        err_pct = (model - justified) / justified * 100
        errors.append(abs(err_pct))
        arr = case["answers"]["profile.arr_amount"]
        print(
            f"{case['name']:<20} {arr:>10,} {justified:>10,} {model:>10,} {err_pct:>+7.1f}%"
        )
        print(f"  Rationale: {case['rationale']}")
    print("-" * 62)
    print(f"Mean absolute error: {sum(errors)/len(errors):.1f}%")


if __name__ == "__main__":
    main()
