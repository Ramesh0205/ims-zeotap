from abc import ABC, abstractmethod
from app.models.sql_models import Priority

class AlertStrategy(ABC):
    @abstractmethod
    def get_priority(self) -> Priority:
        pass

    @abstractmethod
    def get_title(self, component_id: str) -> str:
        pass

class RDBMSAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P0

    def get_title(self, component_id: str) -> str:
        return f"🔴 P0 CRITICAL: Database failure detected on {component_id}"

class CacheAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P2

    def get_title(self, component_id: str) -> str:
        return f"🟡 P2 WARNING: Cache cluster issue on {component_id}"

class APIAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P1

    def get_title(self, component_id: str) -> str:
        return f"🟠 P1 HIGH: API failure on {component_id}"

class QueueAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P1

    def get_title(self, component_id: str) -> str:
        return f"🟠 P1 HIGH: Async queue failure on {component_id}"

class NoSQLAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P2

    def get_title(self, component_id: str) -> str:
        return f"🟡 P2 WARNING: NoSQL store issue on {component_id}"

class MCPAlertStrategy(AlertStrategy):
    def get_priority(self) -> Priority:
        return Priority.P1

    def get_title(self, component_id: str) -> str:
        return f"🟠 P1 HIGH: MCP Host failure on {component_id}"

STRATEGY_MAP = {
    "RDBMS": RDBMSAlertStrategy(),
    "CACHE": CacheAlertStrategy(),
    "API": APIAlertStrategy(),
    "QUEUE": QueueAlertStrategy(),
    "NOSQL": NoSQLAlertStrategy(),
    "MCP": MCPAlertStrategy(),
}

def get_alert_strategy(component_type: str) -> AlertStrategy:
    return STRATEGY_MAP.get(component_type, APIAlertStrategy())
