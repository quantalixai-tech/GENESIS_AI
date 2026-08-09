/**
 * genesis status [--platform]
 *
 * Show a live table of all service health statuses.
 *
 * Queries docker compose ps and the API health endpoint.
 */

import type { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { logStep, printServiceTable, c } from '../lib/output.js';
import { isDockerRunning, getServiceStatus } from '../lib/compose.js';

export function registerStatusCommand(program: Command): void {
  program
    .command('status')
    .description('Show service health status')
    .option('--platform', 'Include API, worker, and web service status')
    .option('--json', 'Output as JSON')
    .action(async (opts: { platform: boolean; json: boolean }) => {
      const stack = opts.platform ? 'platform' : 'core';

      const spinner = ora({ text: 'Fetching status...', color: 'cyan' }).start();

      const dockerOk = await isDockerRunning();
      if (!dockerOk) {
        spinner.fail('Docker is not running.');
        process.exit(1);
      }

      const rows = await getServiceStatus(stack);
      spinner.stop();

      if (opts.json) {
        process.stdout.write(JSON.stringify(rows, null, 2) + '\n');
        return;
      }

      if (rows.length === 0) {
        logStep('Service Status');
        console.log('');
        console.log(`  ${c.muted('No services running. Run')} ${c.info('genesis start')} ${c.muted('to start.')}`);
        console.log('');
        return;
      }

      logStep('Service Status');
      printServiceTable(rows);

      const healthy = rows.filter((r) => r.status === 'healthy' || r.status === 'running').length;
      const total = rows.length;

      if (healthy === total) {
        console.log(chalk.green.bold(`  All ${total} services healthy`));
      } else {
        console.log(chalk.yellow(`  ${healthy}/${total} services healthy`));
      }
      console.log('');
    });
}
