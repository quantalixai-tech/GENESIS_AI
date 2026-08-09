/**
 * genesis dev [--api-only | --web-only]
 *
 * Start the API and/or web in development mode with hot-reload.
 *
 * This runs processes DIRECTLY — not as Docker containers.
 * Core infrastructure (postgres, nats, minio) must already be running.
 *
 * Works identically inside a devcontainer and on a local machine.
 *
 * How it works:
 *   API  — uvicorn with --reload, watching apps/api/src and packages/db
 *   Web  — pnpm dev (Next.js HMR)
 *
 * When running both (default), they are started in parallel and both
 * log to stdout with prefixed labels [api] and [web].
 */

import type { Command } from 'commander';
import path from 'node:path';
import { execa } from 'execa';
import chalk from 'chalk';
import { logStep, logInfo, logErr, logOk, c } from '../lib/output.js';
import { isPortListening, REPO_ROOT, ENV_FILE } from '../lib/compose.js';

// Load .env into the process environment for child processes
async function loadEnv(): Promise<Record<string, string>> {
  const env: Record<string, string> = {};
  try {
    const { readFileSync, existsSync } = await import('node:fs');
    if (!existsSync(ENV_FILE)) return env;
    const raw = readFileSync(ENV_FILE, 'utf-8');
    for (const line of raw.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('='))
        continue;
      const idx = trimmed.indexOf('=');
      const key = trimmed.slice(0, idx).trim();
      const val = trimmed
        .slice(idx + 1)
        .trim()
        .replace(/^["']|["']$/g, '');
      env[key] = val;
    }
  } catch {
    // ignore
  }
  return env;
}

export function registerDevCommand(program: Command): void {
  program
    .command('dev')
    .description(
      'Start API and web in development mode (hot-reload, no Docker rebuild needed)',
    )
    .option('--api', 'Start API only')
    .option('--web', 'Start web only')
    .option('--port-api <port>', 'API port', '8080')
    .option('--port-web <port>', 'Web port', '3000')
    .action(
      async (opts: {
        api: boolean;
        web: boolean;
        portApi: string;
        portWeb: string;
      }) => {
        const apiOnly = opts.api && !opts.web;
        const webOnly = opts.web && !opts.api;
        const both = !apiOnly && !webOnly;

        logStep('Genesis Dev Mode');
        logInfo(
          'Running API and web as processes (hot-reload, not Docker containers)',
        );
        console.log('');

        // Load env
        const dotenv = await loadEnv();
        const mergedEnv = { ...process.env, ...dotenv };

        // Build DATABASE_URL from env
        const pgUser = dotenv['POSTGRES_USER'] ?? 'genesis';
        const pgPass = dotenv['POSTGRES_PASSWORD'] ?? 'genesis';
        const pgHost =
          process.env['GENESIS_DEV_SERVICE_HOST'] ??
          dotenv['GENESIS_DEV_SERVICE_HOST'] ??
          'localhost';
        const pgPort = dotenv['POSTGRES_PORT'] ?? '5432';
        const pgDb = dotenv['POSTGRES_DB'] ?? 'genesis';
        const databaseUrl = `postgresql://${pgUser}:${pgPass}@${pgHost}:${pgPort}/${pgDb}`;

        // Check postgres is up (required for API)
        if (!webOnly) {
          const pgOk = await isPortListening(parseInt(pgPort, 10), pgHost);
          if (!pgOk) {
            logErr(`PostgreSQL is not reachable on ${pgHost}:${pgPort}.`);
            logInfo(
              `Run ${chalk.cyan('genesis start')} to start core infrastructure first.`,
            );
            process.exit(1);
          }
          logOk(`PostgreSQL reachable on ${pgHost}:${pgPort}`);
        }

        const apiSrc = path.join(REPO_ROOT, 'apps/api/src');
        const pkgDb = path.join(REPO_ROOT, 'packages/db');

        const procs: Promise<void>[] = [];

        // === API dev process ===
        if (!webOnly) {
          logInfo(`Starting API on :${opts.portApi} with hot-reload`);

          const apiEnv = {
            ...mergedEnv,
            DATABASE_URL: databaseUrl,
            PYTHONPATH: `${apiSrc}:${pkgDb}${process.env['PYTHONPATH'] ? `:${process.env['PYTHONPATH']}` : ''}`,
          };

          const apiProc = (async () => {
            try {
              const proc = execa(
                'uv',
                [
                  'run',
                  '--package',
                  'api',
                  'uvicorn',
                  'main:app',
                  '--app-dir',
                  apiSrc,
                  '--host',
                  '0.0.0.0',
                  '--port',
                  opts.portApi,
                  '--reload-dir',
                  apiSrc,
                  '--reload-dir',
                  path.join(pkgDb, 'genesis_db'),
                  '--reload',
                ],
                {
                  cwd: REPO_ROOT,
                  env: apiEnv,
                  stdio: 'pipe',
                },
              );

              const prefix = chalk.hex('#6366f1')('[api] ');
              proc.stdout?.on('data', (d: Buffer) => {
                for (const line of d.toString().split('\n').filter(Boolean)) {
                  process.stdout.write(prefix + line + '\n');
                }
              });
              proc.stderr?.on('data', (d: Buffer) => {
                for (const line of d.toString().split('\n').filter(Boolean)) {
                  process.stdout.write(prefix + chalk.yellow(line) + '\n');
                }
              });

              await proc;
            } catch (err: unknown) {
              const isExeca =
                typeof err === 'object' && err !== null && 'signal' in err;
              if (isExeca && (err as { signal?: string }).signal === 'SIGINT')
                return;
              logErr(
                `API process exited: ${err instanceof Error ? err.message : String(err)}`,
              );
            }
          })();

          procs.push(apiProc);
        }

        // === Web dev process ===
        if (!apiOnly) {
          logInfo(`Starting Web on :${opts.portWeb} with HMR`);

          const webProc = (async () => {
            try {
              const proc = execa(
                'pnpm',
                ['--filter', 'web', 'dev'],
                {
                  cwd: REPO_ROOT,
                  env: {
                    ...mergedEnv,
                    PORT: opts.portWeb,
                    NEXT_PUBLIC_API_URL: `http://localhost:${opts.portApi}/api/v1`,
                    API_URL: `http://localhost:${opts.portApi}/api/v1`,
                  },
                  stdio: 'pipe',
                },
              );

              const prefix = chalk.hex('#10b981')('[web] ');
              proc.stdout?.on('data', (d: Buffer) => {
                for (const line of d.toString().split('\n').filter(Boolean)) {
                  process.stdout.write(prefix + line + '\n');
                }
              });
              proc.stderr?.on('data', (d: Buffer) => {
                for (const line of d.toString().split('\n').filter(Boolean)) {
                  process.stdout.write(prefix + chalk.yellow(line) + '\n');
                }
              });

              await proc;
            } catch (err: unknown) {
              const isExeca =
                typeof err === 'object' && err !== null && 'signal' in err;
              if (isExeca && (err as { signal?: string }).signal === 'SIGINT')
                return;
              logErr(
                `Web process exited: ${err instanceof Error ? err.message : String(err)}`,
              );
            }
          })();

          procs.push(webProc);
        }

        console.log('');
        if (both || !webOnly)
          console.log(
            `  ${c.info('API')}  → http://localhost:${opts.portApi}/docs`,
          );
        if (both || !apiOnly)
          console.log(`  ${c.ok('Web')}  → http://localhost:${opts.portWeb}`);
        console.log('');
        console.log(`  ${c.muted('Press Ctrl+C to stop.')}`);
        console.log('');

        // Handle SIGINT gracefully
        process.on('SIGINT', () => {
          console.log('');
          logInfo('Shutting down dev processes...');
          process.exit(0);
        });

        await Promise.all(procs);
      },
    );
}
