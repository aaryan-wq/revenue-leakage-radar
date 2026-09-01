from decimal import Decimal
from unittest.mock import MagicMock

from estimator.headline import estimator_headline_from_model_run, estimator_headline_from_result
from admin.service import _assessment_estimate


def test_estimator_headline_from_result_uses_high_not_central():
    payload = {"estimate": {"central": 100000, "high": 250000, "low": 50000}}
    assert estimator_headline_from_result(payload) == 250000.0


def test_estimator_headline_from_result_returns_none_without_high():
    assert estimator_headline_from_result(None) is None
    assert estimator_headline_from_result({"estimate": {"central": 100}}) is None


def test_estimator_headline_from_model_run_prefers_scenario_percentile():
    aggressive = MagicMock(scenario="aggressive", p90=Decimal("200000"), p75=Decimal("150000"), central_estimate=Decimal("100000"))
    central = MagicMock(scenario="central", p90=Decimal("200000"), p75=Decimal("150000"), central_estimate=Decimal("100000"))
    conservative = MagicMock(scenario="conservative", p90=Decimal("200000"), p50=Decimal("120000"), central_estimate=Decimal("100000"))

    assert estimator_headline_from_model_run(aggressive) == Decimal("200000")
    assert estimator_headline_from_model_run(central) == Decimal("150000")
    assert estimator_headline_from_model_run(conservative) == Decimal("120000")


def test_assessment_estimate_matches_user_headline():
    result = MagicMock()
    result.result_json = {"estimate": {"central": 100000, "high": 250000}}

    assert _assessment_estimate(result, []) == "250000.0"
