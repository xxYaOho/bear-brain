from bear_brain.models import PromoteStatus


def test_promote_status_defaults_to_pending() -> None:
    status = PromoteStatus()
    assert status.state == "pending"
    assert status.promoted_to == []
