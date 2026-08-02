/**
 * Browser Automation Hook
 */

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { automationAPI, automationStepAPI } from "@/lib/api/automation";
import type {
  AutomationJob,
  AutomationJobDetail,
  AutomationStep,
  AutomationStatus,
  AutomationJobCreateRequest,
  AutomationStepCreateRequest,
} from "@/lib/types/automation";

export const useAutomation = () => {
  const queryClient = useQueryClient();
  const [selectedAutomationId, setSelectedAutomationId] = useState<string | null>(
    null
  );

  /**
   * Get a specific automation job
   */
  const getAutomation = useQuery({
    queryKey: ["automation", selectedAutomationId],
    queryFn: () => {
      if (!selectedAutomationId) return Promise.reject("No ID");
      return automationAPI.get(selectedAutomationId);
    },
    enabled: !!selectedAutomationId,
  });

  /**
   * List all automation jobs
   */
  const listAutomation = (status?: string, skip?: number, limit?: number) => {
    return useQuery({
      queryKey: ["automations", status, skip, limit],
      queryFn: () => automationAPI.list(status, skip, limit),
    });
  };

  /**
   * Get automation status
   */
  const getStatus = (automationId: string) => {
    return useQuery({
      queryKey: ["automation", automationId, "status"],
      queryFn: () => automationAPI.getStatus(automationId),
      enabled: !!automationId,
      refetchInterval: 2000, // Poll every 2 seconds
    });
  };

  /**
   * Create automation
   */
  const createAutomation = useMutation({
    mutationFn: (request: AutomationJobCreateRequest) =>
      automationAPI.create(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
      setSelectedAutomationId(data.id);
    },
  });

  /**
   * Start automation
   */
  const startAutomation = useMutation({
    mutationFn: (automationId: string) => automationAPI.start(automationId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["automation", data.automation_id, "status"],
      });
    },
  });

  /**
   * Stop automation
   */
  const stopAutomation = useMutation({
    mutationFn: (automationId: string) => automationAPI.stop(automationId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["automation", data.automation_id, "status"],
      });
    },
  });

  /**
   * Delete automation
   */
  const deleteAutomation = useMutation({
    mutationFn: (automationId: string) => automationAPI.delete(automationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
      setSelectedAutomationId(null);
    },
  });

  /**
   * Create bulk automation jobs
   */
  const createBulkAutomation = useMutation({
    mutationFn: (request: any) => automationAPI.createBulk(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
    },
  });

  return {
    getAutomation,
    listAutomation,
    getStatus,
    createAutomation,
    startAutomation,
    stopAutomation,
    deleteAutomation,
    createBulkAutomation,
    selectedAutomationId,
    setSelectedAutomationId,
  };
};

/**
 * Automation Step Hook
 */
export const useAutomationStep = () => {
  const queryClient = useQueryClient();

  /**
   * List steps for automation
   */
  const listSteps = (automationId: string) => {
    return useQuery({
      queryKey: ["automation", automationId, "steps"],
      queryFn: () => automationStepAPI.list(automationId),
      enabled: !!automationId,
    });
  };

  /**
   * Add step to automation
   */
  const addStep = useMutation({
    mutationFn: ({
      automationId,
      request,
    }: {
      automationId: string;
      request: AutomationStepCreateRequest;
    }) => automationStepAPI.create(automationId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["automation", data.automation_job_id, "steps"],
      });
    },
  });

  return {
    listSteps,
    addStep,
  };
};
