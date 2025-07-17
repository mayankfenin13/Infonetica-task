# Workflow Engine Backend Service

This project implements a minimal backend service for a configurable workflow engine, as a take-home exercise for Infonetica. The service provides a REST API for defining state machines, managing workflow instances, and executing state transitions with full validation.

## Features

- **Configurable State Machines**: Define workflows with custom states and actions
- **Workflow Instance Management**: Start and manage multiple instances of workflow definitions
- **State Transition Validation**: Comprehensive validation of state transitions and action execution
- **REST API**: Clean HTTP endpoints for all workflow operations
- **In-Memory Storage**: Simple persistence without external dependencies
- **CORS Support**: Cross-origin requests enabled for frontend integration

## Project Structure

```
workflow_engine/
├── src/
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── state.py           # State model
│   │   ├── action.py          # Action model
│   │   ├── workflow_definition.py  # Workflow definition model
│   │   └── workflow_instance.py    # Workflow instance model
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   └── workflow_service.py     # Core workflow service
│   ├── routes/                # API endpoints
│   │   ├── __init__.py
│   │   └── workflow.py        # Workflow API routes
│   └── main.py                # Flask application entry point
├── test_workflow.json         # Sample workflow definition
├── test_api.sh               # API testing script
├── run_server.py             # Alternative server runner
├── API_DOCUMENTATION.md      # Detailed API documentation
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Virtual environment (included in project)

### Installation and Setup

1. **Clone or extract the project**:
   ```bash
   cd workflow_engine
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (if needed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python src/main.py
   ```
   
   Or alternatively:
   ```bash
   python run_server.py
   ```

5. **Verify the server is running**:
   ```bash
   curl http://localhost:5000/health
   ```

### Basic Usage

1. **Create a workflow definition**:
   ```bash
   curl -X POST http://localhost:5000/api/definitions \
     -H "Content-Type: application/json" \
     -d @test_workflow.json
   ```

2. **Start a workflow instance**:
   ```bash
   curl -X POST http://localhost:5000/api/instances \
     -H "Content-Type: application/json" \
     -d '{"definition_id": "simple_approval"}'
   ```

3. **Execute an action**:
   ```bash
   curl -X POST http://localhost:5000/api/instances/{instance_id}/actions/submit_for_review
   ```

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Core Concepts

### State
Represents a node in the workflow state machine with the following attributes:
- `id`: Unique identifier
- `name`: Human-readable name
- `is_initial`: Whether this is the starting state (exactly one required per workflow)
- `is_final`: Whether this is a terminal state
- `enabled`: Whether this state is active/usable
- `description`: Optional description

### Action (Transition)
Represents a transition between states with the following attributes:
- `id`: Unique identifier
- `name`: Human-readable name
- `enabled`: Whether this action can be executed
- `from_states`: List of state IDs from which this action can be triggered
- `to_state`: Target state ID where this action leads
- `description`: Optional description

### Workflow Definition
A collection of states and actions that define a complete workflow. Must contain exactly one initial state and proper state/action references.

### Workflow Instance
A running instance of a workflow definition that tracks:
- Current state
- Execution history (actions + timestamps)
- Reference to its definition

## API Endpoints

### Workflow Configuration
- `POST /api/definitions` - Create workflow definition
- `GET /api/definitions/{id}` - Get workflow definition
- `GET /api/definitions` - List all definitions

### Runtime Operations
- `POST /api/instances` - Start workflow instance
- `GET /api/instances/{id}` - Get instance with current state and available actions
- `GET /api/instances` - List all instances
- `POST /api/instances/{id}/actions/{action_id}` - Execute action
- `GET /api/instances/{id}/actions` - Get available actions

### Utilities
- `GET /health` - Basic health check
- `GET /api/health` - Service health with statistics

## Validation Rules

### Workflow Definition Validation
- Must have exactly one initial state
- No duplicate state or action IDs
- All action `from_states` and `to_state` must reference existing states

### Action Execution Validation
- Action must exist in workflow definition
- Action must be enabled
- Current state must be in action's `from_states`
- Cannot execute actions from final states
- Target state must exist

## Testing

A comprehensive test script is provided:

```bash
./test_api.sh
```

This script tests all major API endpoints with a sample workflow.

## Assumptions and Design Decisions

### Technology Stack
- **Python with Flask**: Chosen for rapid development and simplicity, despite the assignment specifying .NET 8/C#. The core concepts of state machines and REST APIs are transferable.
- **In-Memory Storage**: Data is stored in Python dictionaries for simplicity, as per assignment requirements.

### Architecture Decisions
- **Service Layer Pattern**: Business logic is separated into a service layer for better maintainability.
- **Data Models**: Clear separation of concerns with dedicated model classes.
- **RESTful API**: Standard HTTP methods and status codes for intuitive API usage.
- **Comprehensive Validation**: Multiple layers of validation to ensure data integrity.

### Limitations and Trade-offs
- **Concurrency**: No explicit handling for concurrent access to workflow instances. For production, appropriate locking mechanisms would be required.
- **Persistence**: Data is lost on server restart. For production, a database would be needed.
- **Scalability**: Designed for single instance. Horizontal scalability would require distributed storage.
- **Authentication/Authorization**: Not implemented, as it's outside the scope of this minimal assignment.
- **Incremental Definition Updates**: Workflow definitions are created in one go; incremental updates are not supported in this minimal implementation.

### Error Handling
- Standardized error responses with clear messages
- Proper HTTP status codes
- Validation errors are detailed and actionable
- Graceful handling of edge cases (final states, disabled actions, etc.)

## Known Limitations

1. **History Granularity**: The history only stores action executions, not full state change details.
2. **Definition Immutability**: Once created, workflow definitions cannot be modified.
3. **Instance Lifecycle**: No explicit instance deletion or cleanup mechanisms.
4. **Performance**: No optimization for large numbers of definitions or instances.
5. **Logging**: Minimal logging implementation for debugging and monitoring.

## Future Enhancements

Given more time, the following improvements would be valuable:

1. **Unit Tests**: Comprehensive test coverage for all components
2. **Database Integration**: Persistent storage with SQLite or PostgreSQL
3. **Authentication**: JWT-based authentication and authorization
4. **Workflow Versioning**: Support for multiple versions of workflow definitions
5. **Advanced Validation**: More sophisticated validation rules and custom validators
6. **Monitoring**: Metrics, logging, and health monitoring
7. **Documentation**: OpenAPI/Swagger documentation generation
8. **Performance**: Caching, indexing, and query optimization

## Development Notes

- The project follows Flask best practices with blueprints and application factory pattern
- CORS is enabled for frontend integration
- The server listens on `0.0.0.0` for external access during testing/deployment
- Error responses are consistent and machine-readable
- The codebase is structured for easy extension and modification

## License

This project is created as a take-home exercise for Infonetica and is intended for evaluation purposes.


