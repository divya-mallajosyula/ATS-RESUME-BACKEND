"""
Simple runner script for the Flask ATS Resume Analyzer API
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    # Create the Flask app
    app = create_app('development')
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("=" * 50)
    print("ATS Resume Analyzer API")
    print("=" * 50)
    print(f"Starting server on http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/health")
    print(f"API root: http://{host}:{port}/")
    print("=" * 50)
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(host=host, port=port, debug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)

