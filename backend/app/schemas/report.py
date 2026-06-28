from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ReportCreate(BaseModel):
    title: str
    report_type: str
    format: str = "pdf"
    severity: Optional[str] = None
    summary: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    format: str
    status: str
    severity: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    id: int
    title: str
    report_type: str
    format: str
    status: str
    severity: Optional[str] = None
    summary: Optional[str] = None
    executive_summary: Optional[str] = None
    technical_findings: Optional[Any] = None
    risk_assessment: Optional[Any] = None
    recommendations: Optional[Any] = None
    file_path: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
