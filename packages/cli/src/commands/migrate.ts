/**
 * genesis migrate [--check]
 *
 * Run Alembic database migrations.
 *
 * Modes:
 *   (default)   — apply all pending migrations (upgrade head)
 *   --check     — check if migrations are up to date (exits 1 if pending)
 *   --history   — show migration history
 *   --rollback  — roll back one migration step (--rollback N for N steps)
 */

import type { Command } from 'commander';
import path from 'node:path';
import { execa } from 'execa';
import ora from 'ora';
import { logStep, logOk, logErr, logInfo, c } from '../lib/output.js';
import { REPO_ROOT, ENV_FILE } from '../lib/compose.js';

const ALEMBIC_INI = path.join(REPO_ROOT, 'packages/db/alembic.ini');
const DB_PACKAGE = path.join(REPO_ROOT, 'packages/db');

async function buildDatabaseUrl(): Promise<string> {
  const { readFileSync, existsSync } = await import('node:fs');
  if (!existsSync(ENV_FILE)) {
    return 'postgresql://genesis:genesis@localhost:5432/genesis';
  }
  const raw = readFileSync(ENV_FILE, 'utf-8');
  const env: Record<string, string> = {};
  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
    const idx = trimmed.indexOf('=');
    env[trimmed.slice(0, idx).trim()] = trimmed.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
  }
  if (env['DATABASE_URL']) return env['DATABASE_URL'];
  const user = env['POSTGRES_USER'] ?? 'genesis';
  const pass = env['POSTGRES_PASSWORD'] ?? 'genesis';
  const host = env['GENESIS_DEV_SERVICE_HOST'] ?? 'localhost';
  const port = env['POSTGRES_PORT'] ?? '5432';
  const db = env['POSTGRES_DB'] ?? 'genesis';
  return `postgresql://${user}:${pass}@${host}:${port}/${db}`;
}

export function registerMigrateCommand(program: Command): void {
  program
    .command('migrate')
    .description('Run database migrations (Alembic)')
    .option('--check', 'Check if migrations are up to date (exits 1 if pending)')
    .option('--history', 'Show migration history')
    .option('--rollback [steps]', 'Roll back N migrations (default: 1)')
    .action(async (opts: { check: boolean; history: boolean; rollback: string | boolean }) => {
      logStep('Database Migrations');

      const databaseUrl = await buildDatabaseUrl();
      logInfo(`Database: ${c.muted(databaseUrl.replace(/:[^:@]+@/, ':***@'))}`);

      const baseEnv = { ...process.env, DATABASE_URL: databaseUrl };
      const alembicBase = ['run', '-p', DB_PACKAGE, 'alembic', '-c', ALEMBIC_INI];

      if (opts.history) {
        // Show history
        logStep('Migration History');
        try {
          await execa('uv', [...alembicBase, 'history', '--verbose'], {
            cwd: REPO_ROOT,
            env: baseEnv,
            stdio: 'inherit',
          });
        } catch {
          logErr('Failed to fetch migration history');
          process.exit(1);
        }
        return;
      }

      if (opts.rollback !== undefined && opts.rollback !== false) {
        const steps = typeof opts.rollback === 'string' ? parseInt(opts.rollback, 10) : 1;
        const target = `-${steps}`;
        logInfo(`Rolling back ${steps} migration(s)...`);
        const spinner = ora({ text: 'Rolling back...', color: 'cyan' }).start();
        try {
          await execa('uv', [...alembicBase, 'downgrade', target], {
            cwd: REPO_ROOT,
            env: baseEnv,
            stdio: 'pipe',
          });
          spinner.succeed(`Rolled back ${steps} migration(s)`);
        } catch (err) {
          spinner.fail(`Rollback failed: ${err instanceof Error ? err.message : String(err)}`);
          process.exit(1);
        }
        return;
      }

      if (opts.check) {
        // Check mode — exits 1 if not up to date
        logInfo('Checking migration state...');
        try {
          await execa('uv', [...alembicBase, 'check'], {
            cwd: REPO_ROOT,
            env: baseEnv,
            stdio: 'pipe',
          });
          logOk('Database is up to date. No pending migrations.');
        } catch {
          logErr('Database has pending migrations. Run genesis migrate to apply.');
          process.exit(1);
        }
        return;
      }

      // Default: upgrade head
      const spinner = ora({ text: 'Applying migrations...', color: 'cyan' }).start();
      try {
        const result = await execa('uv', [...alembicBase, 'upgrade', 'head'], {
          cwd: REPO_ROOT,
          env: baseEnv,
          stdio: 'pipe',
        });
        spinner.succeed('Migrations applied');
        if (result.stdout) {
          console.log('');
          console.log(result.stdout
            .split('\n')
            .map((l) => `  ${c.muted(l)}`)
            .join('\n'));
        }
      } catch (err) {
        spinner.fail(`Migration failed: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
      }

      console.log('');
    });
}
