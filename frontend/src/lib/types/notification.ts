/**
 * Notification Types
 */

export type NotificationType = "job_alert" | "application_update" | "interview_reminder";
export type NotificationFrequency = "real-time" | "daily" | "weekly";
export type EmailStatus = "pending" | "sent" | "failed" | "bounced";

export interface JobAlert {
  id: string;
  user_id: string;
  keywords?: string;
  locations?: string[];
  job_titles?: string[];
  experience_levels?: string[];
  salary_min?: number;
  salary_max?: number;
  min_match_score: number;
  notification_frequency: NotificationFrequency;
  preferred_time?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  notification_type: NotificationType;
  title: string;
  message: string;
  related_entity_type?: string;
  related_entity_id?: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EmailNotification {
  id: string;
  user_id: string;
  email_address: string;
  notification_type: NotificationType;
  subject: string;
  body: string;
  status: EmailStatus;
  sent_at?: string;
  delivery_error?: string;
  created_at: string;
}

export interface AlertJobMatch {
  id: string;
  alert_id: string;
  job_id: string;
  match_score?: number;
  notification_sent: boolean;
  user_dismissed: boolean;
  created_at: string;
}

export interface NotificationPreferences {
  id: string;
  user_id: string;
  job_alerts_enabled: boolean;
  application_updates_enabled: boolean;
  interview_reminders_enabled: boolean;
  daily_digest_enabled: boolean;
  digest_time?: string;
  email_notifications_enabled: boolean;
  in_app_notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// Request/Response types

export interface JobAlertCreateRequest {
  keywords?: string;
  locations?: string[];
  job_titles?: string[];
  experience_levels?: string[];
  salary_min?: number;
  salary_max?: number;
  min_match_score?: number;
  notification_frequency?: NotificationFrequency;
  preferred_time?: string;
}

export interface JobAlertUpdateRequest {
  keywords?: string;
  locations?: string[];
  job_titles?: string[];
  experience_levels?: string[];
  salary_min?: number;
  salary_max?: number;
  min_match_score?: number;
  notification_frequency?: NotificationFrequency;
  preferred_time?: string;
  is_active?: boolean;
}

export interface NotificationsSummaryResponse {
  total_unread: number;
  total_notifications: number;
  job_alerts_count: number;
  application_updates_count: number;
  interview_reminders_count: number;
  notifications: Notification[];
}

export interface AlertMatchesResponse {
  total_matches: number;
  new_matches: number;
  matches: AlertJobMatch[];
}

export interface NotificationPreferencesUpdateRequest {
  job_alerts_enabled?: boolean;
  application_updates_enabled?: boolean;
  interview_reminders_enabled?: boolean;
  daily_digest_enabled?: boolean;
  digest_time?: string;
  email_notifications_enabled?: boolean;
  in_app_notifications_enabled?: boolean;
}
