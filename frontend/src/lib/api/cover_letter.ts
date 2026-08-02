/**
 * Cover Letter API Client
 */

import { apiClient } from "./client";
import type {
  CoverLetter,
  CoverLetterDetail,
  LetterTemplate,
  LetterExport,
  GenerateCoverLetterRequest,
  GenerateCoverLetterResponse,
  BatchGenerateCoverLettersRequest,
  BatchGenerateCoverLettersResponse,
  LetterTemplateCreateRequest,
  LetterTemplateUpdateRequest,
  CoverLetterUpdateRequest,
} from "@/lib/types/cover_letter";

const BASE_PATH = "/api/cover-letters";

/**
 * Cover Letter Operations
 */
export const coverLetterAPI = {
  /**
   * Generate a new cover letter using AI
   */
  async generate(
    request: GenerateCoverLetterRequest
  ): Promise<GenerateCoverLetterResponse> {
    const response = await apiClient.post(`${BASE_PATH}/generate`, request);
    return response.data;
  },

  /**
   * Generate cover letters for multiple jobs
   */
  async batchGenerate(
    request: BatchGenerateCoverLettersRequest
  ): Promise<BatchGenerateCoverLettersResponse> {
    const response = await apiClient.post(
      `${BASE_PATH}/batch-generate`,
      request
    );
    return response.data;
  },

  /**
   * Get a specific cover letter
   */
  async get(letterId: string): Promise<CoverLetterDetail> {
    const response = await apiClient.get(`${BASE_PATH}/${letterId}`);
    return response.data;
  },

  /**
   * Get the latest cover letter for a job
   */
  async getForJob(jobId: string): Promise<CoverLetter> {
    const response = await apiClient.get(`${BASE_PATH}/job/${jobId}`);
    return response.data;
  },

  /**
   * Update a cover letter
   */
  async update(
    letterId: string,
    request: CoverLetterUpdateRequest
  ): Promise<CoverLetter> {
    const response = await apiClient.put(`${BASE_PATH}/${letterId}`, request);
    return response.data;
  },

  /**
   * Publish a cover letter
   */
  async publish(letterId: string): Promise<CoverLetter> {
    const response = await apiClient.post(`${BASE_PATH}/${letterId}/publish`);
    return response.data;
  },

  /**
   * List all cover letters
   */
  async list(skip: number = 0, limit: number = 20): Promise<CoverLetter[]> {
    const response = await apiClient.get(BASE_PATH, {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Delete a cover letter
   */
  async delete(letterId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${letterId}`);
  },

  /**
   * Get all versions of a cover letter
   */
  async getVersions(letterId: string): Promise<CoverLetter[]> {
    const response = await apiClient.get(`${BASE_PATH}/${letterId}/versions`);
    return response.data;
  },

  /**
   * Export cover letter as PDF
   */
  async exportAsPDF(letterId: string): Promise<LetterExport> {
    const response = await apiClient.post(
      `${BASE_PATH}/${letterId}/export/pdf`
    );
    return response.data;
  },

  /**
   * Export cover letter as DOCX
   */
  async exportAsDOCX(letterId: string): Promise<LetterExport> {
    const response = await apiClient.post(
      `${BASE_PATH}/${letterId}/export/docx`
    );
    return response.data;
  },

  /**
   * Export cover letter as TXT
   */
  async exportAsTXT(letterId: string): Promise<LetterExport> {
    const response = await apiClient.post(`${BASE_PATH}/${letterId}/export/txt`);
    return response.data;
  },

  /**
   * Get all exports for a cover letter
   */
  async getExports(letterId: string): Promise<LetterExport[]> {
    const response = await apiClient.get(`${BASE_PATH}/${letterId}/exports`);
    return response.data;
  },
};

/**
 * Letter Template Operations
 */
export const letterTemplateAPI = {
  /**
   * Create a new letter template
   */
  async create(request: LetterTemplateCreateRequest): Promise<LetterTemplate> {
    const response = await apiClient.post(`${BASE_PATH}/templates`, request);
    return response.data;
  },

  /**
   * Get a specific template
   */
  async get(templateId: string): Promise<LetterTemplate> {
    const response = await apiClient.get(`${BASE_PATH}/templates/${templateId}`);
    return response.data;
  },

  /**
   * List all templates
   */
  async list(skip: number = 0, limit: number = 20): Promise<LetterTemplate[]> {
    const response = await apiClient.get(`${BASE_PATH}/templates`, {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Update a template
   */
  async update(
    templateId: string,
    request: LetterTemplateUpdateRequest
  ): Promise<LetterTemplate> {
    const response = await apiClient.put(
      `${BASE_PATH}/templates/${templateId}`,
      request
    );
    return response.data;
  },

  /**
   * Delete a template
   */
  async delete(templateId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/templates/${templateId}`);
  },
};
