import pytest
from fastapi.testclient import TestClient

def test_rca_validation_fix_applied_too_short():
    from pydantic import ValidationError
    from app.models.schemas import RCACreate
    from datetime import datetime
    with pytest.raises(ValidationError):
        RCACreate(
            incident_start=datetime.utcnow(),
            incident_end=datetime.utcnow(),
            root_cause_category="DB_FAILURE",
            fix_applied="short",
            prevention_steps="short"
        )

def test_rca_validation_success():
    from app.models.schemas import RCACreate
    from datetime import datetime
    rca = RCACreate(
        incident_start=datetime.utcnow(),
        incident_end=datetime.utcnow(),
        root_cause_category="DB_FAILURE",
        fix_applied="We restarted the primary database and promoted the replica.",
        prevention_steps="We will add automated failover and health checks every 30 seconds."
    )
    assert rca.root_cause_category == "DB_FAILURE"

def test_state_transition_open_to_investigating():
    from app.services.state_machine import transition_state
    assert transition_state("OPEN") == "INVESTIGATING"

def test_state_transition_investigating_to_resolved():
    from app.services.state_machine import transition_state
    assert transition_state("INVESTIGATING") == "RESOLVED"

def test_state_transition_resolved_to_closed():
    from app.services.state_machine import transition_state
    assert transition_state("RESOLVED") == "CLOSED"

def test_alert_strategy_rdbms_is_p0():
    from app.services.alert_strategy import get_alert_strategy
    strategy = get_alert_strategy("RDBMS")
    assert strategy.get_priority() == "P0"

def test_alert_strategy_cache_is_p2():
    from app.services.alert_strategy import get_alert_strategy
    strategy = get_alert_strategy("CACHE")
    assert strategy.get_priority() == "P2"
