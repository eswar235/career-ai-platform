/**
 * Analytics Hooks
 */

import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  dashboardAPI,
  statisticsAPI,
  trendsAPI,
  rolesAPI,
  companiesAPI,
  sourceAPI,
  breakdownAPI,
  insightsAPI,
  exportAPI,
} from "@/lib/api/analytics";

/**
 * Dashboard Hook
 */
export const useDashboard = () => {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => dashboardAPI.getDashboard(),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
};

/**
 * Statistics Hook
 */
export const useStatistics = () => {
  return useQuery({
    queryKey: ["statistics"],
    queryFn: () => statisticsAPI.getStatistics(),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Trends Hook
 */
export const useTrends = (period: string = "30days") => {
  return useQuery({
    queryKey: ["trends", period],
    queryFn: () => trendsAPI.getTrends(period),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Top Roles Hook
 */
export const useTopRoles = (limit: number = 5) => {
  return useQuery({
    queryKey: ["top-roles", limit],
    queryFn: () => rolesAPI.getTopRoles(limit),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Top Companies Hook
 */
export const useTopCompanies = (limit: number = 5) => {
  return useQuery({
    queryKey: ["top-companies", limit],
    queryFn: () => companiesAPI.getTopCompanies(limit),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Source Breakdown Hook
 */
export const useSourceBreakdown = () => {
  return useQuery({
    queryKey: ["source-breakdown"],
    queryFn: () => sourceAPI.getSourceBreakdown(),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Detailed Breakdown Hook
 */
export const useDetailedBreakdown = () => {
  return useQuery({
    queryKey: ["detailed-breakdown"],
    queryFn: () => breakdownAPI.getDetailedBreakdown(),
    refetchInterval: 5 * 60 * 1000,
  });
};

/**
 * Insights Hook
 */
export const useInsights = () => {
  return useQuery({
    queryKey: ["insights"],
    queryFn: () => insightsAPI.getInsights(),
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
};

/**
 * Export Hook
 */
export const useExport = () => {
  const queryClient = useQueryClient();

  const download = async () => {
    try {
      await exportAPI.downloadCSV();
    } catch (error) {
      console.error("Failed to export:", error);
      throw error;
    }
  };

  return {
    download,
  };
};

/**
 * Combined Analytics Hook
 */
export const useAnalytics = () => {
  const dashboard = useDashboard();
  const statistics = useStatistics();
  const trends = useTrends("30days");
  const topRoles = useTopRoles();
  const topCompanies = useTopCompanies();
  const sourceBreakdown = useSourceBreakdown();
  const insights = useInsights();

  return {
    dashboard,
    statistics,
    trends,
    topRoles,
    topCompanies,
    sourceBreakdown,
    insights,
    isLoading:
      dashboard.isLoading ||
      statistics.isLoading ||
      trends.isLoading ||
      topRoles.isLoading ||
      topCompanies.isLoading ||
      sourceBreakdown.isLoading ||
      insights.isLoading,
    isError:
      dashboard.isError ||
      statistics.isError ||
      trends.isError ||
      topRoles.isError ||
      topCompanies.isError ||
      sourceBreakdown.isError ||
      insights.isError,
  };
};
