/**
 * Resume optimization types for TypeScript
 */

export interface OptimizationScoreBreakdown {
  ats_score: number;
  keyword_score: number;
  formatting_score: number;
  readability_score: number;
  overall_score: number;
}

export interface OptimizationSuggestion {
  id: string;
  optimization_id: string;
  category: string;
  suggestion: string;
  priority: string;
  impact_score?: number;
  created_at: string;
}

export interface ResumeOptimizationResponse {
  id: string;
  user_id: string;
  original_content: string;
  optimized_content?: string;
  ats_score?: number;
  keyword_score?: number;
  formatting_score?: number;
  readability_score?: number;
  overall_score?: number;
  created_at: string;
  updated_at: string;
  suggestions?: OptimizationSuggestion[];
}

export interface TailoredResumeResponse {
  id: string;
  user_id: string;
  job_id: string;
  tailored_content: string;
  match_keywords?: number;
  ats_score?: number;
  keyword_score?: number;
  recommendations?: string[];
  created_at: string;
  updated_at: string;
}

export interface KeywordAnalysis {
  keywords: string[];
  keyword_count: number;
}
