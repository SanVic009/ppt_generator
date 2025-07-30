import os
import threading
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from project_manager import PPTProjectManager
from themes import PPTThemes
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate_config()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize project manager
project_manager = PPTProjectManager(socketio=socketio)

@app.route('/')
def index():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'PPT Generator API',
        'version': '1.0.0',
        'available_themes': PPTThemes.get_theme_display_info(),
        'endpoints': {
            'generate': '/api/generate',
            'themes': '/api/themes',
            'status': '/api/projects/<id>/status',
            'download': '/api/projects/<id>/download',
            'list': '/api/projects',
            'delete': '/api/projects/<id>'
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_presentation():
    """Start presentation generation"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        user_prompt = data['prompt'].strip()
        num_slides = data.get('num_slides', Config.DEFAULT_SLIDES)
        theme_name = data.get('theme', 'corporate_blue')
        
        # Validate inputs
        if not user_prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        if not isinstance(num_slides, int) or num_slides < 1 or num_slides > Config.MAX_SLIDES:
            return jsonify({'error': f'Number of slides must be between 1 and {Config.MAX_SLIDES}'}), 400
        
        # Validate theme
        available_themes = PPTThemes.get_theme_names()
        if theme_name not in available_themes:
            return jsonify({'error': f'Invalid theme. Available themes: {", ".join(available_themes)}'}), 400
        
        # Generate unique project ID
        import uuid
        project_id = str(uuid.uuid4())
        
        # Start generation in background thread
        def generate_async():
            project_manager.generate_presentation(user_prompt, num_slides, project_id, theme_name)
        
        thread = threading.Thread(target=generate_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'theme': theme_name,
            'message': 'Presentation generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_presentation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get available presentation themes"""
    try:
        themes = PPTThemes.get_theme_display_info()
        return jsonify({
            'success': True,
            'themes': themes,
            'default_theme': 'corporate_blue',
            'total': len(themes)
        })
    except Exception as e:
        logger.error(f"Error getting themes: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """Get project status"""
    try:
        status = project_manager.get_project_status(project_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>/download', methods=['GET'])
def download_project(project_id):
    """Download generated presentation"""
    try:
        file_path = project_manager.download_project(project_id)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Project not found or not ready'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'presentation_{project_id}.pptx',
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        logger.error(f"Error downloading project: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    try:
        projects = project_manager.list_projects()
        return jsonify({'projects': projects})
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        success = project_manager.delete_project(project_id)
        if success:
            return jsonify({'success': True, 'message': 'Project deleted'})
        else:
            return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to PPT Generator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_project')
def handle_join_project(data):
    """Join a project room for real-time updates"""
    project_id = data.get('project_id')
    if project_id:
        join_room(project_id)
        logger.info(f"Client {request.sid} joined project room: {project_id}")
        emit('joined_project', {'project_id': project_id})

@socketio.on('leave_project')
def handle_leave_project(data):
    """Leave a project room"""
    project_id = data.get('project_id')
    if project_id:
        leave_room(project_id)
        logger.info(f"Client {request.sid} left project room: {project_id}")
        emit('left_project', {'project_id': project_id})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting PPT Generator API server...")
    logger.info(f"Configuration: {Config.CREWAI_MODEL}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Auto-reload: {Config.USE_RELOADER}")
    
    # Run the application
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG,
        use_reloader=Config.USE_RELOADER,  # Disable auto-reload to prevent interrupting long-running tasks
        allow_unsafe_werkzeug=True
    )

