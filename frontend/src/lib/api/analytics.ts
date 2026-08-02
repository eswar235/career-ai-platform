/**
 * Analytics API Client
 */

import { apiClient } from "./client";
import type {
  ApplicationStatistics,
  DashboardResponse,
  TrendsResponse,
  TopRolesResponse,
  TopCompaniesResponse,
  SourceBreakdownResponse,
  DetailedBreakdownResponse,
  InsightsResponse,
  ExportResponse,
} from "@/lib/types/analytics";

const BASE_PATH = "/api/analytics";

/**
 * Dashboard Operations
 */
export const dashboardAPI = {
  async getDashboard(): Promise<DashboardResponse> {
    const response = await apiClient.get(`${BASE_PATH}/dashboard`);
    return response.data;
  },
};

/**
 * Statistics Operations
 */
export const statisticsAPI = {
  async getStatistics(): Promise<ApplicationStatistics> {
    const response = await apiClient.get(`${BASE_PATH}/statistics`);
    return response.data;
  },
};

/**
 * Trends Operations
 */
export const trendsAPI = {
  async getTrends(period?: string): Promise<TrendsResponse> {
    const params: any = {};
    if (period) params.period = period;

    const response = await apiClient.get(`${BASE_PATH}/trends`, { params });
    return response.data;
  },
};

/**
 * Top Roles Operations
 */
export const rolesAPI = {
  async getTopRoles(limit?: number): Promise<TopRolesResponse> {
    const params: any = {};
    if (limit) params.limit = limit;

    const response = await apiClient.get(`${BASE_PATH}/top-roles`, { params });
    return response.data;
  },
};

/**
 * Top Companies Operations
 */
export const companiesAPI = {
  async getTopCompanies(limit?: number): Promise<TopCompaniesResponse> {
    const params: any = {};
    if (limit) params.limit = limit;

    const response = await apiClient.get(`${BASE_PATH}/top-companies`, {
      params,
    });
    return response.data;
  },
};

/**
 * Source Operations
 */
export const sourceAPI = {
  async getSourceBreakdown(): Promise<SourceBreakdownResponse> {
    const response = await apiClient.get(`${BASE_PATH}/sources`);
    return response.data;
  },
};

/**
 * Breakdown Operations
 */
export const breakdownAPI = {
  async getDetailedBreakdown(): Promise<DetailedBreakdownResponse> {
    const response = await apiClient.get(`${BASE_PATH}/breakdown`);
    return response.data;
  },
};

/**
 * Insights Operations
 */
export const insightsAPI = {
  async getInsights(): Promise<InsightsResponse> {
    const response = await apiClient.get(`${BASE_PATH}/insights`);
    return response.data;
  },
};

/**
 * Export Operations
 */
export const exportAPI = {
  async exportApplications(): Promise<Blob> {
    const response = await apiClient.get(`${BASE_PATH}/export`, {
      responseType: "blob",
    });
    return response.data;
  },

  async downloadCSV(): Promise<void> {
    const blob = await exportAPI.exportApplications();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `applications-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
};
