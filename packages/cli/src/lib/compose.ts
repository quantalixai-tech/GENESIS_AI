/**
 * Genesis CLI — Docker Compose Wrapper
 *
 * Centralizes all docker compose invocations so the file stack
 * is always consistent regardless of which command calls it.
 *
 * Modes:
 *   core      — postgres, nats, minio only
 *   platform  — core + api + worker + web (production images)
 *   full      — platform (alias for production)
 *
 * The compose file stack is the canonical source of truth.
 * Never call `docker compose` directly in command files.
 */

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execa, ExecaError } from 'execa';
import type { ServiceRow } from './output.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, '../../../../');

const CORE_COMPOSE = path.join(
  REPO_ROOT,
  'infrastructure/docker/compose/docker-compose.yml',
);
const PLATFORM_COMPOSE = path.join(
  REPO_ROOT,
  'infrastructure/docker/compose/docker-compose.platform.yml',
);
const ENV_FILE = path.join(REPO_ROOT, '.env');

export type ComposeStack = 'core' | 'platform';

function composeArgs(stack: ComposeStack): string[] {
  const args: string[] = ['-f', CORE_COMPOSE];
  if (stack === 'platform') {
    args.push('-f', PLATFORM_COMPOSE);
  }
  return args;
}

/**
 * Run a docker compose command and stream output to the terminal.
 */
export async function runCompose(
  stack: ComposeStack,
  args: string[],
  options: { silent?: boolean } = {},
): Promise<void> {
  const baseArgs = composeArgs(stack);
  const fullArgs = [...baseArgs, ...args];

  try {
    const proc = execa('docker', ['compose', ...fullArgs], {
      cwd: REPO_ROOT,
      env: { ...process.env },
      stdio: options.silent ? 'pipe' : 'inherit',
    });
    await proc;
  } catch (err) {
    if (err instanceof ExecaError) {
      throw new Error(`docker compose failed (exit ${err.exitCode ?? '?'})`);
    }
    throw err;
  }
}

/**
 * Get the output of a docker compose command as a string.
 */
export async function captureCompose(
  stack: ComposeStack,
  args: string[],
): Promise<string> {
  const baseArgs = composeArgs(stack);
  const fullArgs = [...baseArgs, ...args];

  try {
    const { stdout } = await execa('docker', ['compose', ...fullArgs], {
      cwd: REPO_ROOT,
      env: { ...process.env },
    });
    return stdout;
  } catch {
    return '';
  }
}

/**
 * Parse `docker compose ps --format json` output into ServiceRow objects.
 * Docker outputs one JSON object per line (JSONL).
 */
export async function getServiceStatus(stack: ComposeStack): Promise<ServiceRow[]> {
  const raw = await captureCompose(stack, ['ps', '--format', 'json']);
  if (!raw.trim()) return [];

  const rows: ServiceRow[] = [];

  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    try {
      const svc = JSON.parse(trimmed) as {
        Name?: string;
        Service?: string;
        State?: string;
        Health?: string;
        Image?: string;
        Publishers?: Array<{ PublishedPort?: number; TargetPort?: number }>;
      };

      const name = svc.Service ?? svc.Name ?? '?';
      const state = (svc.State ?? '').toLowerCase();
      const health = (svc.Health ?? '').toLowerCase();

      let status: ServiceRow['status'] = 'unknown';
      if (state === 'running' && health === 'healthy') status = 'healthy';
      else if (state === 'running' && health === 'unhealthy') status = 'unhealthy';
      else if (state === 'running') status = 'running';
      else if (state === 'exited' || state === 'stopped') status = 'stopped';
      else if (state === 'starting') status = 'starting';

      const ports =
        svc.Publishers
          ?.filter((p) => p.PublishedPort && p.PublishedPort > 0)
          .map((p) => `${p.PublishedPort}→${p.TargetPort}`)
          .join(', ') ?? '';

      rows.push({
        name,
        status,
        image: svc.Image ?? '',
        ports,
      });
    } catch {
      // skip unparseable lines
    }
  }

  return rows;
}

/**
 * Check if Docker daemon is accessible.
 */
export async function isDockerRunning(): Promise<boolean> {
  try {
    await execa('docker', ['info'], { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if a TCP port is reachable (service is responding).
 */
export async function isPortListening(port: number): Promise<boolean> {
  const { createConnection } = await import('node:net');
  return new Promise((resolve) => {
    const socket = createConnection({ port, host: 'localhost' });
    socket.once('connect', () => { socket.destroy(); resolve(true); });
    socket.once('error', () => resolve(false));
    socket.setTimeout(1000, () => { socket.destroy(); resolve(false); });
  });
}

/**
 * Check if the API health endpoint responds with 200.
 */
export async function checkApiHealth(port = 8080): Promise<boolean> {
  try {
    const res = await fetch(`http://localhost:${port}/api/health`, {
      signal: AbortSignal.timeout(3000),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export { ENV_FILE };
