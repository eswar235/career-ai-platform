/**
 * Job Application Types
 */

export interface JobApplication {
  id: string;
  user_id: string;
  job_id: string;
  status: ApplicationStatus;
  application_date: string;
  applied_via?: string;
  cover_letter_id?: string;
  resume_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface JobApplicationDetail extends JobApplication {
  interviews: Interview[];
  activities: ApplicationActivity[];
  offer?: JobOffer;
}

export type ApplicationStatus =
  | "applied"
  | "under_review"
  | "interview_scheduled"
  | "interviewed"
  | "offer_received"
  | "rejected"
  | "withdrawn"
  | "accepted";

export interface Interview {
  id: string;
  application_id: string;
  interview_type?: string;
  scheduled_date?: string;
  duration_minutes?: number;
  interviewer_name?: string;
  interviewer_email?: string;
  meeting_link?: string;
  preparation_notes?: string;
  feedback?: string;
  interview_score?: number;
  status: InterviewStatus;
  created_at: string;
  updated_at: string;
}

export type InterviewStatus = "scheduled" | "completed" | "cancelled" | "rescheduled";

export interface ApplicationActivity {
  id: string;
  application_id: string;
  activity_type: string;
  description?: string;
  previous_status?: string;
  new_status?: string;
  created_at: string;
}

export interface JobOffer {
  id: string;
  application_id: string;
  status: OfferStatus;
  salary?: number;
  start_date?: string;
  bonus?: number;
  benefits?: string;
  offer_letter_url?: string;
  offer_expiration_date?: string;
  negotiation_notes?: string;
  accepted_date?: string;
  created_at: string;
  updated_at: string;
}

export type OfferStatus = "received" | "accepted" | "declined" | "pending";

// Request/Response types

export interface JobApplicationCreateRequest {
  job_id: string;
  applied_via?: string;
  cover_letter_id?: string;
  resume_id?: string;
  notes?: string;
}

export interface JobApplicationUpdateRequest {
  status?: ApplicationStatus;
  notes?: string;
  cover_letter_id?: string;
  resume_id?: string;
}

export interface InterviewCreateRequest {
  interview_type?: string;
  scheduled_date?: string;
  duration_minutes?: number;
  interviewer_name?: string;
  interviewer_email?: string;
  meeting_link?: string;
  preparation_notes?: string;
}

export interface InterviewUpdateRequest extends InterviewCreateRequest {
  status?: InterviewStatus;
  feedback?: string;
  interview_score?: number;
}

export interface JobOfferCreateRequest {
  salary?: number;
  start_date?: string;
  bonus?: number;
  benefits?: string;
  offer_letter_url?: string;
  offer_expiration_date?: string;
}

export interface JobOfferUpdateRequest extends JobOfferCreateRequest {
  status?: OfferStatus;
  negotiation_notes?: string;
}

export interface BulkStatusUpdateRequest {
  application_ids: string[];
  new_status: ApplicationStatus;
  notes?: string;
}

export interface ApplicationStats {
  total_applications: number;
  status_breakdown: Record<ApplicationStatus, number>;
  total_interviews: number;
  completed_interviews: number;
  offers_received: number;
  offers_accepted: number;
  rejection_rate: number;
  average_time_to_interview?: number;
  average_time_to_offer?: number;
}

export interface ApplicationSummary {
  application_id: string;
  job_title: string;
  company: string;
  status: ApplicationStatus;
  days_in_status: number;
  next_step?: string;
  interview_count: number;
  last_activity?: string;
  last_activity_date?: string;
}
