/**
 * Application Tracking Hook
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationAPI, interviewAPI, offerAPI } from "@/lib/api/application";
import type {
  JobApplication,
  JobApplicationDetail,
  Interview,
  JobOffer,
  ApplicationStatus,
  JobApplicationCreateRequest,
  InterviewCreateRequest,
  JobOfferCreateRequest,
} from "@/lib/types/application";

export const useApplication = () => {
  const queryClient = useQueryClient();
  const [selectedApplicationId, setSelectedApplicationId] = useState<
    string | null
  >(null);

  /**
   * Get a specific application
   */
  const getApplication = useQuery({
    queryKey: ["application", selectedApplicationId],
    queryFn: () => {
      if (!selectedApplicationId) return Promise.reject("No ID");
      return applicationAPI.get(selectedApplicationId);
    },
    enabled: !!selectedApplicationId,
  });

  /**
   * List all applications
   */
  const listApplications = (status?: string, skip?: number, limit?: number) => {
    return useQuery({
      queryKey: ["applications", status, skip, limit],
      queryFn: () => applicationAPI.list(status, skip, limit),
    });
  };

  /**
   * Get application for job
   */
  const getForJob = (jobId: string) => {
    return useQuery({
      queryKey: ["application", "job", jobId],
      queryFn: () => applicationAPI.getForJob(jobId),
      enabled: !!jobId,
    });
  };

  /**
   * Create application
   */
  const createApplication = useMutation({
    mutationFn: (request: JobApplicationCreateRequest) =>
      applicationAPI.create(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setSelectedApplicationId(data.id);
    },
  });

  /**
   * Update application
   */
  const updateApplication = useMutation({
    mutationFn: ({
      applicationId,
      request,
    }: {
      applicationId: string;
      request: any;
    }) => applicationAPI.update(applicationId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({
        queryKey: ["application", data.id],
      });
    },
  });

  /**
   * Update status
   */
  const updateStatus = useMutation({
    mutationFn: ({
      applicationId,
      newStatus,
      notes,
    }: {
      applicationId: string;
      newStatus: ApplicationStatus;
      notes?: string;
    }) => applicationAPI.updateStatus(applicationId, newStatus, notes),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({
        queryKey: ["application", data.id],
      });
    },
  });

  /**
   * Delete application
   */
  const deleteApplication = useMutation({
    mutationFn: (applicationId: string) => applicationAPI.delete(applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setSelectedApplicationId(null);
    },
  });

  return {
    getApplication,
    listApplications,
    getForJob,
    createApplication,
    updateApplication,
    updateStatus,
    deleteApplication,
    selectedApplicationId,
    setSelectedApplicationId,
  };
};

/**
 * Interview Hook
 */
export const useInterview = () => {
  const queryClient = useQueryClient();

  /**
   * List interviews
   */
  const listInterviews = (applicationId: string) => {
    return useQuery({
      queryKey: ["interviews", applicationId],
      queryFn: () => interviewAPI.list(applicationId),
      enabled: !!applicationId,
    });
  };

  /**
   * Create interview
   */
  const createInterview = useMutation({
    mutationFn: ({
      applicationId,
      request,
    }: {
      applicationId: string;
      request: InterviewCreateRequest;
    }) => interviewAPI.create(applicationId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["interviews", data.application_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["application", data.application_id],
      });
    },
  });

  /**
   * Update interview
   */
  const updateInterview = useMutation({
    mutationFn: ({
      interviewId,
      request,
    }: {
      interviewId: string;
      request: any;
    }) => interviewAPI.update(interviewId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["interviews", data.application_id],
      });
    },
  });

  /**
   * Delete interview
   */
  const deleteInterview = useMutation({
    mutationFn: (interviewId: string) => interviewAPI.delete(interviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews"] });
    },
  });

  return {
    listInterviews,
    createInterview,
    updateInterview,
    deleteInterview,
  };
};

/**
 * Offer Hook
 */
export const useOffer = () => {
  const queryClient = useQueryClient();

  /**
   * Get offer for application
   */
  const getOffer = (applicationId: string) => {
    return useQuery({
      queryKey: ["offer", applicationId],
      queryFn: () => offerAPI.get(applicationId),
      enabled: !!applicationId,
    });
  };

  /**
   * Create offer
   */
  const createOffer = useMutation({
    mutationFn: ({
      applicationId,
      request,
    }: {
      applicationId: string;
      request: JobOfferCreateRequest;
    }) => offerAPI.create(applicationId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["offer", data.application_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["application", data.application_id],
      });
    },
  });

  /**
   * Update offer
   */
  const updateOffer = useMutation({
    mutationFn: ({
      offerId,
      request,
    }: {
      offerId: string;
      request: any;
    }) => offerAPI.update(offerId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
  });

  /**
   * Accept offer
   */
  const acceptOffer = useMutation({
    mutationFn: (offerId: string) => offerAPI.accept(offerId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["offer", data.application_id],
      });
    },
  });

  /**
   * Decline offer
   */
  const declineOffer = useMutation({
    mutationFn: ({
      offerId,
      reason,
    }: {
      offerId: string;
      reason?: string;
    }) => offerAPI.decline(offerId, reason),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["offer", data.application_id],
      });
    },
  });

  /**
   * Delete offer
   */
  const deleteOffer = useMutation({
    mutationFn: (offerId: string) => offerAPI.delete(offerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
  });

  return {
    getOffer,
    createOffer,
    updateOffer,
    acceptOffer,
    declineOffer,
    deleteOffer,
  };
};
