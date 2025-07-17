import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.services.workflow_service import WorkflowService

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'workflow-engine-secret-key-2024'

# Enable CORS for all routes
CORS(app)

# Initialize the workflow service (in-memory storage)
workflow_service = WorkflowService()

# Make workflow_service available to routes
app.workflow_service = workflow_service

# Import and register blueprints after app initialization
from src.routes.workflow import workflow_bp
app.register_blueprint(workflow_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files or index.html for SPA routing."""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Workflow Engine API - Use /api endpoints", 200

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'workflow-engine'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

