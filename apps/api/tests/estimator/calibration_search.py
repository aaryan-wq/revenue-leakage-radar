"""Targeted calibration search (smaller grid)."""

from __future__ import annotations

from tests.estimator.calibration_fixtures import CALIBRATION_CASES
from tests.estimator.calibration_sim import simulate


def score(**kwargs) -> float:
    return sum(
        abs((simulate(c["answers"], **kwargs) - c["justified_leakage_usd"]) / c["justified_leakage_usd"] * 100)
        for c in CALIBRATION_CASES
    ) / len(CALIBRATION_CASES)


def main() -> None:
    best = (999.0, {})
    for affected in [(2, 10), (3, 12), (3, 10), (4, 14)]:
        for div in [12.0, 10.0, 8.0]:
            for scale in [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]:
                cfg = {
                    "affected": affected,
                    "persistence_divisor": div,
                    "leakage_scale": scale,
                    "use_posterior_gate": True,
                }
                err = score(**cfg)
                if err < best[0]:
                    best = (err, cfg)

    print(f"Best mean abs error: {best[0]:.1f}%")
    print(f"Config: {best[1]}")
    for case in CALIBRATION_CASES:
        model = simulate(case["answers"], **best[1])
        just = case["justified_leakage_usd"]
        err = (model - just) / just * 100
        print(f"  {case['name']:<18} {model:>10,.0f} vs {just:>10,} ({err:+.1f}%)")


if __name__ == "__main__":
    main()
