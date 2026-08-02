/**
 * Cover Letter Hook
 * Manages cover letter state and operations
 */

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { coverLetterAPI, letterTemplateAPI } from "@/lib/api/cover_letter";
import type {
  CoverLetter,
  CoverLetterDetail,
  LetterTemplate,
  LetterExport,
  GenerateCoverLetterRequest,
  GenerateCoverLetterResponse,
  CoverLetterUpdateRequest,
} from "@/lib/types/cover_letter";

export const useCoverLetter = () => {
  const queryClient = useQueryClient();
  const [selectedLetterId, setSelectedLetterId] = useState<string | null>(null);

  /**
   * Get a specific cover letter
   */
  const getCoverLetter = useQuery({
    queryKey: ["coverLetter", selectedLetterId],
    queryFn: () => {
      if (!selectedLetterId) return Promise.reject("No letter ID");
      return coverLetterAPI.get(selectedLetterId);
    },
    enabled: !!selectedLetterId,
  });

  /**
   * Get cover letter for a specific job
   */
  const getCoverLetterForJob = (jobId: string) => {
    return useQuery({
      queryKey: ["coverLetter", "job", jobId],
      queryFn: () => coverLetterAPI.getForJob(jobId),
    });
  };

  /**
   * List all cover letters
   */
  const listCoverLetters = (skip: number = 0, limit: number = 20) => {
    return useQuery({
      queryKey: ["coverLetters", skip, limit],
      queryFn: () => coverLetterAPI.list(skip, limit),
    });
  };

  /**
   * Generate a new cover letter
   */
  const generateCoverLetter = useMutation({
    mutationFn: (request: GenerateCoverLetterRequest) =>
      coverLetterAPI.generate(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
      setSelectedLetterId(data.id);
    },
  });

  /**
   * Update a cover letter
   */
  const updateCoverLetter = useMutation({
    mutationFn: ({
      letterId,
      request,
    }: {
      letterId: string;
      request: CoverLetterUpdateRequest;
    }) => coverLetterAPI.update(letterId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
      queryClient.invalidateQueries({ queryKey: ["coverLetter", data.id] });
    },
  });

  /**
   * Publish a cover letter
   */
  const publishCoverLetter = useMutation({
    mutationFn: (letterId: string) => coverLetterAPI.publish(letterId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
      queryClient.invalidateQueries({ queryKey: ["coverLetter", data.id] });
    },
  });

  /**
   * Delete a cover letter
   */
  const deleteCoverLetter = useMutation({
    mutationFn: (letterId: string) => coverLetterAPI.delete(letterId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
      setSelectedLetterId(null);
    },
  });

  /**
   * Get all versions of a cover letter
   */
  const getVersions = (letterId: string) => {
    return useQuery({
      queryKey: ["coverLetter", letterId, "versions"],
      queryFn: () => coverLetterAPI.getVersions(letterId),
      enabled: !!letterId,
    });
  };

  /**
   * Export as PDF
   */
  const exportAsPDF = useMutation({
    mutationFn: (letterId: string) => coverLetterAPI.exportAsPDF(letterId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
    },
  });

  /**
   * Export as DOCX
   */
  const exportAsDOCX = useMutation({
    mutationFn: (letterId: string) => coverLetterAPI.exportAsDOCX(letterId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
    },
  });

  /**
   * Export as TXT
   */
  const exportAsTXT = useMutation({
    mutationFn: (letterId: string) => coverLetterAPI.exportAsTXT(letterId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
    },
  });

  /**
   * Get all exports
   */
  const getExports = (letterId: string) => {
    return useQuery({
      queryKey: ["coverLetter", letterId, "exports"],
      queryFn: () => coverLetterAPI.getExports(letterId),
      enabled: !!letterId,
    });
  };

  return {
    // Queries
    getCoverLetter,
    getCoverLetterForJob,
    listCoverLetters,
    getVersions,
    getExports,

    // Mutations
    generateCoverLetter,
    updateCoverLetter,
    publishCoverLetter,
    deleteCoverLetter,
    exportAsPDF,
    exportAsDOCX,
    exportAsTXT,

    // State
    selectedLetterId,
    setSelectedLetterId,
  };
};

/**
 * Letter Template Hook
 * Manages letter template state and operations
 */
export const useLetterTemplate = () => {
  const queryClient = useQueryClient();

  /**
   * List all templates
   */
  const listTemplates = (skip: number = 0, limit: number = 20) => {
    return useQuery({
      queryKey: ["letterTemplates", skip, limit],
      queryFn: () => letterTemplateAPI.list(skip, limit),
    });
  };

  /**
   * Get a specific template
   */
  const getTemplate = (templateId: string) => {
    return useQuery({
      queryKey: ["letterTemplate", templateId],
      queryFn: () => letterTemplateAPI.get(templateId),
      enabled: !!templateId,
    });
  };

  /**
   * Create a template
   */
  const createTemplate = useMutation({
    mutationFn: (data: any) => letterTemplateAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["letterTemplates"] });
    },
  });

  /**
   * Update a template
   */
  const updateTemplate = useMutation({
    mutationFn: ({ templateId, data }: { templateId: string; data: any }) =>
      letterTemplateAPI.update(templateId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["letterTemplates"] });
      queryClient.invalidateQueries({
        queryKey: ["letterTemplate", data.id],
      });
    },
  });

  /**
   * Delete a template
   */
  const deleteTemplate = useMutation({
    mutationFn: (templateId: string) => letterTemplateAPI.delete(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["letterTemplates"] });
    },
  });

  return {
    listTemplates,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  };
};

/**
 * Cover Letter Generation Hook
 * Handles batch generation and generation status
 */
export const useCoverLetterGeneration = () => {
  const queryClient = useQueryClient();
  const [generationStatus, setGenerationStatus] = useState({
    total: 0,
    generated: 0,
    failed: 0,
    status: "idle" as "idle" | "pending" | "in_progress" | "completed" | "failed",
  });

  /**
   * Batch generate cover letters
   */
  const batchGenerate = useMutation({
    mutationFn: (request: any) => coverLetterAPI.batchGenerate(request),
    onSuccess: (data) => {
      setGenerationStatus({
        total: data.job_ids.length,
        generated: data.generated,
        failed: data.job_ids.length - data.generated,
        status: "completed",
      });
      queryClient.invalidateQueries({ queryKey: ["coverLetters"] });
    },
    onError: () => {
      setGenerationStatus((prev) => ({
        ...prev,
        status: "failed",
      }));
    },
  });

  const resetStatus = useCallback(() => {
    setGenerationStatus({
      total: 0,
      generated: 0,
      failed: 0,
      status: "idle",
    });
  }, []);

  return {
    batchGenerate,
    generationStatus,
    resetStatus,
  };
};
