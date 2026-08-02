/**
 * Interview Coaching API Client
 */

import { apiClient } from "./client";
import type {
  InterviewSession,
  InterviewSessionDetail,
  InterviewQuestion,
  InterviewAnswer,
  InterviewMetrics,
  SessionResultsResponse,
  InterviewSessionCreateRequest,
  InterviewAnswerCreateRequest,
} from "@/lib/types/interview";

const BASE_PATH = "/api/interviews";

/**
 * Interview Session Operations
 */
export const interviewSessionAPI = {
  async create(
    request: InterviewSessionCreateRequest
  ): Promise<InterviewSession> {
    const response = await apiClient.post(BASE_PATH, request);
    return response.data;
  },

  async get(sessionId: string): Promise<InterviewSessionDetail> {
    const response = await apiClient.get(`${BASE_PATH}/${sessionId}`);
    return response.data;
  },

  async list(
    skip?: number,
    limit?: number
  ): Promise<InterviewSession[]> {
    const params: any = {};
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get(BASE_PATH, { params });
    return response.data;
  },

  async complete(sessionId: string): Promise<SessionResultsResponse> {
    const response = await apiClient.post(
      `${BASE_PATH}/${sessionId}/complete`
    );
    return response.data;
  },
};

/**
 * Interview Question Operations
 */
export const interviewQuestionAPI = {
  async getQuestions(sessionId: string): Promise<InterviewQuestion[]> {
    const response = await apiClient.get(
      `${BASE_PATH}/${sessionId}/questions`
    );
    return response.data;
  },
};

/**
 * Interview Answer Operations
 */
export const interviewAnswerAPI = {
  async submitAnswer(
    questionId: string,
    request: InterviewAnswerCreateRequest
  ): Promise<InterviewAnswer> {
    const response = await apiClient.post(
      `${BASE_PATH}/${questionId}/answer`,
      request
    );
    return response.data;
  },
};

/**
 * Interview Metrics Operations
 */
export const interviewMetricsAPI = {
  async getMetrics(): Promise<InterviewMetrics> {
    const response = await apiClient.get(`${BASE_PATH}/metrics/performance`);
    return response.data;
  },
};
