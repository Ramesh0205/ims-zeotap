from abc import ABC, abstractmethod
from fastapi import HTTPException

class IncidentState(ABC):
    @abstractmethod
    def next_state(self) -> str:
        pass

    @abstractmethod
    def can_close(self) -> bool:
        pass

class OpenState(IncidentState):
    def next_state(self) -> str:
        return "INVESTIGATING"

    def can_close(self) -> bool:
        return False

class InvestigatingState(IncidentState):
    def next_state(self) -> str:
        return "RESOLVED"

    def can_close(self) -> bool:
        return False

class ResolvedState(IncidentState):
    def next_state(self) -> str:
        return "CLOSED"

    def can_close(self) -> bool:
        return True

class ClosedState(IncidentState):
    def next_state(self) -> str:
        raise HTTPException(status_code=400, detail="Incident is already CLOSED.")

    def can_close(self) -> bool:
        return True

STATE_MAP = {
    "OPEN": OpenState(),
    "INVESTIGATING": InvestigatingState(),
    "RESOLVED": ResolvedState(),
    "CLOSED": ClosedState(),
}

def get_state(status: str) -> IncidentState:
    return STATE_MAP.get(status, OpenState())

def transition_state(current_status: str) -> str:
    state = get_state(current_status)
    return state.next_state()
