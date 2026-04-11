/**
 * Real-time activity feed component showing live updates
 * Displays: attendance, assignments, marks, announcements
 */

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { format } from 'date-fns';
import { Bell, CheckCircle2, AlertCircle, BookOpen, Award } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface ActivityItem {
  id: string;
  type: 'attendance' | 'assignment' | 'marks' | 'announcement';
  title: string;
  description: string;
  timestamp: string;
  icon: React.ReactNode;
  color: string; // bg-blue-100, bg-green-100, etc.
  severity?: 'info' | 'warning' | 'success'; // for toast-style display
}

interface RealTimeActivityFeedProps {
  maxItems?: number;
  autoScroll?: boolean;
}

export function RealTimeActivityFeed({ maxItems = 10, autoScroll = true }: RealTimeActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const feedEndRef = React.useRef<HTMLDivElement>(null);

  const { isConnected, on, reconnectAttempts } = useWebSocket();
  const connectionStatus: 'connected' | 'disconnected' | 'reconnecting' =
    isConnected ? 'connected' : reconnectAttempts > 0 ? 'reconnecting' : 'disconnected';

  const addActivity = useCallback((activity: ActivityItem) => {
    setActivities((prev) => [activity, ...prev].slice(0, maxItems));
  }, [maxItems]);

  // Auto-scroll to bottom when new activities are added
  useEffect(() => {
    if (autoScroll && feedEndRef.current) {
      feedEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activities, autoScroll]);

  // Listen for real-time events
  useEffect(() => {
    // Attendance updates
    const unsubAttendance = on('attendance.updated', (data) => {
      const payload = data as { student_id: string; timestamp: string; status: string };
      const activity: ActivityItem = {
        id: `attendance-${payload.student_id}-${payload.timestamp}`,
        type: 'attendance',
        title: 'Attendance Marked',
        description: `Student marked as ${payload.status}`,
        timestamp: payload.timestamp,
        icon: <CheckCircle2 className="w-5 h-5 text-green-600" />,
        color: 'bg-green-50',
        severity: 'success',
      };
      addActivity(activity);
    });

    // Assignment created
    const unsubAssignment = on('assignment.created', (data) => {
      const payload = data as { assignment_id: string; timestamp: string };
      const activity: ActivityItem = {
        id: `assignment-${payload.assignment_id}`,
        type: 'assignment',
        title: 'New Assignment',
        description: 'Assignment has been created for your class',
        timestamp: payload.timestamp,
        icon: <BookOpen className="w-5 h-5 text-blue-600" />,
        color: 'bg-blue-50',
        severity: 'info',
      };
      addActivity(activity);
    });

    // Exam results updated
    const unsubMarks = on('exam.results.updated', (data) => {
      const payload = data as { exam_id: string; score: number; max_score: number; percentage: number; timestamp: string };
      const activity: ActivityItem = {
        id: `marks-${payload.exam_id}`,
        type: 'marks',
        title: 'Exam Results Available',
        description: `Score: ${payload.score}/${payload.max_score} (${payload.percentage}%)`,
        timestamp: payload.timestamp,
        icon: <Award className="w-5 h-5 text-purple-600" />,
        color: 'bg-purple-50',
        severity: 'success',
      };
      addActivity(activity);
    });

    // Generic announcements
    const unsubAnnouncement = on('announcement.sent', (data) => {
      const payload = data as { title?: string; message: string; timestamp: string };
      const activity: ActivityItem = {
        id: `announcement-${payload.timestamp}`,
        type: 'announcement',
        title: payload.title || 'Announcement',
        description: payload.message,
        timestamp: payload.timestamp,
        icon: <Bell className="w-5 h-5 text-amber-600" />,
        color: 'bg-amber-50',
        severity: 'info',
      };
      addActivity(activity);
    });

    return () => {
      unsubAttendance();
      unsubAssignment();
      unsubMarks();
      unsubAnnouncement();
    };
  }, [addActivity, on]);

  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'attendance':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'assignment':
        return <BookOpen className="w-5 h-5 text-blue-600" />;
      case 'marks':
        return <Award className="w-5 h-5 text-purple-600" />;
      case 'announcement':
        return <Bell className="w-5 h-5 text-amber-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 1) return 'just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return format(date, 'MMM d, h:mm a');
    } catch {
      return new Date(timestamp).toLocaleTimeString();
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-gray-700" />
          <h2 className="font-semibold text-gray-900">Live Activity Feed</h2>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : connectionStatus === 'reconnecting' ? 'bg-amber-500' : 'bg-red-500'
            }`}
          />
          <span className="text-xs font-medium text-gray-600">
            {isConnected ? 'Live' : connectionStatus === 'reconnecting' ? 'Reconnecting...' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No activities yet</p>
              <p className="text-xs text-gray-400 mt-1">
                {isConnected ? 'Waiting for live updates...' : 'Connect to receive updates'}
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y">
            {activities.map((activity) => (
              <div key={activity.id} className={`p-4 ${activity.color} hover:bg-gray-50 transition-colors`}>
                <div className="flex gap-3">
                  {/* Icon */}
                  <div className="flex-shrink-0">{getActivityIcon(activity.type)}</div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900">{activity.title}</p>
                    <p className="text-sm text-gray-600 mt-0.5 truncate">{activity.description}</p>
                    <p className="text-xs text-gray-500 mt-1">{formatTime(activity.timestamp)}</p>
                  </div>

                  {/* Badge */}
                  {activity.severity && (
                    <div className={`flex-shrink-0 px-2 py-1 text-xs font-semibold rounded-full ${
                      activity.severity === 'success'
                        ? 'bg-green-200 text-green-800'
                        : activity.severity === 'warning'
                          ? 'bg-amber-200 text-amber-800'
                          : 'bg-blue-200 text-blue-800'
                    }`}>
                      {activity.severity}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        <div ref={feedEndRef} />
      </div>

      {/* Footer - Connection Status */}
      {connectionStatus !== 'connected' && (
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
          {connectionStatus === 'reconnecting' ? (
            <span>Reconnecting (Attempt {reconnectAttempts})...</span>
          ) : (
            <span>Connection lost. Attempting to reconnect...</span>
          )}
        </div>
      )}
    </div>
  );
}
