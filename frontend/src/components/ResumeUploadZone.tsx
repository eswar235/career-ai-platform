/**
 * ResumeUploadZone component for drag-and-drop resume upload
 */

'use client';

import React, { useRef, useState } from 'react';

interface ResumeUploadZoneProps {
  onUpload: (file: File) => Promise<void>;
  loading?: boolean;
  error?: string | null;
  uploadProgress?: { percentage: number } | null;
}

export function ResumeUploadZone({
  onUpload,
  loading = false,
  error = null,
  uploadProgress = null,
}: ResumeUploadZoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = async (file: File) => {
    try {
      setIsUploading(true);
      await onUpload(file);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      // Error is handled by parent component
    } finally {
      setIsUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const isProcessing = loading || isUploading;

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : error
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
        } ${isProcessing ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        {isProcessing && uploadProgress ? (
          // Upload in progress
          <div className="space-y-3">
            <div className="text-sm font-medium text-gray-700">
              Uploading... {uploadProgress.percentage}%
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress.percentage}%` }}
              />
            </div>
          </div>
        ) : isProcessing ? (
          // Loading state
          <div className="space-y-2">
            <div className="animate-spin inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full" />
            <p className="text-sm font-medium text-gray-600">Processing...</p>
          </div>
        ) : (
          // Default state
          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20m-8-12l8 8m0 0V8m0 8h8"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-700">Drag and drop your resume here</p>
              <p className="text-xs text-gray-500">or click to browse</p>
            </div>
            <p className="text-xs text-gray-500">PDF files up to 10MB</p>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileInputChange}
        disabled={isProcessing}
        className="hidden"
        aria-label="Upload resume"
      />

      {error && (
        <div className="mt-3 p-3 rounded-lg bg-red-50 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}
