/**
 * genesis logs [service] [--follow] [--tail N]
 *
 * Tail logs from platform services.
 *
 * Examples:
 *   genesis logs               — show all core infra logs (last 50 lines)
 *   genesis logs api           — show genesis-api logs
 *   genesis logs -f            — follow all core infra logs
 *   genesis logs api -f        — follow API logs
 *   genesis logs --tail 200    — show last 200 lines
 */

import type { Command } from 'commander';
import { execa } from 'execa';
import { logStep, logErr, c } from '../lib/output.js';
import { REPO_ROOT } from '../lib/compose.js';
import path from 'node:path';

const CORE_COMPOSE = path.join(REPO_ROOT, 'infrastructure/docker/compose/docker-compose.yml');
const PLATFORM_COMPOSE = path.join(REPO_ROOT, 'infrastructure/docker/compose/docker-compose.platform.yml');

// Map short names to container names
const SERVICE_ALIASES: Record<string, string> = {
  api: 'genesis-api',
  web: 'genesis-web',
  worker: 'genesis-worker',
  postgres: 'genesis-postgres',
  pg: 'genesis-postgres',
  nats: 'genesis-nats',
  minio: 'genesis-minio',
};

export function registerLogsCommand(program: Command): void {
  program
    .command('logs [service]')
    .description('Tail platform service logs')
    .option('-f, --follow', 'Follow log output (stream)')
    .option('-n, --tail <lines>', 'Number of lines to show from end', '50')
    .option('--platform', 'Include platform services (api, worker, web)')
    .action(async (service: string | undefined, opts: { follow: boolean; tail: string; platform: boolean }) => {
      const stack = opts.platform || service && ['api', 'web', 'worker'].includes(service)
        ? 'platform'
        : 'core';

      const composeFiles = ['-f', CORE_COMPOSE];
      if (stack === 'platform') composeFiles.push('-f', PLATFORM_COMPOSE);

      const args = ['compose', ...composeFiles, 'logs', `--tail=${opts.tail}`];
      if (opts.follow) args.push('-f');

      // Resolve service alias
      if (service) {
        const resolved = SERVICE_ALIASES[service] ?? service;
        args.push(resolved);
        logStep(`Logs: ${resolved}`);
      } else {
        logStep(`Logs: all ${stack} services`);
      }

      console.log(`  ${c.muted(`--tail ${opts.tail}${opts.follow ? '  -f (streaming)' : ''}`)}`);
      console.log('');

      try {
        const proc = execa('docker', args, {
          cwd: REPO_ROOT,
          stdio: 'inherit',
        });
        await proc;
      } catch (err: unknown) {
        // Gracefully handle SIGINT (Ctrl+C) from user
        const isExeca = typeof err === 'object' && err !== null && 'exitCode' in err;
        if (isExeca && (err as { signal?: string }).signal === 'SIGINT') {
          console.log('');
          return;
        }
        logErr(`Failed to fetch logs: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
      }
    });
}
