/**
 * Browser Automation API Client
 */

import { apiClient } from "./client";
import type {
  AutomationJob,
  AutomationJobDetail,
  AutomationStep,
  AutomationLog,
  AutomationJobCreateRequest,
  AutomationStepCreateRequest,
  AutomationStatusResponse,
  BulkAutomationRequest,
  BulkAutomationResponse,
} from "@/lib/types/automation";

const BASE_PATH = "/api/automation";

/**
 * Automation Job Operations
 */
export const automationAPI = {
  /**
   * Create automation job
   */
  async create(request: AutomationJobCreateRequest): Promise<AutomationJob> {
    const response = await apiClient.post(BASE_PATH, request);
    return response.data;
  },

  /**
   * Get automation job
   */
  async get(automationId: string): Promise<AutomationJobDetail> {
    const response = await apiClient.get(`${BASE_PATH}/${automationId}`);
    return response.data;
  },

  /**
   * List automation jobs
   */
  async list(
    status?: string,
    skip?: number,
    limit?: number
  ): Promise<AutomationJob[]> {
    const params: any = {};
    if (status) params.status = status;
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get(BASE_PATH, { params });
    return response.data;
  },

  /**
   * Get automation status
   */
  async getStatus(automationId: string): Promise<AutomationStatusResponse> {
    const response = await apiClient.get(`${BASE_PATH}/${automationId}/status`);
    return response.data;
  },

  /**
   * Start automation job
   */
  async start(automationId: string): Promise<AutomationStatusResponse> {
    const response = await apiClient.post(
      `${BASE_PATH}/${automationId}/start`
    );
    return response.data;
  },

  /**
   * Stop automation job
   */
  async stop(automationId: string): Promise<AutomationStatusResponse> {
    const response = await apiClient.post(`${BASE_PATH}/${automationId}/stop`);
    return response.data;
  },

  /**
   * Delete automation job
   */
  async delete(automationId: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${automationId}`);
  },

  /**
   * Create bulk automation jobs
   */
  async createBulk(request: BulkAutomationRequest): Promise<BulkAutomationResponse> {
    const response = await apiClient.post(`${BASE_PATH}/bulk`, request);
    return response.data;
  },
};

/**
 * Automation Step Operations
 */
export const automationStepAPI = {
  /**
   * Add step to automation
   */
  async create(
    automationId: string,
    request: AutomationStepCreateRequest
  ): Promise<AutomationStep> {
    const response = await apiClient.post(
      `${BASE_PATH}/${automationId}/steps`,
      request
    );
    return response.data;
  },

  /**
   * Get all steps for automation
   */
  async list(automationId: string): Promise<AutomationStep[]> {
    const response = await apiClient.get(`${BASE_PATH}/${automationId}/steps`);
    return response.data;
  },
};
