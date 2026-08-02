/**
 * useEducation Hook - Education management
 */

import { useState, useCallback } from 'react';
import { EducationResponse, EducationCreate, EducationUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseEducationReturn {
  education: EducationResponse[];
  loading: boolean;
  error: string | null;
  addEducation: (data: EducationCreate) => Promise<void>;
  updateEducation: (educationId: string, data: EducationUpdate) => Promise<void>;
  deleteEducation: (educationId: string) => Promise<void>;
  fetchEducation: () => Promise<void>;
}

export function useEducation(): UseEducationReturn {
  const [education, setEducation] = useState<EducationResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEducation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await profileApi.getEducation();
      setEducation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch education');
    } finally {
      setLoading(false);
    }
  }, []);

  const addEducation = useCallback(
    async (data: EducationCreate) => {
      try {
        setLoading(true);
        setError(null);
        const newEducation = await profileApi.addEducation(data);
        setEducation((prev) => [newEducation, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add education');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateEducation = useCallback(
    async (educationId: string, data: EducationUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await profileApi.updateEducation(educationId, data);
        setEducation((prev) =>
          prev.map((edu) => (edu.id === educationId ? updated : edu))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update education');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteEducation = useCallback(
    async (educationId: string) => {
      try {
        setLoading(true);
        setError(null);
        await profileApi.deleteEducation(educationId);
        setEducation((prev) => prev.filter((edu) => edu.id !== educationId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete education');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    education,
    loading,
    error,
    addEducation,
    updateEducation,
    deleteEducation,
    fetchEducation,
  };
}
