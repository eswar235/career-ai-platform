/**
 * Resume API client
 * Handles all resume-related API calls
 */

import axios from 'axios';
import { getAccessToken } from '@/lib/auth/storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ResumeResponse {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  storage_path: string;
  mime_type: string;
  version: string | null;
  is_active: boolean;
  parsing_status: string;
  parsing_error: string | null;
  uploaded_at: string;
  parsed_at: string | null;
  updated_at: string;
}

interface ResumeUploadResponse {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  uploaded_at: string;
  message: string;
}

interface ResumeListResponse {
  resumes: ResumeResponse[];
  total: number;
}

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

/**
 * Upload a resume file
 */
export async function uploadResume(
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<ResumeUploadResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE_URL}/resumes/upload`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to upload resume');
  }
}

/**
 * Get list of all user resumes
 */
export async function getResumes(includeInactive: boolean = false): Promise<ResumeListResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/resumes/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params: {
        include_inactive: includeInactive,
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch resumes');
  }
}

/**
 * Get a specific resume by ID
 */
export async function getResume(resumeId: string): Promise<ResumeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/resumes/${resumeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch resume');
  }
}

/**
 * Set a resume as active
 */
export async function setActiveResume(resumeId: string): Promise<ResumeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/resumes/${resumeId}/set-active`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to set active resume');
  }
}

/**
 * Delete a resume
 */
export async function deleteResume(resumeId: string): Promise<{ message: string }> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await axios.delete(`${API_BASE_URL}/resumes/${resumeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete resume');
  }
}
