from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from config import config
from routes.upload import upload_bp
from routes.analysis import analysis_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8081",
                "https://resumerrs.vercel.app",
                app.config['FRONTEND_URL']
            ],
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            "message": "ATS Resume Analyzer API",
            "version": "1.0.0",
            "endpoints": {
                "upload": "/api/upload-resume",
                "analyze": "/api/analyze-match",
                "history": "/api/analysis-history"
            }
        })
    
    # Health check (for Render and other platforms)
    @app.route('/health')
    @app.route('/health/')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "ATS Resume Analyzer API",
            "version": "1.0.0"
        }), 200
    
    # Handle Render's incorrect health check path (workaround)
    @app.route('/localhost:5000/health')
    def render_health_workaround():
        return jsonify({
            "status": "healthy",
            "service": "ATS Resume Analyzer API",
            "version": "1.0.0",
            "note": "Health check working"
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Log the requested path for debugging
        logger.warning(f"404 Error - Requested path: {request.path}")
        return jsonify({
            "success": False,
            "message": "Endpoint not found",
            "path": request.path,
            "available_endpoints": {
                "health": "/health",
                "root": "/",
                "upload": "/api/upload-resume",
                "analyze": "/api/analyze-match"
            }
        }), 404
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "success": False,
            "message": "File size exceeds 5MB limit"
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
    
    return app

# Create app instance for gunicorn/production servers
# This is needed because gunicorn looks for 'app' variable in the module
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == '__main__':
    # For local development
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True' and env == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

