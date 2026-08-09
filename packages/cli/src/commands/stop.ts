/**
 * genesis stop [--platform] [--volumes]
 *
 * Stop platform services (data is preserved by default).
 *
 * Flags:
 *   --platform  — also stop API + worker + web containers
 *   --volumes   — remove volumes too (DESTRUCTIVE — deletes all data)
 */

import type { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { logStep, logOk, logErr, logWarn, c } from '../lib/output.js';
import { isDockerRunning, runCompose } from '../lib/compose.js';

export function registerStopCommand(program: Command): void {
  program
    .command('stop')
    .description('Stop platform services (data is preserved)')
    .option('--platform', 'Also stop API, worker, and web containers')
    .option('--volumes', 'Remove volumes (DESTRUCTIVE — deletes all data)')
    .action(async (opts: { platform: boolean; volumes: boolean }) => {
      const stack = opts.platform ? 'platform' : 'core';

      if (opts.volumes) {
        logWarn('--volumes will permanently delete PostgreSQL data, NATS data, and MinIO data.');
        logWarn('This cannot be undone.');
        console.log('');
      }

      logStep('Stopping services');

      const spinner = ora({ text: 'Checking Docker...', color: 'cyan' }).start();
      const dockerOk = await isDockerRunning();
      if (!dockerOk) {
        spinner.fail('Docker is not running.');
        process.exit(1);
      }
      spinner.succeed('Docker is running');

      const stopSpinner = ora({ text: 'Stopping...', color: 'cyan' }).start();
      try {
        const args = ['down'];
        if (opts.volumes) args.push('--volumes');
        await runCompose(stack, args, { silent: true });
        stopSpinner.succeed(chalk.bold('Services stopped'));
      } catch (err) {
        stopSpinner.fail(`Failed to stop: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
      }

      console.log('');
      if (opts.volumes) {
        logOk('Volumes removed. All data has been wiped.');
      } else {
        logOk('Data volumes preserved. Run genesis start to restart.');
      }
      console.log('');
      console.log(`  ${c.muted('Run')} ${c.info('genesis start')} ${c.muted('to start again.')}`);
      console.log('');
    });
}
