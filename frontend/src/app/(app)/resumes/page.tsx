/**
 * Resume upload and management page
 */

'use client';

import { useEffect } from 'react';
import { ResumeUploadZone } from '@/components/ResumeUploadZone';
import { ResumeList } from '@/components/ResumeList';
import { useResume } from '@/lib/hooks/useResume';

export default function ResumesPage() {
  const {
    resumes,
    loading,
    error,
    uploadProgress,
    upload,
    fetchResumes,
    setActive,
    deleteItem,
    clearError,
  } = useResume();

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  const handleUpload = async (file: File) => {
    try {
      await upload(file);
    } catch (err) {
      // Error is already set in state by the hook
    }
  };

  const handleSetActive = async (resumeId: string) => {
    try {
      await setActive(resumeId);
    } catch (err) {
      // Error is already set in state by the hook
    }
  };

  const handleDelete = async (resumeId: string) => {
    try {
      await deleteItem(resumeId);
    } catch (err) {
      // Error is already set in state by the hook
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Resumes</h1>
          <p className="mt-2 text-gray-600">
            Upload and manage your resumes. You can upload multiple versions and set which one is
            active.
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload New Resume</h2>
          <ResumeUploadZone
            onUpload={handleUpload}
            loading={loading}
            error={error}
            uploadProgress={uploadProgress}
          />
          {error && (
            <div className="mt-4 flex justify-between items-start p-4 bg-red-50 border border-red-200 rounded-lg">
              <div>
                <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-500 focus:outline-none"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>

        {/* Resumes List Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Your Resumes ({resumes.length})
          </h2>
          <ResumeList
            resumes={resumes}
            loading={loading}
            onSetActive={handleSetActive}
            onDelete={handleDelete}
          />
        </div>

        {/* Info Section */}
        <div className="mt-8 rounded-lg bg-blue-50 border border-blue-200 p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Resume Upload Information</h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Only PDF files are accepted</li>
                  <li>Maximum file size is 5MB</li>
                  <li>You can upload multiple versions of your resume</li>
                  <li>Set which resume is active for applications</li>
                  <li>Resumes are encrypted and stored securely</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
