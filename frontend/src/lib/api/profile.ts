/**
 * Profile API client
 */

import { apiClient } from './client';
import {
  UserProfileResponse,
  UserProfileUpdate,
  SkillResponse,
  SkillCreate,
  SkillUpdate,
  ExperienceResponse,
  ExperienceCreate,
  ExperienceUpdate,
  EducationResponse,
  EducationCreate,
  EducationUpdate,
  ProjectResponse,
  ProjectCreate,
  ProjectUpdate,
  CertificationResponse,
  CertificationCreate,
  CertificationUpdate,
} from '../types/profile';

export const profileApi = {
  // Profile endpoints
  async getProfile(): Promise<UserProfileResponse> {
    const response = await apiClient.get('/api/profile');
    return response.data;
  },

  async updateProfile(data: UserProfileUpdate): Promise<UserProfileResponse> {
    const response = await apiClient.patch('/api/profile', data);
    return response.data;
  },

  // Skills endpoints
  async addSkill(data: SkillCreate): Promise<SkillResponse> {
    const response = await apiClient.post('/api/profile/skills', data);
    return response.data;
  },

  async getSkills(): Promise<SkillResponse[]> {
    const response = await apiClient.get('/api/profile/skills');
    return response.data;
  },

  async updateSkill(skillId: string, data: SkillUpdate): Promise<SkillResponse> {
    const response = await apiClient.patch(`/api/profile/skills/${skillId}`, data);
    return response.data;
  },

  async deleteSkill(skillId: string): Promise<void> {
    await apiClient.delete(`/api/profile/skills/${skillId}`);
  },

  // Experiences endpoints
  async addExperience(data: ExperienceCreate): Promise<ExperienceResponse> {
    const response = await apiClient.post('/api/profile/experiences', data);
    return response.data;
  },

  async getExperiences(): Promise<ExperienceResponse[]> {
    const response = await apiClient.get('/api/profile/experiences');
    return response.data;
  },

  async updateExperience(
    experienceId: string,
    data: ExperienceUpdate
  ): Promise<ExperienceResponse> {
    const response = await apiClient.patch(
      `/api/profile/experiences/${experienceId}`,
      data
    );
    return response.data;
  },

  async deleteExperience(experienceId: string): Promise<void> {
    await apiClient.delete(`/api/profile/experiences/${experienceId}`);
  },

  // Education endpoints
  async addEducation(data: EducationCreate): Promise<EducationResponse> {
    const response = await apiClient.post('/api/profile/education', data);
    return response.data;
  },

  async getEducation(): Promise<EducationResponse[]> {
    const response = await apiClient.get('/api/profile/education');
    return response.data;
  },

  async updateEducation(
    educationId: string,
    data: EducationUpdate
  ): Promise<EducationResponse> {
    const response = await apiClient.patch(
      `/api/profile/education/${educationId}`,
      data
    );
    return response.data;
  },

  async deleteEducation(educationId: string): Promise<void> {
    await apiClient.delete(`/api/profile/education/${educationId}`);
  },

  // Projects endpoints
  async addProject(data: ProjectCreate): Promise<ProjectResponse> {
    const response = await apiClient.post('/api/profile/projects', data);
    return response.data;
  },

  async getProjects(): Promise<ProjectResponse[]> {
    const response = await apiClient.get('/api/profile/projects');
    return response.data;
  },

  async updateProject(
    projectId: string,
    data: ProjectUpdate
  ): Promise<ProjectResponse> {
    const response = await apiClient.patch(
      `/api/profile/projects/${projectId}`,
      data
    );
    return response.data;
  },

  async deleteProject(projectId: string): Promise<void> {
    await apiClient.delete(`/api/profile/projects/${projectId}`);
  },

  // Certifications endpoints
  async addCertification(data: CertificationCreate): Promise<CertificationResponse> {
    const response = await apiClient.post('/api/profile/certifications', data);
    return response.data;
  },

  async getCertifications(): Promise<CertificationResponse[]> {
    const response = await apiClient.get('/api/profile/certifications');
    return response.data;
  },

  async updateCertification(
    certificationId: string,
    data: CertificationUpdate
  ): Promise<CertificationResponse> {
    const response = await apiClient.patch(
      `/api/profile/certifications/${certificationId}`,
      data
    );
    return response.data;
  },

  async deleteCertification(certificationId: string): Promise<void> {
    await apiClient.delete(`/api/profile/certifications/${certificationId}`);
  },
};
