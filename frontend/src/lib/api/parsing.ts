/**
 * Parsing API client
 * Handles all resume parsing API calls
 */

import axios from 'axios';
import { getAccessToken } from '@/lib/auth/storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface SkillData {
  name: string;
  proficiency?: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  years?: number;
}

interface ExperienceData {
  title: string;
  company: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

interface EducationData {
  degree: string;
  institution: string;
  year?: number;
  field?: string;
}

interface CertificationData {
  name: string;
  issuer: string;
  year?: number;
}

export interface ParsedResumeResponse {
  id: string;
  resume_id: string;
  user_id: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  skills: SkillData[];
  experience: ExperienceData[];
  education: EducationData[];
  certifications: CertificationData[];
  confidence_score?: number;
  is_confirmed: boolean;
  created_at: string;
  confirmed_at?: string;
}

export interface ParseResumeResponse {
  parsed_resume_id: string;
  resume_id: string;
  full_name?: string;
  email?: string;
  confidence_score: number;
  message: string;
}

/**
 * Trigger resume parsing
 */
export async function parseResume(resumeId: string): Promise<ParseResumeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/parsing/parse/${resumeId}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to parse resume');
  }
}

/**
 * Get parsed resume data
 */
export async function getParsedResume(resumeId: string): Promise<ParsedResumeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.get(
      `${API_BASE_URL}/parsing/parsed/${resumeId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch parsed resume');
  }
}

/**
 * Update parsed resume with user corrections
 */
export async function updateParsedResume(
  parsedResumeId: string,
  updates: Partial<ParsedResumeResponse>
): Promise<ParsedResumeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.put(
      `${API_BASE_URL}/parsing/parsed/${parsedResumeId}`,
      updates,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to update parsed resume');
  }
}

/**
 * Confirm parsed resume (user reviewed)
 */
export async function confirmParsedResume(parsedResumeId: string): Promise<{ message: string }> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/parsing/parsed/${parsedResumeId}/confirm`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to confirm parsed resume');
  }
}
