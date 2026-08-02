/**
 * ResumeList component for displaying user's resumes
 */

'use client';

import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';

interface Resume {
  id: string;
  original_filename: string;
  file_size: number;
  is_active: boolean;
  parsing_status: string;
  uploaded_at: string;
}

interface ResumeListProps {
  resumes: Resume[];
  loading?: boolean;
  onSetActive?: (resumeId: string) => Promise<void>;
  onDelete?: (resumeId: string) => Promise<void>;
}

export function ResumeList({
  resumes,
  loading = false,
  onSetActive,
  onDelete,
}: ResumeListProps) {
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getParsingStatusBadge = (status: string) => {
    const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
      pending: { bg: 'bg-yellow-50', text: 'text-yellow-700', label: 'Pending' },
      processing: { bg: 'bg-blue-50', text: 'text-blue-700', label: 'Processing' },
      completed: { bg: 'bg-green-50', text: 'text-green-700', label: 'Completed' },
      failed: { bg: 'bg-red-50', text: 'text-red-700', label: 'Failed' },
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const handleSetActive = async (resumeId: string) => {
    if (!onSetActive) return;

    try {
      setActionLoading(resumeId);
      await onSetActive(resumeId);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (resumeId: string) => {
    if (!onDelete) return;

    try {
      setActionLoading(resumeId);
      await onDelete(resumeId);
      setDeleteConfirm(null);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin inline-block w-6 h-6 border-3 border-gray-300 border-t-blue-500 rounded-full" />
      </div>
    );
  }

  if (resumes.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <p className="mt-4 text-gray-600">No resumes uploaded yet</p>
        <p className="text-sm text-gray-500">Upload your first resume to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {resumes.map((resume) => (
        <div
          key={resume.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-colors"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3">
              <svg
                className="h-5 w-5 text-red-500 flex-shrink-0"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M8 16.5a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zM15 16.5a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                <path d="M3 20.293A19.01 19.01 0 0123 16v-2h-4V9h-3V5.5a3 3 0 00-3-3H8a3 3 0 00-3 3V9H2v2h2v4a11 11 0 002 8.293z" />
              </svg>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {resume.original_filename}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(resume.file_size)} • Uploaded{' '}
                  {formatDistanceToNow(new Date(resume.uploaded_at), { addSuffix: true })}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 ml-4">
            <div className="flex items-center gap-2">
              {resume.is_active && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700">
                  Active
                </span>
              )}
              {getParsingStatusBadge(resume.parsing_status)}
            </div>

            <div className="flex items-center gap-1">
              {!resume.is_active && onSetActive && (
                <button
                  onClick={() => handleSetActive(resume.id)}
                  disabled={actionLoading === resume.id}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Set as active"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </button>
              )}

              {onDelete && (
                <div className="relative group">
                  <button
                    onClick={() =>
                      setDeleteConfirm(deleteConfirm === resume.id ? null : resume.id)
                    }
                    disabled={actionLoading === resume.id}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Delete"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>

                  {deleteConfirm === resume.id && (
                    <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-3">
                      <p className="text-sm text-gray-700 mb-3">Delete this resume?</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDelete(resume.id)}
                          disabled={actionLoading === resume.id}
                          className="flex-1 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {actionLoading === resume.id ? 'Deleting...' : 'Delete'}
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(null)}
                          className="flex-1 px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
