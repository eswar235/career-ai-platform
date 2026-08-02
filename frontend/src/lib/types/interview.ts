/**
 * Interview Coaching Types
 */

export type SessionType = "technical" | "behavioral" | "general" | "role_specific";
export type DifficultyLevel = "easy" | "medium" | "hard";
export type QuestionType = "behavioral" | "technical" | "situation";

export interface InterviewSession {
  id: string;
  user_id: string;
  job_id: string;
  session_type?: SessionType;
  difficulty_level?: DifficultyLevel;
  industry?: string;
  role?: string;
  total_questions?: number;
  questions_answered: number;
  overall_score?: number;
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewSessionDetail extends InterviewSession {
  questions: InterviewQuestion[];
}

export interface InterviewQuestion {
  id: string;
  session_id: string;
  question_text: string;
  question_type?: QuestionType;
  category?: string;
  question_order: number;
  time_limit_seconds?: number;
  created_at: string;
  answer?: InterviewAnswer;
}

export interface InterviewAnswer {
  id: string;
  question_id: string;
  user_answer?: string;
  answer_time_seconds?: number;
  score?: number;
  feedback?: string;
  strengths?: string;
  improvements?: string;
  ai_model?: string;
  created_at: string;
}

export interface InterviewTip {
  id: string;
  user_id: string;
  category?: string;
  tip_text: string;
  tip_order?: number;
  helpful_count: number;
  created_at: string;
}

export interface InterviewMetrics {
  id: string;
  user_id: string;
  average_score?: number;
  total_sessions: number;
  total_questions: number;
  strongest_category?: string;
  weakest_category?: string;
  improvement_rate?: number;
  last_updated: string;
}

// Request/Response types

export interface InterviewSessionCreateRequest {
  job_id: string;
  session_type: SessionType;
  difficulty_level?: DifficultyLevel;
  industry?: string;
  role?: string;
  num_questions?: number;
}

export interface InterviewAnswerCreateRequest {
  user_answer: string;
  answer_time_seconds?: number;
}

export interface SessionResultsResponse {
  session_id: string;
  overall_score: number;
  total_questions: number;
  questions_answered: number;
  duration_seconds: number;
  category_scores: Record<string, number>;
  strengths: string[];
  improvements: string[];
  next_steps: string[];
}

export interface QuestionFeedbackResponse {
  question_id: string;
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
  best_answer?: string;
}

export interface ProgressReportResponse {
  total_sessions: number;
  average_score: number;
  best_score: number;
  worst_score: number;
  categories_covered: string[];
  recommended_focus: string[];
  estimated_readiness: number;
}
