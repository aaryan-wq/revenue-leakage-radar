from unittest.mock import patch

from notifications.templates import estimator_summary_email


@patch("notifications.templates.send_email", return_value=True)
def test_estimator_summary_email_includes_estimate_and_links(mock_send):
    sent = estimator_summary_email(
        to="cfo@example.com",
        estimate_high=170_000,
        arr_usd=12_000_000,
        top_mechanisms=[
            {"name": "Contract Configuration", "amount": 15_000},
            {"name": "Enterprise Scaling", "amount": 10_000},
        ],
        result_url="https://paevo.co/saas-revenue-leakage-calculator/result/abc",
        share_url="https://paevo.co/saas-revenue-leakage-calculator/share/token",
        scan_url="https://paevo.co/upload?assessment_id=abc",
    )

    assert sent is True
    mock_send.assert_called_once()
    kwargs = mock_send.call_args.kwargs
    assert kwargs["to"] == "cfo@example.com"
    assert "~$170k/year" in kwargs["subject"]
    assert "Contract Configuration" in kwargs["text"]
    assert "https://paevo.co/upload?assessment_id=abc" in kwargs["text"]
