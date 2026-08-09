/**
 * genesis start [--platform] [--build]
 *
 * Start platform services.
 *
 * Modes:
 *   (default)    — start core infrastructure only (postgres, nats, minio)
 *   --platform   — start full platform (core + api + worker + web production images)
 *   --build      — rebuild images before starting
 *
 * For development (hot-reload), use: genesis dev
 */

import type { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import {
  logStep,
  logOk,
  logErr,
  printEndpoints,
  c,
} from '../lib/output.js';
import { isDockerRunning, runCompose } from '../lib/compose.js';

const CORE_ENDPOINTS = [
  { label: 'PostgreSQL', url: 'postgresql://localhost:5432/genesis' },
  { label: 'NATS', url: 'nats://localhost:4222' },
  { label: 'NATS Monitor', url: 'http://localhost:8222' },
  { label: 'MinIO API', url: 'http://localhost:9000' },
  { label: 'MinIO Console', url: 'http://localhost:9001' },
];

const PLATFORM_ENDPOINTS = [
  ...CORE_ENDPOINTS,
  { label: 'API', url: 'http://localhost:8080/docs' },
  { label: 'Web', url: 'http://localhost:3000' },
];

export function registerStartCommand(program: Command): void {
  program
    .command('start')
    .description('Start platform services')
    .option('--platform', 'Start full platform (API + worker + web) in addition to core infra')
    .option('--build', 'Rebuild Docker images before starting')
    .option('--no-wait', 'Do not wait for health checks before returning')
    .action(async (opts: { platform: boolean; build: boolean; wait: boolean }) => {
      const stack = opts.platform ? 'platform' : 'core';
      const label = opts.platform ? 'full platform' : 'core infrastructure';

      logStep(`Starting ${label}`);

      // Check Docker is running
      const spinner = ora({ text: 'Checking Docker...', color: 'cyan' }).start();
      const dockerOk = await isDockerRunning();
      if (!dockerOk) {
        spinner.fail('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }
      spinner.succeed('Docker is running');

      // Build if requested
      if (opts.build) {
        logStep('Building images');
        try {
          await runCompose(stack, ['build']);
          logOk('Images built');
        } catch (err) {
          logErr(`Build failed: ${err instanceof Error ? err.message : String(err)}`);
          process.exit(1);
        }
      }

      // Start services
      logStep(opts.platform ? 'Starting core + platform services' : 'Starting core infrastructure');
      const startSpinner = ora({ text: 'Starting services...', color: 'cyan' }).start();

      try {
        await runCompose(stack, ['up', '-d'], { silent: true });
        startSpinner.succeed(`${chalk.bold(label)} started`);
      } catch (err) {
        startSpinner.fail(`Failed to start: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
      }

      // Print endpoints
      printEndpoints(opts.platform ? PLATFORM_ENDPOINTS : CORE_ENDPOINTS);

      console.log(chalk.green.bold('  Platform is up.'));
      console.log('');
      console.log(`  ${c.muted('Run')} ${c.info('genesis status')} ${c.muted('to check service health.')}`);
      console.log(`  ${c.muted('Run')} ${c.info('genesis stop')}   ${c.muted('to stop services.')}`);
      if (!opts.platform) {
        console.log(`  ${c.muted('Run')} ${c.info('genesis dev')}    ${c.muted('to start API + web with hot-reload.')}`);
      }
      console.log('');
    });
}
