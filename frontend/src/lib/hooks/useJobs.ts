/**
 * useJobs Hook - Job search management
 */

import { useState, useCallback } from 'react';
import { JobResponse, JobSearchFilters, JobSearchResults } from '../types/jobs';
import { jobsApi } from '../api/jobs';

interface UseJobsReturn {
  results: JobSearchResults | null;
  loading: boolean;
  error: string | null;
  searchJobs: (filters: JobSearchFilters) => Promise<void>;
  getJob: (jobId: string) => Promise<JobResponse>;
}

export function useJobs(): UseJobsReturn {
  const [results, setResults] = useState<JobSearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchJobs = useCallback(async (filters: JobSearchFilters) => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobsApi.searchJobs(filters);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search jobs');
    } finally {
      setLoading(false);
    }
  }, []);

  const getJob = useCallback(async (jobId: string): Promise<JobResponse> => {
    try {
      setLoading(true);
      setError(null);
      const job = await jobsApi.getJob(jobId);
      return job;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch job');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    results,
    loading,
    error,
    searchJobs,
    getJob,
  };
}
