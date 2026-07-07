from types import SimpleNamespace

from reports.summary import audit_has_free_summary


def test_audit_has_free_summary_when_completed():
    audit = SimpleNamespace(status="completed", scan_report=None)
    report = SimpleNamespace()
    assert audit_has_free_summary(audit, report) is True


def test_audit_has_free_summary_when_scan_report_present():
    audit = SimpleNamespace(status="normalizing", scan_report={"rules_total": 26})
    report = SimpleNamespace()
    assert audit_has_free_summary(audit, report) is True


def test_audit_has_free_summary_false_without_report():
    audit = SimpleNamespace(status="normalizing", scan_report=None)
    assert audit_has_free_summary(audit, None) is False
