from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class ProjectFeatures:
    """Features extracted from a bid spreadsheet."""
    total_sheets: Optional[int] = None
    engineering_hrs: Optional[float] = None
    drafting_hrs: Optional[float] = None
    manager_hrs: Optional[float] = None
    cd_fee: Optional[float] = None
    ca_fee: Optional[float] = None
    sq_ft: Optional[int] = None
    total_spent_cd: Optional[float] = None
    total_spent_ca: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "total_sheets": self.total_sheets,
            "engineering_hrs": self.engineering_hrs,
            "drafting_hrs": self.drafting_hrs,
            "manager_hrs": self.manager_hrs,
            "cd_fee": self.cd_fee,
            "ca_fee": self.ca_fee,
            "sq_ft": self.sq_ft,
            "total_spent_cd": self.total_spent_cd,
            "total_spent_ca": self.total_spent_ca,
        }

    def to_vector(self) -> list[float]:
        """Convert features to a numeric vector for similarity computation."""
        return [
            float(self.total_sheets or 0),
            float(self.engineering_hrs or 0),
            float(self.drafting_hrs or 0),
            float(self.manager_hrs or 0),
            float(self.cd_fee or 0),
            float(self.ca_fee or 0),
            float(self.sq_ft or 0),
            float(self.total_spent_cd or 0),
            float(self.total_spent_ca or 0),
        ]

    def get_provided_fields(self) -> list[str]:
        """Return list of field names that have values."""
        fields = []
        if self.total_sheets is not None:
            fields.append("total_sheets")
        if self.engineering_hrs is not None:
            fields.append("engineering_hrs")
        if self.drafting_hrs is not None:
            fields.append("drafting_hrs")
        if self.manager_hrs is not None:
            fields.append("manager_hrs")
        if self.cd_fee is not None:
            fields.append("cd_fee")
        if self.ca_fee is not None:
            fields.append("ca_fee")
        if self.sq_ft is not None:
            fields.append("sq_ft")
        if self.total_spent_cd is not None:
            fields.append("total_spent_cd")
        if self.total_spent_ca is not None:
            fields.append("total_spent_ca")
        return fields


@dataclass
class Project:
    """Represents a bid proposal project."""
    project_id: str
    filename: str
    filepath: Path
    year: int
    features: ProjectFeatures
    similar_projects: list[str] = field(default_factory=list)
    has_training_labels: bool = False

    def to_metadata(self) -> dict:
        """Convert to metadata dict for ChromaDB storage."""
        metadata = {
            "project_id": self.project_id,
            "filename": self.filename,
            "filepath": str(self.filepath),
            "year": self.year,
            "has_training_labels": self.has_training_labels,
            "similar_projects": ",".join(self.similar_projects) if self.similar_projects else "",
        }
        metadata.update(self.features.to_dict())
        return metadata


@dataclass
class SearchResult:
    """A single search result."""
    project_id: str
    filename: str
    similarity_score: float
    year: int

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "filename": self.filename,
            "similarity_score": round(self.similarity_score, 4),
            "year": self.year,
        }


@dataclass
class SearchRequest:
    """Search request from the API."""
    total_sheets: Optional[int] = None
    engineering_hrs: Optional[float] = None
    drafting_hrs: Optional[float] = None
    manager_hrs: Optional[float] = None
    cd_fee: Optional[float] = None
    ca_fee: Optional[float] = None
    sq_ft: Optional[int] = None
    total_spent_cd: Optional[float] = None
    total_spent_ca: Optional[float] = None
    max_results: int = 5

    def to_features(self) -> ProjectFeatures:
        return ProjectFeatures(
            total_sheets=self.total_sheets,
            engineering_hrs=self.engineering_hrs,
            drafting_hrs=self.drafting_hrs,
            manager_hrs=self.manager_hrs,
            cd_fee=self.cd_fee,
            ca_fee=self.ca_fee,
            sq_ft=self.sq_ft,
            total_spent_cd=self.total_spent_cd,
            total_spent_ca=self.total_spent_ca,
        )
