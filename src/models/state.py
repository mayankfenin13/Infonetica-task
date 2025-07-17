"""
State model for the workflow engine.

A State represents a node in the workflow state machine.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class State:
    """
    Represents a state in a workflow definition.
    
    Attributes:
        id: Unique identifier for the state
        name: Human-readable name for the state
        is_initial: Whether this is the starting state of the workflow
        is_final: Whether this is a terminal state of the workflow
        enabled: Whether this state is currently active/usable
        description: Optional description of the state's purpose
    """
    id: str
    name: str
    is_initial: bool = False
    is_final: bool = False
    enabled: bool = True
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate state attributes after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("State ID must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("State name must be a non-empty string")
    
    def to_dict(self) -> dict:
        """Convert state to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'is_initial': self.is_initial,
            'is_final': self.is_final,
            'enabled': self.enabled,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'State':
        """Create State instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            is_initial=data.get('is_initial', False),
            is_final=data.get('is_final', False),
            enabled=data.get('enabled', True),
            description=data.get('description')
        )

