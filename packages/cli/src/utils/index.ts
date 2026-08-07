/**
 * Genesis CLI — Utilities
 *
 * Shared utility functions for CLI commands.
 * Phase 0.3+: Flesh out implementations.
 */

// ---------------------------------------------------------------------------
// Terminal output helpers
// ---------------------------------------------------------------------------

const Colors = {
  red: '\x1b[0;31m',
  green: '\x1b[0;32m',
  yellow: '\x1b[1;33m',
  blue: '\x1b[0;34m',
  cyan: '\x1b[0;36m',
  bold: '\x1b[1m',
  reset: '\x1b[0m',
} as const;

export function logOk(message: string): void {
  console.log(`  ${Colors.green}✓${Colors.reset} ${message}`);
}

export function logError(message: string): void {
  console.log(`  ${Colors.red}✗${Colors.reset} ${message}`);
}

export function logWarn(message: string): void {
  console.log(`  ${Colors.yellow}⚠${Colors.reset} ${message}`);
}

export function logInfo(message: string): void {
  console.log(`  ${Colors.cyan}→${Colors.reset} ${message}`);
}

export function logStep(message: string): void {
  console.log(`\n${Colors.bold}${Colors.blue}▶ ${message}${Colors.reset}`);
}

// ---------------------------------------------------------------------------
// Environment helpers
// ---------------------------------------------------------------------------

/**
 * Check if Docker is available and running.
 * Phase 0.3+: Implement using child_process.exec
 */
export async function isDockerRunning(): Promise<boolean> {
  // TODO(phase-0.3): Implement
  throw new Error('Not implemented — Phase 0.3');
}

/**
 * Check if a TCP port is available (not in use).
 * Phase 0.3+: Implement using net.createConnection
 */
export async function isPortAvailable(port: number): Promise<boolean> {
  // TODO(phase-0.3): Implement
  throw new Error('Not implemented — Phase 0.3');
}

/**
 * Get available disk space in bytes.
 * Phase 0.3+: Implement using df or statvfs
 */
export async function getAvailableDiskSpace(path: string): Promise<number> {
  // TODO(phase-0.3): Implement
  throw new Error('Not implemented — Phase 0.3');
}

/**
 * Check if a service's HTTP health endpoint responds with 200.
 * Phase 0.3+: Implement using fetch
 */
export async function checkHttpHealth(url: string): Promise<boolean> {
  // TODO(phase-0.3): Implement
  throw new Error('Not implemented — Phase 0.3');
}
