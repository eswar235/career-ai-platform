/**
 * Notification API Client
 */

import { apiClient } from "./client";
import type {
  JobAlert,
  Notification,
  EmailNotification,
  AlertJobMatch,
  NotificationPreferences,
  JobAlertCreateRequest,
  JobAlertUpdateRequest,
  NotificationsSummaryResponse,
  AlertMatchesResponse,
  NotificationPreferencesUpdateRequest,
} from "@/lib/types/notification";

const BASE_PATH = "/api/notifications";

/**
 * Job Alert Operations
 */
export const jobAlertAPI = {
  async createOrUpdate(
    request: JobAlertCreateRequest
  ): Promise<JobAlert> {
    const response = await apiClient.post(`${BASE_PATH}/alerts`, request);
    return response.data;
  },

  async get(): Promise<JobAlert> {
    const response = await apiClient.get(`${BASE_PATH}/alerts`);
    return response.data;
  },

  async update(request: JobAlertUpdateRequest): Promise<JobAlert> {
    const response = await apiClient.put(`${BASE_PATH}/alerts`, request);
    return response.data;
  },

  async toggle(isActive: boolean): Promise<JobAlert> {
    const response = await apiClient.post(
      `${BASE_PATH}/alerts/toggle`,
      {},
      { params: { is_active: isActive } }
    );
    return response.data;
  },
};

/**
 * Alert Matches Operations
 */
export const alertMatchesAPI = {
  async getMatches(
    skip?: number,
    limit?: number
  ): Promise<AlertMatchesResponse> {
    const params: any = {};
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get(`${BASE_PATH}/alert-matches`, {
      params,
    });
    return response.data;
  },

  async dismissMatch(matchId: string): Promise<AlertJobMatch> {
    const response = await apiClient.post(
      `${BASE_PATH}/alert-matches/${matchId}/dismiss`
    );
    return response.data;
  },
};

/**
 * In-App Notification Operations
 */
export const notificationAPI = {
  async getNotifications(
    unreadOnly?: boolean,
    skip?: number,
    limit?: number
  ): Promise<NotificationsSummaryResponse> {
    const params: any = {};
    if (unreadOnly !== undefined) params.unread_only = unreadOnly;
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get(BASE_PATH, { params });
    return response.data;
  },

  async getNotification(notificationId: string): Promise<Notification> {
    const response = await apiClient.get(
      `${BASE_PATH}/${notificationId}`
    );
    return response.data;
  },

  async markAsRead(notificationId: string): Promise<Notification> {
    const response = await apiClient.put(
      `${BASE_PATH}/${notificationId}/read`
    );
    return response.data;
  },

  async markAllAsRead(): Promise<{ marked_as_read: number }> {
    const response = await apiClient.post(`${BASE_PATH}/read-all`);
    return response.data;
  },

  async delete(notificationId: string): Promise<{ deleted: boolean }> {
    const response = await apiClient.delete(
      `${BASE_PATH}/${notificationId}`
    );
    return response.data;
  },
};

/**
 * Notification Preferences Operations
 */
export const preferencesAPI = {
  async getPreferences(): Promise<NotificationPreferences> {
    const response = await apiClient.get(`${BASE_PATH}/preferences`);
    return response.data;
  },

  async updatePreferences(
    request: NotificationPreferencesUpdateRequest
  ): Promise<NotificationPreferences> {
    const response = await apiClient.put(
      `${BASE_PATH}/preferences`,
      request
    );
    return response.data;
  },
};
