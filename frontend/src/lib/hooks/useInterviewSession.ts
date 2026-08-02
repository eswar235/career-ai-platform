/**
 * Interview Session Hook
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { interviewSessionAPI } from "@/lib/api/interview";
import type {
  InterviewSession,
  InterviewSessionDetail,
  InterviewSessionCreateRequest,
  SessionResultsResponse,
} from "@/lib/types/interview";

export const useInterviewSession = () => {
  const queryClient = useQueryClient();
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    null
  );

  /**
   * Get a specific session
   */
  const getSession = useQuery({
    queryKey: ["interview-session", selectedSessionId],
    queryFn: () => {
      if (!selectedSessionId) return Promise.reject("No session ID");
      return interviewSessionAPI.get(selectedSessionId);
    },
    enabled: !!selectedSessionId,
  });

  /**
   * List all sessions
   */
  const listSessions = (skip?: number, limit?: number) => {
    return useQuery({
      queryKey: ["interview-sessions", skip, limit],
      queryFn: () => interviewSessionAPI.list(skip, limit),
    });
  };

  /**
   * Create session
   */
  const createSession = useMutation({
    mutationFn: (request: InterviewSessionCreateRequest) =>
      interviewSessionAPI.create(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      setSelectedSessionId(data.id);
    },
  });

  /**
   * Complete session
   */
  const completeSession = useMutation({
    mutationFn: (sessionId: string) =>
      interviewSessionAPI.complete(sessionId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      queryClient.invalidateQueries({
        queryKey: ["interview-session", data.session_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["interview-metrics"],
      });
    },
  });

  return {
    getSession,
    listSessions,
    createSession,
    completeSession,
    selectedSessionId,
    setSelectedSessionId,
  };
};
