/**
 * Jobs API client
 */

import { apiClient } from './client';
import {
  JobResponse,
  JobCreate,
  JobUpdate,
  JobSearchFilters,
  JobSearchResults,
  SavedJobResponse,
  SavedJobCreate,
  JobSearchHistoryResponse,
  JobApplicationResponse,
  JobApplicationCreate,
  JobApplicationUpdate,
  ApplicationStats,
} from '../types/jobs';

export const jobsApi = {
  // Job endpoints
  async createJob(data: JobCreate): Promise<JobResponse> {
    const response = await apiClient.post('/api/jobs', data);
    return response.data;
  },

  async searchJobs(filters: JobSearchFilters): Promise<JobSearchResults> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
    const response = await apiClient.get(`/api/jobs/search?${params}`);
    return response.data;
  },

  async getJob(jobId: string): Promise<JobResponse> {
    const response = await apiClient.get(`/api/jobs/${jobId}`);
    return response.data;
  },

  async updateJob(jobId: string, data: JobUpdate): Promise<JobResponse> {
    const response = await apiClient.patch(`/api/jobs/${jobId}`, data);
    return response.data;
  },

  // Saved jobs endpoints
  async saveJob(data: SavedJobCreate): Promise<SavedJobResponse> {
    const response = await apiClient.post('/api/jobs/saved', data);
    return response.data;
  },

  async getSavedJobs(skip?: number, limit?: number): Promise<SavedJobResponse[]> {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/jobs/saved/list?${params}`);
    return response.data;
  },

  async isJobSaved(jobId: string): Promise<{ job_id: string; is_saved: boolean }> {
    const response = await apiClient.get(`/api/jobs/${jobId}/saved`);
    return response.data;
  },

  async unsaveJob(jobId: string): Promise<void> {
    await apiClient.delete(`/api/jobs/saved/${jobId}`);
  },

  // Search history endpoints
  async getSearchHistory(limit?: number): Promise<JobSearchHistoryResponse[]> {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append('limit', String(limit));
    const response = await apiClient.get(`/api/jobs/history/list?${params}`);
    return response.data;
  },

  // Job applications endpoints
  async applyForJob(data: JobApplicationCreate): Promise<JobApplicationResponse> {
    const response = await apiClient.post('/api/jobs/applications', data);
    return response.data;
  },

  async getApplications(
    skip?: number,
    limit?: number,
    statusFilter?: string
  ): Promise<JobApplicationResponse[]> {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', String(skip));
    if (limit !== undefined) params.append('limit', String(limit));
    if (statusFilter) params.append('status_filter', statusFilter);
    const response = await apiClient.get(`/api/jobs/applications/list?${params}`);
    return response.data;
  },

  async updateApplication(
    applicationId: string,
    data: JobApplicationUpdate
  ): Promise<JobApplicationResponse> {
    const response = await apiClient.patch(
      `/api/jobs/applications/${applicationId}`,
      data
    );
    return response.data;
  },

  async getApplicationStats(): Promise<ApplicationStats> {
    const response = await apiClient.get('/api/jobs/applications/stats');
    return response.data;
  },
};
