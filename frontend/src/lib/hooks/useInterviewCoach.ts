/**
 * Interview Coach Hook
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  interviewQuestionAPI,
  interviewAnswerAPI,
  interviewMetricsAPI,
} from "@/lib/api/interview";
import type {
  InterviewQuestion,
  InterviewAnswer,
  InterviewMetrics,
  InterviewAnswerCreateRequest,
} from "@/lib/types/interview";

export const useInterviewCoach = () => {
  const queryClient = useQueryClient();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [sessionStartTime] = useState(new Date());

  /**
   * Get questions for a session
   */
  const getQuestions = (sessionId: string) => {
    return useQuery({
      queryKey: ["interview-questions", sessionId],
      queryFn: () => interviewQuestionAPI.getQuestions(sessionId),
      enabled: !!sessionId,
    });
  };

  /**
   * Submit answer to question
   */
  const submitAnswer = useMutation({
    mutationFn: ({
      questionId,
      request,
    }: {
      questionId: string;
      request: InterviewAnswerCreateRequest;
    }) => interviewAnswerAPI.submitAnswer(questionId, request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["interview-question", data.question_id],
      });
    },
  });

  /**
   * Get performance metrics
   */
  const getMetrics = useQuery({
    queryKey: ["interview-metrics"],
    queryFn: () => interviewMetricsAPI.getMetrics(),
  });

  /**
   * Move to next question
   */
  const nextQuestion = () => {
    setCurrentQuestionIndex((prev) => prev + 1);
  };

  /**
   * Move to previous question
   */
  const previousQuestion = () => {
    setCurrentQuestionIndex((prev) => Math.max(0, prev - 1));
  };

  /**
   * Reset to first question
   */
  const resetQuestions = () => {
    setCurrentQuestionIndex(0);
  };

  /**
   * Calculate elapsed time
   */
  const getElapsedTime = (): number => {
    return Math.floor(
      (new Date().getTime() - sessionStartTime.getTime()) / 1000
    );
  };

  return {
    getQuestions,
    submitAnswer,
    getMetrics,
    currentQuestionIndex,
    setCurrentQuestionIndex,
    nextQuestion,
    previousQuestion,
    resetQuestions,
    getElapsedTime,
  };
};
