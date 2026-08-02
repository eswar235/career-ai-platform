/**
 * Cover Letter Types
 */

export interface CoverLetter {
  id: string;
  user_id: string;
  job_id: string;
  content: string;
  version_number: number;
  is_draft: boolean;
  custom_edits?: string;
  ai_model?: string;
  generated_at: string;
  created_at: string;
  updated_at: string;
}

export interface CoverLetterDetail extends CoverLetter {
  exports: LetterExport[];
}

export interface CoverLetterCreateRequest {
  job_id: string;
  template_id?: string;
}

export interface CoverLetterUpdateRequest {
  content?: string;
  is_draft?: boolean;
  custom_edits?: string;
}

export interface GenerateCoverLetterRequest {
  job_id: string;
  template_id?: string;
  use_profile?: boolean;
}

export interface GenerateCoverLetterResponse {
  id: string;
  content: string;
  version_number: number;
  generated_at: string;
}

export interface BatchGenerateCoverLettersRequest {
  job_ids: string[];
  template_id?: string;
}

export interface BatchGenerateCoverLettersResponse {
  generated: number;
  job_ids: string[];
  timestamp: string;
}

export interface PublishCoverLetterRequest {
  version_id: string;
}

export interface PublishCoverLetterResponse {
  id: string;
  is_draft: boolean;
  published_at: string;
}

export interface LetterTemplate {
  id: string;
  user_id: string;
  name: string;
  content: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface LetterTemplateCreateRequest {
  name: string;
  content: string;
  is_default?: boolean;
}

export interface LetterTemplateUpdateRequest {
  name?: string;
  content?: string;
  is_default?: boolean;
}

export interface LetterExport {
  id: string;
  cover_letter_id: string;
  format: "pdf" | "docx" | "txt";
  file_url?: string;
  file_size?: number;
  exported_at: string;
  created_at: string;
}

export interface LetterExportCreateRequest {
  format: "pdf" | "docx" | "txt";
}

export type ExportFormat = "pdf" | "docx" | "txt";

export interface CoverLetterListResponse {
  total: number;
  items: CoverLetter[];
  page: number;
  page_size: number;
}

export interface TemplateListResponse {
  total: number;
  items: LetterTemplate[];
  page: number;
  page_size: number;
}

export interface ExportListResponse {
  items: LetterExport[];
}

export interface GenerationStatus {
  total: number;
  generated: number;
  failed: number;
  status: "pending" | "in_progress" | "completed" | "failed";
}
