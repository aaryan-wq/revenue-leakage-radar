from tests.estimator.calibration_fixtures import CALIBRATION_CASES
from tests.estimator.calibration_sim import simulate
from estimator.modeling.complexity import compute_complexity
from estimator.modeling.normalize import normalize_answers


def main() -> None:
    best = (999.0, {})
    for affected in [(2, 10), (3, 12), (2, 8)]:
        for base in [1.85, 1.95, 2.05, 2.15, 2.25]:
            for exp in [0.30, 0.33, 0.36, 0.39, 0.42]:
                errs = []
                for case in CALIBRATION_CASES:
                    cx = compute_complexity(normalize_answers(case["answers"]))["total"]
                    scale = base * (max(cx, 1) ** -exp)
                    model = simulate(
                        case["answers"],
                        affected=affected,
                        persistence_divisor=12.0,
                        leakage_scale=scale,
                    )
                    just = case["justified_leakage_usd"]
                    errs.append(abs((model - just) / just * 100))
                mean_err = sum(errs) / len(errs)
                if mean_err < best[0]:
                    best = (mean_err, {"affected": affected, "base": base, "exp": exp})

    print("Best", best)
    cfg = best[1]
    for case in CALIBRATION_CASES:
        cx = compute_complexity(normalize_answers(case["answers"]))["total"]
        scale = cfg["base"] * (max(cx, 1) ** -cfg["exp"])
        model = simulate(
            case["answers"],
            affected=cfg["affected"],
            persistence_divisor=12.0,
            leakage_scale=scale,
        )
        just = case["justified_leakage_usd"]
        err = (model - just) / just * 100
        print(f"  {case['name']:<18} scale={scale:.2f} err={err:+.1f}%")


if __name__ == "__main__":
    main()
