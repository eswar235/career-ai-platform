/**
 * Job Matching API client
 */

import { apiClient } from './client';
import {
  JobMatchResponse,
  JobMatchDetailResponse,
  SkillAnalysis,
  UserMatchesList,
  BulkMatchingResponse,
} from '../types/matching';

export const matchingApi = {
  // Embedding endpoints
  async createResumeEmbedding(): Promise<{ user_id: string; created_at: string; skills_extracted?: string[] }> {
    const response = await apiClient.post('/api/matching/embeddings/resume');
    return response.data;
  },

  async createJobEmbedding(jobId: string): Promise<{ job_id: string; created_at: string; skills?: string[] }> {
    const response = await apiClient.post(`/api/matching/embeddings/job/${jobId}`);
    return response.data;
  },

  // Skill analysis
  async analyzeSkills(jobId: string): Promise<SkillAnalysis> {
    const response = await apiClient.get(`/api/matching/skills/analysis/${jobId}`);
    return response.data;
  },

  // Job matching
  async computeJobMatch(jobId: string): Promise<JobMatchResponse> {
    const response = await apiClient.post(`/api/matching/jobs/${jobId}`);
    return response.data;
  },

  async getMatchDetail(jobId: string): Promise<JobMatchDetailResponse> {
    const response = await apiClient.get(`/api/matching/jobs/${jobId}/detail`);
    return response.data;
  },

  async getTopMatches(
    minPercentage?: number,
    skip?: number,
    limit?: number
  ): Promise<UserMatchesList> {
    const params = new URLSearchParams();
    if (minPercentage !== undefined) params.append('min_percentage', String(minPercentage));
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/matching/top?${params}`);
    return response.data;
  },

  async getHighMatches(skip?: number, limit?: number): Promise<UserMatchesList> {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/matching/high?${params}`);
    return response.data;
  },

  async getModerateMatches(skip?: number, limit?: number): Promise<UserMatchesList> {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/matching/moderate?${params}`);
    return response.data;
  },

  async computeBulkMatches(): Promise<BulkMatchingResponse> {
    const response = await apiClient.post('/api/matching/bulk');
    return response.data;
  },
};
