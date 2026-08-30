from estimator.questionnaire.engine import (
    answered_question_ids,
    completion_progress,
    pending_question_ids,
    visible_question_ids,
)


def test_pending_and_answered_question_ids():
    answers = {
        "profile.company_type": "b2b_saas",
        "profile.arr_amount": 5_000_000,
        "profile.arr_currency": "USD",
        "profile.customer_count": 120,
    }
    visible = visible_question_ids(answers, "2.0")
    pending = pending_question_ids(answers, "2.0")
    answered = answered_question_ids(answers, "2.0")

    assert len(visible) > len(answered)
    assert len(pending) == len(visible) - len(answered)
    assert all(qid in visible for qid in pending)
    assert all(qid in visible for qid in answered)
    assert not any(qid in answered for qid in pending)


def test_completion_false_when_pending_remain():
    answers = {
        "profile.company_type": "b2b_saas",
        "profile.arr_amount": 5_000_000,
        "profile.arr_currency": "USD",
        "profile.customer_count": 120,
    }
    progress = completion_progress(answers, "2.0")
    pending = pending_question_ids(answers, "2.0")

    assert progress["is_complete"] is False
    assert progress["answered_count"] == len(answered_question_ids(answers, "2.0"))
    assert len(pending) > 0
