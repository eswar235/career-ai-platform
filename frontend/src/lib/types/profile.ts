/**
 * Profile types for TypeScript
 */

export interface SkillResponse {
  id: string;
  profile_id: string;
  skill_name: string;
  proficiency_level?: string;
  years_of_experience?: number;
  endorsed_count: number;
  created_at: string;
  updated_at: string;
}

export interface SkillCreate {
  skill_name: string;
  proficiency_level?: string;
  years_of_experience?: number;
}

export interface SkillUpdate {
  proficiency_level?: string;
  years_of_experience?: number;
}

export interface ExperienceResponse {
  id: string;
  profile_id: string;
  job_title: string;
  company_name: string;
  company_industry?: string;
  employment_type?: string;
  location?: string;
  description?: string;
  start_date: string;
  end_date?: string;
  currently_working: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExperienceCreate {
  job_title: string;
  company_name: string;
  company_industry?: string;
  employment_type?: string;
  location?: string;
  description?: string;
  start_date: string;
  end_date?: string;
  currently_working?: boolean;
}

export interface ExperienceUpdate {
  job_title?: string;
  company_name?: string;
  company_industry?: string;
  employment_type?: string;
  location?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  currently_working?: boolean;
}

export interface EducationResponse {
  id: string;
  profile_id: string;
  institution_name: string;
  degree?: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  grade?: string;
  activities_societies?: string;
  created_at: string;
  updated_at: string;
}

export interface EducationCreate {
  institution_name: string;
  degree?: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  grade?: string;
  activities_societies?: string;
}

export interface EducationUpdate {
  institution_name?: string;
  degree?: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  grade?: string;
  activities_societies?: string;
}

export interface ProjectResponse {
  id: string;
  profile_id: string;
  project_name: string;
  description?: string;
  skills_used?: string[];
  start_date?: string;
  end_date?: string;
  project_url?: string;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  project_name: string;
  description?: string;
  skills_used?: string[];
  start_date?: string;
  end_date?: string;
  project_url?: string;
  image_url?: string;
}

export interface ProjectUpdate {
  project_name?: string;
  description?: string;
  skills_used?: string[];
  start_date?: string;
  end_date?: string;
  project_url?: string;
  image_url?: string;
}

export interface CertificationResponse {
  id: string;
  profile_id: string;
  certification_name: string;
  issuing_organization?: string;
  issue_date?: string;
  expiration_date?: string;
  credential_id?: string;
  credential_url?: string;
  created_at: string;
  updated_at: string;
}

export interface CertificationCreate {
  certification_name: string;
  issuing_organization?: string;
  issue_date?: string;
  expiration_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface CertificationUpdate {
  certification_name?: string;
  issuing_organization?: string;
  issue_date?: string;
  expiration_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface ProfileCompletionTrackingResponse {
  id: string;
  profile_id: string;
  personal_info_complete: boolean;
  skills_added: boolean;
  experience_added: boolean;
  education_added: boolean;
  projects_added: boolean;
  certifications_added: boolean;
  profile_picture_added: boolean;
  professional_summary_added: boolean;
  last_updated: string;
}

export interface UserProfileResponse {
  id: string;
  user_id: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  headline?: string;
  professional_summary?: string;
  profile_picture_url?: string;
  completion_percentage: number;
  verified_by_user: boolean;
  created_from_resume_id?: string;
  created_at: string;
  updated_at: string;
  skills?: SkillResponse[];
  experiences?: ExperienceResponse[];
  education?: EducationResponse[];
  projects?: ProjectResponse[];
  certifications?: CertificationResponse[];
  completion_tracking?: ProfileCompletionTrackingResponse;
}

export interface UserProfileDetailResponse {
  id: string;
  user_id: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  headline?: string;
  professional_summary?: string;
  profile_picture_url?: string;
  completion_percentage: number;
  verified_by_user: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfileCreate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  headline?: string;
  professional_summary?: string;
  profile_picture_url?: string;
}

export interface UserProfileUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  headline?: string;
  professional_summary?: string;
  profile_picture_url?: string;
  verified_by_user?: boolean;
}
