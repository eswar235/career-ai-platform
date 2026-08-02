/**
 * useSavedJobs Hook - Saved jobs management
 */

import { useState, useCallback } from 'react';
import { SavedJobResponse, SavedJobCreate } from '../types/jobs';
import { jobsApi } from '../api/jobs';

interface UseSavedJobsReturn {
  savedJobs: SavedJobResponse[];
  loading: boolean;
  error: string | null;
  saveJob: (data: SavedJobCreate) => Promise<void>;
  unsaveJob: (jobId: string) => Promise<void>;
  fetchSavedJobs: (skip?: number, limit?: number) => Promise<void>;
  isJobSaved: (jobId: string) => Promise<boolean>;
}

export function useSavedJobs(): UseSavedJobsReturn {
  const [savedJobs, setSavedJobs] = useState<SavedJobResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSavedJobs = useCallback(async (skip = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobsApi.getSavedJobs(skip, limit);
      setSavedJobs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch saved jobs');
    } finally {
      setLoading(false);
    }
  }, []);

  const saveJob = useCallback(
    async (data: SavedJobCreate) => {
      try {
        setLoading(true);
        setError(null);
        const savedJob = await jobsApi.saveJob(data);
        setSavedJobs((prev) => [savedJob, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save job');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const unsaveJob = useCallback(
    async (jobId: string) => {
      try {
        setLoading(true);
        setError(null);
        await jobsApi.unsaveJob(jobId);
        setSavedJobs((prev) => prev.filter((job) => job.job_id !== jobId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to unsave job');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const isJobSaved = useCallback(async (jobId: string): Promise<boolean> => {
    try {
      const result = await jobsApi.isJobSaved(jobId);
      return result.is_saved;
    } catch (err) {
      return false;
    }
  }, []);

  return {
    savedJobs,
    loading,
    error,
    saveJob,
    unsaveJob,
    fetchSavedJobs,
    isJobSaved,
  };
}
