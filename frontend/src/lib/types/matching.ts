/**
 * Job matching types for TypeScript
 */

export interface SkillAnalysis {
  user_skills: string[];
  job_required_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  match_count: number;
  missing_count: number;
  skill_match_percentage: number;
}

export interface JobMatchResponse {
  id: string;
  user_id: string;
  job_id: string;
  match_percentage: number;
  match_score: number;
  skills_match?: number;
  skills_missing?: number;
  strengths?: string[];
  gaps?: string[];
  recommendations?: string[];
  created_at: string;
  updated_at: string;
}

export interface JobMatchDetailResponse {
  id: string;
  user_id: string;
  job_id: string;
  match_percentage: number;
  match_score: number;
  skills_match?: number;
  skills_missing?: number;
  strengths?: string[];
  gaps?: string[];
  recommendations?: string[];
  job?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UserMatchesList {
  total: number;
  skip: number;
  limit: number;
  matches: JobMatchResponse[];
}

export interface BulkMatchingResponse {
  total_matches: number;
  matched_jobs: number;
  high_matches: number;
  moderate_matches: number;
  low_matches: number;
  timestamp: string;
}

export interface MatchingResponse {
  user_id: string;
  job_id: string;
  match_percentage: number;
  match_score: number;
  skill_analysis: SkillAnalysis;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
}
