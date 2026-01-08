"""
ChromaDB vector store interface for storing and querying project embeddings.
"""

import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from backend.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)
from backend.models.project import Project, ProjectFeatures

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for project embeddings."""

    def __init__(self, persist_dir: Optional[Path] = None):
        """
        Initialize the vector store.

        Args:
            persist_dir: Directory for persistent storage. Uses config default if not specified.
        """
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.persist_dir = Path(self.persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        # Initialize embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            f"Vector store initialized. Collection '{COLLECTION_NAME}' "
            f"has {self.collection.count()} documents."
        )

    def _create_embedding_text(self, project: Project) -> str:
        """
        Create text representation for embedding generation.

        Combines project metadata into a searchable text format.
        """
        parts = [
            f"Project: {project.project_id}",
            f"File: {project.filename}",
            f"Year: {project.year}",
        ]

        features = project.features
        if features.sq_ft:
            parts.append(f"Square feet: {features.sq_ft}")
        if features.total_sheets:
            parts.append(f"Total sheets: {features.total_sheets}")
        if features.engineering_hrs:
            parts.append(f"Engineering hours: {features.engineering_hrs}")
        if features.drafting_hrs:
            parts.append(f"Drafting hours: {features.drafting_hrs}")
        if features.manager_hrs:
            parts.append(f"Manager hours: {features.manager_hrs}")
        if features.cd_fee:
            parts.append(f"CD fee: ${features.cd_fee:,.2f}")
        if features.ca_fee:
            parts.append(f"CA fee: ${features.ca_fee:,.2f}")

        return " | ".join(parts)

    def _create_query_text(self, features: ProjectFeatures) -> str:
        """Create text representation from query features."""
        parts = []

        if features.sq_ft:
            parts.append(f"Square feet: {features.sq_ft}")
        if features.total_sheets:
            parts.append(f"Total sheets: {features.total_sheets}")
        if features.engineering_hrs:
            parts.append(f"Engineering hours: {features.engineering_hrs}")
        if features.drafting_hrs:
            parts.append(f"Drafting hours: {features.drafting_hrs}")
        if features.manager_hrs:
            parts.append(f"Manager hours: {features.manager_hrs}")
        if features.cd_fee:
            parts.append(f"CD fee: ${features.cd_fee:,.2f}")
        if features.ca_fee:
            parts.append(f"CA fee: ${features.ca_fee:,.2f}")
        if features.total_spent_cd:
            parts.append(f"Total spent CD: ${features.total_spent_cd:,.2f}")
        if features.total_spent_ca:
            parts.append(f"Total spent CA: ${features.total_spent_ca:,.2f}")

        return " | ".join(parts) if parts else "Construction project"

    def add_project(self, project: Project) -> None:
        """
        Add a project to the vector store.

        Args:
            project: Project to add
        """
        # Create embedding text
        text = self._create_embedding_text(project)

        # Generate embedding
        embedding = self.embedding_model.encode(text).tolist()

        # Prepare metadata (ChromaDB only supports str, int, float, bool)
        metadata = {
            "project_id": project.project_id,
            "filename": project.filename,
            "filepath": str(project.filepath),
            "year": project.year,
            "has_training_labels": project.has_training_labels,
            "similar_projects": ",".join(project.similar_projects),
        }

        # Add feature values to metadata
        features = project.features.to_dict()
        for key, value in features.items():
            if value is not None:
                metadata[key] = value

        # Upsert to collection
        self.collection.upsert(
            ids=[project.project_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text],
        )

    def add_projects(self, projects: list[Project]) -> int:
        """
        Add multiple projects to the vector store.

        Args:
            projects: List of projects to add

        Returns:
            Number of projects added
        """
        if not projects:
            return 0

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for project in projects:
            text = self._create_embedding_text(project)
            embedding = self.embedding_model.encode(text).tolist()

            metadata = {
                "project_id": project.project_id,
                "filename": project.filename,
                "filepath": str(project.filepath),
                "year": project.year,
                "has_training_labels": project.has_training_labels,
                "similar_projects": ",".join(project.similar_projects),
            }

            features = project.features.to_dict()
            for key, value in features.items():
                if value is not None:
                    metadata[key] = value

            ids.append(project.project_id)
            embeddings.append(embedding)
            metadatas.append(metadata)
            documents.append(text)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

        logger.info(f"Added {len(projects)} projects to vector store")
        return len(projects)

    def query(
        self,
        features: ProjectFeatures,
        n_results: int = 5,
    ) -> list[dict]:
        """
        Query for similar projects based on features.

        Args:
            features: Query features
            n_results: Maximum number of results to return

        Returns:
            List of result dictionaries with project info and similarity scores
        """
        # Create query text and embedding
        query_text = self._create_query_text(features)
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "distances", "documents"],
        )

        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, project_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0

                # Convert distance to similarity score (cosine distance to similarity)
                similarity = 1 - distance

                formatted_results.append({
                    "project_id": project_id,
                    "filename": metadata.get("filename", ""),
                    "year": metadata.get("year", 0),
                    "similarity_score": similarity,
                    "metadata": metadata,
                })

        return formatted_results

    def get_project(self, project_id: str) -> Optional[dict]:
        """
        Get a specific project by ID.

        Args:
            project_id: Project ID to retrieve

        Returns:
            Project metadata or None if not found
        """
        results = self.collection.get(
            ids=[project_id],
            include=["metadatas", "documents"],
        )

        if results["ids"]:
            return {
                "project_id": results["ids"][0],
                "metadata": results["metadatas"][0] if results["metadatas"] else {},
                "document": results["documents"][0] if results["documents"] else "",
            }

        return None

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()

    def clear(self) -> None:
        """Clear all documents from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Vector store cleared")

    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        count = self.collection.count()

        # Get year distribution
        results = self.collection.get(include=["metadatas"])
        years = {}
        training_count = 0

        if results["metadatas"]:
            for metadata in results["metadatas"]:
                year = metadata.get("year", 0)
                years[year] = years.get(year, 0) + 1
                if metadata.get("has_training_labels"):
                    training_count += 1

        return {
            "total_documents": count,
            "documents_with_training_labels": training_count,
            "years": years,
        }
