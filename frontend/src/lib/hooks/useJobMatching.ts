/**
 * useJobMatching Hook - Job matching and recommendations
 */

import { useState, useCallback } from 'react';
import { JobMatchResponse, UserMatchesList, SkillAnalysis } from '../types/matching';
import { matchingApi } from '../api/matching';

interface UseJobMatchingReturn {
  matches: JobMatchResponse[];
  loading: boolean;
  error: string | null;
  getMatch: (jobId: string) => Promise<JobMatchResponse>;
  getTopMatches: (minPercentage?: number, skip?: number, limit?: number) => Promise<void>;
  getHighMatches: (skip?: number, limit?: number) => Promise<void>;
  getModerateMatches: (skip?: number, limit?: number) => Promise<void>;
  analyzeSkills: (jobId: string) => Promise<SkillAnalysis>;
}

export function useJobMatching(): UseJobMatchingReturn {
  const [matches, setMatches] = useState<JobMatchResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getMatch = useCallback(async (jobId: string): Promise<JobMatchResponse> => {
    try {
      setLoading(true);
      setError(null);
      const match = await matchingApi.computeJobMatch(jobId);
      return match;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to compute match';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTopMatches = useCallback(async (minPercentage = 0, skip = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      const data = await matchingApi.getTopMatches(minPercentage, skip, limit);
      setMatches(data.matches);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch matches');
    } finally {
      setLoading(false);
    }
  }, []);

  const getHighMatches = useCallback(async (skip = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      const data = await matchingApi.getHighMatches(skip, limit);
      setMatches(data.matches);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch high matches');
    } finally {
      setLoading(false);
    }
  }, []);

  const getModerateMatches = useCallback(async (skip = 0, limit = 20) => {
    try {
      setLoading(true);
      setError(null);
      const data = await matchingApi.getModerateMatches(skip, limit);
      setMatches(data.matches);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch moderate matches');
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeSkills = useCallback(async (jobId: string): Promise<SkillAnalysis> => {
    try {
      setLoading(true);
      setError(null);
      const analysis = await matchingApi.analyzeSkills(jobId);
      return analysis;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze skills';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    matches,
    loading,
    error,
    getMatch,
    getTopMatches,
    getHighMatches,
    getModerateMatches,
    analyzeSkills,
  };
}
