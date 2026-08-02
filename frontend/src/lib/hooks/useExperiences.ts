/**
 * useExperiences Hook - Work experience management
 */

import { useState, useCallback } from 'react';
import { ExperienceResponse, ExperienceCreate, ExperienceUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseExperiencesReturn {
  experiences: ExperienceResponse[];
  loading: boolean;
  error: string | null;
  addExperience: (data: ExperienceCreate) => Promise<void>;
  updateExperience: (experienceId: string, data: ExperienceUpdate) => Promise<void>;
  deleteExperience: (experienceId: string) => Promise<void>;
  fetchExperiences: () => Promise<void>;
}

export function useExperiences(): UseExperiencesReturn {
  const [experiences, setExperiences] = useState<ExperienceResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExperiences = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await profileApi.getExperiences();
      setExperiences(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch experiences');
    } finally {
      setLoading(false);
    }
  }, []);

  const addExperience = useCallback(
    async (data: ExperienceCreate) => {
      try {
        setLoading(true);
        setError(null);
        const newExperience = await profileApi.addExperience(data);
        setExperiences((prev) => [newExperience, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add experience');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateExperience = useCallback(
    async (experienceId: string, data: ExperienceUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await profileApi.updateExperience(experienceId, data);
        setExperiences((prev) =>
          prev.map((exp) => (exp.id === experienceId ? updated : exp))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update experience');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteExperience = useCallback(
    async (experienceId: string) => {
      try {
        setLoading(true);
        setError(null);
        await profileApi.deleteExperience(experienceId);
        setExperiences((prev) => prev.filter((exp) => exp.id !== experienceId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete experience');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    experiences,
    loading,
    error,
    addExperience,
    updateExperience,
    deleteExperience,
    fetchExperiences,
  };
}
