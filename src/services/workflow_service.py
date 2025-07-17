"""
Workflow Service for managing workflow definitions and instances.

This service provides the core business logic for the workflow engine.
"""

import uuid
from typing import Dict, List, Optional, Tuple
from src.models import State, Action, WorkflowDefinition, WorkflowInstance


class WorkflowService:
    """
    Service class for managing workflow definitions and instances.
    
    This class provides in-memory storage and business logic for:
    - Creating and retrieving workflow definitions
    - Starting and managing workflow instances
    - Executing actions on workflow instances
    """
    
    def __init__(self):
        """Initialize the workflow service with empty storage."""
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
    
    # Workflow Definition Management
    
    def create_workflow_definition(self, definition_data: dict) -> Tuple[bool, str, Optional[WorkflowDefinition]]:
        """
        Create a new workflow definition.
        
        Args:
            definition_data: Dictionary containing workflow definition data
            
        Returns:
            Tuple of (success: bool, message: str, definition: Optional[WorkflowDefinition])
        """
        try:
            # Create workflow definition
            definition = WorkflowDefinition(
                id=definition_data['id'],
                name=definition_data['name'],
                description=definition_data.get('description')
            )
            
            # Check if definition already exists
            if definition.id in self.definitions:
                return False, f"Workflow definition with ID '{definition.id}' already exists", None
            
            # Add states
            for state_data in definition_data.get('states', []):
                state = State.from_dict(state_data)
                definition.add_state(state)
            
            # Add actions
            for action_data in definition_data.get('actions', []):
                action = Action.from_dict(action_data)
                definition.add_action(action)
            
            # Validate the definition
            validation_errors = definition.validate()
            if validation_errors:
                return False, f"Validation errors: {'; '.join(validation_errors)}", None
            
            # Store the definition
            self.definitions[definition.id] = definition
            
            return True, f"Workflow definition '{definition.id}' created successfully", definition
            
        except Exception as e:
            return False, f"Error creating workflow definition: {str(e)}", None
    
    def get_workflow_definition(self, definition_id: str) -> Optional[WorkflowDefinition]:
        """
        Retrieve a workflow definition by ID.
        
        Args:
            definition_id: ID of the workflow definition
            
        Returns:
            WorkflowDefinition if found, None otherwise
        """
        return self.definitions.get(definition_id)
    
    def list_workflow_definitions(self) -> List[WorkflowDefinition]:
        """
        Get all workflow definitions.
        
        Returns:
            List of all workflow definitions
        """
        return list(self.definitions.values())
    
    # Workflow Instance Management
    
    def start_workflow_instance(self, definition_id: str, instance_id: Optional[str] = None) -> Tuple[bool, str, Optional[WorkflowInstance]]:
        """
        Start a new workflow instance from a definition.
        
        Args:
            definition_id: ID of the workflow definition to instantiate
            instance_id: Optional custom instance ID (auto-generated if not provided)
            
        Returns:
            Tuple of (success: bool, message: str, instance: Optional[WorkflowInstance])
        """
        try:
            # Check if definition exists
            definition = self.definitions.get(definition_id)
            if not definition:
                return False, f"Workflow definition '{definition_id}' not found", None
            
            # Generate instance ID if not provided
            if not instance_id:
                instance_id = str(uuid.uuid4())
            
            # Check if instance ID already exists
            if instance_id in self.instances:
                return False, f"Workflow instance with ID '{instance_id}' already exists", None
            
            # Get initial state
            initial_state = definition.get_initial_state()
            if not initial_state:
                return False, f"Workflow definition '{definition_id}' has no initial state", None
            
            # Create instance
            instance = WorkflowInstance(
                id=instance_id,
                definition_id=definition_id,
                current_state_id=initial_state.id,
                definition=definition
            )
            
            # Store the instance
            self.instances[instance_id] = instance
            
            return True, f"Workflow instance '{instance_id}' started successfully", instance
            
        except Exception as e:
            return False, f"Error starting workflow instance: {str(e)}", None
    
    def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """
        Retrieve a workflow instance by ID.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            WorkflowInstance if found, None otherwise
        """
        instance = self.instances.get(instance_id)
        if instance and not instance.definition:
            # Load the definition reference if not already loaded
            instance.definition = self.definitions.get(instance.definition_id)
        return instance
    
    def list_workflow_instances(self) -> List[WorkflowInstance]:
        """
        Get all workflow instances.
        
        Returns:
            List of all workflow instances
        """
        instances = list(self.instances.values())
        # Ensure all instances have their definition loaded
        for instance in instances:
            if not instance.definition:
                instance.definition = self.definitions.get(instance.definition_id)
        return instances
    
    def execute_action(self, instance_id: str, action_id: str) -> Tuple[bool, str]:
        """
        Execute an action on a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance
            action_id: ID of the action to execute
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get the instance
            instance = self.get_workflow_instance(instance_id)
            if not instance:
                return False, f"Workflow instance '{instance_id}' not found"
            
            # Execute the action
            success, message = instance.execute_action(action_id)
            
            return success, message
            
        except Exception as e:
            return False, f"Error executing action: {str(e)}"
    
    # Utility Methods
    
    def get_available_actions(self, instance_id: str) -> List[Action]:
        """
        Get all actions that can be executed from the current state of an instance.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            List of executable actions
        """
        instance = self.get_workflow_instance(instance_id)
        if not instance or not instance.definition:
            return []
        
        available_actions = []
        for action in instance.definition.actions.values():
            can_execute, _ = instance.can_execute_action(action.id)
            if can_execute:
                available_actions.append(action)
        
        return available_actions
    
    def get_instance_summary(self, instance_id: str) -> Optional[dict]:
        """
        Get a summary of a workflow instance including current state and available actions.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            Dictionary with instance summary or None if not found
        """
        instance = self.get_workflow_instance(instance_id)
        if not instance:
            return None
        
        current_state = instance.get_current_state()
        available_actions = self.get_available_actions(instance_id)
        
        return {
            'instance': instance.to_dict(),
            'current_state': current_state.to_dict() if current_state else None,
            'available_actions': [action.to_dict() for action in available_actions]
        }

