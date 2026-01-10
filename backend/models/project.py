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

    @property
    def total_hours(self) -> Optional[float]:
        """Total Hours = Engineering + Drafting + Manager/Reviewer hours."""
        components = [self.engineering_hrs, self.drafting_hrs, self.manager_hrs]
        valid = [c for c in components if c is not None]
        return sum(valid) if valid else None

    @property
    def total_fee(self) -> Optional[float]:
        """Total Fee = CD Fee + CA Fee."""
        components = [self.cd_fee, self.ca_fee]
        valid = [c for c in components if c is not None]
        return sum(valid) if valid else None

    @property
    def total_spent(self) -> Optional[float]:
        """Total Spent = Total Spent CD + Total Spent CA."""
        components = [self.total_spent_cd, self.total_spent_ca]
        valid = [c for c in components if c is not None]
        return sum(valid) if valid else None

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
            # Computed totals
            "total_hours": self.total_hours,
            "total_fee": self.total_fee,
            "total_spent": self.total_spent,
        }

    def to_vector(self) -> list[float]:
        """Convert features to a numeric vector for similarity computation.

        Uses combined totals for hours, fee, and spent.
        """
        return [
            float(self.total_sheets or 0),
            float(self.total_hours or 0),
            float(self.total_fee or 0),
            float(self.sq_ft or 0),
            float(self.total_spent or 0),
        ]

    def get_provided_fields(self) -> list[str]:
        """Return list of field names that have values (using combined fields)."""
        fields = []
        if self.total_sheets is not None:
            fields.append("total_sheets")
        if self.total_hours is not None:
            fields.append("total_hours")
        if self.total_fee is not None:
            fields.append("total_fee")
        if self.sq_ft is not None:
            fields.append("sq_ft")
        if self.total_spent is not None:
            fields.append("total_spent")
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
    """Search request from the API.

    Accepts combined fields from UI:
    - total_hours: Engineering + Drafting + Manager hours
    - total_fee: SD + DD + CD fee
    - total_spent: SD + DD + CD spent
    """
    sq_ft: Optional[int] = None
    total_hours: Optional[float] = None
    total_fee: Optional[float] = None
    total_spent: Optional[float] = None
    max_results: int = 5

    def to_features(self) -> ProjectFeatures:
        """Convert search request to ProjectFeatures.

        Maps combined fields to component fields for similarity matching.
        Since we only have totals, we store them as the primary component
        (engineering_hrs, cd_fee, total_spent_cd) for compatibility.
        """
        return ProjectFeatures(
            total_sheets=None,  # Not exposed in UI but used for training
            engineering_hrs=self.total_hours,  # Store total in engineering field
            drafting_hrs=None,
            manager_hrs=None,
            cd_fee=self.total_fee,  # Store total in cd_fee field
            ca_fee=None,
            sq_ft=self.sq_ft,
            total_spent_cd=self.total_spent,  # Store total in spent_cd field
            total_spent_ca=None,
        )
