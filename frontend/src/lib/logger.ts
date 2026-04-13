/**
 * Centralized logging service for frontend application.
 * Implements consistent error/warning/info logging across components.
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, unknown>;
  error?: Error;
}

class Logger {
  private static isDevelopment = process.env.NODE_ENV === 'development';
  private static isProduction = process.env.NODE_ENV === 'production';
  private static logBuffer: LogEntry[] = [];
  private static maxBufferSize = 100;

  /**
   * Log an error message with optional context and error object.
   * Errors are always logged regardless of environment.
   */
  static error(message: string, error?: Error | unknown, context?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'error',
      message,
      context,
      error: error instanceof Error ? error : undefined,
    };

    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift();
    }

    if (this.isDevelopment) {
      console.error(`[ERROR] ${message}`, error, context);
    }

    // In production, send to error tracking service (Sentry, etc.)
    if (this.isProduction) {
      this.reportToErrorService(entry);
    }
  }

  /**
   * Log a warning message with optional context.
   * Warnings are logged in development mode only.
   */
  static warn(message: string, context?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'warn',
      message,
      context,
    };

    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift();
    }

    if (this.isDevelopment) {
      console.warn(`[WARN] ${message}`, context);
    }
  }

  /**
   * Log an info message with optional context.
   * Info messages are logged in development mode only.
   */
  static info(message: string, context?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'info',
      message,
      context,
    };

    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift();
    }

    if (this.isDevelopment) {
      console.info(`[INFO] ${message}`, context);
    }
  }

  /**
   * Log a debug message with optional context.
   * Debug messages are logged in development mode only.
   */
  static debug(message: string, context?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'debug',
      message,
      context,
    };

    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift();
    }

    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${message}`, context);
    }
  }

  /**
   * Get recent log entries (useful for debugging and support).
   */
  static getRecentLogs(count: number = 20): LogEntry[] {
    return this.logBuffer.slice(-count);
  }

  /**
   * Clear log buffer.
   */
  static clearBuffer() {
    this.logBuffer.length = 0;
  }

  /**
   * Report error to external error tracking service.
   * Placeholder for Sentry, LogRocket, or similar integration.
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  private static reportToErrorService(entry: LogEntry) {
    // TODO: Integrate with error tracking service (Sentry, LogRocket, etc.)
    // Example:
    // if (typeof window !== 'undefined' && (window as any).Sentry) {
    //   (window as any).Sentry.captureException(entry.error || new Error(entry.message));
    // }
  }
}

export const logger = Logger;
