/**
 * Application Tracking API Client
 */

import { apiClient } from "./client";
import type {
  JobApplication,
  JobApplicationDetail,
  Interview,
  JobOffer,
  JobApplicationCreateRequest,
  JobApplicationUpdateRequest,
  InterviewCreateRequest,
  InterviewUpdateRequest,
  JobOfferCreateRequest,
  JobOfferUpdateRequest,
} from "@/lib/types/application";

const BASE_PATH = "/api/applications";

/**
 * Job Application Operations
 */
export const applicationAPI = {
  async create(
    request: JobApplicationCreateRequest
  ): Promise<JobApplication> {
    const response = await apiClient.post(BASE_PATH, request);
    return response.data;
  },

  async get(applicationId: string): Promise<JobApplicationDetail> {
    const response = await apiClient.get(`${BASE_PATH}/${applicationId}`);
    return response.data;
  },

  async list(
    status?: string,
    skip?: number,
    limit?: number
  ): Promise<JobApplication[]> {
    const params: any = {};
    if (status) params.status = status;
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get(BASE_PATH, { params });
    return response.data;
  },

  async getForJob(jobId: string): Promise<JobApplication> {
    const response = await apiClient.get(`${BASE_PATH}/job/${jobId}`);
    return response.data;
  },

  async update(
    applicationId: string,
    request: JobApplicationUpdateRequest
  ): Promise<JobApplication> {
    const response = await apiClient.put(
      `${BASE_PATH}/${applicationId}`,
      request
    );
    return response.data;
  },

  async updateStatus(
    applicationId: string,
    newStatus: string,
    notes?: string
  ): Promise<JobApplication> {
    const params: any = { new_status: newStatus };
    if (notes) params.notes = notes;

    const response = await apiClient.put(
      `${BASE_PATH}/${applicationId}/status`,
      {},
      { params }
    );
    return response.data;
  },

  async delete(applicationId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${applicationId}`);
  },
};

/**
 * Interview Operations
 */
export const interviewAPI = {
  async create(
    applicationId: string,
    request: InterviewCreateRequest
  ): Promise<Interview> {
    const response = await apiClient.post(
      `${BASE_PATH}/${applicationId}/interviews`,
      request
    );
    return response.data;
  },

  async list(applicationId: string): Promise<Interview[]> {
    const response = await apiClient.get(
      `${BASE_PATH}/${applicationId}/interviews`
    );
    return response.data;
  },

  async update(
    interviewId: string,
    request: InterviewUpdateRequest
  ): Promise<Interview> {
    const response = await apiClient.put(
      `${BASE_PATH}/interviews/${interviewId}`,
      request
    );
    return response.data;
  },

  async delete(interviewId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/interviews/${interviewId}`);
  },
};

/**
 * Job Offer Operations
 */
export const offerAPI = {
  async create(
    applicationId: string,
    request: JobOfferCreateRequest
  ): Promise<JobOffer> {
    const response = await apiClient.post(
      `${BASE_PATH}/${applicationId}/offers`,
      request
    );
    return response.data;
  },

  async get(applicationId: string): Promise<JobOffer> {
    const response = await apiClient.get(
      `${BASE_PATH}/${applicationId}/offers`
    );
    return response.data;
  },

  async update(
    offerId: string,
    request: JobOfferUpdateRequest
  ): Promise<JobOffer> {
    const response = await apiClient.put(
      `${BASE_PATH}/offers/${offerId}`,
      request
    );
    return response.data;
  },

  async accept(offerId: string): Promise<JobOffer> {
    const response = await apiClient.post(
      `${BASE_PATH}/offers/${offerId}/accept`
    );
    return response.data;
  },

  async decline(offerId: string, reason?: string): Promise<JobOffer> {
    const params: any = {};
    if (reason) params.reason = reason;

    const response = await apiClient.post(
      `${BASE_PATH}/offers/${offerId}/decline`,
      {},
      { params }
    );
    return response.data;
  },

  async delete(offerId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/offers/${offerId}`);
  },
};
