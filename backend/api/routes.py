"""
Flask API routes for the Axiom Intelligent Proposal Assistant.
"""

import logging
import time
from flask import Blueprint, request, jsonify

from backend.config import DEFAULT_MAX_RESULTS, MAX_RESULTS_LIMIT, MIN_RESULTS
from backend.db.vector_store import VectorStore
from backend.models.project import ProjectFeatures, SearchRequest
from backend.services.similarity import SimilarityEngine
from backend.services.ingestion import IngestionService

logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint("api", __name__, url_prefix="/api")

# Global service instances (initialized in app.py)
_vector_store: VectorStore = None
_similarity_engine: SimilarityEngine = None
_ingestion_service: IngestionService = None


def init_services(vector_store: VectorStore):
    """Initialize services with shared vector store."""
    global _vector_store, _similarity_engine, _ingestion_service
    _vector_store = vector_store
    _similarity_engine = SimilarityEngine(vector_store)
    _ingestion_service = IngestionService(vector_store)


def get_similarity_engine() -> SimilarityEngine:
    """Get the similarity engine instance."""
    if _similarity_engine is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    return _similarity_engine


def get_ingestion_service() -> IngestionService:
    """Get the ingestion service instance."""
    if _ingestion_service is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    return _ingestion_service


def get_vector_store() -> VectorStore:
    """Get the vector store instance."""
    if _vector_store is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    return _vector_store


@api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "axiom-proposal-assistant",
    })


@api.route("/stats", methods=["GET"])
def get_stats():
    """Get statistics about the indexed data."""
    try:
        store = get_vector_store()
        stats = store.get_stats()
        return jsonify({
            "status": "success",
            "data": stats,
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@api.route("/search", methods=["POST"])
def search():
    """
    Search for similar projects based on input features.

    Request body:
    {
        "total_sheets": int (optional),
        "engineering_hrs": float (optional),
        "drafting_hrs": float (optional),
        "manager_hrs": float (optional),
        "cd_fee": float (optional),
        "ca_fee": float (optional),
        "sq_ft": int (optional),
        "total_spent_cd": float (optional),
        "total_spent_ca": float (optional),
        "max_results": int (optional, default 5, max 10)
    }

    Response:
    {
        "status": "success",
        "results": [
            {
                "project_id": "P24-310A",
                "filename": "P24-310A Sonora.xlsx",
                "similarity_score": 0.89,
                "year": 2024
            },
            ...
        ],
        "query_time_ms": 145
    }
    """
    start_time = time.time()

    try:
        data = request.get_json() or {}

        # Parse max_results with bounds
        max_results = data.get("max_results", DEFAULT_MAX_RESULTS)
        max_results = max(MIN_RESULTS, min(MAX_RESULTS_LIMIT, int(max_results)))

        # Build features from request
        features = ProjectFeatures(
            total_sheets=data.get("total_sheets"),
            engineering_hrs=data.get("engineering_hrs"),
            drafting_hrs=data.get("drafting_hrs"),
            manager_hrs=data.get("manager_hrs"),
            cd_fee=data.get("cd_fee"),
            ca_fee=data.get("ca_fee"),
            sq_ft=data.get("sq_ft"),
            total_spent_cd=data.get("total_spent_cd"),
            total_spent_ca=data.get("total_spent_ca"),
        )

        # Check if at least one feature is provided
        if not features.get_provided_fields():
            return jsonify({
                "status": "error",
                "message": "At least one search parameter is required",
            }), 400

        # Perform search
        engine = get_similarity_engine()
        results = engine.search(features, max_results=max_results)

        # Calculate query time
        query_time_ms = int((time.time() - start_time) * 1000)

        return jsonify({
            "status": "success",
            "results": [r.to_dict() for r in results],
            "query_time_ms": query_time_ms,
            "total_results": len(results),
        })

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@api.route("/similar/<project_id>", methods=["GET"])
def get_similar(project_id: str):
    """
    Get projects similar to a specific project by ID.

    Query parameters:
        max_results: int (optional, default 5, max 10)

    Response:
    {
        "status": "success",
        "reference_project": "P24-310A",
        "results": [...],
        "query_time_ms": 123
    }
    """
    start_time = time.time()

    try:
        max_results = request.args.get("max_results", DEFAULT_MAX_RESULTS, type=int)
        max_results = max(MIN_RESULTS, min(MAX_RESULTS_LIMIT, max_results))

        engine = get_similarity_engine()
        results = engine.get_similar_to_project(project_id, max_results=max_results)

        query_time_ms = int((time.time() - start_time) * 1000)

        return jsonify({
            "status": "success",
            "reference_project": project_id,
            "results": [r.to_dict() for r in results],
            "query_time_ms": query_time_ms,
            "total_results": len(results),
        })

    except Exception as e:
        logger.error(f"Get similar error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@api.route("/ingest", methods=["POST"])
def trigger_ingest():
    """
    Trigger data ingestion.

    Request body:
    {
        "clear_existing": bool (optional, default false),
        "year": int (optional, ingest specific year only)
    }

    Response:
    {
        "status": "success",
        "stats": {
            "total_files": 1500,
            "successful": 1450,
            "failed": 50,
            "with_training_labels": 800
        }
    }
    """
    try:
        data = request.get_json() or {}
        clear_existing = data.get("clear_existing", False)
        year = data.get("year")

        service = get_ingestion_service()

        if year:
            stats = service.ingest_year(year, clear_existing=clear_existing)
        else:
            stats = service.ingest_all(clear_existing=clear_existing)

        return jsonify({
            "status": "success",
            "stats": stats,
        })

    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@api.route("/project/<project_id>", methods=["GET"])
def get_project(project_id: str):
    """
    Get details for a specific project.

    Response:
    {
        "status": "success",
        "project": {
            "project_id": "P24-310A",
            "filename": "P24-310A Sonora.xlsx",
            "year": 2024,
            "features": {...}
        }
    }
    """
    try:
        store = get_vector_store()
        project = store.get_project(project_id)

        if not project:
            return jsonify({
                "status": "error",
                "message": f"Project not found: {project_id}",
            }), 404

        return jsonify({
            "status": "success",
            "project": project,
        })

    except Exception as e:
        logger.error(f"Get project error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500
