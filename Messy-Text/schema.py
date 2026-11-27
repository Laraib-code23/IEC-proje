from typing import Optional

from pydantic import BaseModel, Field


class Extracted(BaseModel):
    """A job post turned into clean data. Anything the text does not say is null."""

    is_job_post: bool = Field(description="True only if the text is a job post")
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = Field(
        default=None, description="full-time, part-time, contract or internship"
    )
    remote: Optional[bool] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = Field(default=None, description="e.g. USD, PKR")
    experience_years: Optional[int] = Field(default=None, description="Minimum years")
    skills: list[str] = Field(default_factory=list)
