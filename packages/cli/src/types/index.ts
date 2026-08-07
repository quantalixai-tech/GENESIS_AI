/**
 * Genesis CLI — Types
 *
 * Shared type definitions for the CLI.
 */

// ---------------------------------------------------------------------------
// Command types
// ---------------------------------------------------------------------------

export interface Command {
  name: string;
  description: string;
  handler: (args?: CommandArgs) => Promise<void>;
}

export interface CommandArgs {
  [key: string]: string | boolean | number | undefined;
}

// ---------------------------------------------------------------------------
// Health check types (mirrors docs/rfc/0004-health.md)
// ---------------------------------------------------------------------------

export type HealthStatus = 'healthy' | 'unhealthy' | 'unknown' | 'skipped';

export interface HealthCheck {
  name: string;
  status: HealthStatus;
  message?: string;
  details?: Record<string, unknown>;
  required: boolean;
}

export interface HealthReport {
  overall: HealthStatus;
  checks: HealthCheck[];
  timestamp: string;
  duration: number;
}

// ---------------------------------------------------------------------------
// Service types
// ---------------------------------------------------------------------------

export type ServiceLayer = 'core' | 'ai' | 'platform' | 'observability';

export interface ServiceInfo {
  name: string;
  layer: ServiceLayer;
  port: number;
  status: 'running' | 'stopped' | 'unknown';
  health: HealthStatus;
}

// ---------------------------------------------------------------------------
// CLI output types
// ---------------------------------------------------------------------------

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface CLIOutput {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
}
