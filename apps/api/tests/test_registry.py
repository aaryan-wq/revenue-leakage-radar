from verification.registry import get_all_rules


def test_registry_has_twenty_six_rules():
    rules = get_all_rules()
    assert len(rules) == 26


def test_registry_rule_ids_unique():
    rules = get_all_rules()
    ids = [r.rule_id for r in rules]
    assert len(ids) == len(set(ids))


def test_all_rules_have_evaluators():
    rules = get_all_rules()
    for rule in rules:
        assert rule.evaluate is not None, f"Missing evaluator for {rule.rule_id}"


def test_all_rules_declare_entities():
    rules = get_all_rules()
    for rule in rules:
        assert len(rule.required_entities) > 0, f"Missing required_entities for {rule.rule_id}"
        assert isinstance(rule.optimal_entities, frozenset), f"Invalid optimal_entities for {rule.rule_id}"
