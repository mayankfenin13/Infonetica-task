"""
Workflow API routes for the workflow engine.

This module defines all HTTP endpoints for workflow management.
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

workflow_bp = Blueprint('workflow', __name__)


def get_workflow_service():
    """Get the workflow service instance from the Flask app."""
    return current_app.workflow_service


def create_error_response(message: str, status_code: int = 400) -> tuple:
    """Create a standardized error response."""
    return jsonify({'error': message, 'success': False}), status_code


def create_success_response(data: Any = None, message: str = None) -> tuple:
    """Create a standardized success response."""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), 200


# Workflow Definition Endpoints

@workflow_bp.route('/definitions', methods=['POST'])
def create_workflow_definition():
    """
    Create a new workflow definition.
    
    Expected JSON payload:
    {
        "id": "string",
        "name": "string",
        "description": "string (optional)",
        "states": [
            {
                "id": "string",
                "name": "string",
                "is_initial": boolean,
                "is_final": boolean,
                "enabled": boolean,
                "description": "string (optional)"
            }
        ],
        "actions": [
            {
                "id": "string",
                "name": "string",
                "enabled": boolean,
                "from_states": ["state_id1", "state_id2"],
                "to_state": "state_id",
                "description": "string (optional)"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Request body must contain JSON data")
        
        # Validate required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in data:
                return create_error_response(f"Missing required field: {field}")
        
        service = get_workflow_service()
        success, message, definition = service.create_workflow_definition(data)
        
        if success:
            return create_success_response(
                data=definition.to_dict(),
                message=message
            )
        else:
            return create_error_response(message)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/definitions/<definition_id>', methods=['GET'])
def get_workflow_definition(definition_id: str):
    """
    Retrieve a workflow definition by ID.
    """
    try:
        service = get_workflow_service()
        definition = service.get_workflow_definition(definition_id)
        
        if definition:
            return create_success_response(data=definition.to_dict())
        else:
            return create_error_response(f"Workflow definition '{definition_id}' not found", 404)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/definitions', methods=['GET'])
def list_workflow_definitions():
    """
    List all workflow definitions.
    """
    try:
        service = get_workflow_service()
        definitions = service.list_workflow_definitions()
        
        return create_success_response(
            data=[definition.to_dict() for definition in definitions]
        )
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


# Workflow Instance Endpoints

@workflow_bp.route('/instances', methods=['POST'])
def start_workflow_instance():
    """
    Start a new workflow instance.
    
    Expected JSON payload:
    {
        "definition_id": "string",
        "instance_id": "string (optional)"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Request body must contain JSON data")
        
        # Validate required fields
        if 'definition_id' not in data:
            return create_error_response("Missing required field: definition_id")
        
        service = get_workflow_service()
        success, message, instance = service.start_workflow_instance(
            definition_id=data['definition_id'],
            instance_id=data.get('instance_id')
        )
        
        if success:
            return create_success_response(
                data=instance.to_dict(),
                message=message
            )
        else:
            return create_error_response(message)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/instances/<instance_id>', methods=['GET'])
def get_workflow_instance(instance_id: str):
    """
    Retrieve a workflow instance by ID with current state and available actions.
    """
    try:
        service = get_workflow_service()
        summary = service.get_instance_summary(instance_id)
        
        if summary:
            return create_success_response(data=summary)
        else:
            return create_error_response(f"Workflow instance '{instance_id}' not found", 404)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/instances', methods=['GET'])
def list_workflow_instances():
    """
    List all workflow instances.
    """
    try:
        service = get_workflow_service()
        instances = service.list_workflow_instances()
        
        return create_success_response(
            data=[instance.to_dict() for instance in instances]
        )
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/instances/<instance_id>/actions/<action_id>', methods=['POST'])
def execute_action(instance_id: str, action_id: str):
    """
    Execute an action on a workflow instance.
    """
    try:
        service = get_workflow_service()
        success, message = service.execute_action(instance_id, action_id)
        
        if success:
            # Get updated instance summary
            summary = service.get_instance_summary(instance_id)
            return create_success_response(
                data=summary,
                message=message
            )
        else:
            return create_error_response(message)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


@workflow_bp.route('/instances/<instance_id>/actions', methods=['GET'])
def get_available_actions(instance_id: str):
    """
    Get all actions that can be executed from the current state of an instance.
    """
    try:
        service = get_workflow_service()
        actions = service.get_available_actions(instance_id)
        
        if actions is not None:
            return create_success_response(
                data=[action.to_dict() for action in actions]
            )
        else:
            return create_error_response(f"Workflow instance '{instance_id}' not found", 404)
            
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


# Utility Endpoints

@workflow_bp.route('/health', methods=['GET'])
def workflow_health():
    """
    Health check endpoint for workflow service.
    """
    try:
        service = get_workflow_service()
        definitions_count = len(service.definitions)
        instances_count = len(service.instances)
        
        return create_success_response(
            data={
                'service': 'workflow-engine',
                'status': 'healthy',
                'definitions_count': definitions_count,
                'instances_count': instances_count
            }
        )
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

