# Workflow Engine API Documentation

This document provides comprehensive documentation for the Workflow Engine REST API endpoints.

## Base URL

```
http://localhost:5000/api
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Optional success message",
  "data": { /* Response data */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Workflow Definition Endpoints

### Create Workflow Definition

**POST** `/definitions`

Creates a new workflow definition with states and actions.

#### Request Body
```json
{
  "id": "string (required)",
  "name": "string (required)",
  "description": "string (optional)",
  "states": [
    {
      "id": "string (required)",
      "name": "string (required)",
      "is_initial": "boolean (default: false)",
      "is_final": "boolean (default: false)",
      "enabled": "boolean (default: true)",
      "description": "string (optional)"
    }
  ],
  "actions": [
    {
      "id": "string (required)",
      "name": "string (required)",
      "enabled": "boolean (default: true)",
      "from_states": ["array of state IDs"],
      "to_state": "string (required)",
      "description": "string (optional)"
    }
  ]
}
```

#### Response
- **200 OK**: Workflow definition created successfully
- **400 Bad Request**: Validation errors or duplicate ID

#### Example
```bash
curl -X POST http://localhost:5000/api/definitions \
  -H "Content-Type: application/json" \
  -d '{
    "id": "simple_approval",
    "name": "Simple Approval Workflow",
    "states": [
      {"id": "draft", "name": "Draft", "is_initial": true},
      {"id": "approved", "name": "Approved", "is_final": true}
    ],
    "actions": [
      {"id": "approve", "name": "Approve", "from_states": ["draft"], "to_state": "approved"}
    ]
  }'
```

### Get Workflow Definition

**GET** `/definitions/{definition_id}`

Retrieves a specific workflow definition by ID.

#### Response
- **200 OK**: Returns the workflow definition
- **404 Not Found**: Workflow definition not found

#### Example
```bash
curl -X GET http://localhost:5000/api/definitions/simple_approval
```

### List Workflow Definitions

**GET** `/definitions`

Retrieves all workflow definitions.

#### Response
- **200 OK**: Returns array of all workflow definitions

#### Example
```bash
curl -X GET http://localhost:5000/api/definitions
```

## Workflow Instance Endpoints

### Start Workflow Instance

**POST** `/instances`

Creates and starts a new workflow instance from a definition.

#### Request Body
```json
{
  "definition_id": "string (required)",
  "instance_id": "string (optional, auto-generated if not provided)"
}
```

#### Response
- **200 OK**: Workflow instance started successfully
- **400 Bad Request**: Definition not found or validation errors

#### Example
```bash
curl -X POST http://localhost:5000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"definition_id": "simple_approval"}'
```

### Get Workflow Instance

**GET** `/instances/{instance_id}`

Retrieves a workflow instance with current state and available actions.

#### Response
- **200 OK**: Returns instance summary with current state and available actions
- **404 Not Found**: Workflow instance not found

#### Response Format
```json
{
  "success": true,
  "data": {
    "instance": {
      "id": "instance-uuid",
      "definition_id": "simple_approval",
      "current_state_id": "draft",
      "history": [],
      "created_at": "2024-01-01T00:00:00",
      "is_final": false
    },
    "current_state": {
      "id": "draft",
      "name": "Draft",
      "is_initial": true,
      "is_final": false,
      "enabled": true
    },
    "available_actions": [
      {
        "id": "approve",
        "name": "Approve",
        "enabled": true,
        "from_states": ["draft"],
        "to_state": "approved"
      }
    ]
  }
}
```

#### Example
```bash
curl -X GET http://localhost:5000/api/instances/your-instance-id
```

### List Workflow Instances

**GET** `/instances`

Retrieves all workflow instances.

#### Response
- **200 OK**: Returns array of all workflow instances

#### Example
```bash
curl -X GET http://localhost:5000/api/instances
```

### Execute Action

**POST** `/instances/{instance_id}/actions/{action_id}`

Executes an action on a workflow instance, transitioning it to a new state.

#### Response
- **200 OK**: Action executed successfully, returns updated instance summary
- **400 Bad Request**: Action cannot be executed (validation errors)
- **404 Not Found**: Instance or action not found

#### Validation Rules
- Action must exist in the workflow definition
- Action must be enabled
- Current state must be in the action's `from_states`
- Cannot execute actions from final states
- Target state must exist

#### Example
```bash
curl -X POST http://localhost:5000/api/instances/your-instance-id/actions/approve
```

### Get Available Actions

**GET** `/instances/{instance_id}/actions`

Retrieves all actions that can be executed from the current state.

#### Response
- **200 OK**: Returns array of executable actions
- **404 Not Found**: Workflow instance not found

#### Example
```bash
curl -X GET http://localhost:5000/api/instances/your-instance-id/actions
```

## Utility Endpoints

### Health Check

**GET** `/health`

Basic health check endpoint.

#### Response
```json
{
  "service": "workflow-engine",
  "status": "healthy"
}
```

### Workflow Service Health

**GET** `/api/health`

Detailed health check with service statistics.

#### Response
```json
{
  "success": true,
  "data": {
    "service": "workflow-engine",
    "status": "healthy",
    "definitions_count": 1,
    "instances_count": 2
  }
}
```

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Validation errors, invalid data |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Unexpected server error |

## Common Error Scenarios

### Workflow Definition Validation Errors
- Missing required fields (`id`, `name`)
- Duplicate state or action IDs
- No initial state or multiple initial states
- Actions referencing non-existent states

### Action Execution Errors
- Action doesn't exist in workflow definition
- Action is disabled
- Current state not in action's `from_states`
- Attempting to execute action from final state
- Target state doesn't exist

## Example Workflow

Here's a complete example of creating and using a simple approval workflow:

```bash
# 1. Create workflow definition
curl -X POST http://localhost:5000/api/definitions \
  -H "Content-Type: application/json" \
  -d '{
    "id": "document_approval",
    "name": "Document Approval Process",
    "states": [
      {"id": "draft", "name": "Draft", "is_initial": true},
      {"id": "review", "name": "Under Review"},
      {"id": "approved", "name": "Approved", "is_final": true},
      {"id": "rejected", "name": "Rejected", "is_final": true}
    ],
    "actions": [
      {"id": "submit", "name": "Submit for Review", "from_states": ["draft"], "to_state": "review"},
      {"id": "approve", "name": "Approve", "from_states": ["review"], "to_state": "approved"},
      {"id": "reject", "name": "Reject", "from_states": ["review"], "to_state": "rejected"},
      {"id": "revise", "name": "Send Back for Revision", "from_states": ["review"], "to_state": "draft"}
    ]
  }'

# 2. Start workflow instance
INSTANCE_RESPONSE=$(curl -s -X POST http://localhost:5000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"definition_id": "document_approval"}')

# Extract instance ID (assuming jq is available)
INSTANCE_ID=$(echo $INSTANCE_RESPONSE | jq -r '.data.id')

# 3. Check current state and available actions
curl -X GET http://localhost:5000/api/instances/$INSTANCE_ID

# 4. Execute submit action
curl -X POST http://localhost:5000/api/instances/$INSTANCE_ID/actions/submit

# 5. Execute approve action
curl -X POST http://localhost:5000/api/instances/$INSTANCE_ID/actions/approve

# 6. Check final state
curl -X GET http://localhost:5000/api/instances/$INSTANCE_ID
```

This workflow demonstrates the complete lifecycle from draft to approval, including the ability to send documents back for revision during the review process.

