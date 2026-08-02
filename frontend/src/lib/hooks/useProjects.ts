/**
 * useProjects Hook - Portfolio projects management
 */

import { useState, useCallback } from 'react';
import { ProjectResponse, ProjectCreate, ProjectUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseProjectsReturn {
  projects: ProjectResponse[];
  loading: boolean;
  error: string | null;
  addProject: (data: ProjectCreate) => Promise<void>;
  updateProject: (projectId: string, data: ProjectUpdate) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  fetchProjects: () => Promise<void>;
}

export function useProjects(): UseProjectsReturn {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await profileApi.getProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  }, []);

  const addProject = useCallback(
    async (data: ProjectCreate) => {
      try {
        setLoading(true);
        setError(null);
        const newProject = await profileApi.addProject(data);
        setProjects((prev) => [newProject, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add project');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateProject = useCallback(
    async (projectId: string, data: ProjectUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await profileApi.updateProject(projectId, data);
        setProjects((prev) =>
          prev.map((project) => (project.id === projectId ? updated : project))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update project');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteProject = useCallback(
    async (projectId: string) => {
      try {
        setLoading(true);
        setError(null);
        await profileApi.deleteProject(projectId);
        setProjects((prev) => prev.filter((project) => project.id !== projectId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete project');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    projects,
    loading,
    error,
    addProject,
    updateProject,
    deleteProject,
    fetchProjects,
  };
}
