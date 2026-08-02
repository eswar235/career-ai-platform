/**
 * useTailoredResume Hook - Tailored resume management
 */

import { useState, useCallback } from 'react';
import { TailoredResumeResponse } from '../types/optimization';
import { optimizationApi } from '../api/optimization';

interface UseTailoredResumeReturn {
  tailoredResumes: TailoredResumeResponse[];
  currentTailored: TailoredResumeResponse | null;
  loading: boolean;
  error: string | null;
  createTailoredResume: (jobId: string) => Promise<void>;
  getTailoredResume: (jobId: string) => Promise<void>;
  listTailoredResumes: (skip?: number, limit?: number) => Promise<void>;
  deleteTailoredResume: (jobId: string) => Promise<void>;
}

export function useTailoredResume(): UseTailoredResumeReturn {
  const [tailoredResumes, setTailoredResumes] = useState<TailoredResumeResponse[]>([]);
  const [currentTailored, setCurrentTailored] = useState<TailoredResumeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createTailoredResume = useCallback(async (jobId: string) => {
    try {
      setLoading(true);
      setError(null);
      const tailored = await optimizationApi.createTailoredResume(jobId);
      setCurrentTailored(tailored);
      setTailoredResumes((prev) => [...prev, tailored]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create tailored resume');
    } finally {
      setLoading(false);
    }
  }, []);

  const getTailoredResume = useCallback(async (jobId: string) => {
    try {
      setLoading(true);
      setError(null);
      const tailored = await optimizationApi.getTailoredResume(jobId);
      setCurrentTailored(tailored);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tailored resume');
    } finally {
      setLoading(false);
    }
  }, []);

  const listTailoredResumes = useCallback(async (skip = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      const resumes = await optimizationApi.listTailoredResumes(skip, limit);
      setTailoredResumes(resumes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to list tailored resumes');
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTailoredResume = useCallback(async (jobId: string) => {
    try {
      setLoading(true);
      setError(null);
      await optimizationApi.deleteTailoredResume(jobId);
      setTailoredResumes((prev) => prev.filter((r) => r.job_id !== jobId));
      if (currentTailored?.job_id === jobId) {
        setCurrentTailored(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete tailored resume');
    } finally {
      setLoading(false);
    }
  }, [currentTailored]);

  return {
    tailoredResumes,
    currentTailored,
    loading,
    error,
    createTailoredResume,
    getTailoredResume,
    listTailoredResumes,
    deleteTailoredResume,
  };
}
