/**
 * AI Session Tracking API Client
 * Captures student learning activity in AI Studio for dashboards and parent insights.
 */

import { api } from "../api";

export interface AISessionEventCreate {
  session_id: string;
  tool_mode: string;
  subject?: string | null;
  topic?: string | null;
  queries_count?: number;
  total_duration_seconds?: number;
  engagement_score?: number;
  key_concepts?: string;
  misconceptions?: string;
  mastery_level?: string;
  confidence_change?: number;
  was_quiz_attempted?: boolean;
  quiz_score_percent?: number | null;
  flashcard_correct_count?: number;
  flashcard_total_shown?: number;
}

export interface AISessionEventUpdate {
  ended_at: string; // ISO datetime string
  total_duration_seconds?: number;
  engagement_score?: number;
  key_concepts?: string;
  misconceptions?: string;
  mastery_level?: string;
  confidence_change?: number;
  was_quiz_attempted?: boolean;
  quiz_score_percent?: number | null;
  flashcard_correct_count?: number;
  flashcard_total_shown?: number;
}

export interface AISessionEventResponse {
  id: string;
  session_id: string;
  tool_mode: string;
  subject: string | null;
  topic: string | null;
  queries_count: number;
  total_duration_seconds: number;
  engagement_score: number;
  mastery_level: string;
  confidence_change: number;
  was_quiz_attempted: boolean;
  quiz_score_percent: number | null;
  started_at: string;
  ended_at: string | null;
}

export interface AISessionSummary {
  session_id: string;
  tool_mode: string;
  subject: string | null;
  topic: string | null;
  duration_seconds: number;
  engagement_score: number;
  mastery_level: string;
  quiz_score_percent: number | null;
  started_at: string;
  ended_at: string | null;
  key_insights: string[];
}

export interface ParentInsightsSummary {
  total_sessions: number;
  total_study_time_hours: number;
  active_subjects: string[];
  average_engagement: number;
  recent_topics: string[];
  quiz_attempts: number;
  average_quiz_score: number | null;
  mastery_progress: Record<string, string>;
  recommended_topics: string[];
}

export const sessionTracking = {
  /**
   * Create a new AI session event (called when session starts)
   */
  async createSession(event: AISessionEventCreate): Promise<AISessionEventResponse> {
    return api.sessionTracking.createSession(event);
  },

  /**
   * Update an existing session event (called when session ends)
   */
  async updateSession(
    sessionEventId: string,
    update: AISessionEventUpdate
  ): Promise<AISessionEventResponse> {
    return api.sessionTracking.updateSession(sessionEventId, update);
  },

  /**
   * Get recent sessions for current student
   */
  async getRecentSessions(days: number = 7, limit: number = 10): Promise<AISessionSummary[]> {
    return api.sessionTracking.getRecentSessions(days, limit);
  },

  /**
   * Get all sessions for a specific subject
   */
  async getSessionsBySubject(
    subject: string,
    days: number = 30
  ): Promise<AISessionSummary[]> {
    return api.sessionTracking.getSessionsBySubject(subject, days);
  },

  /**
   * Get parent-friendly insights for child's learning activity
   */
  async getParentInsights(childId?: string, days: number = 30): Promise<ParentInsightsSummary> {
    return api.sessionTracking.getParentInsights(childId, days);
  },
};
