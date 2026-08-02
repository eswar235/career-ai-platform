/**
 * useResume hook for managing resume state and operations
 */

'use client';

import { useState, useCallback } from 'react';
import {
  uploadResume as uploadResumeAPI,
  getResumes as getResumesAPI,
  setActiveResume as setActiveResumeAPI,
  deleteResume as deleteResumeAPI,
  UploadProgress,
} from '@/lib/api/resume';

interface Resume {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  storage_path: string;
  mime_type: string;
  version: string | null;
  is_active: boolean;
  parsing_status: string;
  parsing_error: string | null;
  uploaded_at: string;
  parsed_at: string | null;
  updated_at: string;
}

interface UseResumeState {
  resumes: Resume[];
  loading: boolean;
  error: string | null;
  uploadProgress: UploadProgress | null;
}

export function useResume() {
  const [state, setState] = useState<UseResumeState>({
    resumes: [],
    loading: false,
    error: null,
    uploadProgress: null,
  });

  /**
   * Upload a new resume
   */
  const upload = useCallback(
    async (file: File, onProgress?: (progress: UploadProgress) => void) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        // Validate file
        if (!file.name.toLowerCase().endsWith('.pdf')) {
          throw new Error('Only PDF files are allowed');
        }

        if (file.size > 10 * 1024 * 1024) {
          throw new Error('File size must be less than 10MB');
        }

        // Upload
        const response = await uploadResumeAPI(file, (progress) => {
          setState((prev) => ({ ...prev, uploadProgress: progress }));
          onProgress?.(progress);
        });

        // Refresh list
        await fetchResumes();

        setState((prev) => ({ ...prev, loading: false, uploadProgress: null }));
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to upload resume';
        setState((prev) => ({
          ...prev,
          loading: false,
          error: errorMessage,
          uploadProgress: null,
        }));
        throw err;
      }
    },
    []
  );

  /**
   * Fetch all resumes for current user
   */
  const fetchResumes = useCallback(async (includeInactive: boolean = false) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await getResumesAPI(includeInactive);
      setState((prev) => ({
        ...prev,
        resumes: data.resumes,
        loading: false,
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch resumes';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Set a resume as active
   */
  const setActive = useCallback(async (resumeId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await setActiveResumeAPI(resumeId);

      // Update local state
      setState((prev) => ({
        ...prev,
        resumes: prev.resumes.map((r) => ({
          ...r,
          is_active: r.id === resumeId,
        })),
        loading: false,
      }));

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to set active resume';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Delete a resume
   */
  const deleteItem = useCallback(async (resumeId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      await deleteResumeAPI(resumeId);

      // Update local state
      setState((prev) => ({
        ...prev,
        resumes: prev.resumes.filter((r) => r.id !== resumeId),
        loading: false,
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete resume';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    resumes: state.resumes,
    loading: state.loading,
    error: state.error,
    uploadProgress: state.uploadProgress,
    upload,
    fetchResumes,
    setActive,
    deleteItem,
    clearError,
  };
}
