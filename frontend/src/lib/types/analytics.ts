/**
 * Analytics Types
 */

export interface ApplicationStatistics {
  id: string;
  user_id: string;
  total_submitted: number;
  total_pending: number;
  total_rejected: number;
  total_interviews: number;
  total_offers: number;
  response_rate?: number;
  average_response_time_days?: number;
  success_rate?: number;
  last_updated: string;
}

export interface ApplicationTrend {
  id: string;
  user_id: string;
  date: string;
  applications_submitted: number;
  applications_reviewed: number;
  interviews_scheduled: number;
  rejections_received: number;
  offers_received: number;
}

export interface RoleAnalytics {
  id: string;
  job_title: string;
  application_count: number;
  interview_count: number;
  offer_count: number;
  rejection_count: number;
  last_applied?: string;
  success_rate?: number;
}

export interface CompanyAnalytics {
  id: string;
  company_name: string;
  application_count: number;
  interview_count: number;
  offer_count: number;
  rejection_count: number;
  last_applied?: string;
  success_rate?: number;
}

export interface SourceAnalytics {
  id: string;
  source_name: string;
  application_count: number;
  interview_count: number;
  offer_count: number;
  rejection_count: number;
  success_rate?: number;
}

// Response types

export interface DashboardMetrics {
  total_applications: number;
  pending_applications: number;
  rejected_applications: number;
  interview_scheduled: number;
  offers_received: number;
  response_rate?: number;
  success_rate?: number;
  average_response_time?: number;
}

export interface DashboardResponse {
  metrics: DashboardMetrics;
  top_roles: RoleAnalytics[];
  top_companies: CompanyAnalytics[];
  sources: SourceAnalytics[];
  recent_trends?: ApplicationTrend[];
  last_updated: string;
}

export interface TrendsResponse {
  period: "30days" | "90days" | "all_time";
  trends: ApplicationTrend[];
  total_applications: number;
  average_per_day: number;
  peak_day?: string;
}

export interface TopRolesResponse {
  top_roles: RoleAnalytics[];
  total_unique_roles: number;
}

export interface TopCompaniesResponse {
  top_companies: CompanyAnalytics[];
  total_unique_companies: number;
}

export interface SourceBreakdownResponse {
  sources: SourceAnalytics[];
  total_sources: number;
}

export interface StatusBreakdown {
  status: string;
  count: number;
  percentage: number;
}

export interface DetailedBreakdownResponse {
  by_status: StatusBreakdown[];
  by_title: Record<string, number>;
  by_company: Record<string, number>;
  by_source: Record<string, number>;
  by_experience_level: Record<string, number>;
}

export interface ApplicationInsight {
  insight_type: "strength" | "opportunity" | "warning";
  title: string;
  description: string;
  metric?: number;
}

export interface InsightsResponse {
  insights: ApplicationInsight[];
  generated_at: string;
}

export interface ExportRecord {
  job_title: string;
  company_name: string;
  job_source?: string;
  submission_date: string;
  current_status: string;
  resume_version?: string;
  cover_letter_version?: string;
}

export interface ExportResponse {
  total_records: number;
  records: ExportRecord[];
  exported_at: string;
}
