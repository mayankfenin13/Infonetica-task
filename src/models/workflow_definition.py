"""
Workflow Definition model for the workflow engine.

A WorkflowDefinition contains the states and actions that define a complete workflow.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from src.models.state import State
from src.models.action import Action


@dataclass
class WorkflowDefinition:
    """
    Represents a complete workflow definition with states and actions.
    
    Attributes:
        id: Unique identifier for the workflow definition
        name: Human-readable name for the workflow
        description: Optional description of the workflow's purpose
        states: Dictionary mapping state IDs to State objects
        actions: Dictionary mapping action IDs to Action objects
    """
    id: str
    name: str
    description: Optional[str] = None
    states: Dict[str, State] = field(default_factory=dict)
    actions: Dict[str, Action] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate workflow definition after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Workflow definition ID must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Workflow definition name must be a non-empty string")
    
    def add_state(self, state: State) -> None:
        """Add a state to the workflow definition."""
        if state.id in self.states:
            raise ValueError(f"State with ID '{state.id}' already exists")
        self.states[state.id] = state
    
    def add_action(self, action: Action) -> None:
        """Add an action to the workflow definition."""
        if action.id in self.actions:
            raise ValueError(f"Action with ID '{action.id}' already exists")
        self.actions[action.id] = action
    
    def get_initial_state(self) -> Optional[State]:
        """Get the initial state of the workflow."""
        initial_states = [state for state in self.states.values() if state.is_initial]
        return initial_states[0] if initial_states else None
    
    def validate(self) -> List[str]:
        """
        Validate the workflow definition and return a list of validation errors.
        
        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors = []
        
        # Check for exactly one initial state
        initial_states = [state for state in self.states.values() if state.is_initial]
        if len(initial_states) == 0:
            errors.append("Workflow must have exactly one initial state")
        elif len(initial_states) > 1:
            errors.append("Workflow must have exactly one initial state, found multiple")
        
        # Check for duplicate state IDs (already handled in add_state, but double-check)
        state_ids = [state.id for state in self.states.values()]
        if len(state_ids) != len(set(state_ids)):
            errors.append("Duplicate state IDs found")
        
        # Check for duplicate action IDs (already handled in add_action, but double-check)
        action_ids = [action.id for action in self.actions.values()]
        if len(action_ids) != len(set(action_ids)):
            errors.append("Duplicate action IDs found")
        
        # Validate that all action from_states and to_state reference existing states
        for action in self.actions.values():
            for from_state_id in action.from_states:
                if from_state_id not in self.states:
                    errors.append(f"Action '{action.id}' references non-existent from_state '{from_state_id}'")
            
            if action.to_state not in self.states:
                errors.append(f"Action '{action.id}' references non-existent to_state '{action.to_state}'")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if the workflow definition is valid."""
        return len(self.validate()) == 0
    
    def to_dict(self) -> dict:
        """Convert workflow definition to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'states': {state_id: state.to_dict() for state_id, state in self.states.items()},
            'actions': {action_id: action.to_dict() for action_id, action in self.actions.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkflowDefinition':
        """Create WorkflowDefinition instance from dictionary."""
        definition = cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description')
        )
        
        # Add states
        for state_data in data.get('states', {}).values():
            state = State.from_dict(state_data)
            definition.add_state(state)
        
        # Add actions
        for action_data in data.get('actions', {}).values():
            action = Action.from_dict(action_data)
            definition.add_action(action)
        
        return definition

