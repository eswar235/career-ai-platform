"""
Pydantic schemas for browser automation
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# ========== Automation Step Schemas ==========

class AutomationStepBase(BaseModel):
    """Base automation step schema"""

    step_name: Optional[str] = Field(None, description="Step name")
    action_type: str = Field(..., description="Action type: click, type, wait, upload, etc")
    selector: Optional[str] = Field(None, description="CSS or XPath selector")
    value: Optional[str] = Field(None, description="Value to type or select")
    wait_time_ms: Optional[int] = Field(None, description="Wait time in milliseconds")
    retry_on_fail: bool = Field(False, description="Retry if step fails")


class AutomationStepCreate(BaseModel):
    """Create automation step"""

    step_order: int = Field(..., description="Step order")
    step_name: Optional[str] = Field(None)
    action_type: str = Field(...)
    selector: Optional[str] = Field(None)
    value: Optional[str] = Field(None)
    wait_time_ms: Optional[int] = Field(None)
    retry_on_fail: bool = Field(False)


class AutomationStepResponse(BaseModel):
    """Automation step response"""

    id: uuid.UUID
    automation_job_id: uuid.UUID
    step_order: int
    step_name: Optional[str]
    action_type: str
    selector: Optional[str]
    value: Optional[str]
    wait_time_ms: Optional[int]
    retry_on_fail: bool
    success: Optional[bool]
    error_message: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# ========== Automation Log Schemas ==========

class AutomationLogResponse(BaseModel):
    """Automation log response"""

    id: uuid.UUID
    automation_job_id: uuid.UUID
    log_level: str
    message: Optional[str]
    screenshot_url: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# ========== Automation Job Schemas ==========

class AutomationJobBase(BaseModel):
    """Base automation job schema"""

    job_url: str = Field(..., description="URL of job posting")
    automation_type: Optional[str] = Field(None, description="linkedin_apply, indeed_apply, etc")
    browser_type: str = Field("chrome", description="chrome or firefox")
    headless: bool = Field(True, description="Run in headless mode")
    max_retries: int = Field(3, ge=1, le=10, description="Max retry attempts")


class AutomationJobCreate(BaseModel):
    """Create automation job"""

    job_id: uuid.UUID = Field(..., description="Job ID")
    job_url: str = Field(..., description="URL of job posting")
    automation_type: Optional[str] = Field(None)
    browser_type: str = Field("chrome")
    headless: bool = Field(True)
    max_retries: int = Field(3)


class AutomationJobUpdate(BaseModel):
    """Update automation job"""

    status: Optional[str] = Field(None, description="Job status")
    max_retries: Optional[int] = Field(None)


class AutomationJobResponse(BaseModel):
    """Automation job response"""

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    job_url: str
    status: str
    automation_type: Optional[str]
    browser_type: Optional[str]
    headless: bool
    max_retries: int
    current_retry: int
    error_message: Optional[str]
    result: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutomationJobDetailResponse(AutomationJobResponse):
    """Detailed automation job with steps and logs"""

    steps: list[AutomationStepResponse] = Field(default_factory=list)
    logs: list[AutomationLogResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ========== Automation Control Schemas ==========

class StartAutomationRequest(BaseModel):
    """Request to start automation"""

    job_id: uuid.UUID = Field(..., description="Job ID")
    job_url: str = Field(..., description="Job URL")
    automation_type: Optional[str] = Field(None, description="Type of automation")
    browser_type: str = Field("chrome", description="Browser to use")
    headless: bool = Field(True, description="Headless mode")


class StopAutomationRequest(BaseModel):
    """Request to stop automation"""

    automation_id: uuid.UUID = Field(..., description="Automation job ID")


class AutomationStatusResponse(BaseModel):
    """Automation status response"""

    automation_id: uuid.UUID
    status: str
    current_step: Optional[int]
    total_steps: Optional[int]
    progress: float
    error_message: Optional[str]


class AutomationStepExecutionRequest(BaseModel):
    """Request to execute automation step"""

    automation_id: uuid.UUID = Field(..., description="Automation job ID")
    step: AutomationStepCreate = Field(..., description="Step to execute")


class AutomationStepExecutionResponse(BaseModel):
    """Response from step execution"""

    step_id: uuid.UUID
    success: bool
    error_message: Optional[str]
    screenshot_url: Optional[str]
    timestamp: datetime


# ========== Bulk Automation Schemas ==========

class BulkAutomationRequest(BaseModel):
    """Request for bulk automation"""

    job_ids: list[uuid.UUID] = Field(..., description="List of job IDs")
    automation_type: Optional[str] = Field(None)
    browser_type: str = Field("chrome")
    headless: bool = Field(True)
    max_retries: int = Field(3)


class BulkAutomationResponse(BaseModel):
    """Response from bulk automation"""

    created: int
    failed: int
    status: str
    automation_ids: list[uuid.UUID]


# ========== Automation Report Schemas ==========

class AutomationReport(BaseModel):
    """Automation statistics report"""

    total_jobs: int
    completed: int
    failed: int
    pending: int
    success_rate: float
    average_time_seconds: float
    most_common_error: Optional[str]


class AutomationHistoryResponse(BaseModel):
    """Automation history response"""

    automation_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    error_message: Optional[str]
