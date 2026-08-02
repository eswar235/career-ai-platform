/**
 * useSkills Hook - Skills management
 */

import { useState, useCallback } from 'react';
import { SkillResponse, SkillCreate, SkillUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseSkillsReturn {
  skills: SkillResponse[];
  loading: boolean;
  error: string | null;
  addSkill: (data: SkillCreate) => Promise<void>;
  updateSkill: (skillId: string, data: SkillUpdate) => Promise<void>;
  deleteSkill: (skillId: string) => Promise<void>;
  fetchSkills: () => Promise<void>;
}

export function useSkills(): UseSkillsReturn {
  const [skills, setSkills] = useState<SkillResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSkills = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await profileApi.getSkills();
      setSkills(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch skills');
    } finally {
      setLoading(false);
    }
  }, []);

  const addSkill = useCallback(
    async (data: SkillCreate) => {
      try {
        setLoading(true);
        setError(null);
        const newSkill = await profileApi.addSkill(data);
        setSkills((prev) => [newSkill, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add skill');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateSkill = useCallback(
    async (skillId: string, data: SkillUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await profileApi.updateSkill(skillId, data);
        setSkills((prev) =>
          prev.map((skill) => (skill.id === skillId ? updated : skill))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update skill');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteSkill = useCallback(
    async (skillId: string) => {
      try {
        setLoading(true);
        setError(null);
        await profileApi.deleteSkill(skillId);
        setSkills((prev) => prev.filter((skill) => skill.id !== skillId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete skill');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    skills,
    loading,
    error,
    addSkill,
    updateSkill,
    deleteSkill,
    fetchSkills,
  };
}
