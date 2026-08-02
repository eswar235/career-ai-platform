/**
 * useResumeOptimization Hook - Resume optimization management
 */

import { useState, useCallback } from 'react';
import { ResumeOptimizationResponse, OptimizationScoreBreakdown, KeywordAnalysis } from '../types/optimization';
import { optimizationApi } from '../api/optimization';

interface UseResumeOptimizationReturn {
  analysis: ResumeOptimizationResponse | null;
  scores: OptimizationScoreBreakdown | null;
  keywords: KeywordAnalysis | null;
  loading: boolean;
  error: string | null;
  analyzeResume: (content: string) => Promise<void>;
  getAnalysis: () => Promise<void>;
  getScores: () => Promise<void>;
  optimizeResume: () => Promise<void>;
  getOptimized: () => Promise<{ original_content: string; optimized_content?: string; overall_score?: number }>;
  analyzeKeywords: () => Promise<void>;
}

export function useResumeOptimization(): UseResumeOptimizationReturn {
  const [analysis, setAnalysis] = useState<ResumeOptimizationResponse | null>(null);
  const [scores, setScores] = useState<OptimizationScoreBreakdown | null>(null);
  const [keywords, setKeywords] = useState<KeywordAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeResume = useCallback(async (content: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await optimizationApi.analyzeResume(content);
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze resume');
    } finally {
      setLoading(false);
    }
  }, []);

  const getAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await optimizationApi.getAnalysis();
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analysis');
    } finally {
      setLoading(false);
    }
  }, []);

  const getScores = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await optimizationApi.getScores();
      setScores(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch scores');
    } finally {
      setLoading(false);
    }
  }, []);

  const optimizeResume = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await optimizationApi.optimizeResume();
      await getAnalysis(); // Refresh analysis
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize resume');
    } finally {
      setLoading(false);
    }
  }, [getAnalysis]);

  const getOptimized = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await optimizationApi.getOptimized();
        return data;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch optimized resume');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const analyzeKeywords = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await optimizationApi.analyzeKeywords();
      setKeywords(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze keywords');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    analysis,
    scores,
    keywords,
    loading,
    error,
    analyzeResume,
    getAnalysis,
    getScores,
    optimizeResume,
    getOptimized,
    analyzeKeywords,
  };
}
