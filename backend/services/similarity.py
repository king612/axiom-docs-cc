"""
Similarity engine for finding similar bid proposals.

Combines:
- Embedding-based similarity (from ChromaDB)
- Feature-based similarity (weighted Euclidean distance)
- Recency bias (favor more recent projects)
"""

import logging
import math
from datetime import datetime
from typing import Optional

from backend.config import FEATURE_WEIGHTS, RECENCY_WEIGHT, DEFAULT_MAX_RESULTS
from backend.db.vector_store import VectorStore
from backend.models.project import ProjectFeatures, SearchResult

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Engine for computing similarity between projects."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the similarity engine.

        Args:
            vector_store: VectorStore instance (creates new one if not provided)
        """
        self.vector_store = vector_store or VectorStore()

        # Feature normalization ranges (will be computed from data)
        self._normalization_ranges: Optional[dict] = None

    def _compute_normalization_ranges(self) -> dict:
        """
        Compute min/max ranges for each feature from the stored data.

        Returns:
            Dictionary with min/max for each feature
        """
        # Get all documents from vector store
        results = self.vector_store.collection.get(include=["metadatas"])

        ranges = {
            "total_sheets": {"min": float("inf"), "max": float("-inf")},
            "engineering_hrs": {"min": float("inf"), "max": float("-inf")},
            "drafting_hrs": {"min": float("inf"), "max": float("-inf")},
            "manager_hrs": {"min": float("inf"), "max": float("-inf")},
            "cd_fee": {"min": float("inf"), "max": float("-inf")},
            "ca_fee": {"min": float("inf"), "max": float("-inf")},
            "sq_ft": {"min": float("inf"), "max": float("-inf")},
            "total_spent_cd": {"min": float("inf"), "max": float("-inf")},
            "total_spent_ca": {"min": float("inf"), "max": float("-inf")},
        }

        if results["metadatas"]:
            for metadata in results["metadatas"]:
                for feature in ranges:
                    value = metadata.get(feature)
                    if value is not None:
                        ranges[feature]["min"] = min(ranges[feature]["min"], value)
                        ranges[feature]["max"] = max(ranges[feature]["max"], value)

        # Handle case where no data exists
        for feature in ranges:
            if ranges[feature]["min"] == float("inf"):
                ranges[feature]["min"] = 0
                ranges[feature]["max"] = 1

        return ranges

    def _normalize_value(self, value: float, feature: str) -> float:
        """Normalize a value to [0, 1] range based on stored data ranges."""
        if self._normalization_ranges is None:
            self._normalization_ranges = self._compute_normalization_ranges()

        ranges = self._normalization_ranges.get(feature, {"min": 0, "max": 1})
        min_val = ranges["min"]
        max_val = ranges["max"]

        if max_val == min_val:
            return 0.5

        return (value - min_val) / (max_val - min_val)

    def _compute_feature_similarity(
        self,
        query_features: ProjectFeatures,
        stored_metadata: dict,
    ) -> float:
        """
        Compute feature-based similarity between query and stored project.

        Uses weighted normalized difference for each feature.

        Returns:
            Similarity score between 0 and 1
        """
        total_weight = 0
        weighted_similarity = 0

        provided_fields = query_features.get_provided_fields()

        for field in provided_fields:
            query_value = getattr(query_features, field)
            stored_value = stored_metadata.get(field)

            if query_value is None or stored_value is None:
                continue

            # Normalize both values
            norm_query = self._normalize_value(float(query_value), field)
            norm_stored = self._normalize_value(float(stored_value), field)

            # Compute similarity (1 - normalized difference)
            diff = abs(norm_query - norm_stored)
            field_similarity = 1 - diff

            # Apply weight
            weight = FEATURE_WEIGHTS.get(field, 1.0)
            weighted_similarity += field_similarity * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5  # Default similarity if no fields match

        return weighted_similarity / total_weight

    def _compute_recency_score(self, year: int) -> float:
        """
        Compute recency score for a project.

        More recent projects get higher scores.

        Returns:
            Score between 0 and 1
        """
        current_year = datetime.now().year
        years_old = max(0, current_year - year)

        # Exponential decay: projects lose ~10% relevance per year
        decay_rate = 0.1
        return math.exp(-decay_rate * years_old)

    def search(
        self,
        features: ProjectFeatures,
        max_results: int = DEFAULT_MAX_RESULTS,
    ) -> list[SearchResult]:
        """
        Search for similar projects based on features.

        Combines embedding similarity, feature similarity, and recency.

        Args:
            features: Query features
            max_results: Maximum number of results to return

        Returns:
            List of SearchResult objects, sorted by similarity (best first)
        """
        # Get more results from vector store than needed for re-ranking
        vector_results = self.vector_store.query(
            features=features,
            n_results=max_results * 3,  # Over-fetch for re-ranking
        )

        if not vector_results:
            logger.warning("No results from vector store")
            return []

        # Reset normalization ranges to ensure fresh computation
        self._normalization_ranges = None

        # Re-rank with combined scoring
        scored_results = []

        for result in vector_results:
            # Embedding similarity from vector store
            embedding_similarity = result["similarity_score"]

            # Feature-based similarity
            feature_similarity = self._compute_feature_similarity(
                features, result["metadata"]
            )

            # Recency score
            year = result.get("year", 2020)
            recency_score = self._compute_recency_score(year)

            # Combined score
            # Weight: 40% embedding, 50% features, 10% recency
            combined_score = (
                0.4 * embedding_similarity
                + 0.5 * feature_similarity
                + RECENCY_WEIGHT * recency_score
            )

            scored_results.append({
                "project_id": result["project_id"],
                "filename": result["filename"],
                "year": year,
                "similarity_score": combined_score,
                "embedding_score": embedding_similarity,
                "feature_score": feature_similarity,
                "recency_score": recency_score,
            })

        # Sort by combined score (descending)
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Convert to SearchResult objects
        results = []
        for r in scored_results[:max_results]:
            results.append(
                SearchResult(
                    project_id=r["project_id"],
                    filename=r["filename"],
                    similarity_score=r["similarity_score"],
                    year=r["year"],
                )
            )

        logger.info(
            f"Search returned {len(results)} results "
            f"(top score: {results[0].similarity_score:.4f})" if results else ""
        )

        return results

    def get_similar_to_project(
        self,
        project_id: str,
        max_results: int = DEFAULT_MAX_RESULTS,
    ) -> list[SearchResult]:
        """
        Find projects similar to an existing project by ID.

        Args:
            project_id: ID of the reference project
            max_results: Maximum number of results

        Returns:
            List of similar projects (excluding the reference project)
        """
        # Get the reference project
        project = self.vector_store.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return []

        metadata = project["metadata"]

        # Create features from stored metadata
        features = ProjectFeatures(
            total_sheets=metadata.get("total_sheets"),
            engineering_hrs=metadata.get("engineering_hrs"),
            drafting_hrs=metadata.get("drafting_hrs"),
            manager_hrs=metadata.get("manager_hrs"),
            cd_fee=metadata.get("cd_fee"),
            ca_fee=metadata.get("ca_fee"),
            sq_ft=metadata.get("sq_ft"),
            total_spent_cd=metadata.get("total_spent_cd"),
            total_spent_ca=metadata.get("total_spent_ca"),
        )

        # Search and filter out the reference project
        results = self.search(features, max_results=max_results + 1)
        return [r for r in results if r.project_id != project_id][:max_results]
