/**
 * genesis doctor
 *
 * Run platform pre-flight health checks.
 * Checks: Docker, required ports, .env, disk space, API health.
 */

import type { Command } from 'commander';
import { statfs } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import chalk from 'chalk';
import {
  logStep,
  logOk,
  logWarn,
  logErr,
  logInfo,
  c,
} from '../lib/output.js';
import { isDockerRunning, isPortListening, checkApiHealth, REPO_ROOT, ENV_FILE } from '../lib/compose.js';

const REQUIRED_PORTS = [
  { port: 5432, label: 'PostgreSQL', hostEnv: 'GENESIS_DEV_SERVICE_HOST' },
  { port: 4222, label: 'NATS', hostEnv: 'GENESIS_DEV_NATS_HOST' },
  { port: 8222, label: 'NATS Monitor', hostEnv: 'GENESIS_DEV_NATS_HOST' },
  { port: 9000, label: 'MinIO', hostEnv: 'GENESIS_DEV_MINIO_HOST' },
  { port: 9001, label: 'MinIO Console', hostEnv: 'GENESIS_DEV_MINIO_HOST' },
  { port: 8080, label: 'API (genesis dev)', hostEnv: null },
  { port: 3000, label: 'Web (genesis dev)', hostEnv: null },
];

const MIN_DISK_GB = 5;

export function registerDoctorCommand(program: Command): void {
  program
    .command('doctor')
    .description('Run platform health checks')
    .option('--json', 'Output results as JSON')
    .action(async (opts: { json: boolean }) => {
      logStep('Genesis Doctor — Pre-flight Checks');

      const results: Array<{ check: string; ok: boolean; detail: string }> = [];

      const check = (label: string, ok: boolean, detail: string) => {
        results.push({ check: label, ok, detail });
        if (ok) {
          logOk(`${label.padEnd(24)} ${c.muted(detail)}`);
        } else {
          logErr(`${label.padEnd(24)} ${c.muted(detail)}`);
        }
      };

      // 1. Docker
      const dockerOk = await isDockerRunning();
      check('Docker daemon', dockerOk, dockerOk ? 'running' : 'not running — start Docker Desktop');

      // 2. .env file
      const envOk = existsSync(ENV_FILE);
      check('.env file', envOk, envOk ? ENV_FILE : 'missing — copy .env.example to .env');

      // 3. JWT_SECRET in .env
      let jwtOk = false;
      if (envOk) {
        const { readFileSync } = await import('node:fs');
        const env = readFileSync(ENV_FILE, 'utf-8');
        const match = env.match(/^JWT_SECRET=(.+)$/m);
        jwtOk = !!(match?.[1]?.trim());
      }
      check('JWT_SECRET set', jwtOk, jwtOk ? 'set' : 'missing — set JWT_SECRET in .env');

      // 4. Disk space
      try {
        const stats = await statfs(REPO_ROOT);
        const availableGb = (stats.bfree * stats.bsize) / (1024 ** 3);
        const diskOk = availableGb >= MIN_DISK_GB;
        check(
          'Disk space',
          diskOk,
          `${availableGb.toFixed(1)} GB available (need ${MIN_DISK_GB} GB)`,
        );
      } catch {
        check('Disk space', false, 'unable to check');
      }

      // 5. Core service ports
      logStep('Checking service connectivity');

      for (const { port, label, hostEnv } of REQUIRED_PORTS) {
        const host = (hostEnv ? process.env[hostEnv] : undefined) ?? 'localhost';
        const listening = await isPortListening(port, host);
        const isRequired = port < 8080; // core infra ports are required; app ports are optional
        if (listening) {
          logOk(`${label.padEnd(20)} ${c.muted(`${host}:${port}`)}`);
        } else if (isRequired) {
          logWarn(`${label.padEnd(20)} ${c.muted(`${host}:${port} — not reachable (run: genesis start)`)}`);
        } else {
          logInfo(`${label.padEnd(20)} ${c.muted(`${host}:${port} — not running (optional)`)}`);
        }
      }

      // 6. API health check (only if port 8080 is listening)
      const apiListening = await isPortListening(8080);
      if (apiListening) {
        logStep('API Health');
        const apiHealthy = await checkApiHealth();
        check('API /health', apiHealthy, apiHealthy ? 'HTTP 200' : 'unhealthy response');
      }

      // Summary
      const failed = results.filter((r) => !r.ok);
      console.log('');
      if (failed.length === 0) {
        console.log(chalk.green.bold('  ✓ All checks passed. Platform is ready.'));
      } else {
        console.log(chalk.yellow.bold(`  ⚠ ${failed.length} check(s) need attention:`));
        for (const f of failed) {
          console.log(`    ${c.err('✗')} ${f.check}: ${c.muted(f.detail)}`);
        }
      }
      console.log('');

      if (opts.json) {
        process.stdout.write(JSON.stringify(results, null, 2) + '\n');
      }

      process.exit(failed.some((f) => ['Docker daemon', '.env file', 'JWT_SECRET set'].includes(f.check)) ? 1 : 0);
    });
}
