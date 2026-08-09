/**
 * genesis setup
 *
 * First-time environment setup.
 * Creates .env from .env.example and generates a secure JWT_SECRET.
 */

import type { Command } from 'commander';
import { existsSync, readFileSync, writeFileSync, copyFileSync } from 'node:fs';
import path from 'node:path';
import { randomBytes } from 'node:crypto';
import chalk from 'chalk';
import { logStep, logOk, logWarn, logInfo, logErr, c } from '../lib/output.js';
import { REPO_ROOT } from '../lib/compose.js';

const ENV_EXAMPLE = path.join(REPO_ROOT, '.env.example');
const ENV_FILE = path.join(REPO_ROOT, '.env');

export function registerSetupCommand(program: Command): void {
  program
    .command('setup')
    .description('First-time environment setup — creates .env and generates secrets')
    .option('--force', 'Overwrite existing .env file')
    .action(async (opts: { force: boolean }) => {
      logStep('Genesis Setup');

      // Check for .env.example
      if (!existsSync(ENV_EXAMPLE)) {
        logErr('.env.example not found. Are you in the GENESIS_AI repo root?');
        process.exit(1);
      }

      // Handle existing .env
      if (existsSync(ENV_FILE) && !opts.force) {
        logOk('.env already exists. Skipping. (Use --force to overwrite)');
        console.log('');
        logInfo(`Run ${c.info('genesis doctor')} to verify your configuration.`);
        console.log('');
        return;
      }

      if (existsSync(ENV_FILE) && opts.force) {
        logWarn('Overwriting existing .env (--force)');
      }

      // Copy .env.example → .env
      copyFileSync(ENV_EXAMPLE, ENV_FILE);
      logOk('.env created from .env.example');

      // Generate a secure JWT_SECRET
      const secret = randomBytes(32).toString('hex');
      let env = readFileSync(ENV_FILE, 'utf-8');

      if (env.includes('JWT_SECRET=')) {
        env = env.replace(/^JWT_SECRET=.*$/m, `JWT_SECRET=${secret}`);
      } else {
        env += `\nJWT_SECRET=${secret}\n`;
      }

      writeFileSync(ENV_FILE, env, 'utf-8');
      logOk('Generated and set JWT_SECRET');

      console.log('');
      console.log(chalk.green.bold('  Setup complete.'));
      console.log('');
      console.log(chalk.bold('  Next steps:'));
      console.log(`  ${c.muted('1.')} Review ${c.info('.env')} and adjust any values for your environment`);
      console.log(`  ${c.muted('2.')} Run ${c.info('genesis start')} to start core infrastructure`);
      console.log(`  ${c.muted('3.')} Run ${c.info('genesis migrate')} to apply database migrations`);
      console.log(`  ${c.muted('4.')} Run ${c.info('genesis dev')} to start API + web with hot-reload`);
      console.log('');
    });
}
