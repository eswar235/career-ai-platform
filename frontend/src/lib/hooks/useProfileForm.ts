/**
 * useProfileForm Hook - Profile form data management
 */

import { useState, useCallback } from 'react';
import { UserProfileUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseProfileFormReturn {
  loading: boolean;
  error: string | null;
  success: boolean;
  updateProfile: (data: UserProfileUpdate) => Promise<void>;
  clearMessages: () => void;
}

export function useProfileForm(): UseProfileFormReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const updateProfile = useCallback(async (data: UserProfileUpdate) => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      await profileApi.updateProfile(data);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return {
    loading,
    error,
    success,
    updateProfile,
    clearMessages,
  };
}
