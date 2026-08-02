/**
 * Notification Hooks
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobAlertAPI, alertMatchesAPI, notificationAPI, preferencesAPI } from "@/lib/api/notification";
import type {
  JobAlert,
  Notification,
  AlertJobMatch,
  NotificationPreferences,
  JobAlertCreateRequest,
  JobAlertUpdateRequest,
  NotificationPreferencesUpdateRequest,
} from "@/lib/types/notification";

/**
 * Job Alert Hook
 */
export const useJobAlert = () => {
  const queryClient = useQueryClient();

  /**
   * Get job alert
   */
  const getAlert = useQuery({
    queryKey: ["job-alert"],
    queryFn: () => jobAlertAPI.get(),
  });

  /**
   * Create/Update alert
   */
  const createOrUpdateAlert = useMutation({
    mutationFn: (request: JobAlertCreateRequest) =>
      jobAlertAPI.createOrUpdate(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["job-alert"] });
    },
  });

  /**
   * Update alert
   */
  const updateAlert = useMutation({
    mutationFn: (request: JobAlertUpdateRequest) =>
      jobAlertAPI.update(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["job-alert"] });
    },
  });

  /**
   * Toggle alert
   */
  const toggleAlert = useMutation({
    mutationFn: (isActive: boolean) => jobAlertAPI.toggle(isActive),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["job-alert"] });
    },
  });

  return {
    getAlert,
    createOrUpdateAlert,
    updateAlert,
    toggleAlert,
  };
};

/**
 * Alert Matches Hook
 */
export const useAlertMatches = () => {
  const queryClient = useQueryClient();

  /**
   * Get matches
   */
  const getMatches = (skip?: number, limit?: number) => {
    return useQuery({
      queryKey: ["alert-matches", skip, limit],
      queryFn: () => alertMatchesAPI.getMatches(skip, limit),
    });
  };

  /**
   * Dismiss match
   */
  const dismissMatch = useMutation({
    mutationFn: (matchId: string) => alertMatchesAPI.dismissMatch(matchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alert-matches"] });
    },
  });

  return {
    getMatches,
    dismissMatch,
  };
};

/**
 * Notifications Hook
 */
export const useNotifications = () => {
  const queryClient = useQueryClient();
  const [selectedNotificationId, setSelectedNotificationId] = useState<
    string | null
  >(null);

  /**
   * Get notifications
   */
  const getNotifications = (
    unreadOnly?: boolean,
    skip?: number,
    limit?: number
  ) => {
    return useQuery({
      queryKey: ["notifications", unreadOnly, skip, limit],
      queryFn: () =>
        notificationAPI.getNotifications(unreadOnly, skip, limit),
    });
  };

  /**
   * Get single notification
   */
  const getNotification = useQuery({
    queryKey: ["notification", selectedNotificationId],
    queryFn: () => {
      if (!selectedNotificationId) return Promise.reject("No ID");
      return notificationAPI.getNotification(selectedNotificationId);
    },
    enabled: !!selectedNotificationId,
  });

  /**
   * Mark as read
   */
  const markAsRead = useMutation({
    mutationFn: (notificationId: string) =>
      notificationAPI.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({
        queryKey: ["notification", selectedNotificationId],
      });
    },
  });

  /**
   * Mark all as read
   */
  const markAllAsRead = useMutation({
    mutationFn: () => notificationAPI.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  /**
   * Delete notification
   */
  const deleteNotification = useMutation({
    mutationFn: (notificationId: string) =>
      notificationAPI.delete(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      setSelectedNotificationId(null);
    },
  });

  return {
    getNotifications,
    getNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    selectedNotificationId,
    setSelectedNotificationId,
  };
};

/**
 * Notification Preferences Hook
 */
export const useNotificationPreferences = () => {
  const queryClient = useQueryClient();

  /**
   * Get preferences
   */
  const getPreferences = useQuery({
    queryKey: ["notification-preferences"],
    queryFn: () => preferencesAPI.getPreferences(),
  });

  /**
   * Update preferences
   */
  const updatePreferences = useMutation({
    mutationFn: (request: NotificationPreferencesUpdateRequest) =>
      preferencesAPI.updatePreferences(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["notification-preferences"],
      });
    },
  });

  return {
    getPreferences,
    updatePreferences,
  };
};
