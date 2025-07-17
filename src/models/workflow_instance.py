"""
Workflow Instance model for the workflow engine.

A WorkflowInstance represents a running instance of a workflow definition.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.models.workflow_definition import WorkflowDefinition


@dataclass
class HistoryEntry:
    """
    Represents a single entry in the workflow instance history.
    
    Attributes:
        action_id: ID of the action that was executed
        timestamp: When the action was executed
        from_state_id: State ID before the action
        to_state_id: State ID after the action
    """
    action_id: str
    timestamp: datetime
    from_state_id: str
    to_state_id: str
    
    def to_dict(self) -> dict:
        """Convert history entry to dictionary representation."""
        return {
            'action_id': self.action_id,
            'timestamp': self.timestamp.isoformat(),
            'from_state_id': self.from_state_id,
            'to_state_id': self.to_state_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryEntry':
        """Create HistoryEntry instance from dictionary."""
        return cls(
            action_id=data['action_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            from_state_id=data['from_state_id'],
            to_state_id=data['to_state_id']
        )


@dataclass
class WorkflowInstance:
    """
    Represents a running instance of a workflow definition.
    
    Attributes:
        id: Unique identifier for the workflow instance
        definition_id: ID of the workflow definition this instance is based on
        current_state_id: ID of the current state
        history: List of executed actions with timestamps
        created_at: When the instance was created
        definition: Reference to the workflow definition (not persisted)
    """
    id: str
    definition_id: str
    current_state_id: str
    history: List[HistoryEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    definition: Optional[WorkflowDefinition] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Validate workflow instance after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Workflow instance ID must be a non-empty string")
        if not self.definition_id or not isinstance(self.definition_id, str):
            raise ValueError("Workflow instance must reference a valid definition ID")
        if not self.current_state_id or not isinstance(self.current_state_id, str):
            raise ValueError("Workflow instance must have a valid current state ID")
    
    def can_execute_action(self, action_id: str) -> tuple[bool, str]:
        """
        Check if an action can be executed in the current state.
        
        Returns:
            Tuple of (can_execute: bool, reason: str)
        """
        if not self.definition:
            return False, "Workflow definition not loaded"
        
        # Check if action exists
        if action_id not in self.definition.actions:
            return False, f"Action '{action_id}' does not exist in workflow definition"
        
        action = self.definition.actions[action_id]
        
        # Check if action is enabled
        if not action.enabled:
            return False, f"Action '{action_id}' is disabled"
        
        # Check if current state is final
        current_state = self.definition.states.get(self.current_state_id)
        if current_state and current_state.is_final:
            return False, f"Cannot execute actions from final state '{self.current_state_id}'"
        
        # Check if action can be executed from current state
        if not action.can_execute_from_state(self.current_state_id):
            return False, f"Action '{action_id}' cannot be executed from state '{self.current_state_id}'"
        
        # Check if target state exists
        if action.to_state not in self.definition.states:
            return False, f"Action '{action_id}' targets non-existent state '{action.to_state}'"
        
        return True, "Action can be executed"
    
    def execute_action(self, action_id: str) -> tuple[bool, str]:
        """
        Execute an action and update the instance state.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        can_execute, reason = self.can_execute_action(action_id)
        if not can_execute:
            return False, reason
        
        action = self.definition.actions[action_id]
        old_state_id = self.current_state_id
        
        # Update current state
        self.current_state_id = action.to_state
        
        # Add to history
        history_entry = HistoryEntry(
            action_id=action_id,
            timestamp=datetime.now(),
            from_state_id=old_state_id,
            to_state_id=action.to_state
        )
        self.history.append(history_entry)
        
        return True, f"Action '{action_id}' executed successfully"
    
    def get_current_state(self):
        """Get the current state object."""
        if self.definition and self.current_state_id in self.definition.states:
            return self.definition.states[self.current_state_id]
        return None
    
    def is_in_final_state(self) -> bool:
        """Check if the instance is in a final state."""
        current_state = self.get_current_state()
        return current_state.is_final if current_state else False
    
    def to_dict(self) -> dict:
        """Convert workflow instance to dictionary representation."""
        return {
            'id': self.id,
            'definition_id': self.definition_id,
            'current_state_id': self.current_state_id,
            'history': [entry.to_dict() for entry in self.history],
            'created_at': self.created_at.isoformat(),
            'is_final': self.is_in_final_state()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkflowInstance':
        """Create WorkflowInstance instance from dictionary."""
        instance = cls(
            id=data['id'],
            definition_id=data['definition_id'],
            current_state_id=data['current_state_id'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
        
        # Add history entries
        for entry_data in data.get('history', []):
            entry = HistoryEntry.from_dict(entry_data)
            instance.history.append(entry)
        
        return instance

