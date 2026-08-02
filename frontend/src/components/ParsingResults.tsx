/**
 * ParsingResults component for displaying and editing parsed resume data
 */

'use client';

import React, { useState } from 'react';
import { ParsedResumeResponse } from '@/lib/api/parsing';

interface ParsingResultsProps {
  parsedResume: ParsedResumeResponse;
  loading?: boolean;
  onUpdate?: (updates: Partial<ParsedResumeResponse>) => Promise<void>;
  onConfirm?: () => Promise<void>;
}

export function ParsingResults({
  parsedResume,
  loading = false,
  onUpdate,
  onConfirm,
}: ParsingResultsProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(parsedResume);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!onUpdate) return;

    try {
      setSaving(true);
      await onUpdate(editData);
      setIsEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleConfirm = async () => {
    if (!onConfirm) return;

    try {
      setSaving(true);
      await onConfirm();
    } finally {
      setSaving(false);
    }
  };

  const confidenceColor =
    parsedResume.confidence_score !== undefined
      ? parsedResume.confidence_score >= 80
        ? 'text-green-700 bg-green-50'
        : parsedResume.confidence_score >= 60
          ? 'text-yellow-700 bg-yellow-50'
          : 'text-orange-700 bg-orange-50'
      : 'text-gray-700 bg-gray-50';

  return (
    <div className="space-y-6">
      {/* Header with Confidence Score */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Parsing Results</h2>
          <p className="mt-1 text-gray-600">Review extracted information below</p>
        </div>
        {parsedResume.confidence_score !== undefined && (
          <div className={`px-4 py-2 rounded-lg text-sm font-medium ${confidenceColor}`}>
            {parsedResume.confidence_score}% Confidence
          </div>
        )}
      </div>

      {/* Personal Information */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>

        {isEditing ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Full Name"
                value={editData.full_name || ''}
                onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="email"
                placeholder="Email"
                value={editData.email || ''}
                onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="tel"
                placeholder="Phone"
                value={editData.phone || ''}
                onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Location"
                value={editData.location || ''}
                onChange={(e) => setEditData({ ...editData, location: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <textarea
              placeholder="Professional Summary"
              value={editData.summary || ''}
              onChange={(e) => setEditData({ ...editData, summary: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
          </div>
        ) : (
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-600">Name</dt>
              <dd className="text-gray-900">{parsedResume.full_name || '-'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Email</dt>
              <dd className="text-gray-900">{parsedResume.email || '-'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Phone</dt>
              <dd className="text-gray-900">{parsedResume.phone || '-'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Location</dt>
              <dd className="text-gray-900">{parsedResume.location || '-'}</dd>
            </div>
            {parsedResume.summary && (
              <div className="col-span-2">
                <dt className="text-sm font-medium text-gray-600">Summary</dt>
                <dd className="text-gray-900 mt-1">{parsedResume.summary}</dd>
              </div>
            )}
          </dl>
        )}
      </div>

      {/* Skills */}
      {parsedResume.skills && parsedResume.skills.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills</h3>
          <div className="space-y-2">
            {parsedResume.skills.map((skill, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <p className="font-medium text-gray-900">{skill.name}</p>
                  <p className="text-sm text-gray-600">
                    {skill.proficiency}
                    {skill.years && ` • ${skill.years} years`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Experience */}
      {parsedResume.experience && parsedResume.experience.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Experience</h3>
          <div className="space-y-4">
            {parsedResume.experience.map((exp, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4">
                <p className="font-semibold text-gray-900">{exp.title}</p>
                <p className="text-sm text-gray-600">{exp.company}</p>
                {exp.start_date && (
                  <p className="text-sm text-gray-500">
                    {exp.start_date}
                    {exp.end_date && ` - ${exp.end_date}`}
                  </p>
                )}
                {exp.description && <p className="text-sm text-gray-700 mt-2">{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {parsedResume.education && parsedResume.education.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Education</h3>
          <div className="space-y-4">
            {parsedResume.education.map((edu, idx) => (
              <div key={idx} className="border-l-4 border-green-500 pl-4">
                <p className="font-semibold text-gray-900">{edu.degree}</p>
                <p className="text-sm text-gray-600">{edu.institution}</p>
                {edu.field && <p className="text-sm text-gray-500">Field: {edu.field}</p>}
                {edu.year && <p className="text-sm text-gray-500">{edu.year}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        {isEditing ? (
          <>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              onClick={() => {
                setEditData(parsedResume);
                setIsEditing(false);
              }}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setIsEditing(true)}
              disabled={loading}
              className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Edit Information
            </button>
            {!parsedResume.is_confirmed && onConfirm && (
              <button
                onClick={handleConfirm}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {saving ? 'Confirming...' : 'Confirm & Continue'}
              </button>
            )}
          </>
        )}
      </div>

      {parsedResume.is_confirmed && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-800">✓ Parsing confirmed and saved</p>
        </div>
      )}
    </div>
  );
}
