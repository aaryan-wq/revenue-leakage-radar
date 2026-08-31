from typing import Any

from estimator.questionnaire.schema import load_questionnaire


def _normalize_answer_value(answer: dict[str, Any]) -> Any:
    if answer.get("value_boolean") is not None:
        return answer["value_boolean"]
    if answer.get("value_enum") is not None:
        return answer["value_enum"]
    if answer.get("value_numeric") is not None:
        return float(answer["value_numeric"])
    if answer.get("value_json") is not None:
        return answer["value_json"]
    if answer.get("value_text") is not None:
        return answer["value_text"]
    return None


def answers_to_map(raw_answers: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in raw_answers:
        result[row["question_id"]] = _normalize_answer_value(row)
        if row.get("value_text") and row["question_id"] == "profile.arr_amount":
            result["profile.arr_currency"] = row["value_text"]
    return result


def _branch_unlocked(question: dict[str, Any], answers: dict[str, Any]) -> list[str]:
    branches = question.get("branches") or {}
    value = answers.get(question["id"])
    if value is True and "true" in branches:
        return list(branches["true"])
    if value is False and "false" in branches:
        return list(branches["false"])
    if isinstance(value, str) and value in branches:
        return list(branches[value])
    return []


def _visibility_met(question: dict[str, Any], answers: dict[str, Any]) -> bool:
    visibility = question.get("visibility")
    if not visibility:
        return True
    ref = visibility.get("when")
    actual = answers.get(ref)
    if "contains" in visibility:
        needle = visibility["contains"]
        if isinstance(actual, list):
            return needle in actual
        return False
    if "not_equals" in visibility:
        return actual != visibility["not_equals"]
    expected = visibility.get("equals")
    return actual == expected


def is_question_visible(question_id: str, answers: dict[str, Any], version: str = "2.0") -> bool:
    from estimator.questionnaire.schema import get_question_by_id

    question = get_question_by_id(question_id, version)
    if question is None:
        return False
    return _visibility_met(question, answers)


def visible_question_ids(answers: dict[str, Any], version: str = "2.0") -> list[str]:
    questionnaire = load_questionnaire(version)
    visible: set[str] = set()
    pending = [q["id"] for q in questionnaire["questions"]]

    for question in questionnaire["questions"]:
        qid = question["id"]
        if not _visibility_met(question, answers):
            continue
        visible.add(qid)
        for unlocked in _branch_unlocked(question, answers):
            visible.add(unlocked)

    ordered = [q["id"] for q in questionnaire["questions"] if q["id"] in visible]
    return ordered


def answered_question_ids(answers: dict[str, Any], version: str = "2.0") -> list[str]:
    visible = visible_question_ids(answers, version)
    return [qid for qid in visible if qid in answers and answers[qid] is not None]


def pending_question_ids(answers: dict[str, Any], version: str = "2.0") -> list[str]:
    visible = visible_question_ids(answers, version)
    return [qid for qid in visible if qid not in answers or answers[qid] is None]


def next_unanswered_question(answers: dict[str, Any], version: str = "2.0") -> dict[str, Any] | None:
    from estimator.questionnaire.schema import get_question_by_id

    for question_id in visible_question_ids(answers, version):
        if question_id not in answers or answers[question_id] is None:
            question = get_question_by_id(question_id, version)
            if question:
                return question
    return None


def completion_progress(answers: dict[str, Any], version: str = "2.0") -> dict[str, Any]:
    visible = visible_question_ids(answers, version)
    answered = [qid for qid in visible if qid in answers and answers[qid] is not None]
    remaining_seconds = 0
    questionnaire = load_questionnaire(version)
    section_seconds = {s["id"]: s["estimated_seconds"] for s in questionnaire["sections"]}
    for question in questionnaire["questions"]:
        if question["id"] in visible and question["id"] not in answered:
            remaining_seconds += section_seconds.get(question["section"], 10)

    return {
        "visible_count": len(visible),
        "answered_count": len(answered),
        "completion_rate": len(answered) / len(visible) if visible else 0,
        "estimated_seconds_remaining": max(remaining_seconds, 15),
        "is_complete": len(answered) == len(visible) and len(visible) > 0,
    }


def current_section(answers: dict[str, Any], version: str = "2.0") -> str | None:
    next_q = next_unanswered_question(answers, version)
    if next_q:
        return next_q["section"]
    visible = visible_question_ids(answers, version)
    if not visible:
        return None
    from estimator.questionnaire.schema import get_question_by_id

    last = get_question_by_id(visible[-1], version)
    return last["section"] if last else None
