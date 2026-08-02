/**
 * useCertifications Hook - Certifications management
 */

import { useState, useCallback } from 'react';
import { CertificationResponse, CertificationCreate, CertificationUpdate } from '../types/profile';
import { profileApi } from '../api/profile';

interface UseCertificationsReturn {
  certifications: CertificationResponse[];
  loading: boolean;
  error: string | null;
  addCertification: (data: CertificationCreate) => Promise<void>;
  updateCertification: (certificationId: string, data: CertificationUpdate) => Promise<void>;
  deleteCertification: (certificationId: string) => Promise<void>;
  fetchCertifications: () => Promise<void>;
}

export function useCertifications(): UseCertificationsReturn {
  const [certifications, setCertifications] = useState<CertificationResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCertifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await profileApi.getCertifications();
      setCertifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch certifications');
    } finally {
      setLoading(false);
    }
  }, []);

  const addCertification = useCallback(
    async (data: CertificationCreate) => {
      try {
        setLoading(true);
        setError(null);
        const newCertification = await profileApi.addCertification(data);
        setCertifications((prev) => [newCertification, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add certification');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateCertification = useCallback(
    async (certificationId: string, data: CertificationUpdate) => {
      try {
        setLoading(true);
        setError(null);
        const updated = await profileApi.updateCertification(certificationId, data);
        setCertifications((prev) =>
          prev.map((cert) => (cert.id === certificationId ? updated : cert))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update certification');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteCertification = useCallback(
    async (certificationId: string) => {
      try {
        setLoading(true);
        setError(null);
        await profileApi.deleteCertification(certificationId);
        setCertifications((prev) =>
          prev.filter((cert) => cert.id !== certificationId)
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete certification');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    certifications,
    loading,
    error,
    addCertification,
    updateCertification,
    deleteCertification,
    fetchCertifications,
  };
}
