/**
 * Browser Automation Types
 */

export type AutomationStatus = "pending" | "in_progress" | "completed" | "failed" | "paused";
export type ActionType = "click" | "type" | "wait" | "upload" | "select" | "scroll";
export type BrowserType = "chrome" | "firefox";
export type LogLevel = "INFO" | "WARNING" | "ERROR";

export interface AutomationJob {
  id: string;
  user_id: string;
  job_id: string;
  job_url: string;
  status: AutomationStatus;
  automation_type?: string;
  browser_type?: BrowserType;
  headless: boolean;
  max_retries: number;
  current_retry: number;
  error_message?: string;
  result?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AutomationJobDetail extends AutomationJob {
  steps: AutomationStep[];
  logs: AutomationLog[];
}

export interface AutomationStep {
  id: string;
  automation_job_id: string;
  step_order: number;
  step_name?: string;
  action_type: ActionType;
  selector?: string;
  value?: string;
  wait_time_ms?: number;
  retry_on_fail: boolean;
  success?: boolean;
  error_message?: string;
  timestamp: string;
}

export interface AutomationLog {
  id: string;
  automation_job_id: string;
  log_level: LogLevel;
  message?: string;
  screenshot_url?: string;
  timestamp: string;
}

// Request/Response types

export interface AutomationJobCreateRequest {
  job_id: string;
  job_url: string;
  automation_type?: string;
  browser_type?: BrowserType;
  headless?: boolean;
  max_retries?: number;
}

export interface AutomationStepCreateRequest {
  step_order: number;
  step_name?: string;
  action_type: ActionType;
  selector?: string;
  value?: string;
  wait_time_ms?: number;
  retry_on_fail?: boolean;
}

export interface AutomationStatusResponse {
  automation_id: string;
  status: AutomationStatus;
  current_step?: number;
  total_steps?: number;
  progress: number;
  error_message?: string;
}

export interface BulkAutomationRequest {
  job_ids: string[];
  automation_type?: string;
  browser_type?: BrowserType;
  headless?: boolean;
  max_retries?: number;
}

export interface BulkAutomationResponse {
  created: number;
  failed: number;
  status: string;
  automation_ids: string[];
}

export interface AutomationReport {
  total_jobs: number;
  completed: number;
  failed: number;
  pending: number;
  success_rate: number;
  average_time_seconds: number;
  most_common_error?: string;
}
