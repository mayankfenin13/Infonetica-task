"""
Action model for the workflow engine.

An Action represents a transition between states in the workflow state machine.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Action:
    """
    Represents an action (transition) in a workflow definition.
    
    Attributes:
        id: Unique identifier for the action
        name: Human-readable name for the action
        enabled: Whether this action can be executed
        from_states: List of state IDs from which this action can be triggered
        to_state: Target state ID where this action leads
        description: Optional description of the action's purpose
    """
    id: str
    name: str
    enabled: bool = True
    from_states: List[str] = None
    to_state: str = ""
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate action attributes after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Action ID must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Action name must be a non-empty string")
        if not self.to_state or not isinstance(self.to_state, str):
            raise ValueError("Action must have a valid target state")
        if self.from_states is None:
            self.from_states = []
        if not isinstance(self.from_states, list):
            raise ValueError("from_states must be a list")
    
    def can_execute_from_state(self, state_id: str) -> bool:
        """Check if this action can be executed from the given state."""
        return state_id in self.from_states
    
    def to_dict(self) -> dict:
        """Convert action to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'enabled': self.enabled,
            'from_states': self.from_states,
            'to_state': self.to_state,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Action':
        """Create Action instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            enabled=data.get('enabled', True),
            from_states=data.get('from_states', []),
            to_state=data['to_state'],
            description=data.get('description')
        )

