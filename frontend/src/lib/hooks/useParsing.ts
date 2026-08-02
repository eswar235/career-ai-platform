/**
 * useParsing hook for managing resume parsing state and operations
 */

'use client';

import { useState, useCallback } from 'react';
import {
  parseResume as parseResumeAPI,
  getParsedResume as getParsedResumeAPI,
  updateParsedResume as updateParsedResumeAPI,
  confirmParsedResume as confirmParsedResumeAPI,
  ParsedResumeResponse,
} from '@/lib/api/parsing';

interface UseParsingState {
  parsedResume: ParsedResumeResponse | null;
  loading: boolean;
  parsing: boolean;
  error: string | null;
  success: string | null;
}

export function useParsing() {
  const [state, setState] = useState<UseParsingState>({
    parsedResume: null,
    loading: false,
    parsing: false,
    error: null,
    success: null,
  });

  /**
   * Parse a resume (trigger parsing)
   */
  const parse = useCallback(async (resumeId: string) => {
    setState((prev) => ({ ...prev, parsing: true, error: null, success: null }));

    try {
      const response = await parseResumeAPI(resumeId);

      // Get the parsed data
      const parsedData = await getParsedResumeAPI(resumeId);
      setState((prev) => ({
        ...prev,
        parsedResume: parsedData,
        parsing: false,
        success: `Resume parsed with ${response.confidence_score}% confidence`,
      }));

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to parse resume';
      setState((prev) => ({
        ...prev,
        parsing: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Fetch parsed resume data
   */
  const fetch = useCallback(async (resumeId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await getParsedResumeAPI(resumeId);
      setState((prev) => ({
        ...prev,
        parsedResume: data,
        loading: false,
      }));
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch parsed resume';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Update parsed resume with user corrections
   */
  const update = useCallback(async (parsedResumeId: string, updates: Partial<ParsedResumeResponse>) => {
    setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

    try {
      const updated = await updateParsedResumeAPI(parsedResumeId, updates);
      setState((prev) => ({
        ...prev,
        parsedResume: updated,
        loading: false,
        success: 'Resume data updated successfully',
      }));
      return updated;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update resume';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  /**
   * Confirm parsed resume
   */
  const confirm = useCallback(async (parsedResumeId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

    try {
      await confirmParsedResumeAPI(parsedResumeId);

      // Mark as confirmed
      setState((prev) => ({
        ...prev,
        parsedResume: prev.parsedResume
          ? { ...prev.parsedResume, is_confirmed: true }
          : null,
        loading: false,
        success: 'Resume parsing confirmed!',
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to confirm resume';
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

  /**
   * Clear success message
   */
  const clearSuccess = useCallback(() => {
    setState((prev) => ({ ...prev, success: null }));
  }, []);

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setState((prev) => ({ ...prev, error: null, success: null }));
  }, []);

  return {
    parsedResume: state.parsedResume,
    loading: state.loading,
    parsing: state.parsing,
    error: state.error,
    success: state.success,
    parse,
    fetch,
    update,
    confirm,
    clearError,
    clearSuccess,
    clearMessages,
  };
}
