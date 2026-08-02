/**
 * Job search types for TypeScript
 */

export interface JobResponse {
  id: string;
  title: string;
  company_name: string;
  company_id?: string;
  location?: string;
  job_type?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  description?: string;
  requirements?: string;
  benefits?: string;
  industry?: string;
  experience_level?: string;
  skills_required?: string[];
  posted_date: string;
  application_deadline?: string;
  source?: string;
  source_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  title: string;
  company_name: string;
  company_id?: string;
  location?: string;
  job_type?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  description?: string;
  requirements?: string;
  benefits?: string;
  industry?: string;
  experience_level?: string;
  skills_required?: string[];
  posted_date: string;
  application_deadline?: string;
  source?: string;
  source_url?: string;
}

export interface JobUpdate {
  title?: string;
  company_name?: string;
  location?: string;
  job_type?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  description?: string;
  requirements?: string;
  benefits?: string;
  industry?: string;
  experience_level?: string;
  skills_required?: string[];
  application_deadline?: string;
  source_url?: string;
  is_active?: boolean;
}

export interface SavedJobResponse {
  id: string;
  user_id: string;
  job_id: string;
  saved_at: string;
  notes?: string;
  job?: JobResponse;
}

export interface SavedJobCreate {
  job_id: string;
  notes?: string;
}

export interface JobSearchFilters {
  keyword?: string;
  location?: string;
  job_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  industry?: string;
  company_name?: string;
  posted_after?: string;
  skip?: number;
  limit?: number;
  sort_by?: string;
}

export interface JobSearchResults {
  total: number;
  skip: number;
  limit: number;
  jobs: JobResponse[];
}

export interface JobSearchHistoryResponse {
  id: string;
  user_id: string;
  search_query?: string;
  filters_applied?: Record<string, any>;
  results_count?: number;
  searched_at: string;
}

export interface JobApplicationCreate {
  job_id: string;
  notes?: string;
}

export interface JobApplicationUpdate {
  status?: string;
  notes?: string;
}

export interface JobApplicationResponse {
  id: string;
  user_id: string;
  job_id: string;
  status: string;
  applied_date: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  job?: JobResponse;
}

export interface ApplicationStats {
  total: number;
  applied: number;
  interviewed: number;
  offered: number;
  rejected: number;
}
