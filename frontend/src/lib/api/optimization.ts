/**
 * Resume Optimization API client
 */

import { apiClient } from './client';
import {
  ResumeOptimizationResponse,
  OptimizationScoreBreakdown,
  TailoredResumeResponse,
  KeywordAnalysis,
} from '../types/optimization';

export const optimizationApi = {
  // Resume analysis
  async analyzeResume(content: string): Promise<ResumeOptimizationResponse> {
    const response = await apiClient.post('/api/optimization/analyze', {
      original_content: content,
    });
    return response.data;
  },

  async getAnalysis(): Promise<ResumeOptimizationResponse> {
    const response = await apiClient.get('/api/optimization/analysis');
    return response.data;
  },

  async getScores(): Promise<OptimizationScoreBreakdown> {
    const response = await apiClient.get('/api/optimization/scores');
    return response.data;
  },

  // Optimization
  async optimizeResume(): Promise<{ optimized_content: string; improved: boolean }> {
    const response = await apiClient.post('/api/optimization/optimize');
    return response.data;
  },

  async getOptimized(): Promise<{
    original_content: string;
    optimized_content?: string;
    overall_score?: number;
  }> {
    const response = await apiClient.get('/api/optimization/optimized');
    return response.data;
  },

  // Keywords
  async analyzeKeywords(): Promise<KeywordAnalysis> {
    const response = await apiClient.get('/api/optimization/keywords');
    return response.data;
  },

  // Tailored resumes
  async createTailoredResume(jobId: string): Promise<TailoredResumeResponse> {
    const response = await apiClient.post(`/api/optimization/tailor/${jobId}`);
    return response.data;
  },

  async getTailoredResume(jobId: string): Promise<TailoredResumeResponse> {
    const response = await apiClient.get(`/api/optimization/tailored/${jobId}`);
    return response.data;
  },

  async listTailoredResumes(skip?: number, limit?: number): Promise<TailoredResumeResponse[]> {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/optimization/tailored/list?${params}`);
    return response.data;
  },

  async deleteTailoredResume(jobId: string): Promise<void> {
    await apiClient.delete(`/api/optimization/tailored/${jobId}`);
  },
};
