/**
 * useJobApplications Hook - Job applications management
 */

import { useState, useCallback } from 'react';
import { JobApplicationResponse, JobApplicationCreate, JobApplicationUpdate, ApplicationStats } from '../types/jobs';
import { jobsApi } from '../api/jobs';

interface UseJobApplicationsReturn {
  applications: JobApplicationResponse[];
  stats: ApplicationStats | null;
  loading: boolean;
  error: string | null;
  applyForJob: (data: JobApplicationCreate) => Promise<void>;
  updateApplication: (applicationId: string, data: JobApplicationUpdate) => Promise<void>;
  fetchApplications: (skip?: number, limit?: number, statusFilter?: string) => Promise<void>;
  fetchStats: () => Promise<void>;
}

export function useJobApplications(): UseJobApplicationsReturn {
  const [applications, setApplications] = useState<JobApplicationResponse[]>([]);
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchApplications = useCallback(
    async (skip = 0, limit = 20, statusFilter?: string) => {
      try {
        setLoading(true);
        setError(null);
        const data = await jobsApi.getApplications(skip, limit, statusFilter);
        setApplications(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch applications');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobsApi.getApplicationStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  }, []);

  const applyForJob = useCallback(
    async (data: JobApplicationCreate) => {
      try {
        setLoading(true);
        setError(null);
        const application = await jobsApi.applyForJob(data);
        setApplications((prev) => [application, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to apply for job');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateApplication = useCallback(
    async (applicationId: string, data: JobApplicationUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await jobsApi.updateApplication(applicationId, data);
        setApplications((prev) =>
          prev.map((app) => (app.id === applicationId ? updated : app))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update application');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    applications,
    stats,
    loading,
    error,
    applyForJob,
    updateApplication,
    fetchApplications,
    fetchStats,
  };
}
