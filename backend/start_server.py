#!/usr/bin/env python3
"""
Production-style startup script for the PPT Generator API.
This script disables Flask's auto-reload feature to prevent interruptions during long-running tasks.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging before importing app modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ppt_generator.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Start the PPT Generator API server with optimal configuration."""
    
    # Set environment variables for stable operation
    os.environ['FLASK_USE_RELOADER'] = 'False'
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'  # Prevent double startup in debug mode
    
    # Clear any existing Werkzeug server file descriptors to prevent conflicts
    if 'WERKZEUG_SERVER_FD' in os.environ:
        del os.environ['WERKZEUG_SERVER_FD']
    
    logger.info("=== PPT Generator API Server ===")
    logger.info("Starting in stable mode (auto-reload disabled)")
    logger.info("This prevents interruptions during presentation generation")
    
    try:
        # Import after setting environment variables
        from app import app, socketio
        from config import Config
        
        logger.info(f"Model: {Config.CREWAI_MODEL}")
        logger.info(f"Fallback Model: {Config.FALLBACK_MODEL}")
        logger.info(f"Max Retries: {Config.MAX_RETRIES}")
        logger.info(f"Debug Mode: {Config.DEBUG}")
        logger.info(f"Auto-reload: {Config.USE_RELOADER}")
        logger.info("Server ready for presentation generation requests")
        logger.info("Access the API at: http://localhost:5000")
        
        # Start the server with proper configuration
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disable debug mode to prevent werkzeug issues
            use_reloader=False,  # Force disable reloader
            log_output=True,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
