"""
Flask application entry point for Axiom Intelligent Proposal Assistant.
"""

import logging
import os
import sys

from flask import Flask
from flask_cors import CORS

from backend.config import FLASK_DEBUG
from backend.db.vector_store import VectorStore
from backend.api.routes import api, init_services

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if FLASK_DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Enable CORS for frontend
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Initialize vector store and services
    logger.info("Initializing vector store...")
    vector_store = VectorStore()
    init_services(vector_store)

    # Register blueprints
    app.register_blueprint(api)

    # Root endpoint
    @app.route("/")
    def index():
        return {
            "service": "Axiom Intelligent Proposal Assistant",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "search": "/api/search",
                "stats": "/api/stats",
                "ingest": "/api/ingest",
            },
        }

    logger.info("Application initialized successfully")
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    # Run development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=FLASK_DEBUG)
